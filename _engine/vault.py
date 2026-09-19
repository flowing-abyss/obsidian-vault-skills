#!/usr/bin/env python3
"""Vault engine: validate and edit notes by the vault manifests.

    vault.py check PATH...            validate notes
    vault.py fix PATH...              apply fixed values, defaults, property order
    vault.py types [PREFIX]           list note types with their meaning, for example: types source
    vault.py schema TYPE              fields of one type: meaning, allowed values, what is filled for you
    vault.py new TYPE --title T       create a note (validated before writing)
    vault.py set PATH key=value...    set properties (also: add, remove)
    vault.py find QUERY               list notes by tags and properties (paths only)
    vault.py values TYPE FIELD        values a field accepts (options or allowed link targets)
    vault.py audit                    health report: manifests, templates, every note; --links for bodies
    vault.py checks                   list checks and their severity
    vault.py config                   show the effective config
    vault.py hook AGENT EVENT         agent hook entry point (reads JSON on stdin)

Exit codes: 0 clean, 1 findings or refused write, 2 hook feedback, 3 usage.
Works with any agent. Python 3.9+, standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine import write  # noqa: E402
from engine.findings import LEVELS, describe_options  # noqa: E402
from engine.yamlio import dump_scalar  # noqa: E402
from engine.report import MAX_FINDINGS, render  # noqa: E402
from engine.sources import describe  # noqa: E402
from engine.validate import Engine  # noqa: E402
from engine.vault import DEFAULT_CONFIG, ConfigError, Vault  # noqa: E402

def _schema_name(engine: Engine, path: str) -> str:
    try:
        note = engine.vault.read_note(path)
        schema = engine.schemas.for_note(path, note.frontmatter) if not note.error else None
        return schema.name if schema else ""
    except OSError:
        return ""


def _locate(engine: Engine, ref: str):
    path = engine.vault.locate(ref)
    if path is None:
        print(f'"{ref}" was not found. Pass a vault path, a note name or a task id.', file=sys.stderr)
    return path


def cmd_find(engine: Engine, args) -> int:
    from engine import query
    from engine.vault import tags_of

    columns = [c.strip() for c in (args.show or "").split(",") if c.strip()]
    hits = []
    for path in sorted(engine.vault.notes()):
        fm = engine.vault.frontmatter_of(path)
        if engine.vault.is_ignored(path) or not query.evaluate(args.query, path, tags_of(fm), fm):
            continue
        hits.append(path)
    for path in hits[: args.limit]:
        fm = engine.vault.frontmatter_of(path)
        extra = "".join(f" | {c}: {query.value_text(fm.get(c)) if not isinstance(fm.get(c), list) else ', '.join(map(str, fm.get(c)))}" for c in columns)
        print(path + extra)
    if len(hits) > args.limit:
        print(f"and {len(hits) - args.limit} more. Narrow the query or raise --limit.")
    if not hits:
        print("No notes match.")
    return 0


def cmd_values(engine: Engine, args) -> int:
    schema = engine.schemas.for_type(args.type)
    if schema is None or args.field not in schema.fields:
        known = ", ".join(schema.fields) if schema else "run vault.py schema"
        print(f'Unknown type or field. Known fields: {known}', file=sys.stderr)
        return 1
    field = schema.fields[args.field]
    if field.get("description"):
        print(field["description"])
    current = {k: write.coerce(schema.fields.get(k), v, k) for k, v in write.parse_assignments(args.given or []).items()}
    options = field.get("options")
    if isinstance(options, list):
        print(describe_options(options, limit=500))
        return 0
    source = options.get("source") if isinstance(options, dict) else field.get("source")
    if not isinstance(source, dict):
        print("Any value is accepted.")
        return 0
    res = engine.sources.resolve(source, current)
    if not res.resolved:
        print(f"The values cannot be listed: {res.reason}.")
        return 0
    if describe(source):
        print(describe(source))
    values = sorted(res.values)
    if args.like:
        values = [v for v in values if args.like.lower() in v.lower()]
    print("\n".join(values[: args.limit]) if values else "No values. Check the --given properties.")
    if len(values) > args.limit:
        print(f"and {len(values) - args.limit} more. Use --like TEXT to filter.")
    return 0


def _untyped_note(engine: Engine, path: str, findings) -> str:
    if findings or _schema_name(engine, path):
        return ""
    return " (no manifest matches its tags, so nothing was checked)"


def cmd_check(engine: Engine, args) -> int:
    status, payload = 0, []
    for raw in args.paths:
        path = engine.vault.locate(raw) or engine.vault.rel(raw)
        if not engine.vault.exists(path):
            print(f'"{raw}" was not found in the vault.', file=sys.stderr)
            status = 1
            continue
        findings = engine.check_path(path)
        if any(f.severity in ("error", "warning") for f in findings):
            status = 1
        if args.json:
            payload.append({"path": path, "findings": [f.to_dict() for f in findings]})
        else:
            print(render(path, findings, _schema_name(engine, path)) + _untyped_note(engine, path, findings))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return status


def cmd_fix(engine: Engine, args) -> int:
    writer = write.Writer(engine)
    status = 0
    for raw in args.paths:
        path = engine.vault.locate(raw) or engine.vault.rel(raw)
        try:
            result = writer.fix(path, dry_run=args.dry_run)
        except (write.WriteError, OSError) as exc:
            print(f"{path}: {getattr(exc, 'message', exc)}", file=sys.stderr)
            status = 1
            continue
        verb = "Would fix" if args.dry_run else "Fixed"
        if result.filled:
            print(f"{verb} {path}: {', '.join(result.filled)}")
        print(render(path, result.findings))
        if any(f.severity == "error" for f in result.findings):
            status = 1
    return status


def cmd_types(engine: Engine, args) -> int:
    schemas = engine.schemas
    prefix = (getattr(args, "prefix", None) or "").lstrip("#").lower()
    shown = 0
    for schema in sorted(schemas.all(), key=lambda s: s.type_tag or ""):
        tag = schema.type_tag
        if not tag or (schema.has_children and not schema.own.get("target")):
            continue
        if prefix and not (tag.lower() == prefix or tag.lower().startswith(prefix + "/")):
            continue
        shown += 1
        mark = " (parent, pick a specific type)" if _is_parent(schemas, schema) else ""
        print(f"{tag}  {schema.name}{mark}")
        if schema.description:
            print(f"    {schema.description}")
    if not shown:
        print(f'No note type starts with "{prefix}". Run "vault.py types" to list all.')
    return 0


def cmd_schema(engine: Engine, args) -> int:
    schemas = engine.schemas
    if not args.type:
        return cmd_types(engine, args)
    schema = schemas.for_type(args.type)
    if schema is None:
        print(f'Unknown note type "{args.type}". Run "vault.py schema" to list types.', file=sys.stderr)
        return 1
    print(f"{schema.name}  tag: {schema.type_tag}  folder: {schema.enforce_folder or '-'}")
    if schema.description:
        print(schema.description)
    print(f"Manifest: {' > '.join(schema.chain)}")
    print()
    auto, manual = [], []
    for name in schema.order + [n for n in schema.fields if n not in schema.order]:
        field = schema.fields.get(name)
        if field is None:
            continue
        if field.get("fixed") is not None:
            auto.append(f"{name} = {field['fixed']}")
            continue
        parts = [f"{name}: {field.get('type')}"]
        if field.get("required"):
            parts.append("key must exist, may be empty")
        if name == "tags" and schema.type_tag:
            parts.append(f"default {schema.type_tag}")
        elif field.get("default") is not None:
            parts.append(f"default {dump_scalar(field['default'])}")
        if field.get("min") is not None or field.get("max") is not None:
            parts.append(f"range {field.get('min', '')}..{field.get('max', '')}")
        options = field.get("options")
        listed = None
        if isinstance(options, list):
            listed = options
        elif isinstance(options, dict) and field.get("strict") is not False:
            res = engine.sources.resolve(options.get("source"), {})
            if res.resolved:
                listed = sorted(res.values)
        source = field.get("source")
        if isinstance(source, dict) and describe(source):
            parts.append(describe(source))
        line = "  " + " | ".join(parts)
        if field.get("description"):
            line += f"\n      {field['description']}"
        if listed:
            text = describe_options(listed, limit=200 if args.verbose else 8)
            if field.get("strict") is False:
                text = text.replace("Allowed:", "Known values (other values are accepted too):", 1)
            line += "\n      " + text.replace("\n", "\n      ")
        manual.append(line)
    print("Fields you set:")
    print("\n".join(manual))
    if auto:
        print("\nFilled for you: " + "; ".join(auto) + "; created; updated")
    return 0


def _is_parent(schemas, schema) -> bool:
    tag = schema.type_tag or ""
    return any((s.type_tag or "").startswith(tag + "/") for s in schemas.all())


def _report_write(result, verb: str) -> int:
    print(f"{verb} {result.path}")
    if result.filled:
        print(f"  Filled for you: {', '.join(result.filled)}")
    shown = [f for f in result.findings if f.severity != "info"]
    if shown:
        print(render(result.path, result.findings))
    return 0


def _fail_write(exc: write.WriteError) -> int:
    print(exc.message, file=sys.stderr)
    for f in exc.findings[:MAX_FINDINGS]:
        print("  " + f.line().replace("\n", "\n    "), file=sys.stderr)
    return 1


def cmd_new(engine: Engine, args) -> int:
    body = args.body or ""
    if args.body_file:
        body = sys.stdin.read() if args.body_file == "-" else Path(args.body_file).read_text(encoding="utf-8")
    try:
        values = write.parse_assignments(args.set or [])
        result = write.Writer(engine).new(args.type, args.title, values, body, args.folder, args.dry_run)
    except write.WriteError as exc:
        return _fail_write(exc)
    return _report_write(result, "Would create" if args.dry_run else "Created")


def cmd_change(engine: Engine, args) -> int:
    path = _locate(engine, args.path)
    if path is None:
        return 1
    try:
        values = write.parse_assignments(args.pairs)
        kwargs = {{"set": "set_values", "add": "add_values", "remove": "remove_values"}[args.command]: values}
        result = write.Writer(engine).change(path, dry_run=args.dry_run, **kwargs)
    except write.WriteError as exc:
        return _fail_write(exc)
    return _report_write(result, "Would update" if args.dry_run else "Updated")


def cmd_audit(engine: Engine, args) -> int:
    from engine import audit

    def section(title, lines, note=""):
        print(f"== {title}: {len(lines) if lines else 'ok'}{note}")
        for line in lines[: args.limit]:
            print(f"  {line}")
        if len(lines) > args.limit:
            print(f"  and {len(lines) - args.limit} more. Raise --limit to see them.")

    problems = 0
    if not args.folder and not args.rule:
        for title, lines in (("Manifests", audit.manifests(engine)), ("Sources", audit.sources(engine)),
                             ("Templates", audit.templates(engine))):
            section(title, lines)
            problems += len(lines)

    result = audit.notes(engine, args.folder, args.rule, args.errors)
    files = result["files"]
    problems += len(files)
    print(f"== Notes: {result['checked']} checked, {len(files)} with findings")
    if not args.summary:
        for path, findings in files[: args.limit]:
            print(render(path, findings))
        if len(files) > args.limit:
            print(f"and {len(files) - args.limit} more notes. Raise --limit, or narrow with --folder, --rule, --errors.")
    if result["by_rule"]:
        print("Findings by rule:")
        for rule, n in sorted(result["by_rule"].items(), key=lambda kv: -kv[1]):
            print(f"  {rule:18} {n}")
    if args.summary:
        print("Notes by type:")
        for kind, n in sorted(result["by_type"].items(), key=lambda kv: -kv[1]):
            print(f"  {kind:18} {n}")

    if args.links:
        lines = audit.body_links(engine, args.folder)
        section("Broken links in note bodies", lines)
        problems += len(lines)
    return 1 if problems else 0


def cmd_checks(engine: Engine, args) -> int:
    print(f"Severity levels: {', '.join(LEVELS)}. Override in .claude/_engine/local/config.json under \"checks\".")
    for module in engine.checks + engine.computes:
        origin = "local" if "/local/" in str(getattr(module, "__file__", "")) else "engine"
        level = engine.vault.config.get("checks", {}).get(module.ID, "default")
        print(f"  {module.ID:18} [{origin}] level: {level}\n      {getattr(module, 'ABOUT', '')}")
    return 0


def cmd_config(engine: Engine, args) -> int:
    print(f"Vault: {engine.vault.root}")
    print(f"Schemas root: {engine.vault.schemas_root}")
    print(f"User config: {engine.vault.local_dir / 'config.json'} (optional, holds only your changes)")
    print(f"Keys: {', '.join(sorted(DEFAULT_CONFIG))}")
    print(json.dumps(engine.vault.config, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vault.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--vault", help="vault root (default: found from this file)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("check")
    p.add_argument("paths", nargs="+")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("fix")
    p.add_argument("paths", nargs="+")
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("types")
    p.add_argument("prefix", nargs="?")
    p = sub.add_parser("schema")
    p.add_argument("type", nargs="?")
    p.add_argument("-v", "--verbose", action="store_true", help="describe every option, also in long lists")
    p = sub.add_parser("new")
    p.add_argument("type")
    p.add_argument("--title", required=True)
    p.add_argument("--set", action="append", metavar="key=value", help="repeat a key to build a list")
    p.add_argument("--body")
    p.add_argument("--body-file", help='file with the note body, or "-" for stdin')
    p.add_argument("--folder", help="only for types without enforce_folder")
    p.add_argument("--dry-run", action="store_true")
    for name in ("set", "add", "remove"):
        p = sub.add_parser(name)
        p.add_argument("path")
        p.add_argument("pairs", nargs="+", metavar="key=value")
        p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("find")
    p.add_argument("query", help='for example: "#task AND project=[[Open Vault]] AND status=🟦"')
    p.add_argument("--show", help="properties to print next to each path, comma separated")
    p.add_argument("--limit", type=int, default=30)
    p = sub.add_parser("values")
    p.add_argument("type")
    p.add_argument("field")
    p.add_argument("--given", action="append", metavar="key=value", help="properties the note already has, for related fields")
    p.add_argument("--like", help="keep values that contain this text")
    p.add_argument("--limit", type=int, default=40)
    p = sub.add_parser("audit")
    p.add_argument("--folder")
    p.add_argument("--summary", action="store_true")
    p.add_argument("--errors", action="store_true", help="errors only")
    p.add_argument("--rule", help="only this rule id, for example link-exists")
    p.add_argument("--links", action="store_true", help="also report broken wikilinks in note bodies")
    p.add_argument("--limit", type=int, default=40)
    sub.add_parser("checks")
    sub.add_parser("config")
    p = sub.add_parser("hook")
    p.add_argument("agent")
    p.add_argument("event")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "hook":
        from adapters import run_hook

        return run_hook(args.agent, args.event, args.vault)
    try:
        engine = Engine(Vault(args.vault))
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    handler = {
        "types": cmd_types, "check": cmd_check, "fix": cmd_fix, "schema": cmd_schema, "new": cmd_new,
        "set": cmd_change, "add": cmd_change, "remove": cmd_change,
        "find": cmd_find, "values": cmd_values, "audit": cmd_audit, "checks": cmd_checks, "config": cmd_config,
    }[args.command]
    return handler(engine, args)


if __name__ == "__main__":
    sys.exit(main())

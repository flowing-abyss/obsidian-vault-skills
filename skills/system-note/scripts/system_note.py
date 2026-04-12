#!/usr/bin/env python3
"""Manage system notes in the Obsidian vault.

Usage:
    python system_note.py create --title "Title" --tag system/high/meta --category "Category" [options]
    python system_note.py update --title "Title" --tag system/high/meta [options]

Exit codes:
    0  success
    1  validation error or I/O failure
"""

import argparse
import re
import sys
from pathlib import Path

_tools = Path(__file__).parent.parent.parent.parent / "tools"
sys.path.insert(0, str(_tools))

from vault_utils import (
    find_vault_root,
    split_frontmatter,
    now_iso,
    fmt_link,
    normalize_frontmatter_scalar,
    normalize_cli_link_arg,
    normalize_cli_list_arg,
    normalize_note_key,
    read_fm_list,
    die,
)
from validators import (
    validate_title,
    validate_system_note_relations,
)


SYSTEM_KINDS = {
    "meta": {"folder": "base/_meta-notes", "tag": "system/high/meta"},
    "problem": {"folder": "base/_problems", "tag": "system/high/problem"},
    "hierarchy": {"folder": "base/_hierarchy", "tag": "system/high/hierarchy"},
}

SYSTEM_TAG_TO_KIND = {v["tag"]: k for k, v in SYSTEM_KINDS.items()}


def _target_dir(vault_root: Path, kind: str) -> Path:
    return vault_root / SYSTEM_KINDS[kind]["folder"]


def _kind_from_tag(tag: str) -> str:
    kind = SYSTEM_TAG_TO_KIND.get(tag)
    if not kind:
        die(
            "invalid tag, expected one of: "
            + ", ".join(sorted(SYSTEM_TAG_TO_KIND.keys()))
        )
    return kind


def _find_by_stem(root: Path, title: str) -> Path | None:
    if not root.is_dir():
        return None
    stem = normalize_note_key(title)
    for f in root.rglob("*.md"):
        if normalize_note_key(f.stem) == stem:
            return f
    return None


def _find_note_in_vault(vault_root: Path, title: str) -> Path | None:
    stem = normalize_note_key(title)
    for f in vault_root.rglob("*.md"):
        if normalize_note_key(f.stem) == stem:
            return f
    return None


def _find_system_note(vault_root: Path, kind: str, title: str) -> Path | None:
    return _find_by_stem(_target_dir(vault_root, kind), title)


def _extract_first_list_item(file_path: Path, key: str) -> str | None:
    raw = file_path.read_text(encoding="utf-8")
    values = read_fm_list(raw, key)
    return values[0] if values else None


def _list_block(key: str, items: list[str], as_links: bool = True) -> list[str]:
    if items:
        vals = [fmt_link(i) for i in items] if as_links else items
        return [f"{key}:"] + [f"  - {v}" for v in vals]
    return [f"{key}:"]


def _set_scalar(fm: str, key: str, value: str) -> str:
    value = normalize_frontmatter_scalar(value)
    pattern = re.compile(rf"^({re.escape(key)}:[ \t]*).*$", re.MULTILINE)
    if pattern.search(fm):
        return pattern.sub(rf"\g<1>{value}", fm, count=1)
    return fm.rstrip() + f"\n{key}: {value}"


def _set_list(fm: str, key: str, items: list[str], as_links: bool = True) -> str:
    vals = [fmt_link(i) for i in items] if as_links else items
    new_block = f"{key}:\n" + "\n".join(f"  - {v}" for v in vals) if vals else f"{key}:"
    pattern = re.compile(
        rf"^{re.escape(key)}:[ \t]*\n(?:[ \t]+-[ \t]+.*\n)*",
        re.MULTILINE,
    )
    if pattern.search(fm):
        return pattern.sub(new_block + "\n", fm, count=1)
    scalar = re.compile(rf"^{re.escape(key)}:.*$", re.MULTILINE)
    if scalar.search(fm):
        return scalar.sub(new_block, fm, count=1)
    return fm.rstrip() + f"\n{new_block}"


def _build_frontmatter(args, now: str) -> str:
    lines = ["---"]
    lines += _list_block("tags", [args.tag], as_links=False)
    lines += _list_block("aliases", args.alias, as_links=False)
    lines += _list_block("category", [args.category])

    if args.kind in ("problem", "hierarchy"):
        lines += _list_block("meta", [args.meta] if args.meta else [])
    if args.kind == "hierarchy":
        lines += _list_block("problem", [args.problem] if args.problem else [])

    lines += [f"relevant: {normalize_frontmatter_scalar(args.relevant)}"]
    lines += [f"created: {now}"]
    lines += [f"updated: {now}"]
    lines += ["---"]
    return "\n".join(lines)


def _patch_frontmatter(fm: str, args, now: str) -> str:
    fm = _set_list(fm, "tags", [args.tag], as_links=False)
    if args.alias is not None:
        fm = _set_list(fm, "aliases", args.alias, as_links=False)
    if args.category is not None:
        fm = _set_list(fm, "category", [args.category])

    if args.kind in ("problem", "hierarchy") and args.meta is not None:
        fm = _set_list(fm, "meta", [args.meta] if args.meta else [])
    if args.kind == "hierarchy" and args.problem is not None:
        fm = _set_list(fm, "problem", [args.problem] if args.problem else [])

    if args.relevant is not None:
        fm = _set_scalar(fm, "relevant", args.relevant)
    fm = _set_scalar(fm, "updated", now)
    return fm


def cmd_create(args, vault_root: Path) -> None:
    args.kind = _kind_from_tag(args.tag)
    args.alias, _ = normalize_cli_list_arg(args.alias, field="alias", as_links=False)
    args.alias = args.alias if args.alias is not None else []
    args.category, _ = normalize_cli_link_arg(args.category, field="category")
    args.meta, _ = normalize_cli_link_arg(args.meta, field="meta")
    args.problem, _ = normalize_cli_link_arg(args.problem, field="problem")

    errors = []

    def check(err):
        if err:
            errors.append(err)

    check(validate_title(args.title))
    if _find_note_in_vault(vault_root, args.title):
        errors.append(f'note "{args.title}" already exists in vault')

    errors += validate_system_note_relations(
        args.kind, args.category, args.meta, args.problem, vault_root
    )

    if errors:
        die("Validation failed:\n" + "\n".join(f"  • {e}" for e in errors))

    now = now_iso()
    content = _build_frontmatter(args, now) + "\n\n" + (args.body or "💤") + "\n"
    target = _target_dir(vault_root, args.kind) / f"{args.title.strip()}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

    print(f"✓ Created:  {SYSTEM_KINDS[args.kind]['folder']}/{target.name}")
    print(f"  Tag:      {args.tag}")
    print(f"  Category: {args.category}")


def cmd_update(args, vault_root: Path) -> None:
    args.kind = _kind_from_tag(args.tag)
    args.alias, _ = normalize_cli_list_arg(args.alias, field="alias", as_links=False)
    for field in ("category", "meta", "problem"):
        normalized, _ = normalize_cli_link_arg(getattr(args, field), field=field)
        setattr(args, field, normalized)

    target = _find_system_note(vault_root, args.kind, args.title)
    if not target:
        die(
            f'{args.tag} note "{args.title}" not found in {SYSTEM_KINDS[args.kind]["folder"]}/'
        )

    raw = target.read_text(encoding="utf-8")
    fm_raw, body = split_frontmatter(raw)

    current_category = _extract_first_list_item(target, "category")
    current_meta = _extract_first_list_item(target, "meta")
    current_problem = _extract_first_list_item(target, "problem")

    effective_category = (
        args.category if args.category is not None else current_category
    )
    effective_meta = args.meta if args.meta is not None else current_meta
    effective_problem = args.problem if args.problem is not None else current_problem

    errors = validate_system_note_relations(
        args.kind,
        effective_category,
        effective_meta,
        effective_problem,
        vault_root,
    )
    if errors:
        die("Validation failed:\n" + "\n".join(f"  • {e}" for e in errors))

    now = now_iso()
    new_fm = _patch_frontmatter(fm_raw, args, now)
    new_body = args.body if args.body is not None else body
    target.write_text(f"---\n{new_fm}\n---\n\n{new_body.strip()}\n", encoding="utf-8")

    print(f"✓ Updated:  {SYSTEM_KINDS[args.kind]['folder']}/{target.name}")
    print(f"  Tag:      {args.tag}")


def _add_shared_fields(p: argparse.ArgumentParser, create: bool) -> None:
    p.add_argument("--alias", action="append", default=[] if create else None)
    p.add_argument("--category", required=create, default=None)
    p.add_argument("--meta", default=None)
    p.add_argument("--problem", default=None)
    p.add_argument("--relevant", default="false" if create else None)
    p.add_argument("--body", default="💤" if create else None)
    p.add_argument("--vault", default="", help="Vault root (auto-detected if omitted)")


def parse_args():
    p = argparse.ArgumentParser(
        description="Manage system notes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("create", help="Create a new system note")
    c.add_argument("--title", required=True, help="Note title")
    c.add_argument("--tag", required=True, choices=sorted(SYSTEM_TAG_TO_KIND.keys()))
    _add_shared_fields(c, create=True)

    u = sub.add_parser("update", help="Update existing system note")
    u.add_argument("--title", required=True, help="Note title")
    u.add_argument("--tag", required=True, choices=sorted(SYSTEM_TAG_TO_KIND.keys()))
    _add_shared_fields(u, create=False)

    return p.parse_args()


def main():
    args = parse_args()

    vault_root = find_vault_root(Path(args.vault) if args.vault else None)
    if not vault_root:
        die("Vault not found. Run from inside the vault or set VAULT_PATH env var.")

    if args.command == "create":
        cmd_create(args, vault_root)
    else:
        cmd_update(args, vault_root)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Manage source notes in the Obsidian vault.

Usage:
    python source.py create --title "Title" [options]
    python source.py update --title "Title" [options]

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
    default_if_empty,
    find_vault_root,
    normalize_cli_list_arg,
    normalize_frontmatter_scalar,
    normalize_note_key,
    read_fm_field,
    read_fm_list,
    split_frontmatter,
    now_iso,
    fmt_link,
    die,
)
from validators import (
    validate_title,
    validate_status,
    validate_creator,
    validate_production,
    validate_date_range,
    resolve_date_range_for_update,
    resolve_taxonomy_for_update,
    validate_taxonomy_links,
)


SOURCE_STATUSES = {"⬛", "🟥", "🟦", "⚛️", "🟩"}
SOURCE_RATINGS = {"🌕", "🌔", "🌓", "🌒", "🌑"}
SOURCE_SCIENTIFICITY = {"🅰️", "🅱️", "👓", "📢", "💬"}
_DEFAULT_SOURCE_STATUS = "🟥"


def _load_source_types(vault_root: Path) -> set[str]:
    """Load valid source/* tags from templates/lists/list of tags (sources).md."""
    tags_file = vault_root / "templates" / "lists" / "list of tags (sources).md"
    if not tags_file.exists():
        return set()
    tags = set()
    for line in tags_file.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if value.startswith("source/"):
            tags.add(value)
    return tags


def _find_source(title: str, vault_root: Path) -> Path | None:
    sources_dir = vault_root / "sources"
    if not sources_dir.is_dir():
        return None
    stem = normalize_note_key(title)
    for f in sources_dir.rglob("*.md"):
        if normalize_note_key(f.stem) == stem:
            return f
    return None


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


def _validate_source_fields(
    args,
    vault_root: Path,
    taxonomy: tuple[list[str], list[str], list[str]] | None = None,
) -> list[str]:
    errors = []

    def check(err):
        if err:
            errors.append(err)

    source_types = _load_source_types(vault_root)
    if not source_types:
        errors.append(
            "no source types found in templates/lists/list of tags (sources).md"
        )

    if args.status is not None:
        check(validate_status(args.status, SOURCE_STATUSES))

    if args.rating is not None and args.rating and args.rating not in SOURCE_RATINGS:
        errors.append(
            f'invalid rating "{args.rating}", expected one of: {", ".join(sorted(SOURCE_RATINGS))}'
        )

    if (
        args.scientificity is not None
        and args.scientificity
        and args.scientificity not in SOURCE_SCIENTIFICITY
    ):
        errors.append(
            f'invalid scientificity "{args.scientificity}", expected one of: {", ".join(sorted(SOURCE_SCIENTIFICITY))}'
        )

    if args.tag is not None and args.tag and args.tag not in source_types:
        errors.append(
            f'invalid tag "{args.tag}", expected one of: {", ".join(sorted(source_types))}'
        )

    category_values, meta_values, problem_values = taxonomy or (
        args.category or [],
        args.meta or [],
        args.problem or [],
    )
    for err in validate_taxonomy_links(
        category_values, meta_values, problem_values, vault_root
    ):
        check(err)
    for c in args.creator or []:
        check(validate_creator(c, vault_root))
    for p in args.production or []:
        check(validate_production(p, vault_root))

    for err in validate_date_range(args.start, args.end):
        check(err)

    return errors


def _build_frontmatter(args, now: str) -> str:
    lines = ["---"]
    lines += _list_block("tags", [args.tag] if args.tag else [], as_links=False)
    lines += _list_block("aliases", args.alias, as_links=False)
    lines += [f"status: {normalize_frontmatter_scalar(args.status)}"]
    lines += [f"rating: {normalize_frontmatter_scalar(args.rating)}"]
    lines += [f"scientificity: {normalize_frontmatter_scalar(args.scientificity)}"]
    lines += [f"created: {now}"]
    lines += [f"updated: {now}"]
    lines += [f"start: {normalize_frontmatter_scalar(args.start)}"]
    lines += [f"end: {normalize_frontmatter_scalar(args.end)}"]
    lines += _list_block("category", args.category)
    lines += _list_block("meta", args.meta)
    lines += _list_block("problem", args.problem)
    lines += _list_block("creator", args.creator)
    lines += _list_block("production", args.production)
    lines += ["---"]
    return "\n".join(lines)


def _patch_frontmatter(fm: str, args, now: str) -> str:
    if args.tag is not None:
        fm = _set_list(fm, "tags", [args.tag] if args.tag else [], as_links=False)
    if args.alias is not None:
        fm = _set_list(fm, "aliases", args.alias, as_links=False)
    if args.status is not None:
        fm = _set_scalar(fm, "status", args.status)
    if args.rating is not None:
        fm = _set_scalar(fm, "rating", args.rating)
    if args.scientificity is not None:
        fm = _set_scalar(fm, "scientificity", args.scientificity)
    if args.start is not None:
        fm = _set_scalar(fm, "start", args.start)
    if args.end is not None:
        fm = _set_scalar(fm, "end", args.end)
    if args.category is not None:
        fm = _set_list(fm, "category", args.category)
    if args.meta is not None:
        fm = _set_list(fm, "meta", args.meta)
    if args.problem is not None:
        fm = _set_list(fm, "problem", args.problem)
    if args.creator is not None:
        fm = _set_list(fm, "creator", args.creator)
    if args.production is not None:
        fm = _set_list(fm, "production", args.production)
    fm = _set_scalar(fm, "updated", now)
    return fm


def cmd_create(args, vault_root: Path) -> None:
    args.alias, _ = normalize_cli_list_arg(args.alias, field="alias", as_links=False)
    args.alias = args.alias if args.alias is not None else []
    for field in ("category", "meta", "problem", "creator", "production"):
        normalized, _ = normalize_cli_list_arg(
            getattr(args, field), field=field, as_links=True
        )
        setattr(args, field, normalized if normalized is not None else [])
    args.status = default_if_empty(args.status, _DEFAULT_SOURCE_STATUS)

    errors = []

    def check(err):
        if err:
            errors.append(err)

    check(validate_title(args.title))
    if _find_source(args.title, vault_root):
        errors.append(f'source "{args.title}" already exists in sources/')

    errors += _validate_source_fields(args, vault_root)

    if errors:
        die("Validation failed:\n" + "\n".join(f"  • {e}" for e in errors))

    now = now_iso()
    content = _build_frontmatter(args, now) + "\n\n" + (args.body or "💤") + "\n"

    source_path = vault_root / "sources" / f"{args.title.strip()}.md"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(content, encoding="utf-8")

    print(f"✓ Created:  sources/{source_path.name}")
    print(f"  Title:    {args.title}")


def cmd_update(args, vault_root: Path) -> None:
    args.alias, _ = normalize_cli_list_arg(args.alias, field="alias", as_links=False)
    for field in ("category", "meta", "problem", "creator", "production"):
        normalized, _ = normalize_cli_list_arg(
            getattr(args, field), field=field, as_links=True
        )
        setattr(args, field, normalized)
    args.status = default_if_empty(args.status, _DEFAULT_SOURCE_STATUS)

    source_path = _find_source(args.title, vault_root)
    if not source_path:
        die(f'source "{args.title}" not found in sources/')

    raw = source_path.read_text(encoding="utf-8")
    fm_raw, body = split_frontmatter(raw)

    args.start, args.end, borrowed_start, borrowed_end = resolve_date_range_for_update(
        args.start,
        args.end,
        read_fm_field(fm_raw, "start"),
        read_fm_field(fm_raw, "end"),
    )

    effective_taxonomy = resolve_taxonomy_for_update(
        args.category,
        args.meta,
        args.problem,
        read_fm_list(fm_raw, "category"),
        read_fm_list(fm_raw, "meta"),
        read_fm_list(fm_raw, "problem"),
    )

    errors = _validate_source_fields(args, vault_root, taxonomy=effective_taxonomy)
    if errors:
        die("Validation failed:\n" + "\n".join(f"  • {e}" for e in errors))

    if borrowed_start:
        args.start = None
    if borrowed_end:
        args.end = None

    now = now_iso()
    new_fm = _patch_frontmatter(fm_raw, args, now)
    new_body = args.body if args.body is not None else body

    source_path.write_text(
        f"---\n{new_fm}\n---\n\n{new_body.strip()}\n", encoding="utf-8"
    )

    print(f"✓ Updated:  sources/{source_path.name}")
    print(f"  Title:    {args.title}")


def _add_shared_fields(p: argparse.ArgumentParser, create: bool) -> None:
    p.add_argument("--tag", required=create, default=None)
    p.add_argument("--alias", action="append", default=[] if create else None)
    p.add_argument("--status", default="🟥" if create else None)
    p.add_argument("--rating", default="" if create else None)
    p.add_argument("--scientificity", default="" if create else None)

    for field in ("category", "meta", "problem", "creator", "production"):
        flag = "--" + field
        p.add_argument(
            flag,
            action="append",
            default=[] if create else None,
            metavar="LINK",
            help=(
                f"{field} link, repeatable"
                if create
                else f"{field} link (replaces list), repeatable"
            ),
        )

    p.add_argument("--start", default="" if create else None)
    p.add_argument("--end", default="" if create else None)
    p.add_argument("--body", default="💤" if create else None)
    p.add_argument("--vault", default="", help="Vault root (auto-detected if omitted)")


def parse_args():
    p = argparse.ArgumentParser(
        description="Manage source notes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("create", help="Create a new source note")
    c.add_argument("--title", required=True, help="Source title (used as filename)")
    _add_shared_fields(c, create=True)

    u = sub.add_parser("update", help="Update an existing source note by title")
    u.add_argument("--title", required=True, help="Source title")
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

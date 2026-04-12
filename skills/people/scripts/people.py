#!/usr/bin/env python3
"""Manage people notes in the Obsidian vault.

Usage:
    python people.py create --title "Name" --tag contact/working [options]
    python people.py update --title "Name" --tag contact/working [options]

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
    normalize_cli_list_arg,
    normalize_frontmatter_scalar,
    normalize_note_key,
    read_fm_list,
    split_frontmatter,
    now_iso,
    fmt_link,
    die,
)
from validators import (
    validate_title,
    resolve_taxonomy_for_update,
    validate_taxonomy_links,
)


PEOPLE_TYPES = {
    "contact": {
        "folder": "base/contacts",
        "tags_file": "templates/lists/list of tags (contact).md",
    },
    "creator": {
        "folder": "base/creators",
        "tags_file": "templates/lists/list of tags (creator).md",
    },
    "production": {
        "folder": "base/productions",
        "tags_file": "templates/lists/list of tags (production).md",
    },
}

TASK_BLOCK = """> [!todo]- tasks (`$=dv.pages().file.tasks.where(t => !t.completed).where(t => dv.func.contains(t.outlinks, dv.current().file.link)).length`)
> > [!info]+ mentions
> > ```dataviewjs
> > dv.taskList(dv.pages().file.tasks
> >  .where(t => !t.completed)
> >  .where(t => !t.text.includes("#task/waiting_for"))
> >  .where(t => dv.func.contains(t.outlinks, dv.current().file.link))
> >  .groupBy(t => ""))
> > ```
>
> > [!check]+ delegated
> > ```dataviewjs
> > dv.taskList(dv.pages().file.tasks
> >  .where(t => !t.completed)
> >  .where(t => t.text.includes("#task/waiting_for"))
> >  .where(t => dv.func.contains(t.outlinks, dv.current().file.link))
> >  .groupBy(t => ""))
> > ```"""


def _target_dir(vault_root: Path, person_type: str) -> Path:
    return vault_root / PEOPLE_TYPES[person_type]["folder"]


def _infer_type_from_tag(tag: str) -> str | None:
    if not tag or "/" not in tag:
        return None
    candidate = tag.split("/", 1)[0].strip()
    return candidate if candidate in PEOPLE_TYPES else None


def _load_people_tags(vault_root: Path, person_type: str) -> set[str]:
    tags_file = vault_root / PEOPLE_TYPES[person_type]["tags_file"]
    if not tags_file.exists():
        return set()
    tags = set()
    for line in tags_file.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if value.startswith(person_type + "/"):
            tags.add(value)
    return tags


def _find_person(vault_root: Path, person_type: str, title: str) -> Path | None:
    root = _target_dir(vault_root, person_type)
    if not root.is_dir():
        return None
    stem = normalize_note_key(title)
    for f in root.rglob("*.md"):
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


def _ensure_task_block(body: str | None) -> str:
    content = (body or "").strip()
    if content.startswith(TASK_BLOCK):
        return content
    if not content:
        return TASK_BLOCK
    return TASK_BLOCK + "\n\n" + content


def _validate_fields(
    args,
    vault_root: Path,
    taxonomy: tuple[list[str], list[str], list[str]] | None = None,
) -> list[str]:
    errors = []

    def check(err):
        if err:
            errors.append(err)

    person_type = _infer_type_from_tag(args.tag)
    if not person_type:
        errors.append(
            "invalid tag prefix, expected one of: contact/, creator/, production/"
        )
        return errors

    args.person_type = person_type
    allowed_tags = _load_people_tags(vault_root, person_type)
    if not allowed_tags:
        errors.append(f'no tags found in {PEOPLE_TYPES[person_type]["tags_file"]}')
    if args.tag is not None and args.tag and args.tag not in allowed_tags:
        errors.append(
            f'invalid tag "{args.tag}", expected one of: {", ".join(sorted(allowed_tags))}'
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

    return errors


def _build_frontmatter(args, now: str) -> str:
    lines = ["---"]
    lines += _list_block("tags", [args.tag] if args.tag else [], as_links=False)
    lines += _list_block("aliases", args.alias, as_links=False)
    lines += [f"description: {normalize_frontmatter_scalar(args.description)}"]
    lines += _list_block("category", args.category)
    lines += _list_block("meta", args.meta)
    lines += _list_block("problem", args.problem)
    lines += [f"relevant: {normalize_frontmatter_scalar(args.relevant)}"]
    lines += [f"created: {now}"]
    lines += [f"updated: {now}"]
    lines += ["---"]
    return "\n".join(lines)


def _patch_frontmatter(fm: str, args, now: str) -> str:
    if args.tag is not None:
        fm = _set_list(fm, "tags", [args.tag] if args.tag else [], as_links=False)
    if args.alias is not None:
        fm = _set_list(fm, "aliases", args.alias, as_links=False)
    if args.description is not None:
        fm = _set_scalar(fm, "description", args.description)
    if args.category is not None:
        fm = _set_list(fm, "category", args.category)
    if args.meta is not None:
        fm = _set_list(fm, "meta", args.meta)
    if args.problem is not None:
        fm = _set_list(fm, "problem", args.problem)
    if args.relevant is not None:
        fm = _set_scalar(fm, "relevant", args.relevant)
    fm = _set_scalar(fm, "updated", now)
    return fm


def cmd_create(args, vault_root: Path) -> None:
    args.alias, _ = normalize_cli_list_arg(args.alias, field="alias", as_links=False)
    args.alias = args.alias if args.alias is not None else []
    for field in ("category", "meta", "problem"):
        normalized, _ = normalize_cli_list_arg(
            getattr(args, field), field=field, as_links=True
        )
        setattr(args, field, normalized if normalized is not None else [])

    errors = []

    def check(err):
        if err:
            errors.append(err)

    check(validate_title(args.title))
    errors += _validate_fields(args, vault_root)

    if not errors and _find_person(vault_root, args.person_type, args.title):
        errors.append(
            f'{args.person_type} "{args.title}" already exists in {PEOPLE_TYPES[args.person_type]["folder"]}/'
        )

    if errors:
        die("Validation failed:\n" + "\n".join(f"  • {e}" for e in errors))

    now = now_iso()
    content = (
        _build_frontmatter(args, now) + "\n\n" + _ensure_task_block(args.body) + "\n"
    )
    target = _target_dir(vault_root, args.person_type) / f"{args.title.strip()}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

    print(f"✓ Created:  {PEOPLE_TYPES[args.person_type]['folder']}/{target.name}")
    print(f"  Type:     {args.person_type}")
    print(f"  Title:    {args.title}")


def cmd_update(args, vault_root: Path) -> None:
    args.alias, _ = normalize_cli_list_arg(args.alias, field="alias", as_links=False)
    for field in ("category", "meta", "problem"):
        normalized, _ = normalize_cli_list_arg(
            getattr(args, field), field=field, as_links=True
        )
        setattr(args, field, normalized)

    errors = _validate_fields(args, vault_root, taxonomy=([], [], []))
    if errors:
        die("Validation failed:\n" + "\n".join(f"  • {e}" for e in errors))

    target = _find_person(vault_root, args.person_type, args.title)
    if not target:
        die(
            f'{args.person_type} "{args.title}" not found in {PEOPLE_TYPES[args.person_type]["folder"]}/'
        )

    raw = target.read_text(encoding="utf-8")
    fm_raw, body = split_frontmatter(raw)

    effective_taxonomy = resolve_taxonomy_for_update(
        args.category,
        args.meta,
        args.problem,
        read_fm_list(fm_raw, "category"),
        read_fm_list(fm_raw, "meta"),
        read_fm_list(fm_raw, "problem"),
    )

    errors = _validate_fields(args, vault_root, taxonomy=effective_taxonomy)
    if errors:
        die("Validation failed:\n" + "\n".join(f"  • {e}" for e in errors))

    now = now_iso()
    new_fm = _patch_frontmatter(fm_raw, args, now)
    base_body = args.body if args.body is not None else body
    new_body = _ensure_task_block(base_body)

    target.write_text(f"---\n{new_fm}\n---\n\n{new_body}\n", encoding="utf-8")

    print(f"✓ Updated:  {PEOPLE_TYPES[args.person_type]['folder']}/{target.name}")
    print(f"  Type:     {args.person_type}")
    print(f"  Title:    {args.title}")


def _add_shared_fields(p: argparse.ArgumentParser, create: bool) -> None:
    p.add_argument("--tag", required=True)
    p.add_argument("--alias", action="append", default=[] if create else None)
    p.add_argument("--description", default="" if create else None)
    p.add_argument("--category", action="append", default=[] if create else None)
    p.add_argument("--meta", action="append", default=[] if create else None)
    p.add_argument("--problem", action="append", default=[] if create else None)
    p.add_argument("--relevant", default="false" if create else None)
    p.add_argument("--body", default="" if create else None)
    p.add_argument("--vault", default="", help="Vault root (auto-detected if omitted)")


def parse_args():
    p = argparse.ArgumentParser(
        description="Manage people notes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("create", help="Create a new people note")
    c.add_argument("--title", required=True, help="Person/organization title")
    _add_shared_fields(c, create=True)

    u = sub.add_parser("update", help="Update existing people note")
    u.add_argument("--title", required=True, help="Person/organization title")
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

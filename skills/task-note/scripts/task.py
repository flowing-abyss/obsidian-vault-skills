#!/usr/bin/env python3
"""Manage project task notes in the Obsidian vault.

Usage:
    python task.py create --title "Title" --project "ProjectName" [options]
    python task.py update (--id OVN-5 | --title "Title") [options]

Exit codes:
    0  success
    1  validation error or I/O failure
"""

import argparse
import hashlib
import os
import re
import sys
import time
from pathlib import Path

_tools = Path(__file__).parent.parent.parent.parent / "tools"
sys.path.insert(0, str(_tools))

from vault_utils import (
    default_if_empty,
    find_vault_root,
    normalize_cli_list_arg,
    read_fm_field,
    read_fm_list,
    split_frontmatter,
    update_fm_field,
    now_iso,
    fmt_link,
    fmt_yaml_string,
    normalize_frontmatter_scalar,
    normalize_note_key,
    normalize_note_ref,
    die,
)
from validators import (
    TASK_STATUSES,
    TASK_PRIORITIES,
    validate_title,
    validate_status,
    validate_priority,
    validate_project,
    validate_milestone,
    validate_task_ref,
    validate_creator,
    validate_production,
    validate_url,
    validate_date_range,
    validate_blocked_by_dates,
    resolve_date_range_for_update,
    resolve_taxonomy_for_update,
    validate_taxonomy_links,
)


# ---------------------------------------------------------------------------
# Task ID helpers
# ---------------------------------------------------------------------------

_TASK_ID_LOCK_TIMEOUT_SECONDS = 30.0
_TASK_ID_LOCK_POLL_SECONDS = 0.1
_TASK_ID_LOCK_STALE_SECONDS = 300.0
_TASK_TAGS = {"task/default", "task/milestone"}
_DEFAULT_TASK_TAG = "task/default"
_DEFAULT_TASK_STATUS = "📥"
_DEFAULT_TASK_PRIORITY = "🇨"


def _resolve_task_id(project_name: str, vault_root: Path) -> tuple:
    """Return (task_id, project_file, prefix, count) without writing."""
    from validators import _find_in

    project_file = _find_in(project_name, vault_root, "projects")
    if not project_file:
        die(f'project "{project_name}" not found in projects/')

    content = project_file.read_text(encoding="utf-8")
    prefix = read_fm_field(content, "prefix")
    if not prefix:
        words = project_name.strip().split()
        if len(words) >= 3:
            prefix = "".join(w[0].upper() for w in words[:3])
        elif len(words) == 2:
            prefix = (words[0][:2] + words[1][0]).upper()
        else:
            prefix = words[0][:3].upper()

    raw_count = read_fm_field(content, "taskCount")
    count = int(raw_count) + 1 if raw_count and raw_count.isdigit() else 1
    return f"{prefix}-{count}", project_file, prefix, count


def _preview_id(project_name: str, vault_root: Path) -> str:
    return _resolve_task_id(project_name, vault_root)[0]


def _next_available_task_id(project_name: str, vault_root: Path) -> tuple:
    task_id, project_file, prefix, count = _resolve_task_id(project_name, vault_root)
    while _id_exists(task_id, vault_root):
        count += 1
        task_id = f"{prefix}-{count}"
    return task_id, project_file, prefix, count


def _write_project_task_state(project_file: Path, prefix: str, count: int) -> None:
    content = project_file.read_text(encoding="utf-8")
    content = update_fm_field(content, "prefix", prefix)
    content = update_fm_field(content, "taskCount", count)
    project_file.write_text(content, encoding="utf-8")


def _task_id_lock_path(project_file: Path, vault_root: Path) -> Path:
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", project_file.stem).strip("-.")
    if not safe_name:
        safe_name = "project"
    digest = hashlib.sha1(
        str(project_file.relative_to(vault_root)).encode("utf-8")
    ).hexdigest()[:10]
    return vault_root / f".task-id-{safe_name}-{digest}.lock"


def _acquire_task_id_lock(project_file: Path, vault_root: Path) -> Path:
    lock_path = _task_id_lock_path(project_file, vault_root)
    deadline = time.monotonic() + _TASK_ID_LOCK_TIMEOUT_SECONDS

    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(f"{os.getpid()}\n")
            return lock_path
        except FileExistsError:
            try:
                age_seconds = time.time() - lock_path.stat().st_mtime
            except FileNotFoundError:
                continue

            if age_seconds > _TASK_ID_LOCK_STALE_SECONDS:
                try:
                    lock_path.unlink()
                except FileNotFoundError:
                    pass
                continue

            if time.monotonic() >= deadline:
                die(
                    f'timed out waiting for task ID lock for project "{project_file.stem}"'
                )

            time.sleep(_TASK_ID_LOCK_POLL_SECONDS)


def _release_task_id_lock(lock_path: Path) -> None:
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass


def _id_exists(task_id: str, vault_root: Path) -> str | None:
    tasks_dir = vault_root / "base" / "tasks"
    if not tasks_dir.is_dir():
        return None
    pattern = re.compile(rf"^id:\s*{re.escape(task_id)}\s*$", re.MULTILINE)
    for f in tasks_dir.rglob("*.md"):
        if pattern.search(f.read_text(encoding="utf-8")):
            return f.name
    return None


def _find_task(task_id: str, vault_root: Path) -> Path | None:
    tasks_dir = vault_root / "base" / "tasks"
    if not tasks_dir.is_dir():
        return None
    pattern = re.compile(rf"^id:\s*{re.escape(task_id)}\s*$", re.MULTILINE)
    for f in tasks_dir.rglob("*.md"):
        if pattern.search(f.read_text(encoding="utf-8")):
            return f
    return None


def _find_task_by_title(title: str, vault_root: Path) -> Path | None:
    tasks_dir = vault_root / "base" / "tasks"
    if not tasks_dir.is_dir():
        return None
    stem = normalize_note_key(title)
    for f in tasks_dir.rglob("*.md"):
        if normalize_note_key(f.stem) == stem:
            return f
    return None


# ---------------------------------------------------------------------------
# Shared validation helpers
# ---------------------------------------------------------------------------


def _validate_fields(
    args,
    vault_root: Path,
    is_update: bool = False,
    taxonomy: tuple[list[str], list[str], list[str]] | None = None,
    blocked_by_values: list[str] | None = None,
    blocked_start_value: str | None = None,
) -> list[str]:
    errors = []

    def check(err):
        if err:
            errors.append(err)

    status = getattr(args, "status", None)
    priority = getattr(args, "priority", None)
    tag = getattr(args, "tag", None)

    if tag is not None and tag not in _TASK_TAGS:
        errors.append(
            f'invalid tag "{tag}", expected one of: {", ".join(sorted(_TASK_TAGS))}'
        )
    if status is not None:
        check(validate_status(status, TASK_STATUSES))
    if priority is not None:
        check(validate_priority(priority))

    for ms in getattr(args, "milestone", None) or []:
        check(validate_milestone(ms, vault_root))
    for r in getattr(args, "related", None) or []:
        check(validate_task_ref(r, vault_root, "related"))
    effective_blocked_by = (
        blocked_by_values
        if blocked_by_values is not None
        else (getattr(args, "blocked_by", None) or [])
    )
    for b in effective_blocked_by:
        check(validate_task_ref(b, vault_root, "blocked-by"))
    category_values, meta_values, problem_values = taxonomy or (
        getattr(args, "category", None) or [],
        getattr(args, "meta", None) or [],
        getattr(args, "problem", None) or [],
    )
    for err in validate_taxonomy_links(
        category_values, meta_values, problem_values, vault_root
    ):
        check(err)

    for creator in getattr(args, "creator", None) or []:
        check(validate_creator(creator, vault_root))
    for production in getattr(args, "production", None) or []:
        check(validate_production(production, vault_root))

    for u in getattr(args, "url", None) or []:
        check(validate_url(u))

    for err in validate_date_range(
        getattr(args, "start", None), getattr(args, "end", None)
    ):
        check(err)
    for err in validate_blocked_by_dates(
        effective_blocked_by,
        blocked_start_value
        if blocked_start_value is not None
        else getattr(args, "start", None),
        vault_root,
    ):
        check(err)

    return errors


# ---------------------------------------------------------------------------
# Frontmatter: build (create) and patch (update)
# ---------------------------------------------------------------------------


def _list_block(
    key: str,
    items: list[str],
    as_links: bool = True,
    quote_plain: bool = False,
) -> list[str]:
    if items:
        if as_links:
            vals = [fmt_link(i) for i in items]
        elif quote_plain:
            vals = [fmt_yaml_string(i) for i in items]
        else:
            vals = items
        return [f"{key}:"] + [f"  - {v}" for v in vals]
    return [f"{key}:"]


def _build_frontmatter(args, task_id: str, now: str) -> str:
    lines = ["---"]
    lines += ["tags:", f"  - {normalize_frontmatter_scalar(args.tag)}"]
    lines += ["aliases: []"]
    lines += [f"id: {task_id}"]
    lines += _list_block("attribute", args.attribute, as_links=False, quote_plain=True)
    lines += [f"description: {fmt_yaml_string(normalize_frontmatter_scalar(args.description) or '')}"]
    lines += [f"project:", f"  - {fmt_link(args.project)}"]
    lines += _list_block("milestone", args.milestone)
    lines += [f"status: {normalize_frontmatter_scalar(args.status)}"]
    lines += [f"priority: {normalize_frontmatter_scalar(args.priority)}"]
    lines += _list_block("related", args.related)
    lines += _list_block("blockedBy", args.blocked_by)
    lines += _list_block("category", args.category)
    lines += _list_block("meta", args.meta)
    lines += _list_block("problem", args.problem)
    lines += _list_block("creator", args.creator)
    lines += _list_block("production", args.production)
    lines += _list_block("url", args.url, as_links=False, quote_plain=True)
    lines += [f"start: {normalize_frontmatter_scalar(args.start) or now}"]
    lines += [f"end: {normalize_frontmatter_scalar(args.end)}"]
    lines += [f"created: {now}"]
    lines += [f"updated: {now}"]
    lines += ["---"]
    return "\n".join(lines)


def _set_scalar(fm: str, key: str, value: str) -> str:
    value = normalize_frontmatter_scalar(value)
    pattern = re.compile(rf"^({re.escape(key)}:[ \t]*).*$", re.MULTILINE)
    if pattern.search(fm):
        return pattern.sub(rf"\g<1>{value}", fm, count=1)
    return fm.rstrip() + f"\n{key}: {value}"


def _set_list(
    fm: str,
    key: str,
    items: list[str],
    as_links: bool = True,
    quote_plain: bool = False,
) -> str:
    if as_links:
        vals = [fmt_link(i) for i in items]
    elif quote_plain:
        vals = [fmt_yaml_string(i) for i in items]
    else:
        vals = items
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


def _dedupe_items(items: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for item in items:
        key = normalize_note_key(item)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _merge_related_items(
    related: list[str] | None, blocked_by: list[str] | None
) -> list[str]:
    return _dedupe_items((related or []) + (blocked_by or []))


def _apply_empty_value_semantics(args, create: bool) -> set[str]:
    explicitly_cleared = set()

    attribute_values, attribute_cleared = normalize_cli_list_arg(
        args.attribute, field="attribute", as_links=False
    )
    args.attribute = (
        attribute_values if attribute_values is not None else ([] if create else None)
    )
    if attribute_cleared:
        explicitly_cleared.add("attribute")

    for field in (
        "milestone",
        "related",
        "blocked_by",
        "category",
        "meta",
        "problem",
        "creator",
        "production",
    ):
        normalized, cleared = normalize_cli_list_arg(
            getattr(args, field), field=field, as_links=True
        )
        setattr(args, field, normalized if normalized is not None else ([] if create else None))
        if cleared:
            explicitly_cleared.add(field)

    url_values, url_cleared = normalize_cli_list_arg(
        args.url, field="url", as_links=False
    )
    args.url = url_values if url_values is not None else ([] if create else None)
    if url_cleared:
        explicitly_cleared.add("url")

    args.status = default_if_empty(args.status, _DEFAULT_TASK_STATUS)
    args.priority = default_if_empty(args.priority, _DEFAULT_TASK_PRIORITY)
    args.tag = default_if_empty(args.tag, _DEFAULT_TASK_TAG)

    return explicitly_cleared


def _write_task_note(task_path: Path, fm: str, body: str) -> None:
    content = f"---\n{fm.strip(chr(10))}\n---\n"
    if body:
        content += f"\n{body.rstrip(chr(10))}\n"
    else:
        content += "\n"
    task_path.write_text(content, encoding="utf-8")


def _sync_related_backlinks(
    task_path: Path, related: list[str], now: str, vault_root: Path
) -> None:
    from validators import _find_in

    backlink = task_path.stem

    for related_name in _dedupe_items(related):
        related_path = _find_in(related_name, vault_root, "base/tasks")
        if not related_path or related_path == task_path:
            continue

        raw = related_path.read_text(encoding="utf-8")
        fm_raw, body = split_frontmatter(raw)
        existing_related = _dedupe_items(read_fm_list(fm_raw, "related"))
        if normalize_note_key(backlink) in {
            normalize_note_key(item) for item in existing_related
        }:
            continue

        fm_raw = _set_list(fm_raw, "related", existing_related + [backlink])
        fm_raw = _set_scalar(fm_raw, "updated", now)
        _write_task_note(related_path, fm_raw, body)


def _patch_frontmatter(fm: str, args, now: str) -> str:
    if args.tag is not None:
        fm = _set_list(fm, "tags", [args.tag], as_links=False)
    if args.status is not None:
        fm = _set_scalar(fm, "status", args.status)
    if args.priority is not None:
        fm = _set_scalar(fm, "priority", args.priority)
    if args.attribute is not None:
        fm = _set_list(fm, "attribute", args.attribute, as_links=False, quote_plain=True)
    if args.description is not None:
        fm = _set_scalar(fm, "description", fmt_yaml_string(normalize_frontmatter_scalar(args.description) or ""))
    if args.milestone is not None:
        fm = _set_list(fm, "milestone", args.milestone)
    if args.related is not None:
        fm = _set_list(fm, "related", args.related)
    if args.blocked_by is not None:
        fm = _set_list(fm, "blockedBy", args.blocked_by)
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
    if args.url is not None:
        fm = _set_list(fm, "url", args.url, as_links=False, quote_plain=True)
    if args.start is not None:
        fm = _set_scalar(fm, "start", args.start)
    if args.end is not None:
        fm = _set_scalar(fm, "end", args.end)
    fm = _set_scalar(fm, "updated", now)
    return fm


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_create(args, vault_root: Path) -> None:
    from validators import _find_in

    # Accept path-like inputs (e.g. base/tasks/Note.md) but normalize to bare title.
    args.project = normalize_note_ref(args.project, field="project")
    explicitly_cleared = _apply_empty_value_semantics(args, create=True)
    args.related = _merge_related_items(args.related, args.blocked_by)
    args.blocked_by = _dedupe_items(args.blocked_by)

    # Inherit category / meta / problem from project if not provided
    project_file = _find_in(args.project, vault_root, "projects")
    if project_file:
        content = project_file.read_text(encoding="utf-8")
        if not args.category and "category" not in explicitly_cleared:
            args.category = read_fm_list(content, "category")
        if not args.meta and "meta" not in explicitly_cleared:
            args.meta = read_fm_list(content, "meta")
        if not args.problem and "problem" not in explicitly_cleared:
            args.problem = read_fm_list(content, "problem")

    errors = []

    def check(err):
        if err:
            errors.append(err)

    check(validate_title(args.title))
    if (vault_root / "base" / "tasks" / (args.title.strip() + ".md")).exists():
        errors.append(f'task "{args.title}" already exists in base/tasks/')

    check(validate_project(args.project, vault_root))

    pid = _preview_id(args.project, vault_root)
    existing = _id_exists(pid, vault_root)
    if existing:
        errors.append(f'task with ID "{pid}" already exists: {existing}')

    errors += _validate_fields(
        args,
        vault_root,
        blocked_by_values=args.blocked_by,
        blocked_start_value=args.start,
    )

    if errors:
        die("Validation failed:\n" + "\n".join(f"  • {e}" for e in errors))

    filename = args.title.strip() + ".md"
    task_path = vault_root / "base" / "tasks" / filename

    lock_path = _acquire_task_id_lock(project_file, vault_root)
    try:
        now = now_iso()
        task_id, project_file, prefix, count = _next_available_task_id(
            args.project, vault_root
        )
        content = (
            _build_frontmatter(args, task_id, now)
            + "\n\n"
            + (args.body or "💤")
            + "\n"
        )

        task_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with task_path.open("x", encoding="utf-8") as handle:
                handle.write(content)
        except FileExistsError:
            die(f"File already exists: base/tasks/{filename}")

        _write_project_task_state(project_file, prefix, count)
    finally:
        _release_task_id_lock(lock_path)

    if args.related:
        _sync_related_backlinks(task_path, args.related, now, vault_root)

    print(f"✓ Created:  base/tasks/{filename}")
    print(f"  ID:       {task_id}")
    print(f"  Project:  {args.project}")
    if args.milestone:
        print(f'  Milestone: {", ".join(args.milestone)}')


def cmd_update(args, vault_root: Path) -> None:
    _apply_empty_value_semantics(args, create=False)
    if args.related is not None:
        args.related = _dedupe_items(args.related)
    if args.blocked_by is not None:
        args.blocked_by = _dedupe_items(args.blocked_by)

    task_path = (
        _find_task(args.id, vault_root)
        if args.id
        else _find_task_by_title(args.title, vault_root)
    )
    if not task_path:
        if args.id:
            die(f'task with ID "{args.id}" not found in base/tasks/')
        die(f'task "{args.title}" not found in base/tasks/')

    raw = task_path.read_text(encoding="utf-8")
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
    effective_blocked_by = (
        args.blocked_by
        if args.blocked_by is not None
        else read_fm_list(fm_raw, "blockedBy")
    )
    effective_related = _merge_related_items(
        args.related if args.related is not None else read_fm_list(fm_raw, "related"),
        effective_blocked_by,
    )
    args.related = effective_related

    errors = _validate_fields(
        args,
        vault_root,
        is_update=True,
        taxonomy=effective_taxonomy,
        blocked_by_values=effective_blocked_by,
        blocked_start_value=args.start
        if args.start is not None
        else read_fm_field(fm_raw, "start"),
    )
    if errors:
        die("Validation failed:\n" + "\n".join(f"  • {e}" for e in errors))

    if borrowed_start:
        args.start = None
    if borrowed_end:
        args.end = None

    now = now_iso()
    new_fm = _patch_frontmatter(fm_raw, args, now)
    new_body = args.body if args.body is not None else body

    _write_task_note(task_path, new_fm, new_body)
    if args.related:
        _sync_related_backlinks(task_path, args.related, now, vault_root)

    print(f"✓ Updated:  base/tasks/{task_path.name}")
    print(f'  Lookup:   {"id=" + args.id if args.id else "title=" + args.title}')


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_LIST_FIELDS = dict(
    milestone=("Milestone from base/tasks/ (task/milestone tag)", True),
    related=("Related task from base/tasks/", True),
    blocked_by=("Blocking task from base/tasks/", True),
    category=("Category from base/categories/", True),
    meta=("Meta-note from base/_meta-notes/", True),
    problem=("Problem from base/_problems/", True),
    creator=("Creator from base/creators/ or base/contacts/", True),
    production=("Production from base/productions/", True),
    url=('Markdown link "[Name](https://...)"', False),
)


def _add_shared_fields(p: argparse.ArgumentParser, create: bool) -> None:
    default_none = (
        None if not create else None
    )  # always None for update; create sets own defaults

    p.add_argument("--status", default="📥" if create else None)
    p.add_argument("--priority", default="🇨" if create else None)
    p.add_argument("--tag", default=_DEFAULT_TASK_TAG if create else None)
    p.add_argument("--attribute", action="append", default=[] if create else None)
    p.add_argument("--description", default="" if create else None)

    for field, (help_text, _) in _LIST_FIELDS.items():
        flag = "--" + field.replace("_", "-")
        dest = field
        p.add_argument(
            flag,
            action="append",
            default=[] if create else None,
            dest=dest,
            metavar="LINK",
            help=help_text
            + (", repeatable" if create else " (replaces list), repeatable"),
        )

    p.add_argument("--start", default="" if create else None)
    p.add_argument("--end", default="" if create else None)
    p.add_argument("--body", default="💤" if create else None)
    p.add_argument("--vault", default="", help="Vault root (auto-detected if omitted)")


def parse_args():
    p = argparse.ArgumentParser(
        description="Manage project task notes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("create", help="Create a new task note")
    c.add_argument("--title", required=True, help="Task title (used as filename)")
    c.add_argument(
        "--project", required=True, help="Project name — must exist in projects/"
    )
    _add_shared_fields(c, create=True)

    u = sub.add_parser("update", help="Update an existing task note by ID or title")
    lookup = u.add_mutually_exclusive_group(required=True)
    lookup.add_argument("--id", help="Task ID, e.g. OVN-5")
    lookup.add_argument("--title", help="Task title / filename stem")
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

#!/usr/bin/env python3
"""Manage project notes in the Obsidian vault.

Usage:
    python project.py create --title "Title" [options]
    python project.py update --title "Title" [options]
    python project.py create-scene --project "Project Title" --title "Scene Title" [options]
    python project.py update-scene --project "Project Title" --title "Scene Title" [options]

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
    read_fm_field,
    read_fm_list,
    split_frontmatter,
    now_iso,
    fmt_link,
    fmt_yaml_string,
    normalize_frontmatter_scalar,
    normalize_note_key,
    normalize_note_ref,
    die,
)
from validators import (
    validate_title,
    validate_status,
    validate_priority,
    validate_creator,
    validate_production,
    validate_url,
    validate_date_range,
    resolve_date_range_for_update,
    resolve_taxonomy_for_update,
    validate_taxonomy_links,
)

PROJECT_STATUSES = {"⬛", "🟥", "🟦", "🟩", "📢"}
SCENE_STATUSES = {"⬛", "🟥", "💡", "🧠", "🔎", "🟦", "📋", "🖍", "🟩", "📦", "📢"}
_DEFAULT_PROJECT_STATUS = "🟥"
_DEFAULT_PROJECT_PRIORITY = "🇨"


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def _find_project_file(name: str, vault_root: Path) -> Path | None:
    from validators import _find_in

    candidate = _find_in(name, vault_root, "projects")
    if not candidate:
        return None
    raw = candidate.read_text(encoding="utf-8")
    if "project/single" in raw or "project/longform" in raw:
        return candidate
    return None


def _project_kind(project_file: Path) -> str:
    raw = project_file.read_text(encoding="utf-8")
    if "project/longform" in raw:
        return "longform"
    return "single"


def _find_longform_index(project_name: str, vault_root: Path) -> Path | None:
    """Find canonical longform index: projects/<Title>/<Title>.md."""
    target_stem = normalize_note_key(project_name)
    projects_dir = vault_root / "projects"
    if not projects_dir.is_dir():
        return None

    matches = []
    for f in projects_dir.rglob("*.md"):
        if normalize_note_key(f.stem) != target_stem:
            continue
        raw = f.read_text(encoding="utf-8")
        if "project/longform" not in raw:
            continue
        # Longform index must live inside its own folder and match folder name.
        if f.parent == projects_dir:
            continue
        if normalize_note_key(f.parent.name) != normalize_note_key(f.stem):
            continue
        matches.append(f)

    if len(matches) > 1:
        die(
            f'found multiple longform project indexes for "{project_name}"; '
            "use unique project titles"
        )
    return matches[0] if matches else None


def _find_scene_file(
    project_name: str, scene_title: str, vault_root: Path
) -> Path | None:
    """Find a scene file inside a resolved longform project folder."""
    project_file = _find_longform_index(project_name, vault_root)
    if not project_file:
        return None
    scene_path = project_file.parent / f"{scene_title.strip()}.md"
    if not scene_path.exists():
        return None
    raw = scene_path.read_text(encoding="utf-8")
    if "mark/scene" not in raw:
        return None
    return scene_path


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_fields(
    args,
    vault_root: Path,
    taxonomy: tuple[list[str], list[str], list[str]] | None = None,
) -> list[str]:
    errors = []

    def check(err):
        if err:
            errors.append(err)

    status = getattr(args, "status", None)
    priority = getattr(args, "priority", None)

    if status is not None:
        check(validate_status(status, PROJECT_STATUSES))
    if priority is not None:
        check(validate_priority(priority))

    category_values, meta_values, problem_values = taxonomy or (
        getattr(args, "category", None) or [],
        getattr(args, "meta", None) or [],
        getattr(args, "problem", None) or [],
    )
    for err in validate_taxonomy_links(
        category_values, meta_values, problem_values, vault_root
    ):
        check(err)
    for c in getattr(args, "creator", None) or []:
        check(validate_creator(c, vault_root))
    for p in getattr(args, "production", None) or []:
        check(validate_production(p, vault_root))
    for u in getattr(args, "url", None) or []:
        check(validate_url(u))

    for err in validate_date_range(
        getattr(args, "start", None), getattr(args, "end", None)
    ):
        check(err)

    return errors


# ---------------------------------------------------------------------------
# Frontmatter helpers
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


def _longform_block(title: str) -> list[str]:
    return [
        "longform:",
        "  format: scenes",
        f"  title: {title}",
        "  workflow: Default Workflow",
        "  sceneFolder: /",
        "  scenes: []",
        "  sceneTemplate: templates/create/projects/longform/scene template.md",
        "  ignoredFiles: []",
    ]


def _build_frontmatter(args, now: str) -> str:
    tag = "project/longform" if args.type == "longform" else "project/single"

    lines = ["---"]
    lines += ["tags:", f"  - {tag}"]
    lines += ["aliases: []"]
    lines += [f"status: {normalize_frontmatter_scalar(args.status)}"]
    lines += [f"priority: {normalize_frontmatter_scalar(args.priority)}"]
    lines += [f"cover: {normalize_frontmatter_scalar(args.cover)}"]

    if args.type == "longform":
        lines += _longform_block(args.title)

    lines += [f"created: {now}"]
    lines += [f"updated: {now}"]
    lines += [f"start: {normalize_frontmatter_scalar(args.start)}"]
    lines += [f"end: {normalize_frontmatter_scalar(args.end)}"]
    lines += _list_block("category", args.category)
    lines += _list_block("meta", args.meta)
    lines += _list_block("problem", args.problem)
    lines += _list_block("creator", args.creator)
    lines += _list_block("production", args.production)
    lines += _list_block("url", args.url, as_links=False, quote_plain=True)
    lines += ["---"]
    return "\n".join(lines)


def _default_body(kind: str, body: str) -> str:
    blocks = [
        "> [!toc]- Table of contents",
        "> ```table-of-contents",
        "> ```",
        "",
        "> [!todo]- Tasks",
        "> ```tasks",
        "> path includes {{query.file.path}}",
        "> group by heading",
        "> hide task count",
        "> ```",
        "",
    ]

    if kind == "longform":
        blocks += [
            "> [!todo]- Scene tasks",
            "> ```tasks",
            "> path includes {{query.file.folder}}",
            "> path does not include {{query.file.path}}",
            "> group by backlink",
            "> hide task count",
            "> ```",
            "",
        ]

    blocks += ["# Description", "", body.strip() if body.strip() else "💤", ""]
    return "\n".join(blocks)


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


def _patch_frontmatter(fm: str, args, now: str) -> str:
    if args.status is not None:
        fm = _set_scalar(fm, "status", args.status)
    if args.priority is not None:
        fm = _set_scalar(fm, "priority", args.priority)
    if args.cover is not None:
        fm = _set_scalar(fm, "cover", args.cover)
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
    if args.url is not None:
        fm = _set_list(fm, "url", args.url, as_links=False, quote_plain=True)
    fm = _set_scalar(fm, "updated", now)
    return fm


def _set_longform_scenes(fm: str, scenes: list[str]) -> str:
    lines = fm.splitlines()
    lf_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "longform:":
            lf_idx = i
            break
    if lf_idx is None:
        return fm

    block_end = len(lines)
    for j in range(lf_idx + 1, len(lines)):
        if lines[j] and not lines[j].startswith("  "):
            block_end = j
            break

    scene_idx = None
    for j in range(lf_idx + 1, block_end):
        if lines[j].startswith("  scenes:"):
            scene_idx = j
            break

    scene_lines = ["  scenes:"] + [f"    - {s}" for s in scenes]

    if scene_idx is None:
        insert_at = block_end
        lines = lines[:insert_at] + scene_lines + lines[insert_at:]
        return "\n".join(lines)

    scene_end = scene_idx + 1
    while scene_end < block_end and lines[scene_end].startswith("    - "):
        scene_end += 1

    lines = lines[:scene_idx] + scene_lines + lines[scene_end:]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_create(args, vault_root: Path) -> None:
    for field in ("category", "meta", "problem", "creator", "production"):
        normalized, _ = normalize_cli_list_arg(
            getattr(args, field), field=field, as_links=True
        )
        setattr(args, field, normalized if normalized is not None else [])
    url_values, _ = normalize_cli_list_arg(args.url, field="url", as_links=False)
    args.url = url_values if url_values is not None else []
    args.status = default_if_empty(args.status, _DEFAULT_PROJECT_STATUS)
    args.priority = default_if_empty(args.priority, _DEFAULT_PROJECT_PRIORITY)

    errors = []

    def check(err):
        if err:
            errors.append(err)

    check(validate_title(args.title))

    if args.type == "single":
        target = vault_root / "projects" / f"{args.title.strip()}.md"
    else:
        target = (
            vault_root / "projects" / args.title.strip() / f"{args.title.strip()}.md"
        )

    if target.exists():
        errors.append(
            f'project "{args.title}" already exists: {target.relative_to(vault_root)}'
        )

    errors += _validate_fields(args, vault_root)

    if errors:
        die("Validation failed:\n" + "\n".join(f"  • {e}" for e in errors))

    now = now_iso()
    content = (
        _build_frontmatter(args, now) + "\n\n" + _default_body(args.type, args.body)
    )

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

    print(f"✓ Created:  {target.relative_to(vault_root)}")
    print(f"  Type:     {args.type}")
    print(f"  Title:    {args.title}")


def cmd_update(args, vault_root: Path) -> None:
    for field in ("category", "meta", "problem", "creator", "production"):
        normalized, _ = normalize_cli_list_arg(
            getattr(args, field), field=field, as_links=True
        )
        setattr(args, field, normalized)
    args.url, _ = normalize_cli_list_arg(args.url, field="url", as_links=False)
    args.status = default_if_empty(args.status, _DEFAULT_PROJECT_STATUS)
    args.priority = default_if_empty(args.priority, _DEFAULT_PROJECT_PRIORITY)

    project_file = _find_project_file(args.title, vault_root)
    if not project_file:
        die(f'project "{args.title}" not found in projects/')

    raw = project_file.read_text(encoding="utf-8")
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

    errors = _validate_fields(args, vault_root, taxonomy=effective_taxonomy)
    if errors:
        die("Validation failed:\n" + "\n".join(f"  • {e}" for e in errors))

    if borrowed_start:
        args.start = None
    if borrowed_end:
        args.end = None

    now = now_iso()
    new_fm = _patch_frontmatter(fm_raw, args, now)
    new_body = args.body if args.body is not None else body

    project_file.write_text(
        f"---\n{new_fm}\n---\n\n{new_body.strip()}\n", encoding="utf-8"
    )

    print(f"✓ Updated:  {project_file.relative_to(vault_root)}")
    print(f"  Title:    {args.title}")


def cmd_create_scene(args, vault_root: Path) -> None:
    args.project = normalize_note_ref(args.project, field="project")

    project_file = _find_longform_index(args.project, vault_root)
    if not project_file:
        die(
            f'longform project "{args.project}" not found as '
            "projects/<Title>/<Title>.md"
        )

    err = validate_status(args.status, SCENE_STATUSES)
    if err:
        die(f"Validation failed:\n  • {err}")

    err = validate_title(args.title)
    if err:
        die(f"Validation failed:\n  • {err}")

    scene_path = project_file.parent / f"{args.title.strip()}.md"
    if scene_path.exists():
        die(f"Scene already exists: {scene_path.relative_to(vault_root)}")

    now = now_iso()
    scene_content = (
        "---\n"
        "tags:\n"
        "  - mark/scene\n"
        "up:\n"
        f"  - {fmt_link(project_file.stem)}\n"
        f"status: {args.status}\n"
        f"created: {now}\n"
        f"updated: {now}\n"
        "---\n\n"
        f"{(args.body or '💤').strip()}\n"
    )
    scene_path.write_text(scene_content, encoding="utf-8")

    raw = project_file.read_text(encoding="utf-8")
    fm_raw, body = split_frontmatter(raw)

    existing = re.findall(r"^\s{4}-\s*(.+)$", fm_raw, re.MULTILINE)
    scenes = [s.strip() for s in existing if s.strip()]
    if args.title not in scenes:
        scenes.append(args.title)

    fm_raw = _set_longform_scenes(fm_raw, scenes)
    fm_raw = _set_scalar(fm_raw, "updated", now)
    project_file.write_text(f"---\n{fm_raw}\n---\n\n{body.strip()}\n", encoding="utf-8")

    print(f"✓ Created:  {scene_path.relative_to(vault_root)}")
    print(f"  Project:  {project_file.relative_to(vault_root)}")


def cmd_update_scene(args, vault_root: Path) -> None:
    args.project = normalize_note_ref(args.project, field="project")

    scene_path = _find_scene_file(args.project, args.title, vault_root)
    if not scene_path:
        die(f'scene "{args.title}" not found in longform project "{args.project}"')

    if args.status is not None:
        err = validate_status(args.status, SCENE_STATUSES)
        if err:
            die(f"Validation failed:\n  • {err}")

    raw = scene_path.read_text(encoding="utf-8")
    fm_raw, body = split_frontmatter(raw)

    now = now_iso()
    if args.status is not None:
        fm_raw = _set_scalar(fm_raw, "status", args.status)
    fm_raw = _set_scalar(fm_raw, "updated", now)
    new_body = args.body if args.body is not None else body

    scene_path.write_text(
        f"---\n{fm_raw}\n---\n\n{new_body.strip()}\n", encoding="utf-8"
    )

    print(f"✓ Updated:  {scene_path.relative_to(vault_root)}")
    print(f"  Project:  {args.project}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _add_link_fields(p: argparse.ArgumentParser, create: bool) -> None:
    for field in ("category", "meta", "problem", "creator", "production", "url"):
        p.add_argument(
            "--" + field,
            action="append",
            default=[] if create else None,
            metavar="VALUE",
            help=("repeatable" + ("" if create else ", replaces list")),
        )


def parse_args():
    p = argparse.ArgumentParser(description="Manage project notes")
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("create", help="Create a project note")
    c.add_argument("--title", required=True, help="Project title")
    c.add_argument("--type", choices=("single", "longform"), default="single")
    c.add_argument("--status", default="🟥")
    c.add_argument("--priority", default="🇨")
    c.add_argument("--cover", default="")
    c.add_argument("--start", default="")
    c.add_argument("--end", default="")
    c.add_argument("--body", default="💤")
    c.add_argument("--vault", default="", help="Vault root (auto-detected if omitted)")
    _add_link_fields(c, create=True)

    u = sub.add_parser("update", help="Update an existing project note")
    u.add_argument("--title", required=True, help="Project title")
    u.add_argument("--status", default=None)
    u.add_argument("--priority", default=None)
    u.add_argument("--cover", default=None)
    u.add_argument("--start", default=None)
    u.add_argument("--end", default=None)
    u.add_argument("--body", default=None)
    u.add_argument("--vault", default="", help="Vault root (auto-detected if omitted)")
    _add_link_fields(u, create=False)

    s = sub.add_parser("create-scene", help="Create a scene file in a longform project")
    s.add_argument("--project", required=True, help="Longform project title")
    s.add_argument("--title", required=True, help="Scene title")
    # Backward-compat alias for older calls.
    s.add_argument("--scene", dest="title", help=argparse.SUPPRESS)
    s.add_argument("--status", default="🟥")
    s.add_argument("--body", default="💤")
    s.add_argument("--vault", default="", help="Vault root (auto-detected if omitted)")

    us = sub.add_parser("update-scene", help="Update a scene in a longform project")
    us.add_argument("--project", required=True, help="Longform project title")
    us.add_argument("--title", required=True, help="Scene title")
    us.add_argument("--status", default=None)
    us.add_argument("--body", default=None)
    us.add_argument("--vault", default="", help="Vault root (auto-detected if omitted)")

    return p.parse_args()


def main() -> None:
    args = parse_args()
    vault_root = find_vault_root(Path(args.vault) if args.vault else None)
    if not vault_root:
        die("Vault not found. Run from inside the vault or set VAULT_PATH env var.")

    if args.command == "create":
        cmd_create(args, vault_root)
    elif args.command == "update":
        cmd_update(args, vault_root)
    elif args.command == "create-scene":
        cmd_create_scene(args, vault_root)
    else:
        cmd_update_scene(args, vault_root)


if __name__ == "__main__":
    main()

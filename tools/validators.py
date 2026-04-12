"""Field validators for vault note creation scripts.

All functions return None on success, or a str error message on failure.
Only stdlib — no third-party dependencies.
"""

import re
from datetime import date as _Date
from pathlib import Path

from vault_utils import (
    normalize_frontmatter_scalar,
    normalize_note_key,
    read_fm_field,
    read_fm_list,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TASK_STATUSES = {"📥", "🟥", "🟦", "❄", "🟩", "📢", "⬛"}

TASK_PRIORITIES = {"🇦", "🇧", "🇨", "🇩", "🇪"}

# Characters forbidden in filenames on Windows (superset of macOS/Linux)
_FORBIDDEN_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

_MARKDOWN_LINK_RE = re.compile(r"^\[.+\]\(https?://.+\)$")

_DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

_WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _bare_name(raw: str) -> str:
    """Extract plain note name from [[wikilink]] or plain string."""
    return normalize_note_key(raw)


def _find_in(name: str, vault_root: Path, *folders: str) -> Path | None:
    """Find a note by stem within one or more vault subfolders (first match)."""
    stem = _bare_name(name)
    for folder in folders:
        target = vault_root / folder
        if not target.is_dir():
            continue
        for p in target.rglob("*.md"):
            if normalize_note_key(p.stem) == stem:
                return p
    return None


def _parse_date(value: str) -> _Date | None:
    m = _DATE_RE.search(value)
    if not m:
        return None
    try:
        return _Date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Text
# ---------------------------------------------------------------------------


def validate_title(title: str) -> str | None:
    """Non-empty; no OS-forbidden filename characters; ≤255 chars."""
    if not title or not title.strip():
        return "title must not be empty"
    bad = _FORBIDDEN_CHARS.findall(title)
    if bad:
        return f"title contains forbidden characters: {set(bad)}"
    if len(title.strip()) > 255:
        return "title exceeds 255 characters"
    return None


# ---------------------------------------------------------------------------
# Status / priority
# ---------------------------------------------------------------------------


def validate_status(status: str, allowed: set[str]) -> str | None:
    status = normalize_frontmatter_scalar(status)
    if status not in allowed:
        return (
            f'invalid status "{status}", expected one of: {", ".join(sorted(allowed))}'
        )
    return None


def validate_priority(priority: str) -> str | None:
    priority = normalize_frontmatter_scalar(priority)
    if priority not in TASK_PRIORITIES:
        return f'invalid priority "{priority}", expected one of: {", ".join(sorted(TASK_PRIORITIES))}'
    return None


# ---------------------------------------------------------------------------
# Folder-scoped link validators
# ---------------------------------------------------------------------------


def validate_project(name: str, vault_root: Path) -> str | None:
    if not _find_in(name, vault_root, "projects"):
        return f'project "{name}" not found in projects/'
    return None


def validate_milestone(name: str, vault_root: Path) -> str | None:
    f = _find_in(name, vault_root, "base/tasks")
    if not f:
        return f'milestone "{name}" not found in base/tasks/'
    if "task/milestone" not in f.read_text(encoding="utf-8"):
        return f'"{name}" exists in base/tasks/ but is not tagged task/milestone'
    return None


def validate_task_ref(name: str, vault_root: Path, field: str) -> str | None:
    """Validate a link that must point to a note in base/tasks/."""
    if not _find_in(name, vault_root, "base/tasks"):
        return f'{field} "{name}" not found in base/tasks/'
    return None


def validate_category(name: str, vault_root: Path) -> str | None:
    if not _find_in(name, vault_root, "base/categories"):
        return f'category "{name}" not found in base/categories/'
    return None


def validate_meta(name: str, vault_root: Path) -> str | None:
    if not _find_in(name, vault_root, "base/_meta-notes"):
        return f'meta "{name}" not found in base/_meta-notes/'
    return None


def validate_problem(name: str, vault_root: Path) -> str | None:
    if not _find_in(name, vault_root, "base/_problems"):
        return f'problem "{name}" not found in base/_problems/'
    return None


def _intersects(left: list[str], right: list[str]) -> bool:
    if not left or not right:
        return False
    right_keys = {_bare_name(item) for item in right}
    return any(_bare_name(item) in right_keys for item in left)


def _load_taxonomy_note(
    name: str, vault_root: Path, folder: str
) -> dict[str, list[str]] | None:
    note_file = _find_in(name, vault_root, folder)
    if not note_file:
        return None

    raw = note_file.read_text(encoding="utf-8")
    return {
        "category": read_fm_list(raw, "category"),
        "meta": read_fm_list(raw, "meta"),
        "problem": read_fm_list(raw, "problem"),
    }


def resolve_taxonomy_for_update(
    category: list[str] | None,
    meta: list[str] | None,
    problem: list[str] | None,
    current_category: list[str] | None = None,
    current_meta: list[str] | None = None,
    current_problem: list[str] | None = None,
) -> tuple[list[str], list[str], list[str]]:
    """Fill omitted taxonomy lists from persisted values for update validation."""
    return (
        current_category if category is None else category,
        current_meta if meta is None else meta,
        current_problem if problem is None else problem,
    )


def validate_taxonomy_links(
    category: list[str] | None,
    meta: list[str] | None,
    problem: list[str] | None,
    vault_root: Path,
) -> list[str]:
    """Validate taxonomy existence and category->meta->problem consistency."""
    errors = []

    categories = category or []
    metas = meta or []
    problems = problem or []

    if metas and not categories:
        errors.append("meta notes require at least one category")
    if problems and not categories:
        errors.append("problem notes require at least one category")
    if problems and not metas:
        errors.append("problem notes require at least one meta note")

    for item in categories:
        err = validate_category(item, vault_root)
        if err:
            errors.append(err)

    meta_data = {}
    for item in metas:
        err = validate_meta(item, vault_root)
        if err:
            errors.append(err)
            continue
        meta_data[item] = _load_taxonomy_note(item, vault_root, "base/_meta-notes")

    problem_data = {}
    for item in problems:
        err = validate_problem(item, vault_root)
        if err:
            errors.append(err)
            continue
        problem_data[item] = _load_taxonomy_note(item, vault_root, "base/_problems")

    if categories:
        for item, data in meta_data.items():
            linked_categories = data.get("category", []) if data else []
            if linked_categories and not _intersects(linked_categories, categories):
                errors.append(
                    f'meta "{item}" does not belong to provided categories: {", ".join(categories)}'
                )

        for item, data in problem_data.items():
            linked_categories = data.get("category", []) if data else []
            if linked_categories and not _intersects(linked_categories, categories):
                errors.append(
                    f'problem "{item}" does not belong to provided categories: {", ".join(categories)}'
                )

    if metas:
        for item, data in problem_data.items():
            linked_meta = data.get("meta", []) if data else []
            if linked_meta and not _intersects(linked_meta, metas):
                errors.append(
                    f'problem "{item}" does not belong to provided meta notes: {", ".join(metas)}'
                )

    return errors


def validate_system_note_relations(
    kind: str,
    category: str | None,
    meta: str | None,
    problem: str | None,
    vault_root: Path,
) -> list[str]:
    """Validate required fields and taxonomy consistency for system notes."""
    errors = []

    if not category:
        errors.append("category is required for all system notes")

    if kind == "problem" and not meta:
        errors.append("meta is required for problem notes")

    errors.extend(
        validate_taxonomy_links(
            [category] if category else [],
            [meta] if meta else [],
            [problem] if problem else [],
            vault_root,
        )
    )

    return errors


def validate_creator(name: str, vault_root: Path) -> str | None:
    if _find_in(name, vault_root, "base/creators", "base/contacts"):
        return None
    return f'creator "{name}" not found in base/creators/ or base/contacts/'


def validate_production(name: str, vault_root: Path) -> str | None:
    if not _find_in(name, vault_root, "base/productions"):
        return f'production "{name}" not found in base/productions/'
    return None


# ---------------------------------------------------------------------------
# URL
# ---------------------------------------------------------------------------


def validate_url(url: str) -> str | None:
    """Each URL must be a Markdown link: [Name](https://...)"""
    url = normalize_frontmatter_scalar(url)
    if not url or not url.strip():
        return None
    if not _MARKDOWN_LINK_RE.match(url.strip()):
        return f'url must be a Markdown link "[Name](https://...)", got: {url!r}'
    return None


# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------


def validate_date(value: str, field: str = "date") -> str | None:
    """Must contain a valid YYYY-MM-DD date component."""
    value = normalize_frontmatter_scalar(value)
    if not value or not value.strip():
        return None
    if _parse_date(value) is None:
        return f"{field} must contain a valid date in YYYY-MM-DD format, got: {value!r}"
    return None


def resolve_date_range_for_update(
    start: str | None,
    end: str | None,
    current_start: str | None = None,
    current_end: str | None = None,
) -> tuple[str | None, str | None, bool, bool]:
    """Fill the missing side of a partial update from current persisted values."""
    start = normalize_frontmatter_scalar(start)
    end = normalize_frontmatter_scalar(end)
    current_start = normalize_frontmatter_scalar(current_start)
    current_end = normalize_frontmatter_scalar(current_end)
    borrowed_start = end is not None and start is None
    borrowed_end = start is not None and end is None

    effective_start = current_start if borrowed_start else start
    effective_end = current_end if borrowed_end else end

    return effective_start, effective_end, borrowed_start, borrowed_end


def validate_date_range(start: str | None, end: str | None) -> list[str]:
    """Validate start/end independently and as an ordered range."""
    errors = []
    start = normalize_frontmatter_scalar(start)
    end = normalize_frontmatter_scalar(end)

    start_err = validate_date(start, "start")
    if start_err:
        errors.append(start_err)

    end_err = validate_date(end, "end")
    if end_err:
        errors.append(end_err)

    if not end_err and start and start.strip() and end and end.strip():
        d_start = _parse_date(start)
        d_end = _parse_date(end)
        if d_start and d_end and d_end < d_start:
            errors.append(f"end ({d_end}) must not be before start ({d_start})")

    return errors


def validate_blocked_by_dates(
    blocked_by: list[str] | None,
    start: str | None,
    vault_root: Path,
) -> list[str]:
    """Blocked task must not start before any blocking task ends."""
    errors = []
    start = normalize_frontmatter_scalar(start)
    if not blocked_by or not start or not start.strip():
        return errors

    start_date = _parse_date(start)
    if not start_date:
        return errors

    for blocker in blocked_by:
        blocker_file = _find_in(blocker, vault_root, "base/tasks")
        if not blocker_file:
            continue

        blocker_raw = blocker_file.read_text(encoding="utf-8")
        blocker_end = normalize_frontmatter_scalar(read_fm_field(blocker_raw, "end"))
        if not blocker_end or not blocker_end.strip():
            continue

        blocker_end_date = _parse_date(blocker_end)
        if blocker_end_date and start_date < blocker_end_date:
            errors.append(
                f'start ({start_date}) must not be before end ({blocker_end_date}) of blocking task "{blocker}"'
            )

    return errors


def validate_end_date(end: str, start: str) -> str | None:
    """End date must be >= start date (if both are provided)."""
    end = normalize_frontmatter_scalar(end)
    start = normalize_frontmatter_scalar(start)
    if not end or not end.strip():
        return None
    err = validate_date(end, "end")
    if err:
        return err
    if start and start.strip():
        d_start = _parse_date(start)
        d_end = _parse_date(end)
        if d_start and d_end and d_end < d_start:
            return f"end ({d_end}) must not be before start ({d_start})"
    return None

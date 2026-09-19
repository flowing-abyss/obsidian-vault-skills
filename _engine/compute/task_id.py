"""Task ids: `<project prefix>-<number>`, unique in the vault.

The number comes from `taskCount` on the project note. Templater uses the
same rule in templates/scripts/taskID.js. Whoever creates the id, `verify`
checks the result.
"""

import os
import re
import time

from engine import yamlio
from engine.findings import Finding
from engine.links import link_name
from engine.vault import tags_of

ID = "task-id"
WHEN = "#task/default OR #task/milestone"
FIELD = "id"
ABOUT = "Task ids follow the project prefix, are unique, and stay within the project counter."

_ID_RE = re.compile(r"^(?P<prefix>[^\s-][^\s]*?)-(?P<number>\d+)$")


def default_prefix(project_name):
    words = project_name.strip().split()
    if len(words) >= 3:
        return "".join(w[0].upper() for w in words[:3])
    if len(words) == 2:
        return (words[0][:2] + words[1][0]).upper()
    return words[0][:3].upper() if words else "TSK"


def _project(ctx):
    raw = ctx.frontmatter.get("project")
    first = (raw[0] if isinstance(raw, list) and raw else raw) or ""
    name = link_name(str(first)) if first else ""
    path = ctx.vault.resolve_link(name) if name else None
    return name, path


def _task_ids(ctx, skip_path):
    ids = {}
    for path in ctx.vault.notes():
        if path == skip_path or ctx.vault.is_ignored(path):
            continue
        fm = ctx.vault.frontmatter_of(path)
        if fm.get(FIELD) and any(t == "task" or t.startswith("task/") for t in tags_of(fm)):
            ids[str(fm[FIELD])] = path
    return ids


def generate(ctx):
    if ctx.frontmatter.get(FIELD):
        return []
    name, project_path = _project(ctx)
    if not project_path:
        return []
    project = ctx.vault.frontmatter_of(project_path)
    prefix = str(project.get("prefix") or default_prefix(name))
    count = project.get("taskCount")
    number = (count if isinstance(count, int) and not isinstance(count, bool) else 0) + 1
    taken = _task_ids(ctx, ctx.path)
    while f"{prefix}-{number}" in taken:
        number += 1
    ctx.frontmatter[FIELD] = f"{prefix}-{number}"
    return [FIELD]


def after_create(ctx):
    """Store the prefix and the new counter on the project note."""
    m = _ID_RE.match(str(ctx.frontmatter.get(FIELD) or ""))
    name, project_path = _project(ctx)
    if not m or not project_path:
        return []
    lock = ctx.vault.local_dir / "state" / "task-id.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    handle = None
    for _ in range(50):
        try:
            handle = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            if time.time() - lock.stat().st_mtime > 30:
                lock.unlink()
            time.sleep(0.1)
    try:
        note = ctx.vault.read_note(project_path)
        changes = {"taskCount": max(int(m.group("number")), _int(note.frontmatter.get("taskCount")))}
        if not note.frontmatter.get("prefix"):
            changes["prefix"] = m.group("prefix")
        text = yamlio.join_note(yamlio.rewrite_frontmatter(note.fm_text or "", changes), note.body)
        (ctx.vault.root / project_path).write_text(text, encoding="utf-8")
        ctx.vault.refresh()
    finally:
        if handle is not None:
            os.close(handle)
            lock.unlink()
    return []


def _int(value):
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def verify(ctx):
    if ctx.schema is None or FIELD not in ctx.schema.fields:
        return []
    if not _project(ctx)[0]:
        return [Finding(ID, "A task needs a project. The task id is computed from it.", field="project",
                        hint='Pass project="Project Title". List projects with: vault.py find "#project"')]
    value = ctx.frontmatter.get(FIELD)
    if value in (None, ""):
        return []
    text = str(value)
    m = _ID_RE.match(text)
    if not m:
        return [Finding(ID, f'Task id "{text}" must look like PREFIX-NUMBER, for example "OV-12".', field=FIELD)]
    out = []
    other = _task_ids(ctx, ctx.path).get(text)
    if other:
        out.append(Finding(ID, f'Task id "{text}" is already used by "{other}".', field=FIELD,
                           hint="Create tasks with the new command so the id is computed."))
    name, project_path = _project(ctx)
    if project_path:
        project = ctx.vault.frontmatter_of(project_path)
        prefix = project.get("prefix")
        if prefix and str(prefix) != m.group("prefix"):
            out.append(Finding(ID, f'Task id "{text}" does not use the project prefix "{prefix}".', field=FIELD,
                               severity="warning"))
    return out

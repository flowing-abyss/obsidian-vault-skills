"""Task notes and their project.

- A new task takes category, meta and problem from its project when not given.
- `related` is kept two way: the other task links back.
- A blocked task must not start before the task that blocks it ends.
"""

from engine import yamlio
from engine.findings import Finding
from engine.links import link_name

ID = "task-links"
WHEN = "#task/default OR #task/milestone"
ABOUT = "Tasks inherit taxonomy from the project, keep related links two way, and respect blockers."

INHERITED = ("category", "meta", "problem")


def _items(value):
    if value in (None, ""):
        return []
    return value if isinstance(value, list) else [value]


def _project_path(ctx):
    first = (_items(ctx.frontmatter.get("project")) or [""])[0]
    return ctx.vault.resolve_link(str(first)) if first else None


def generate(ctx):
    project = _project_path(ctx)
    if not project:
        return []
    source = ctx.vault.frontmatter_of(project)
    touched = []
    for name in INHERITED:
        if ctx.schema and name in ctx.schema.fields and not ctx.frontmatter.get(name) and source.get(name):
            ctx.frontmatter[name] = list(_items(source[name]))
            touched.append(name)
    return touched


def _link_back(ctx):
    me = ctx.path.rsplit("/", 1)[-1][:-3]
    for raw in _items(ctx.frontmatter.get("related")):
        other = ctx.vault.resolve_link(str(raw))
        if not other or other == ctx.path:
            continue
        note = ctx.vault.read_note(other)
        if note.error or note.fm_text is None:
            continue
        current = _items(note.frontmatter.get("related"))
        if me in {link_name(str(v)) for v in current}:
            continue
        fm = yamlio.rewrite_frontmatter(note.fm_text, {"related": current + [f"[[{me}]]"]})
        (ctx.vault.root / other).write_text(yamlio.join_note(fm, note.body), encoding="utf-8")
    ctx.vault.refresh()
    return []


def after_create(ctx):
    return _link_back(ctx)


def after_change(ctx):
    return _link_back(ctx) if "related" in ctx.changed else []


def verify(ctx):
    out = []
    me = ctx.path.rsplit("/", 1)[-1][:-3]
    for name in ("blockedBy", "related", "milestone"):
        if me in {link_name(str(v)) for v in _items(ctx.frontmatter.get(name))}:
            out.append(Finding("task-self-link", f'"{name}" links to this task itself.', field=name,
                               hint="Remove the link."))
    start = ctx.frontmatter.get("start")
    if not isinstance(start, str) or len(start) < 10:
        return out
    for raw in _items(ctx.frontmatter.get("blockedBy")):
        other = ctx.vault.resolve_link(str(raw))
        end = ctx.vault.frontmatter_of(other).get("end") if other else None
        if isinstance(end, str) and len(end) >= 10 and start[:10] < end[:10]:
            out.append(Finding("task-blocked", f'"start" ({start[:10]}) is before the end ({end[:10]}) of the blocking task "{link_name(str(raw))}".',
                               field="start", severity="warning"))
    return out

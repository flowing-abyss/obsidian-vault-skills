"""Longform projects and their scenes.

A longform project lives in its own folder: projects/<Title>/<Title>.md and
carries a `longform` block for the Longform plugin. A scene is a note in that
folder that links `up` to the project and is listed in `longform.scenes`.
"""

from engine import yamlio
from engine.links import link_name

ID = "longform"
WHEN = "#project/longform OR #mark/scene"
# Properties `new` accepts for these notes although the manifest does not list them.
ACCEPTS = {"up": {"type": "multilink"}}
ABOUT = "Places longform projects and scenes in the project folder and keeps the scene list."


def _is_scene(ctx):
    return any(t == "mark/scene" for t in ctx.note.tags)


def _index_of(ctx):
    up = ctx.frontmatter.get("up")
    first = (up[0] if isinstance(up, list) and up else up) or ""
    path = ctx.vault.resolve_link(str(first)) if first else None
    if path and "project/longform" in [t for t in ctx.vault.frontmatter_of(path).get("tags") or []]:
        return path
    return None


def place(ctx):
    if _is_scene(ctx):
        index = _index_of(ctx)
        if not index:
            from engine.write import WriteError

            raise WriteError('A scene needs its longform project: pass --set up="Project Title". '
                             'List projects with: vault.py find "#project/longform"')
        return index.rsplit("/", 1)[0]
    return f"projects/{ctx.title}"


def generate(ctx):
    if _is_scene(ctx) or ctx.frontmatter.get("longform"):
        return []
    ctx.frontmatter["longform"] = {
        "format": "scenes", "title": ctx.title, "workflow": "Default Workflow", "sceneFolder": "/",
        "scenes": [], "sceneTemplate": "templates/create/projects/longform/scene template.md", "ignoredFiles": [],
    }
    return ["longform"]


def after_create(ctx):
    if not _is_scene(ctx):
        return []
    index = _index_of(ctx)
    if not index:
        return []
    note = ctx.vault.read_note(index)
    block = note.frontmatter.get("longform")
    if note.error or not isinstance(block, dict):
        return []
    scenes = list(block.get("scenes") or [])
    if ctx.title not in scenes:
        block = dict(block, scenes=scenes + [ctx.title])
        fm = yamlio.rewrite_frontmatter(note.fm_text or "", {"longform": block})
        (ctx.vault.root / index).write_text(yamlio.join_note(fm, note.body), encoding="utf-8")
        ctx.vault.refresh()
    return []


def verify(ctx):
    from engine.findings import Finding

    if _is_scene(ctx) and ctx.frontmatter.get("up") and not _index_of(ctx):
        return [Finding(ID, '"up" must link to a longform project.', field="up")]
    return []

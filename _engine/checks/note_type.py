"""The note must match a concrete manifest."""

from engine.findings import Finding, join_values, suggestion

ID = "unknown-type"
ORDER = 5
ABOUT = "Tags select a known note type. Reports likely typos and parent types."


def run(ctx):
    if not ctx.note.has_frontmatter or ctx.note.error:
        return []
    known = ctx.schemas.type_tags()
    if ctx.schema is None:
        out = []
        for tag in ctx.note.tags:
            near = suggestion(tag, known)
            if near:
                out.append(Finding(ID, f'Tag "{tag}" matches no manifest.', field="tags",
                                   severity="warning", hint=f'Did you mean "{near}"?'))
        if not out and not ctx.vault.is_ignored(ctx.path):
            folder = ctx.path.rsplit("/", 1)[0] if "/" in ctx.path else ""
            homes = sorted({s.type_tag.split("/")[0] for s in ctx.schemas.all()
                            if isinstance(s.enforce_folder, str) and s.type_tag and s.enforce_folder.strip("/") == folder})
            if homes:
                near = suggestion("tags", [k for k in ctx.frontmatter if k != "tags"]) if "tags" not in ctx.frontmatter else None
                hint = f'Property "{near}" looks like a typo of "tags".' if near else f"Notes in this folder are tagged: {join_values(homes)}."
                out.append(Finding(ID, f'The tags of this note match no manifest, so nothing else was checked.',
                                   field="tags", severity="warning", hint=hint))
        return out

    parent_tag = ctx.schema.type_tag
    if not parent_tag or not ctx.schema.has_children:
        return []
    described = {
        s.type_tag: s.description for s in ctx.schemas.all()
        if s.type_tag and s.type_tag.startswith(parent_tag + "/") and ctx.schema.path in s.chain
    }
    children = sorted(described)
    if not children:
        return []
    typed = [t for t in ctx.note.tags if t == parent_tag or t.startswith(parent_tag + "/")]
    if len(children) <= 12:
        hint = "Known types:\n" + "\n".join(f"  {tag}  {described[tag]}".rstrip() for tag in children)
    else:
        hint = f"Known types: {join_values(children)}."
    for tag in typed:
        near = suggestion(tag, children)
        if near and near != tag:
            hint = f'Did you mean "{near}"? ' + hint
            break
    return [Finding("abstract-type",
                    f'The note matches only the parent manifest "{ctx.schema.name}", not a specific type.',
                    field="tags", severity="warning", hint=hint)]

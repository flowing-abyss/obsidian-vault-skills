"""Catch property names that look like typos of manifest fields."""

from engine.findings import Finding, suggestion

ID = "unknown-property"
ORDER = 70
ABOUT = "A property that is not in the manifest and looks like a typo of one that is."


def run(ctx):
    if ctx.schema is None:
        return []
    known = list(ctx.schema.fields)
    out = []
    for key in ctx.frontmatter:
        if key in ctx.schema.fields:
            continue
        near = suggestion(key, [k for k in known if k not in ctx.frontmatter])
        if near:
            out.append(Finding(ID, f'Property "{key}" is not in the manifest.', field=key,
                               severity="warning", hint=f'Did you mean "{near}"?'))
    return out

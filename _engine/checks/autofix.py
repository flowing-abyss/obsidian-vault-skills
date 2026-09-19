"""Report what `fix` would change: fixed values, defaults, property order."""

from engine import autofix
from engine.findings import Finding, short

ID = "autofix"
ORDER = 80
ABOUT = "Fixed values, defaults and property order match the manifest. All are fixable."


def run(ctx):
    if ctx.schema is None:
        return []
    _, changes = autofix.plan(ctx.schema, ctx.frontmatter)
    out = []
    for name, rule in changes:
        field = ctx.schema.fields.get(name, {})
        if rule == "fixed":
            message = f'"{name}" must be "{short(field.get("fixed"))}" for this note type.'
        elif rule == "default":
            message = f'"{name}" is empty. The default is "{short(field.get("default"))}".'
        elif rule == "property-order":
            message = "Properties are not in the manifest order."
        else:
            continue
        out.append(Finding(rule, message, field=name, severity="warning", fixable=True))
    return out

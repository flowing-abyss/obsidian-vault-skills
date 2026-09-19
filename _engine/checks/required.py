"""Required properties must be present. An empty value is allowed."""

from engine.findings import Finding, meaning

ID = "required"
ORDER = 10
ABOUT = "Every required property exists in the frontmatter."


def run(ctx):
    if ctx.schema is None:
        return []
    out = []
    for name, field in ctx.schema.fields.items():
        if not field.get("required") or name in ctx.frontmatter:
            continue
        if field.get("fixed") is not None or field.get("default") is not None:
            continue  # reported by the autofix check
        out.append(Finding(ID, f'"{name}" is required but missing.', field=name, fixable=True,
                           hint=f"Add the property. It may be empty. {meaning(field)}".strip()))
    return out

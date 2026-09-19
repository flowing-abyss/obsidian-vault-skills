"""Values of select and multiselect fields must come from the options."""

from engine.findings import Finding, describe_options, meaning, suggestion

ID = "options"
ORDER = 30
ABOUT = "Values come from the allowed options. Fields with strict: false are not checked."


def run(ctx):
    if ctx.schema is None:
        return []
    out = []
    for name, field in ctx.schema.fields.items():
        options = field.get("options")
        value = ctx.frontmatter.get(name)
        if not options or value is None or value == "" or field.get("strict") is False:
            continue
        listed = options if isinstance(options, list) else None
        if listed is not None:
            allowed = [str(o.get("value")) if isinstance(o, dict) else str(o) for o in options]
        elif isinstance(options, dict) and options.get("source"):
            resolution = ctx.sources.resolve(options["source"], ctx.frontmatter)
            if not resolution.resolved:
                continue
            allowed = sorted(resolution.values)
        else:
            continue
        values = value if isinstance(value, list) else [value]
        invalid = [v for v in values if not isinstance(v, (list, dict)) and str(v) not in allowed]
        if not invalid:
            continue
        hint = describe_options(listed if listed is not None else allowed)
        near = suggestion(str(invalid[0]), allowed)
        if near:
            hint = f'Did you mean "{near}"? ' + hint
        if meaning(field):
            hint = f"{meaning(field)} {hint}"
        shown = ", ".join(f'"{v}"' for v in invalid)
        out.append(Finding(ID, f'"{name}" has a value that is not allowed: {shown}.', field=name, hint=hint))
    return out

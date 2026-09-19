"""Numbers must stay inside min and max."""

from engine.findings import Finding

ID = "number-range"
ORDER = 40
ABOUT = "Number fields respect min and max."


def run(ctx):
    if ctx.schema is None:
        return []
    out = []
    for name, field in ctx.schema.fields.items():
        value = ctx.frontmatter.get(name)
        if field.get("type") != "number" or isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        low, high = field.get("min"), field.get("max")
        if low is not None and value < low:
            out.append(Finding(ID, f'"{name}" is {value}, below the minimum {low}.', field=name))
        elif high is not None and value > high:
            out.append(Finding(ID, f'"{name}" is {value}, above the maximum {high}.', field=name))
    return out

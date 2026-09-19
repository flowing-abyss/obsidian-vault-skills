"""A note that has both `start` and `end` must not end before it starts."""

from engine.findings import Finding

ID = "date-order"
ORDER = 45
ABOUT = "When a type has start and end dates, end is not before start."


def run(ctx):
    if ctx.schema is None or not {"start", "end"} <= set(ctx.schema.fields):
        return []
    start, end = ctx.frontmatter.get("start"), ctx.frontmatter.get("end")
    if not isinstance(start, str) or not isinstance(end, str) or len(start) < 10 or len(end) < 10:
        return []
    if end[:10] < start[:10]:
        return [Finding(ID, f'"end" ({end[:10]}) is before "start" ({start[:10]}).', field="end")]
    return []

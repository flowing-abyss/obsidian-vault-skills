"""Fill `created` and `updated` with the current local time."""

import datetime

ID = "timestamps"
ABOUT = "Sets created and updated on new notes. Bumps updated on a change when the note has it."


def now():
    text = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    return text[:-2] + ":" + text[-2:] if text[-5] in "+-" else text


def _has(ctx, name):
    return ctx.schema is not None and name in ctx.schema.fields


def generate(ctx):
    stamp, touched = now(), []
    for name in ("created", "updated"):
        if _has(ctx, name) and not ctx.frontmatter.get(name):
            ctx.frontmatter[name] = stamp
            touched.append(name)
    return touched


def touch(ctx):
    if "updated" in ctx.frontmatter:
        ctx.frontmatter["updated"] = now()
        return ["updated"]
    return []

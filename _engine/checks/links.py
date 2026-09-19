"""Links must point to existing notes, and to notes the manifest allows."""

from engine.findings import Finding, suggestion
from engine.links import link_name
from engine.sources import describe

ID = "link-exists"
ORDER = 50
ABOUT = "Link fields point to existing notes (link-exists) from the allowed source (link-source)."


def run(ctx):
    if ctx.schema is None:
        return []
    out = []
    for name, field in ctx.schema.fields.items():
        if field.get("type") not in ("link", "multilink"):
            continue
        value = ctx.frontmatter.get(name)
        if value is None or value == "":
            continue
        values = [str(v).strip() for v in (value if isinstance(value, list) else [value])
                  if isinstance(v, (str, int, float)) and str(v).strip()]

        missing = [v for v in values if ctx.vault.resolve_link(v) is None]
        if field.get("validate_exists") is False:
            # The manifest allows links to notes that are not written yet.
            values = [v for v in values if v not in missing]
        else:
            if missing:
                shown = ", ".join(f'"{v}"' for v in missing)
                out.append(Finding(ID, f'"{name}" links to a note that does not exist: {shown}.', field=name,
                                   hint="Create the note first or fix the name."))
                values = [v for v in values if v not in missing]

        if not field.get("source") or not values:
            continue
        resolution = ctx.sources.resolve(field["source"], ctx.frontmatter)
        if not resolution.resolved:
            continue
        outside = [v for v in values if link_name(v) not in resolution.base]
        unrelated = [v for v in values if v not in outside and link_name(v) not in resolution.values]
        if outside:
            shown = ", ".join(f'"{v}"' for v in outside)
            near = suggestion(link_name(outside[0]), resolution.base)
            hint = f'Did you mean "[[{near}]]"?' if near else describe(field["source"])
            out.append(Finding("link-source", f'"{name}" links to a note the manifest does not allow here: {shown}.',
                               field=name, hint=hint))
        if unrelated:
            shown = ", ".join(f'"{v}"' for v in unrelated)
            out.append(Finding("link-relation", f'"{name}" links to a note that is not related to this one: {shown}.',
                               field=name, severity="warning", hint=describe(field["source"])))
    return out


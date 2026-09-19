"""The value shape must fit the field type."""

import re

from engine.findings import Finding, short
from engine.links import is_wikilink

ID = "type"
ORDER = 20
ABOUT = "Lists are lists, numbers are numbers, links are quoted wikilinks."

LIST_TYPES = {"list", "multiselect", "multilink"}
_URL_RE = re.compile(r"(^|\()[A-Za-z][A-Za-z0-9+.-]*:")


def _unquoted_link(value):
    return (isinstance(value, list) and len(value) == 1 and isinstance(value[0], list)
            and len(value[0]) == 1 and isinstance(value[0][0], str))


def run(ctx):
    if ctx.schema is None:
        return []
    out = []
    for name, field in ctx.schema.fields.items():
        value = ctx.frontmatter.get(name)
        if value is None or value == "":
            continue
        kind = field.get("type")
        items = value if isinstance(value, list) else [value]

        broken = [v for v in items if _unquoted_link(v)] or ([value] if _unquoted_link(value) else [])
        if broken:
            inner = broken[0][0][0]
            out.append(Finding(ID, f'"{name}" holds an unquoted wikilink.', field=name, fixable=True,
                               hint=f'Write it in quotes: "[[{inner}]]".'))
            continue
        if isinstance(value, dict) or any(isinstance(v, (dict, list)) for v in items):
            out.append(Finding(ID, f'"{name}" must hold plain values, not nested data.', field=name))
            continue

        if kind in LIST_TYPES and not isinstance(value, list):
            out.append(Finding(ID, f'"{name}" must be a list.', field=name, fixable=kind == "list",
                               hint=f'Write it as a list:\n{name}:\n  - {short(value)}'))
        elif kind in ("text", "date", "url", "link", "number", "boolean") and isinstance(value, list):
            out.append(Finding(ID, f'"{name}" must be a single value, not a list.', field=name, severity="warning"))
            continue
        if kind == "number" and any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in items):
            out.append(Finding(ID, f'"{name}" must be a number, got "{short(value)}".', field=name))
        elif kind == "boolean" and any(not isinstance(v, bool) for v in items):
            out.append(Finding(ID, f'"{name}" must be true or false, got "{short(value)}".', field=name))
        elif kind in ("link", "multilink"):
            plain = [v for v in items if not is_wikilink(v)]
            if plain:
                out.append(Finding("link-format", f'"{name}" must hold wikilinks, got "{short(plain[0])}".',
                                   field=name, severity="warning",
                                   hint=f'Write it as "[[{short(plain[0])}]]".'))
        elif kind == "url":
            bad = [v for v in items if not _URL_RE.search(str(v)) and not is_wikilink(v)]
            if bad:
                out.append(Finding("url-format", f'"{name}" does not look like a URL: "{short(bad[0])}".',
                                   field=name, severity="warning"))
    return out

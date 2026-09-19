"""Deterministic fixes, the same ones the plugin applies when a note opens:
`fixed`, `default`, required placeholder, list wrapping, `sort`, property order.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Tuple

from .manifests import Schema


def is_empty(value: Any) -> bool:
    return value is None or value == "" or (isinstance(value, list) and not value)


def _sorted(values: List[Any], descending: bool) -> List[Any]:
    return sorted(values, key=lambda v: str(v).casefold(), reverse=descending)


def _is_bare_link(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 1 and isinstance(value[0], list) \
        and len(value[0]) == 1 and isinstance(value[0][0], str)


def _quote_links(value: Any) -> Any:
    """`- [[Note]]` without quotes parses as a nested list. Turn it back into a link."""
    if _is_bare_link(value):
        return f"[[{value[0][0]}]]"
    if isinstance(value, list) and any(_is_bare_link(v) for v in value):
        return [f"[[{v[0][0]}]]" if _is_bare_link(v) else v for v in value]
    return None


def plan(schema: Schema, frontmatter: Dict[str, Any], sort: bool = False) -> Tuple[Dict[str, Any], List[Tuple[str, str]]]:
    """Return (fixed frontmatter, [(field, rule)]). The input is not changed.

    Sorting is off by default. The plugin sorts with locale rules that Python
    cannot match exactly, so sorting existing lists is left to the plugin.
    """
    fm = copy.deepcopy(frontmatter)
    changes: List[Tuple[str, str]] = []
    for name, value in list(fm.items()):
        repaired = _quote_links(value)
        if repaired is not None:
            fm[name] = repaired
            changes.append((name, "link-quotes"))
    for name, field in schema.fields.items():
        current = fm.get(name)
        if "fixed" in field and field["fixed"] is not None:
            if current != field["fixed"]:
                fm[name] = copy.deepcopy(field["fixed"])
                changes.append((name, "fixed"))
            continue
        if field.get("default") is not None and is_empty(current):
            fm[name] = copy.deepcopy(field["default"])
            changes.append((name, "default"))
        elif field.get("required") and name not in fm:
            fm[name] = None
            changes.append((name, "required"))
        value = fm.get(name)
        if field.get("type") == "list" and value is not None and not isinstance(value, list):
            fm[name] = [value]
            changes.append((name, "shape"))
        value = fm.get(name)
        if sort and field.get("sort") in ("alphabetical", "alphabetical-desc") and isinstance(value, list):
            if all(not isinstance(v, (list, dict)) for v in value):
                ordered = _sorted(value, field["sort"] == "alphabetical-desc")
                if ordered != value:
                    fm[name] = ordered
                    changes.append((name, "sort"))

    order = schema.order
    keys = list(fm)
    wanted = [k for k in order if k in fm] + [k for k in keys if k not in order]
    if wanted != keys:
        fm = {k: fm[k] for k in wanted}
        # Report the order only when the properties that were already there
        # are out of order. A property added above is not an order problem.
        before = [k for k in keys if k in frontmatter]
        if before != [k for k in wanted if k in frontmatter]:
            changes.append(("", "property-order"))
    return fm, changes

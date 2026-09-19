"""Query language used by manifest `target.query` and field sources.

Same grammar as the Metadata Validator plugin:

    term AND term     both must match (binds tighter than OR)
    term OR term      either must match
    -term / NOT term  negation
    ( ... )           grouping of a whole term

Terms:

    #tag              note has the tag or a child tag
    "folder/"         note path starts with the prefix
    key=value         property equals value (a list: contains value)
    key=              property is empty or absent
    key<value         also >, <=, >= (numbers, ISO dates, then strings)
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from .links import is_wikilink, link_name

_TERM_RE = re.compile(r"^([^<>=#\"'][^<>=]*?)\s*(<=|>=|<|>|=)\s*([\s\S]*)$")
_DATE_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?$"
)
_TAG_RE = re.compile(r"#([\w/-]+)")


def evaluate(
    query: str,
    path: str,
    tags: List[str],
    frontmatter: Dict[str, Any],
    dataview: bool = False,
) -> bool:
    """True when the note matches. `dataview` reads a quoted term as a folder."""
    for group in _split_outer(query, " OR "):
        terms = _split_outer(group, " AND ")
        if terms and all(_term(t.strip(), path, tags, frontmatter, dataview) for t in terms):
            return True
    return False


def first_tag(query: str) -> Optional[str]:
    """First #tag named in a query, without the hash. Negated tags are skipped."""
    for m in _TAG_RE.finditer(query or ""):
        before = query[: m.start()].rstrip()
        if before.endswith("-") or before.upper().endswith("NOT"):
            continue
        return m.group(1)
    return None


def _split_outer(text: str, sep: str) -> List[str]:
    out: List[str] = []
    depth = 0
    quote = ""
    start = 0
    upper = text.upper()
    sep_upper = sep.upper()
    i = 0
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == quote:
                quote = ""
        elif ch in "\"'":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif depth == 0 and upper.startswith(sep_upper, i):
            out.append(text[start:i].strip())
            i += len(sep)
            start = i
            continue
        i += 1
    out.append(text[start:].strip())
    return [p for p in out if p]


def _term(raw: str, path: str, tags: List[str], fm: Dict[str, Any], dataview: bool) -> bool:
    term = raw.strip()
    negate = False
    while term:
        if term.startswith("-"):
            negate = not negate
            term = term[1:].strip()
        elif re.match(r"^NOT\s+", term, re.I):
            negate = not negate
            term = term[3:].strip()
        else:
            break
    if not term:
        return False
    result = _base_term(term, path, tags, fm, dataview)
    return not result if negate else result


def _base_term(term: str, path: str, tags: List[str], fm: Dict[str, Any], dataview: bool) -> bool:
    if term.startswith("(") and term.endswith(")"):
        return evaluate(term[1:-1].strip(), path, tags, fm, dataview)

    if term.startswith("#"):
        wanted = term[1:].lower()
        for tag in tags:
            have = tag.lstrip("#").lower()
            if have == wanted or have.startswith(wanted + "/"):
                return True
        return False

    m = _TERM_RE.match(term)
    if m:
        return _property_term(fm.get(m.group(1).strip()), m.group(2), _unquote(m.group(3).strip()))

    folder = re.sub(r"^[\"']|[\"']$", "", term)
    if folder.endswith("/"):
        return path.startswith(folder)
    if dataview and term[:1] in "\"'":
        return path.startswith(folder + "/")
    return False


def _unquote(raw: str) -> str:
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return re.sub(r"\\([\"'])", r"\1", raw[1:-1])
    return raw


def _is_empty(value: Any) -> bool:
    return value is None or value == "" or (isinstance(value, list) and not value)


def value_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (str, int, float)):
        return str(value)
    return repr(value)


def values_equal(a: Any, b: Any) -> bool:
    """Links compare by note name, everything else by text."""
    if a is None or b is None:
        return a is b
    sa, sb = value_text(a), value_text(b)
    if is_wikilink(sa) or is_wikilink(sb):
        return link_name(sa) == link_name(sb)
    return sa == sb


def _property_term(have: Any, op: str, want: str) -> bool:
    if op == "=":
        if want == "":
            return _is_empty(have)
        if _is_empty(have):
            return False
        values = have if isinstance(have, list) else [have]
        return any(values_equal(v, want) for v in values)
    if _is_empty(have) or want == "":
        return False
    values = have if isinstance(have, list) else [have]
    for v in values:
        cmp = _compare(v, want)
        if cmp is None:
            continue
        if (
            (op == "<" and cmp < 0)
            or (op == ">" and cmp > 0)
            or (op == "<=" and cmp <= 0)
            or (op == ">=" and cmp >= 0)
        ):
            return True
    return False


def _compare(a: Any, b: str) -> Optional[int]:
    sa, sb = value_text(a).strip(), b.strip()
    if not sa or not sb:
        return None
    try:
        na, nb = float(sa), float(sb)
        return (na > nb) - (na < nb)
    except ValueError:
        pass
    if _DATE_RE.match(sa) and _DATE_RE.match(sb):
        if len(sa) == 10 or len(sb) == 10:
            sa, sb = sa[:10], sb[:10]
        return (sa > sb) - (sa < sb)
    return (sa > sb) - (sa < sb)

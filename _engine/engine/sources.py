"""Resolve a field source to the set of allowed values.

Declarative sources (`query`, `folder`, `tag`, `property`) are evaluated
directly. JavaScript sources are never executed. A few fixed shapes are
recognised and answered from the vault index:

  1. dv.pages("QUERY")  with an optional relation filter
       .where(p => [].concat(p.X || []).some(c => [].concat(currentPage.Y ...
     Allowed: notes matching QUERY whose X shares a value with this note's Y.
  2. manifests under a schemas folder, mapped to their type tag
  3. a static list "a,b,c".split(",") mapped to `prefix/${v}`
  4. every distinct value of one frontmatter property across the vault

Any other JavaScript is reported as unresolved and the check is skipped,
so an unknown source never turns into an empty allow-list.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set

from . import query
from .links import link_name, nfc
from .manifests import Schemas
from .vault import Vault, tags_of

_DV_PAGES_RE = re.compile(r"""dv\.pages\(\s*(["'])(.*?)\1\s*\)""")
_RELATION_RE = re.compile(
    r"\.where\(\s*p\s*=>\s*\[\]\.concat\(p\.([\w-]+)\s*\|\|\s*\[\]\)\.some\(\s*c\s*=>\s*"
    r"\[\]\.concat\(\s*(?:currentPage\s*&&\s*)?currentPage\.([\w-]+)\s*\|\|\s*\[\]\)"
)
_MANIFEST_DIR_RE = re.compile(r"""f\.path\.startsWith\(\s*(["'])(.*?)\1\s*\)\s*&&\s*f\.basename\s*={2,3}\s*(["'])manifest\3""")
_STATIC_LIST_RE = re.compile(r"""(["'])([\w\-/, ]+)\1\.split\(\s*(["']),\3\s*\)\.map\(\s*v\s*=>\s*\(\{\s*value\s*:\s*`([^`$]*)\$\{v\}`""")
_DISTINCT_RE = re.compile(r"getFileCache\(f\)\?\.frontmatter\?\.([\w-]+)\s*\|\|\s*\[\]")


class Resolution:
    def __init__(self, values: Optional[Set[str]], reason: str = "", base: Optional[Set[str]] = None):
        self.values = values
        self.reason = reason
        # Values before a relation filter. Tells "wrong kind of note" from
        # "right kind, but not related to this note".
        self.base = base if base is not None else values

    @property
    def resolved(self) -> bool:
        return self.values is not None


class Sources:
    def __init__(self, vault: Vault, schemas: Schemas):
        self.vault = vault
        self.schemas = schemas
        self._query_cache: Dict[str, List[str]] = {}

    def resolve(self, source: Any, current: Dict[str, Any]) -> Resolution:
        if not isinstance(source, dict) or not source:
            return Resolution(None, "source is empty")
        js = source.get("js")
        if js:
            return self._javascript(str(js), current)
        if source.get("query"):
            return Resolution({_stem(p) for p in self._matching(str(source["query"]), False)})
        return Resolution({_stem(p) for p in self.vault.notes() if self._declarative(p, source)})

    # -- declarative -------------------------------------------------------

    def _declarative(self, path: str, source: Dict[str, Any]) -> bool:
        fm = self.vault.frontmatter_of(path)
        if source.get("folder") and not path.startswith(str(source["folder"])):
            return False
        if source.get("tag"):
            wanted = str(source["tag"]).lstrip("#").lower()
            if not any(t.lower() == wanted or t.lower().startswith(wanted + "/") for t in tags_of(fm)):
                return False
        prop = source.get("property")
        if isinstance(prop, dict):
            for key, want in prop.items():
                have = fm.get(key)
                values = have if isinstance(have, list) else [have]
                if not any(query.value_text(v) == str(want) for v in values):
                    return False
        return bool(source.get("folder") or source.get("tag") or source.get("property"))

    def _matching(self, q: str, dataview: bool) -> List[str]:
        key = f"{int(dataview)}|{q}"
        if key not in self._query_cache:
            hits = []
            for path in self.vault.notes():
                fm = self.vault.frontmatter_of(path)
                if query.evaluate(q, path, tags_of(fm), fm, dataview=dataview):
                    hits.append(path)
            self._query_cache[key] = hits
        return self._query_cache[key]

    # -- recognised JavaScript shapes --------------------------------------

    def _javascript(self, js: str, current: Dict[str, Any]) -> Resolution:
        pages = _DV_PAGES_RE.search(js)
        if pages:
            return self._dv_pages(js, pages.group(2), current)

        values: Set[str] = set()
        recognised = False
        for m in _STATIC_LIST_RE.finditer(js):
            recognised = True
            prefix = m.group(4)
            values.update(prefix + v.strip() for v in m.group(2).split(",") if v.strip())
        for m in _MANIFEST_DIR_RE.finditer(js):
            recognised = True
            for schema in self.schemas.under(m.group(2)):
                tag = schema.type_tag
                if tag and "/" in tag:
                    values.add(tag)
        if recognised:
            return Resolution(values)

        distinct = _DISTINCT_RE.search(js)
        if distinct and "getMarkdownFiles()" in js:
            key = distinct.group(1)
            for path in self.vault.notes():
                have = self.vault.frontmatter_of(path).get(key)
                for v in have if isinstance(have, list) else [have]:
                    if v not in (None, ""):
                        values.add(query.value_text(v))
            return Resolution(values)

        return Resolution(None, "JavaScript source has a shape the engine does not recognise")

    def _dv_pages(self, js: str, q: str, current: Dict[str, Any]) -> Resolution:
        relations = _RELATION_RE.findall(js)
        if js.count(".where(") + js.count(".filter(") != len(relations):
            return Resolution(None, "JavaScript source filters pages in a way the engine does not recognise")
        paths = self._matching(q, True)
        base = {_stem(p) for p in paths}
        for their_key, my_key in relations:
            mine = {link_name(query.value_text(v)) for v in _as_list(current.get(my_key))}
            paths = [
                p for p in paths
                if mine & {link_name(query.value_text(v)) for v in _as_list(self.vault.frontmatter_of(p).get(their_key))}
            ]
        return Resolution({_stem(p) for p in paths}, base=base)


def _as_list(value: Any) -> List[Any]:
    if value is None or value == "":
        return []
    items = value if isinstance(value, list) else [value]
    # An unquoted `- [[Note]]` parses as a nested list. Read it as the link it
    # was meant to be, so one mistake does not cascade into a relation warning.
    return [f"[[{v[0][0]}]]" if isinstance(v, list) and len(v) == 1 and isinstance(v[0], list) and len(v[0]) == 1 else v
            for v in items]


def _stem(path: str) -> str:
    name = path.rsplit("/", 1)[-1]
    return nfc(name[:-3] if name.endswith(".md") else name)


def describe(source: Any) -> str:
    """One plain sentence about which notes a link source allows."""
    if not isinstance(source, dict):
        return ""
    js = str(source.get("js") or "")
    q = source.get("query")
    if not q:
        m = _DV_PAGES_RE.search(js)
        q = m.group(2) if m else None
    text = f"Allowed notes match: {q}." if q else ""
    relation = _RELATION_RE.search(js)
    if relation:
        text += f' They must share a value in "{relation.group(1)}" with this note\'s "{relation.group(2)}".'
    return text.strip()

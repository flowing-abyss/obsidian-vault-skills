"""Whole vault health report. Read only.

Sections:
  manifests   YAML problems, keys the engine does not know, folders that are missing
  sources     JavaScript sources the engine cannot answer
  templates   template.md properties that drifted from the manifest
  notes       findings of every note, grouped by rule
  links       broken wikilinks in note bodies (only with links=True)
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from .validate import Engine

_TEMPLATE_KEY_RE = re.compile(r"^([A-Za-z][\w-]*):", re.M)
_FENCE_RE = re.compile(r"^(`{3,}|~{3,}).*?^\1[ \t]*$", re.S | re.M)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
_COMMENT_RE = re.compile(r"%%.*?%%|<!--.*?-->", re.S)
_WIKILINK_RE = re.compile(r"!?\[\[([^\]\n]+?)\]\]")
# Properties a template may carry although no manifest lists them.
_TEMPLATE_EXTRAS = {"longform"}  # a nested block for the Longform plugin; no field type can describe it


def manifests(engine: Engine) -> List[str]:
    out = [f"{p.path}: {p.message}" for p in engine.schemas.problems]
    seen = set()
    for schema in engine.schemas.all():
        folder = schema.enforce_folder
        if isinstance(folder, str) and folder not in seen:
            seen.add(folder)
            if not (engine.vault.root / folder.strip("/")).is_dir():
                out.append(f'{schema.path}: enforce_folder "{folder}" does not exist in the vault.')
    return out


def sources(engine: Engine) -> List[str]:
    out = {}
    for schema in engine.schemas.all():
        fields = schema.own.get("fields")
        for name, field in (fields.items() if isinstance(fields, dict) else []):
            options = field.get("options")
            for source in (field.get("source"), options.get("source") if isinstance(options, dict) else None):
                if isinstance(source, dict) and source.get("js"):
                    res = engine.sources.resolve(source, {})
                    if not res.resolved:
                        out[f"{schema.path}: {name}"] = res.reason
    return [f"{where}: {reason}. The field is checked only in part." for where, reason in sorted(out.items())]


def templates(engine: Engine) -> List[str]:
    """Compare the properties of each `template.md` with its manifest."""
    out = []
    for schema in engine.schemas.all():
        file = engine.vault.root / schema.folder / "template.md"
        if not file.is_file() or not schema.type_tag:
            continue
        parts = re.split(r'^(?:<% "---" %>|---)[ \t]*$', file.read_text(encoding="utf-8"), maxsplit=2, flags=re.M)
        if len(parts) != 3:
            continue
        keys = _TEMPLATE_KEY_RE.findall(parts[1])
        # A parent template serves every child type, so a property that any
        # child manifest defines (icon, color) is not drift.
        inherited = {name for child in engine.schemas.all() if schema.path in child.chain for name in child.fields}
        extra = [k for k in keys if k not in schema.fields and k not in inherited and k not in _TEMPLATE_EXTRAS]
        # Only required properties must be in a template. Optional ones are the
        # author's choice, and the plugin writes `fixed` values itself.
        missing = [k for k, f in schema.fields.items()
                   if k not in keys and f.get("required") and f.get("fixed") is None]
        where = f"{schema.folder}/template.md"
        if extra:
            out.append(f"{where}: has properties the manifest does not define: {', '.join(extra)}.")
        if missing:
            out.append(f"{where}: lacks required manifest properties: {', '.join(missing)}.")
    return out


def notes(engine: Engine, folder: Optional[str] = None, rule: Optional[str] = None, errors_only: bool = False) -> Dict[str, Any]:
    by_rule: Dict[str, int] = {}
    by_type: Dict[str, int] = {}
    files = []
    checked = 0
    for path in sorted(engine.vault.notes()):
        if engine.vault.is_ignored(path) or (folder and not path.startswith(folder)):
            continue
        try:
            note = engine.vault.read_note(path)
        except (OSError, UnicodeDecodeError):
            continue  # moved or deleted while the audit ran
        checked += 1
        schema = engine.schemas.for_note(path, note.frontmatter) if note.has_frontmatter and not note.error else None
        kind = schema.type_tag.split("/")[0] if schema and schema.type_tag else "(no manifest)"
        by_type[kind] = by_type.get(kind, 0) + 1
        found = [f for f in engine.check_note(note) if f.severity in ("error", "warning")]
        if errors_only:
            found = [f for f in found if f.severity == "error"]
        if rule:
            found = [f for f in found if f.rule == rule]
        if not found:
            continue
        for f in found:
            by_rule[f.rule] = by_rule.get(f.rule, 0) + 1
        files.append((path, found))
    return {"checked": checked, "by_rule": by_rule, "by_type": by_type, "files": files}


def body_links(engine: Engine, folder: Optional[str] = None) -> List[str]:
    out = []
    for path in sorted(engine.vault.notes()):
        if engine.vault.is_ignored(path) or (folder and not path.startswith(folder)):
            continue
        try:
            body = engine.vault.read_note(path).body
        except (OSError, UnicodeDecodeError):
            continue
        text = _COMMENT_RE.sub("", _INLINE_CODE_RE.sub("", _FENCE_RE.sub("", body)))
        missing = []
        for m in _WIKILINK_RE.finditer(text):
            target = m.group(1).split("|")[0].split("#")[0].strip()
            if target and "<%" not in target and "{{" not in target and engine.vault.resolve_link(target) is None:
                if target not in missing:
                    missing.append(target)
        if missing:
            shown = ", ".join(f"[[{t}]]" for t in missing[:5])
            more = f", and {len(missing) - 5} more" if len(missing) > 5 else ""
            out.append(f"{path}: {shown}{more}")
    return out

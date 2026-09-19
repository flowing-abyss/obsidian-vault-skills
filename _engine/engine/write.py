"""Create notes and change properties. Every write is validated first.

Nothing is written when the result would have errors. Writes are atomic and
touch only the properties that change. The body and unknown properties keep
their exact text.
"""

from __future__ import annotations

import copy
import os
import re
from typing import Any, Dict, List, Optional

from . import autofix, yamlio
from .findings import Finding
from .links import as_wikilink
from .validate import Context, Engine, applies
from .vault import Note

LIST_TYPES = {"list", "multiselect", "multilink"}
# Warnings in old notes, but a new write must not introduce them.
STRICT_ON_WRITE = {"link-relation", "task-self-link"}
_FORBIDDEN = re.compile(r'[\\/:*?"<>|#^\[\]]')


class WriteError(Exception):
    def __init__(self, message: str, findings: Optional[List[Finding]] = None):
        super().__init__(message)
        self.message = message
        self.findings = findings or []


class Result:
    def __init__(self, path: str, findings: List[Finding], filled: List[str], written: bool):
        self.path = path
        self.findings = findings
        self.filled = filled
        self.written = written


# ---------------------------------------------------------------------------
# Value parsing
# ---------------------------------------------------------------------------


def parse_assignments(pairs: List[str]) -> Dict[str, List[str]]:
    """["key=value", ...] to {key: [values]}. Repeating a key adds values."""
    out: Dict[str, List[str]] = {}
    for pair in pairs:
        if "=" not in pair:
            raise WriteError(f'Expected key=value, got "{pair}".')
        key, value = pair.split("=", 1)
        out.setdefault(key.strip(), []).append(value.strip())
    return out


def coerce(field: Optional[Dict[str, Any]], raw: List[str], name: str = "") -> Any:
    """Turn command line text into the value the field type expects."""
    kind = (field or {}).get("type", "text")
    if name in ("tags", "aliases", "cssclasses"):
        kind = "list"  # Obsidian always stores these as lists
    values: List[Any] = [v for v in raw if v != ""]
    if kind in ("link", "multilink"):
        values = [as_wikilink(v) for v in values]
    elif kind == "number":
        values = [yamlio.plain_scalar(v) for v in values]
    elif kind == "boolean":
        values = [yamlio.plain_scalar(v.lower()) for v in values]
    if kind in LIST_TYPES or (field is None and len(values) > 1):
        return values
    if not values:
        return None
    if len(values) > 1:
        return values  # the type check reports this
    return values[0]


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------


class Writer:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.vault = engine.vault

    def new(
        self,
        type_name: str,
        title: str,
        values: Dict[str, List[str]],
        body: str = "",
        folder: Optional[str] = None,
        dry_run: bool = False,
    ) -> Result:
        schema = self.engine.schemas.for_type(type_name)
        if schema is None:
            from .findings import suggestion

            tags = self.engine.schemas.type_tags()
            near = suggestion(type_name.lstrip("#"), tags)
            family = type_name.lstrip("#").split("/")[0]
            related = [t for t in tags if t.split("/")[0] == family]
            text = f'Unknown note type "{type_name}".'
            if near:
                text += f' Did you mean "{near}"?'
            if related:
                text += f' Types in "{family}": {", ".join(related)}.'
            else:
                text += " List all types with: vault.py types"
            raise WriteError(text)
        title = title.strip()
        bad = sorted(set(_FORBIDDEN.findall(title)))
        if not title or bad or len(title) > 200:
            reason = "is empty" if not title else f'has characters not allowed in a file name: {" ".join(bad)}' if bad else "is longer than 200 characters"
            raise WriteError(f'Title "{title}" {reason}.')
        probe = Note(f"{title}.md", "")
        probe.frontmatter = {"tags": [schema.type_tag] if schema.type_tag else []}
        extra: Dict[str, Any] = {}
        for module in self.engine.computes:
            if applies(module, Context(self.engine, probe, schema)):
                extra.update(getattr(module, "ACCEPTS", {}))
        unknown = [k for k in values if k not in schema.fields and k not in extra]
        if unknown:
            known = ", ".join(list(schema.fields) + list(extra))
            raise WriteError(f'Properties not in manifest "{schema.name}": {", ".join(unknown)}. Known: {known}')
        frontmatter: Dict[str, Any] = {}
        for name in schema.order + [n for n in schema.fields if n not in schema.order]:
            if name not in schema.fields or name in frontmatter:
                continue
            frontmatter[name] = coerce(schema.fields[name], values[name], name) if name in values else None
        if "tags" in schema.fields and not frontmatter.get("tags") and schema.type_tag:
            frontmatter["tags"] = [schema.type_tag]
        for name, field in extra.items():
            if name in values and name not in frontmatter:
                frontmatter[name] = coerce(field, values[name], name)
        draft = Note(f"{title}.md", "")
        draft.frontmatter = frontmatter
        draft_ctx = Context(self.engine, draft, schema)
        draft_ctx.title = title

        placed, may_create = None, False
        for module in self.engine.computes:
            fn = getattr(module, "place", None)
            if fn is not None and applies(module, draft_ctx):
                placed = fn(draft_ctx) or placed
                may_create = may_create or bool(placed)
        target_folder = folder or placed or (schema.enforce_folder if isinstance(schema.enforce_folder, str) else None)
        if not target_folder:
            raise WriteError(f'Manifest "{schema.name}" sets no enforce_folder. Pass --folder.')
        target_folder = target_folder.strip("/")
        if not (self.vault.root / target_folder).is_dir() and not (may_create and target_folder == (placed or "").strip("/")):
            raise WriteError(f'Folder "{target_folder}" does not exist. New folders are not created.')
        path = f"{target_folder}/{title}.md"
        if self.vault.exists(path):
            raise WriteError(f'"{path}" already exists. Use set, add or remove to change it.')

        note = Note(path, "")
        note.frontmatter = frontmatter
        ctx = Context(self.engine, note, schema)
        ctx.title = title
        filled = self._compute(ctx, "generate")
        frontmatter = note.frontmatter
        frontmatter, changes = autofix.plan(schema, frontmatter, sort=True)
        filled += [name for name, rule in changes if rule in ("fixed", "default") and name]

        lines: List[str] = []
        for key, value in frontmatter.items():
            lines += yamlio.dump_property(key, value)
        scaffold = schema.template_body(self.vault)
        if body.strip():
            scaffold = scaffold.replace("💤", "").rstrip()
        full_body = "\n\n".join(part for part in (scaffold.strip("\n"), body.strip("\n")) if part.strip())
        text = yamlio.join_note("\n".join(lines), ("\n" + full_body + "\n") if full_body else "")
        return self._commit(path, text, filled, dry_run, created=True)

    def change(
        self,
        path: str,
        set_values: Optional[Dict[str, List[str]]] = None,
        add_values: Optional[Dict[str, List[str]]] = None,
        remove_values: Optional[Dict[str, List[str]]] = None,
        dry_run: bool = False,
    ) -> Result:
        note = self.vault.read_note(path)
        if note.error:
            raise WriteError(f"Frontmatter is not valid YAML: {note.error}. Fix it by hand first.")
        schema = self.engine.schemas.for_note(path, note.frontmatter)
        fields = schema.fields if schema else {}
        fm = copy.deepcopy(note.frontmatter)
        changes: Dict[str, Any] = {}

        for key, raw in (set_values or {}).items():
            changes[key] = coerce(fields.get(key), raw, key)
        for key in list(add_values or {}) + list(remove_values or {}):
            kind = fields.get(key, {}).get("type")
            if kind and kind not in LIST_TYPES and key not in ("tags", "aliases", "cssclasses"):
                raise WriteError(f'"{key}" holds a single value ({kind}). Use: set "{path}" {key}=value')
        for key, raw in (add_values or {}).items():
            current = changes.get(key, fm.get(key))
            items = [] if current is None else list(current) if isinstance(current, list) else [current]
            for value in _as_items(coerce(fields.get(key, {"type": "list"}), raw, key)):
                if value not in items:
                    items.append(value)
            changes[key] = items
        for key, raw in (remove_values or {}).items():
            current = changes.get(key, fm.get(key))
            drop = _as_items(coerce(fields.get(key, {"type": "list"}), raw, key))
            if isinstance(current, list):
                changes[key] = [v for v in current if v not in drop]
            elif current in drop:
                changes[key] = None
        if not changes:
            raise WriteError("Nothing to change. Pass key=value pairs.")

        fm.update(changes)
        staged = Note(path, note.text)
        staged.frontmatter = fm
        ctx = Context(self.engine, staged, schema)
        for name in self._compute(ctx, "touch"):
            changes[name] = fm[name]
        new_fm = yamlio.rewrite_frontmatter(note.fm_text or "", changes)
        text = yamlio.join_note(new_fm, note.body)
        return self._commit(path, text, [], dry_run, before=self.engine.check_note(note), changed=sorted(changes))

    def fix(self, path: str, dry_run: bool = False) -> Result:
        note = self.vault.read_note(path)
        if note.error or not note.has_frontmatter:
            raise WriteError("The note has no valid frontmatter. Fix it by hand first.")
        schema = self.engine.schemas.for_note(path, note.frontmatter)
        if schema is None:
            return Result(path, self.engine.check_note(note), [], False)
        fixed, plan = autofix.plan(schema, note.frontmatter)
        if not plan:
            return Result(path, self.engine.check_note(note), [], False)
        changes = {name: fixed[name] for name, rule in plan if name}
        order = list(fixed) if any(rule == "property-order" for _, rule in plan) else None
        new_fm = yamlio.rewrite_frontmatter(note.fm_text or "", changes, order=order)
        text = yamlio.join_note(new_fm, note.body)
        labels = [f"{name or 'properties'} ({rule})" for name, rule in plan]
        return self._commit(path, text, labels, dry_run, allow_errors=True)

    # -- helpers -----------------------------------------------------------

    def _compute(self, ctx: Context, hook: str) -> List[str]:
        touched: List[str] = []
        for module in self.engine.computes:
            fn = getattr(module, hook, None)
            if fn is None or not applies(module, ctx):
                continue
            touched += fn(ctx) or []
        return touched

    def _commit(
        self,
        path: str,
        text: str,
        filled: List[str],
        dry_run: bool,
        created: bool = False,
        allow_errors: bool = False,
        before: Optional[List[Finding]] = None,
        changed: Optional[List[str]] = None,
    ) -> Result:
        staged = Note(path, text)
        findings = self.engine.check_note(staged)
        errors = [f for f in findings if f.severity == "error" or f.rule in STRICT_ON_WRITE]
        if before is not None:
            old = {(f.rule, f.field, f.message) for f in before}
            errors = [f for f in errors if (f.rule, f.field, f.message) not in old]
        if errors and not allow_errors:
            raise WriteError("Nothing was written. The result would have errors.", errors)
        if dry_run:
            return Result(path, findings, filled, False)
        full = self.vault.root / path
        full.parent.mkdir(parents=True, exist_ok=True)  # only a compute `place` can name a new folder
        tmp = full.with_name(full.name + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, full)
        self.vault.refresh()
        ctx = Context(self.engine, staged, self.engine.schemas.for_note(path, staged.frontmatter))
        ctx.changed = changed or []
        self._compute(ctx, "after_create" if created else "after_change")
        return Result(path, findings, filled, True)


def _as_items(value: Any) -> List[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]

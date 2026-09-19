"""Validation pipeline: note -> schema -> checks -> findings."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .findings import LEVELS, Finding
from .manifests import Schema, Schemas
from .sources import Sources
from .vault import ENGINE_DIR, Note, Vault


class Context:
    """Everything a check may need for one note."""

    def __init__(self, engine: "Engine", note: Note, schema: Optional[Schema]):
        self.engine = engine
        self.vault = engine.vault
        self.schemas = engine.schemas
        self.sources = engine.sources
        self.note = note
        self.path = note.path
        self.frontmatter = note.frontmatter
        self.schema = schema
        self.title = note.path.rsplit("/", 1)[-1][:-3]
        self.changed: List[str] = []

    @property
    def manifest(self) -> str:
        return self.schema.path if self.schema else ""


class Engine:
    def __init__(self, vault: Optional[Vault] = None):
        self.vault = vault or Vault()
        self.schemas = Schemas(self.vault)
        self.sources = Sources(self.vault, self.schemas)
        self.checks = _load_plugins("checks", self.vault)
        self.computes = _load_plugins("compute", self.vault)

    def severity(self, check_id: str, default: str) -> str:
        level = self.vault.config.get("checks", {}).get(check_id, default)
        return level if level in LEVELS else default

    def check_note(self, note: Note) -> List[Finding]:
        findings: List[Finding] = []
        schema = None
        if note.has_frontmatter and note.error is None:
            schema = self.schemas.for_note(note.path, note.frontmatter)
        ctx = Context(self, note, schema)
        runners = [getattr(m, "run", None) for m in self.checks]
        runners += [getattr(m, "verify", None) for m in self.computes if applies(m, ctx)]
        for runner in runners:
            if runner is None:
                continue
            for finding in runner(ctx) or []:
                level = self.severity(finding.rule, finding.severity)
                if level == "off":
                    continue
                finding.severity = level
                if not finding.manifest and schema is not None:
                    finding.manifest = schema.origin(finding.field)
                findings.append(finding)
        rank = {"error": 0, "warning": 1, "info": 2}
        findings.sort(key=lambda f: rank.get(f.severity, 3))
        return findings

    def check_path(self, path: str) -> List[Finding]:
        return self.check_note(self.vault.read_note(path))


def applies(module: Any, ctx: Context) -> bool:
    """A compute module runs only for notes that match its WHEN query."""
    from . import query

    when = getattr(module, "WHEN", "")
    if not when:
        return True
    return query.evaluate(when, ctx.path, ctx.note.tags, ctx.frontmatter)


def _load_plugins(kind: str, vault: Vault) -> List[Any]:
    """Import every module in `_engine/<kind>/` and `_engine/local/<kind>/`."""
    modules = []
    for folder in (ENGINE_DIR / kind, vault.local_dir / kind):
        if not folder.is_dir():
            continue
        for file in sorted(folder.glob("*.py")):
            if file.name.startswith("_"):
                continue
            name = f"vault_engine_{kind}_{folder.parent.name}_{file.stem}"
            spec = importlib.util.spec_from_file_location(name, file)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            if getattr(module, "ID", None):
                modules.append(module)
    modules.sort(key=lambda m: getattr(m, "ORDER", 50))
    return modules

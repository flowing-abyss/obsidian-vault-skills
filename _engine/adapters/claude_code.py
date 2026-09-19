"""Claude Code hooks.

pre-tool-use   before Write, Edit or MultiEdit.
               Protected zone: the first attempt is stopped with a notice. The
               same edit repeated within ten minutes goes through. The agent is
               warned before the change, nothing is forbidden for good, and no
               setting has to be switched while the user works on the vault.
               Notes: remembers the findings the note already has. Never prints.
post-tool-use  after the edit: validates the note and lists only findings the
               edit introduced. Older errors are counted in one line.
               Exit 2 sends stderr back to the agent.

The hooks never write to the vault. Any internal error exits 0.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import List, Optional, Set

from engine.findings import Finding
from engine.report import render
from engine.validate import Engine
from engine.vault import Vault

ZONE_WINDOW_SECONDS = 600


def run(event: str, vault_root=None) -> int:
    if event not in ("pre-tool-use", "post-tool-use"):
        return 0
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    file_path = (payload.get("tool_input") or {}).get("file_path")
    if not file_path:
        return 0
    vault = Vault(vault_root)
    path = vault.rel(file_path)
    if path.startswith("/") or path.startswith(".."):
        return 0
    key = hashlib.sha1(path.encode("utf-8")).hexdigest()
    state = vault.local_dir / "state"
    snapshot = state / "pre" / f"{key}.json"
    zone_mark = state / "zone" / key
    is_note = path.endswith(".md") and not vault.is_ignored(path) and not path.startswith(".")
    notice = vault.zone_notice(path)

    if event == "pre-tool-use":
        if notice:
            recent = zone_mark.is_file() and time.time() - zone_mark.stat().st_mtime < ZONE_WINDOW_SECONDS
            zone_mark.parent.mkdir(parents=True, exist_ok=True)
            if not recent:
                zone_mark.write_text("asked", encoding="utf-8")
                print(f'Stopped once: "{path}" is in a protected zone. {notice} '
                      "If the user approved this exact change, repeat the same edit and it will go through. "
                      "If not, ask the user first.", file=sys.stderr)
                return 2
            zone_mark.write_text("passed", encoding="utf-8")
        if is_note and vault.exists(path):
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            snapshot.write_text(json.dumps(sorted(_signatures(_findings(vault, path)))), encoding="utf-8")
        return 0

    messages: List[str] = []
    warned_before = (zone_mark.is_file() and zone_mark.read_text(encoding="utf-8") == "passed"
                     and time.time() - zone_mark.stat().st_mtime < ZONE_WINDOW_SECONDS)
    if notice and not warned_before:
        messages.append(f'Notice: "{path}" is in a protected zone. {notice}')
    if is_note and vault.exists(path):
        findings = _findings(vault, path)
        known = _load(snapshot)
        fresh = [f for f in findings if known is None or _signature(f) not in known]
        older = [f for f in findings if f not in fresh]
        older_errors = sum(1 for f in older if f.severity == "error")
        tail = f'python3 .claude/_engine/vault.py check "{path}"'
        if fresh:
            text = render(path, fresh)
            if older:
                text += f"\n  {len(older)} older finding(s) were here before this edit and are not listed. See all: {tail}"
            messages.append(text)
        elif older_errors:
            messages.append(f"{path}: this edit added no problems, but the note still has {older_errors} older error(s). See them: {tail}")
    if snapshot.is_file():
        snapshot.unlink()
    if not messages:
        return 0
    print("\n".join(messages), file=sys.stderr)
    return 2


def _findings(vault: Vault, path: str) -> List[Finding]:
    return [f for f in Engine(vault).check_path(path) if f.severity in ("error", "warning")]


def _signature(finding: Finding) -> str:
    return f"{finding.rule}|{finding.field}|{finding.message}"


def _signatures(findings: List[Finding]) -> Set[str]:
    return {_signature(f) for f in findings}


def _load(snapshot: Path) -> Optional[Set[str]]:
    if not snapshot.is_file():
        return None
    try:
        return set(json.loads(snapshot.read_text(encoding="utf-8")))
    except (ValueError, OSError):
        return None

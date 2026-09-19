"""Finding: one validation result. Same shape as the plugin's ValidationResult."""

from __future__ import annotations

from typing import Any, Dict, Optional

LEVELS = ("off", "info", "warning", "error")


class Finding:
    def __init__(
        self,
        rule: str,
        message: str,
        field: str = "",
        severity: str = "error",
        manifest: str = "",
        hint: str = "",
        fixable: bool = False,
    ):
        self.rule = rule
        self.message = message
        self.field = field
        self.severity = severity
        self.manifest = manifest
        self.hint = hint
        self.fixable = fixable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "field": self.field,
            "message": self.message,
            "hint": self.hint,
            "manifest": self.manifest,
            "fixable": self.fixable,
        }

    def line(self) -> str:
        mark = ", fixable" if self.fixable else ""
        text = f"[{self.severity}{mark}] {self.rule}: {self.message}"
        if self.hint:
            text += f" {self.hint}"
        return text


def short(value: Any, limit: int = 60) -> str:
    text = str(value)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def join_values(values, limit: int = 12) -> str:
    items = [str(v) for v in values]
    shown = ", ".join(items[:limit])
    if len(items) > limit:
        shown += f", and {len(items) - limit} more"
    return shown


def describe_options(options, limit: int = 8) -> str:
    """Allowed values for a hint. Short lists also carry the manifest descriptions."""
    pairs = []
    for option in options:
        if isinstance(option, dict):
            pairs.append((str(option.get("value")), str(option.get("description") or "").strip()))
        else:
            pairs.append((str(option), ""))
    if len(pairs) <= limit and any(text for _, text in pairs):
        return "Allowed:\n" + "\n".join(f"  {value}  {text}".rstrip() for value, text in pairs)
    return f"Allowed: {join_values([value for value, _ in pairs])}."


def meaning(field) -> str:
    """The manifest description of a field, as one short sentence for a hint."""
    text = str((field or {}).get("description") or "").strip()
    return f"Meaning: {text}" if text else ""


def suggestion(wrong: str, candidates) -> Optional[str]:
    import difflib

    hits = difflib.get_close_matches(str(wrong), [str(c) for c in candidates], n=1, cutoff=0.75)
    return hits[0] if hits else None

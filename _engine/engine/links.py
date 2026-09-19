"""Wikilink text helpers."""

from __future__ import annotations

import unicodedata
from typing import Any


def nfc(text: str) -> str:
    """macOS stores file names decomposed. Compare names in one form."""
    return unicodedata.normalize("NFC", text)


def is_wikilink(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    s = value.strip()
    return s.startswith("[[") and s.endswith("]]") and len(s) > 4


def link_target(raw: str) -> str:
    """`[[path/name#heading|alias]]` to `path/name`. Plain text passes through."""
    s = str(raw).strip()
    if s.startswith("[["):
        s = s[2:]
    if s.endswith("]]"):
        s = s[:-2]
    for sep in ("|", "#"):
        idx = s.find(sep)
        if idx != -1:
            s = s[:idx]
    if s.endswith(".md"):
        s = s[:-3]
    return nfc(s.strip())


def link_name(raw: str) -> str:
    """`[[path/name|alias]]` to `name`."""
    target = link_target(raw)
    return target.rsplit("/", 1)[-1]


def as_wikilink(raw: str) -> str:
    s = str(raw).strip()
    return s if is_wikilink(s) else f"[[{link_target(s)}]]"

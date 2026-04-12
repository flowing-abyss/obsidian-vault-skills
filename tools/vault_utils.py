"""Shared utilities for Obsidian vault scripts.

Path resolution strategy (in order):
  1. Explicit hint / --vault argument
  2. Check VAULT_PATH environment variable
  3. Walk up from this script's location looking for .obsidian/
  4. Walk up from current working directory
"""

import os
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Vault root
# ---------------------------------------------------------------------------


def find_vault_root(hint: Path = None) -> Path | None:
    """Return the vault root (directory containing .obsidian/)."""
    candidates = []
    if hint:
        candidates.append(Path(hint).resolve())

    env = os.environ.get("VAULT_PATH")
    if env:
        candidates.append(Path(env).resolve())

    candidates.append(Path(__file__).resolve().parent)
    candidates.append(Path.cwd())

    for start in candidates:
        for path in [start] + list(start.parents):
            if (path / ".obsidian").is_dir():
                return path

    return None


# ---------------------------------------------------------------------------
# Link resolution
# ---------------------------------------------------------------------------

_WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


def _extract_name(raw: str) -> str:
    """Extract bare name from [[wikilink]] or plain string."""
    m = _WIKILINK_RE.match(raw.strip())
    if m:
        raw = m.group(1)
    # Take only the last path segment and strip .md
    return raw.strip().split("/")[-1].removesuffix(".md")


def normalize_note_key(raw: str) -> str:
    """Return a canonical comparison key for note titles across NFC/NFD and case."""
    return unicodedata.normalize("NFC", _extract_name(raw)).casefold()


def _looks_like_path(raw: str) -> bool:
    """Return True when input resembles a path to a note file."""
    s = (raw or "").strip()
    if not s:
        return False
    # Ignore plain wikilinks like [[Note]]; warn for folder/file-like values.
    if _WIKILINK_RE.match(s):
        inner = _WIKILINK_RE.match(s).group(1)
        return "/" in inner or "\\" in inner or inner.lower().endswith(".md")
    return "/" in s or "\\" in s or s.lower().endswith(".md")


def normalize_note_ref(raw: str, field: str = "link") -> str:
    """Normalize note input to a bare title and print a soft hint for path-like values."""
    name = _extract_name(raw)
    if _looks_like_path(raw):
        print(
            f'Note: "{field}" received a path-like value "{raw}". '
            f'Using title "{name}". Please pass only the note title next time.',
            file=sys.stderr,
        )
    return name


def normalize_note_refs(values: list[str], field: str = "links") -> list[str]:
    """Normalize a list of note references to bare titles with soft path hints."""
    return [normalize_note_ref(v, field=field) if v else v for v in values]


def default_if_empty(value: str | None, default: str) -> str | None:
    """Replace an explicit empty CLI scalar with a script-defined default."""
    return default if value == "" else value


def normalize_cli_link_arg(
    value: str | None, field: str = "link"
) -> tuple[str | None, bool]:
    """Normalize a single CLI link argument and detect explicit clearing."""
    if value is None:
        return None, False
    if not value.strip():
        return "", True
    return normalize_note_ref(value, field=field), False


def normalize_cli_list_arg(
    values: list[str] | None, field: str = "links", as_links: bool = True
) -> tuple[list[str] | None, bool]:
    """Normalize a repeatable CLI argument list and detect explicit clearing."""
    if values is None:
        return None, False
    if any(not (value or "").strip() for value in values):
        return [], True
    if as_links:
        return normalize_note_refs(values, field=field), False
    return [value.strip() for value in values], False


def normalize_frontmatter_scalar(value: str | None) -> str | None:
    """Normalize a scalar frontmatter value to a single physical line."""
    if value is None:
        return None
    normalized_lines = [line.strip() for line in str(value).splitlines() if line.strip()]
    if not normalized_lines:
        return ""
    return " ".join(normalized_lines)


def resolve_link(raw: str, vault_root: Path) -> Path | None:
    """Resolve a note name or [[wikilink]] to an existing .md file.

    Uses Obsidian's 'first match' strategy: searches the entire vault
    for a file whose stem matches the given name (case-insensitive).
    Returns None if not found; returns the first match if several exist.
    """
    name_key = normalize_note_key(raw)
    matches = [p for p in vault_root.rglob("*.md") if normalize_note_key(p.stem) == name_key]
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]
    # Prefer a match whose relative path contains the original raw hint
    hint = raw.strip().strip('"').lstrip("[[").rstrip("]]")
    for m in matches:
        if hint in str(m.relative_to(vault_root)):
            return m
    return matches[0]


def validate_links(raws: list[str], vault_root: Path) -> list[str]:
    """Return list of raw link strings that could not be resolved."""
    return [r for r in raws if r and resolve_link(r, vault_root) is None]


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

_FM_BOUNDARY = re.compile(r"^---\s*$", re.MULTILINE)


def split_frontmatter(content: str) -> tuple[str, str]:
    """Split note content into (raw_yaml, body). raw_yaml excludes --- lines."""
    parts = _FM_BOUNDARY.split(content, maxsplit=2)
    if len(parts) >= 3 and content.startswith("---"):
        return parts[1], parts[2].lstrip("\n")
    return "", content


def update_fm_field(content: str, key: str, value) -> str:
    """Set a scalar frontmatter field in raw note content (in-place regex)."""
    pattern = re.compile(rf"^({re.escape(key)}:[ \t]*).*$", re.MULTILINE)
    replacement = rf"\g<1>{value}"
    if pattern.search(content):
        return pattern.sub(replacement, content, count=1)
    # Field doesn't exist — insert before closing ---
    boundary = content.find("\n---", content.index("---") + 3)
    if boundary != -1:
        return content[:boundary] + f"\n{key}: {value}" + content[boundary:]
    return content


def read_fm_field(content: str, key: str) -> str | None:
    """Read the value of a scalar frontmatter field."""
    m = re.search(rf"^{re.escape(key)}:[ \t]*(.*)$", content, re.MULTILINE)
    return m.group(1).strip() if m else None


def read_fm_list(content: str, key: str) -> list[str]:
    """Read a YAML list frontmatter field. Returns bare names (no [[]] or quotes)."""
    # Find the key with an empty value (list follows on next lines)
    m = re.search(rf"^{re.escape(key)}:\s*$", content, re.MULTILINE)
    if not m:
        return []
    # Find frontmatter end boundary
    fm_end_m = re.search(r"^\-\-\-\s*$", content[m.end() :], re.MULTILINE)
    block = (
        content[m.end() : m.end() + fm_end_m.start()]
        if fm_end_m
        else content[m.end() :]
    )
    items = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if not stripped.startswith("- "):
            break  # next frontmatter key — stop
        raw = stripped[2:].strip().strip('"')
        # Extract name from [[wikilink]] if present
        wm = re.match(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", raw)
        name = wm.group(1).split("/")[-1].removesuffix(".md") if wm else raw
        if name:
            items.append(name)
    return items


# ---------------------------------------------------------------------------
# Date / time
# ---------------------------------------------------------------------------


def now_iso() -> str:
    """Return current local time as ISO-8601 with colon in UTC offset."""
    now = datetime.now(timezone.utc).astimezone()
    s = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    # %z gives +0300 — insert colon → +03:00
    if len(s) > 19 and s[-5] in ("+", "-"):
        s = s[:-2] + ":" + s[-2:]
    return s


# ---------------------------------------------------------------------------
# Wikilink formatting
# ---------------------------------------------------------------------------


def fmt_link(raw: str) -> str:
    """Return a properly quoted wikilink: \"[[Name]]\"."""
    name = _extract_name(raw)
    return f'"[[{name}]]"'


def fmt_yaml_string(raw: str) -> str:
    """Return a YAML-safe double-quoted scalar."""
    escaped = raw.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


# ---------------------------------------------------------------------------
# Error helper
# ---------------------------------------------------------------------------


def die(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)

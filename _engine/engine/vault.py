"""Vault access: root discovery, config, notes, and a cached index."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from . import yamlio
from .links import link_target, nfc

ENGINE_DIR = Path(__file__).resolve().parent.parent
INDEX_VERSION = 1
SKIP_DIRS = {"node_modules"}

DEFAULT_CONFIG: Dict[str, Any] = {
    # Folder that holds manifest.md files. Empty means: read the plugin setting.
    "schemas_root": "",
    # Severity per check id: "off", "info", "warning" or "error".
    "checks": {},
    # Path prefixes where an edit gives the agent a notice. Value is the notice.
    "zones": {
        "base/categories/": "Categories are owned by the user. Do not create, edit, rename or delete them.",
        "templates/": "Templates and manifests define the vault. Edit only after the user approved this exact change.",
        "home/databases/": "Databases define the vault. Edit only after the user approved this exact change.",
        "home/prefixes.md": "Prefixes define the vault. Edit only after the user approved this exact change.",
        "periodic/statuses/": "Statuses define the vault. Edit only after the user approved this exact change.",
    },
    # Path prefixes that are never validated.
    "ignore": ["templates/", "files/"],
}


class ConfigError(ValueError):
    pass


def find_root(start: Optional[str] = None) -> Path:
    """Vault root: the folder that holds `.obsidian`, searched upward."""
    here = Path(start).resolve() if start else ENGINE_DIR
    for folder in [here, *here.parents]:
        if (folder / ".obsidian").is_dir():
            return folder
    return ENGINE_DIR.parent.parent


class Note:
    def __init__(self, path: str, text: str):
        self.path = path
        self.text = text
        self.fm_text, self.body = yamlio.split_frontmatter(text)
        self.error: Optional[str] = None
        self.frontmatter: Dict[str, Any] = {}
        if self.fm_text is not None:
            try:
                self.frontmatter = yamlio.parse_mapping(self.fm_text)
            except yamlio.YamlError as exc:
                self.error = str(exc)

    @property
    def has_frontmatter(self) -> bool:
        return self.fm_text is not None

    @property
    def tags(self) -> List[str]:
        return tags_of(self.frontmatter)


def tags_of(frontmatter: Dict[str, Any]) -> List[str]:
    raw = frontmatter.get("tags")
    if isinstance(raw, list):
        return [str(t).lstrip("#") for t in raw if t is not None]
    if isinstance(raw, str) and raw:
        return [raw.lstrip("#")]
    return []


class Vault:
    def __init__(self, root: Optional[str] = None, use_cache: bool = True):
        self.root = Path(root).resolve() if root else find_root()
        # User owned part of the engine: config, own checks, cache. An engine
        # update replaces everything in `_engine/` except this folder.
        self.local_dir = self.root / ".claude" / "_engine" / "local"
        self.use_cache = use_cache
        self.config = self._load_config()
        self._entries: Optional[Dict[str, Dict[str, Any]]] = None
        self._by_name: Dict[str, List[str]] = {}
        self._all_files: Dict[str, List[str]] = {}

    # -- config ------------------------------------------------------------

    def _load_config(self) -> Dict[str, Any]:
        config = json.loads(json.dumps(DEFAULT_CONFIG))
        path = self.local_dir / "config.json"
        if path.is_file():
            try:
                user = json.loads(path.read_text(encoding="utf-8"))
            except ValueError as exc:
                raise ConfigError(f"{path}: invalid JSON: {exc}")
            if not isinstance(user, dict):
                raise ConfigError(f"{path}: must be a JSON object")
            for key, value in user.items():
                if key not in DEFAULT_CONFIG:
                    known = ", ".join(sorted(DEFAULT_CONFIG))
                    raise ConfigError(f'{path}: unknown key "{key}". Known keys: {known}')
                if isinstance(DEFAULT_CONFIG[key], dict) and isinstance(value, dict):
                    config[key].update(value)
                else:
                    config[key] = value
        return config

    @property
    def schemas_root(self) -> str:
        root = self.config.get("schemas_root") or ""
        if not root:
            data = self.root / ".obsidian" / "plugins" / "metadata-validator" / "data.json"
            if data.is_file():
                try:
                    root = json.loads(data.read_text(encoding="utf-8")).get("schemasRoot", "")
                except ValueError:
                    root = ""
        return (root or "templates/create").strip("/")

    def is_ignored(self, path: str) -> bool:
        if path.startswith(self.schemas_root + "/"):
            return True
        return any(path.startswith(prefix) for prefix in self.config.get("ignore", []))

    def zone_notice(self, path: str) -> Optional[str]:
        for prefix, notice in self.config.get("zones", {}).items():
            if notice and (path == prefix or path.startswith(prefix)):
                return str(notice)
        return None

    # -- files -------------------------------------------------------------

    def rel(self, path: str) -> str:
        p = Path(path)
        if not p.is_absolute():
            p = Path.cwd() / p
        try:
            return p.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return Path(path).as_posix()

    def read_note(self, path: str) -> Note:
        return Note(path, (self.root / path).read_text(encoding="utf-8"))

    def exists(self, path: str) -> bool:
        return (self.root / path).is_file()

    def locate(self, ref: str) -> Optional[str]:
        """Find a note by vault path, by note name, or by its `id` property."""
        path = self.rel(ref)
        if self.exists(path):
            return path
        name = ref[:-3] if ref.endswith(".md") else ref
        hit = self.resolve_link(name)
        if hit and hit.endswith(".md"):
            return hit
        for candidate in self.notes():
            if str(self.frontmatter_of(candidate).get("id") or "") == ref and not self.is_ignored(candidate):
                return candidate
        return None

    # -- index -------------------------------------------------------------

    def _cache_path(self) -> Path:
        return self.local_dir / "state" / "index.json"

    def _build(self) -> None:
        cached: Dict[str, Dict[str, Any]] = {}
        if self.use_cache and self._cache_path().is_file():
            try:
                data = json.loads(self._cache_path().read_text(encoding="utf-8"))
                if data.get("version") == INDEX_VERSION:
                    cached = data.get("files", {})
            except (ValueError, OSError):
                cached = {}

        entries: Dict[str, Dict[str, Any]] = {}
        all_files: Dict[str, List[str]] = {}
        dirty = False
        for folder, dirs, files in os.walk(self.root):
            dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d not in SKIP_DIRS)
            rel_folder = Path(folder).relative_to(self.root).as_posix()
            for name in sorted(files):
                rel = name if rel_folder == "." else f"{rel_folder}/{name}"
                all_files.setdefault(nfc(name).lower(), []).append(rel)
                if not name.endswith(".md"):
                    continue
                try:
                    stat = os.stat(os.path.join(folder, name))
                except OSError:
                    continue
                old = cached.get(rel)
                if old and old.get("m") == stat.st_mtime_ns and old.get("s") == stat.st_size:
                    entries[rel] = old
                    continue
                dirty = True
                entries[rel] = self._index_entry(rel, stat)
        if len(entries) != len(cached):
            dirty = True
        self._entries = entries
        self._all_files = all_files
        self._by_name = {}
        for rel in entries:
            self._by_name.setdefault(nfc(Path(rel).stem).lower(), []).append(rel)
        if dirty and self.use_cache:
            self._save_cache()

    def _index_entry(self, rel: str, stat: os.stat_result) -> Dict[str, Any]:
        entry: Dict[str, Any] = {"m": stat.st_mtime_ns, "s": stat.st_size, "fm": {}}
        try:
            note = self.read_note(rel)
        except (OSError, UnicodeDecodeError):
            return entry
        if note.error is None:
            try:
                json.dumps(note.frontmatter)
                entry["fm"] = note.frontmatter
            except (TypeError, ValueError):
                entry["fm"] = {}
        return entry

    def _save_cache(self) -> None:
        try:
            path = self._cache_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(
                json.dumps({"version": INDEX_VERSION, "files": self._entries}, ensure_ascii=False),
                encoding="utf-8",
            )
            os.replace(tmp, path)
        except OSError:
            pass

    def refresh(self) -> None:
        self._entries = None

    def _ready(self) -> Dict[str, Dict[str, Any]]:
        if self._entries is None:
            self._build()
        assert self._entries is not None
        return self._entries

    def notes(self) -> Iterator[str]:
        return iter(self._ready())

    def frontmatter_of(self, path: str) -> Dict[str, Any]:
        entry = self._ready().get(path)
        return entry.get("fm", {}) if entry else {}

    def paths_by_name(self, name: str) -> List[str]:
        self._ready()
        return list(self._by_name.get(nfc(name).lower(), []))

    def resolve_link(self, raw: str) -> Optional[str]:
        """Path of the file a link points to, or None. Mirrors Obsidian: by
        note name, by path, or by file name with an extension."""
        self._ready()
        target = link_target(raw)
        if not target:
            return None
        if "/" in target:
            wanted = target.lower()
            for rel in self._entries or {}:
                stem = nfc(rel[:-3]).lower()
                if stem == wanted or stem.endswith("/" + wanted):
                    return rel
            name = wanted.rsplit("/", 1)[-1]
            for rel in self._all_files.get(name, []):
                if nfc(rel).lower().endswith(wanted):
                    return rel
            return None
        hits = self._by_name.get(target.lower())
        if hits:
            return hits[0]
        files = self._all_files.get(target.lower())
        return files[0] if files else None

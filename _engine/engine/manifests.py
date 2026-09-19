"""Load manifest.md files, merge inheritance, and match a note to a schema.

Mirrors the Metadata Validator plugin:
  - the parent is `extends`, else the manifest in the direct parent folder
  - a child field replaces a same-named parent field as a whole
  - `exclude` drops inherited fields
  - `target` is the child's own when it has one
  - several matches: higher `priority`, then more specific target, then
    the longer inheritance chain wins
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from . import query, yamlio
from .vault import Vault, tags_of

KNOWN_MANIFEST_KEYS = {
    "name", "description", "priority", "extends", "target", "enforce_folder",
    "fields", "exclude", "rules", "formatting", "tags", "aliases", "icon",
    "color", "created", "updated", "cssclasses",
}
KNOWN_FIELD_KEYS = {
    "type", "label", "description", "required", "hidden", "default", "fixed",
    "validate_exists", "sort", "min", "max", "format", "options", "strict",
    "source", "validate",
}
FIELD_TYPES = {
    "text", "number", "select", "multiselect", "list", "date", "link",
    "multilink", "boolean", "url",
}


class Schema:
    def __init__(self, path: str, folder: str, own: Dict[str, Any], merged: Dict[str, Any], chain: List[str]):
        self.path = path
        self.folder = folder
        self.own = own
        self.chain = chain
        self.name: str = str(merged.get("name") or folder.rsplit("/", 1)[-1])
        self.description: str = str(own.get("description") or "")
        self.priority: int = int(merged.get("priority") or 0)
        self.enforce_folder = merged.get("enforce_folder")
        self.target: Dict[str, Any] = merged.get("target") or {}
        self.fields: Dict[str, Dict[str, Any]] = merged.get("fields") or {}
        formatting = merged.get("formatting") or {}
        self.property_order: List[str] = list(formatting.get("property_order") or [])
        self.has_children = False
        self.origins: Dict[str, str] = {}

    def origin(self, field: str) -> str:
        """Path of the manifest that defines a field. The leaf for anything else."""
        return self.origins.get(field, self.path)

    def template_body(self, vault: Vault) -> str:
        """Body of the nearest `template.md` in the chain, without Templater code.

        Templates stay the single source for the body scaffold of a note type.
        """
        import re

        for manifest in reversed(self.chain):
            file = vault.root / manifest.rsplit("/", 1)[0] / "template.md"
            if not file.is_file():
                continue
            text = file.read_text(encoding="utf-8")
            parts = re.split(r'^(?:<% "---" %>|---)[ \t]*$', text, maxsplit=2, flags=re.M)
            body = parts[2] if len(parts) == 3 else ""
            body = re.sub(r"<%[\s\S]*?%>", "", body)
            return body.strip("\n")
        return ""

    @property
    def type_tag(self) -> Optional[str]:
        return query.first_tag(str(self.target.get("query") or ""))

    @property
    def order(self) -> List[str]:
        return self.property_order or list(self.fields)

    def matches(self, path: str, tags: List[str], frontmatter: Dict[str, Any]) -> bool:
        q = self.target.get("query")
        if q:
            return query.evaluate(str(q), path, tags, frontmatter)
        prop = self.target.get("property")
        if isinstance(prop, dict) and prop:
            for key, want in prop.items():
                have = frontmatter.get(key)
                if ("" if have is None else query.value_text(have)) != str(want):
                    return False
            return True
        return False

    def specificity(self) -> int:
        return (2 if self.target.get("query") else 0) + (1 if self.target.get("property") else 0)


class ManifestProblem:
    def __init__(self, path: str, message: str):
        self.path = path
        self.message = message


class Schemas:
    def __init__(self, vault: Vault):
        self.vault = vault
        self.problems: List[ManifestProblem] = []
        self.raw: Dict[str, Dict[str, Any]] = {}
        self.by_path: Dict[str, Schema] = {}
        self._load()

    # -- loading -----------------------------------------------------------

    def _load(self) -> None:
        root = self.vault.root / self.vault.schemas_root
        if not root.is_dir():
            self.problems.append(ManifestProblem(self.vault.schemas_root, "Schemas folder was not found."))
            return
        for file in sorted(root.rglob("manifest.md")):
            rel = file.relative_to(self.vault.root).as_posix()
            fm_text, _ = yamlio.split_frontmatter(file.read_text(encoding="utf-8"))
            if fm_text is None:
                continue
            try:
                data = yamlio.parse_mapping(fm_text)
            except yamlio.YamlError as exc:
                self.problems.append(ManifestProblem(rel, f"Manifest YAML is invalid: {exc}"))
                continue
            self.raw[rel] = data
            self._lint(rel, data)
        merged: Dict[str, Dict[str, Any]] = {}
        chains: Dict[str, List[str]] = {}
        for rel in self.raw:
            self._resolve(rel, merged, chains, set())
        for rel, data in merged.items():
            folder = rel.rsplit("/", 1)[0]
            self.by_path[rel] = Schema(rel, folder, self.raw[rel], data, chains[rel])
        for schema in self.by_path.values():
            for link in schema.chain:
                for name in (self.raw.get(link, {}).get("fields") or {}):
                    if name in schema.fields:
                        schema.origins[name] = link
            for parent in schema.chain[:-1]:
                if parent in self.by_path:
                    self.by_path[parent].has_children = True

    def _lint(self, rel: str, data: Dict[str, Any]) -> None:
        for key in data:
            if key not in KNOWN_MANIFEST_KEYS:
                self.problems.append(ManifestProblem(rel, f'Manifest key "{key}" is not known to the engine and is ignored.'))
        fields = data.get("fields")
        if fields is None:
            return
        if not isinstance(fields, dict):
            self.problems.append(ManifestProblem(rel, '"fields" must be a map.'))
            data["fields"] = {}
            return
        for name, field in list(fields.items()):
            if not isinstance(field, dict):
                self.problems.append(ManifestProblem(rel, f'Field "{name}" must be a map.'))
                del fields[name]
                continue
            if field.get("type") not in FIELD_TYPES:
                self.problems.append(ManifestProblem(rel, f'Field "{name}" has unknown type "{field.get("type")}".'))
            for key in field:
                if key not in KNOWN_FIELD_KEYS:
                    self.problems.append(ManifestProblem(rel, f'Field "{name}" uses key "{key}" that the engine does not check.'))

    def _parent_of(self, rel: str) -> Optional[str]:
        data = self.raw[rel]
        extends = data.get("extends")
        if extends:
            base = str(extends).strip("/")
            if base.endswith("/manifest.md"):
                base = base[: -len("/manifest.md")]
            candidate = f"{base}/manifest.md"
            return candidate if candidate in self.raw else None
        folder = rel.rsplit("/", 1)[0]
        if "/" not in folder:
            return None
        candidate = f"{folder.rsplit('/', 1)[0]}/manifest.md"
        return candidate if candidate in self.raw else None

    def _resolve(self, rel: str, merged: Dict[str, Dict[str, Any]], chains: Dict[str, List[str]], visiting: set) -> Optional[Dict[str, Any]]:
        if rel in merged:
            return merged[rel]
        if rel in visiting:
            self.problems.append(ManifestProblem(rel, "Circular manifest inheritance."))
            return None
        visiting.add(rel)
        child = self.raw[rel]
        parent_rel = self._parent_of(rel)
        parent = self._resolve(parent_rel, merged, chains, visiting) if parent_rel else None
        visiting.discard(rel)
        if parent is None:
            merged[rel] = child
            chains[rel] = [rel]
            return child
        fields = dict(parent.get("fields") or {})
        fields.update(child.get("fields") or {})
        for key in child.get("exclude") or []:
            fields.pop(key, None)
        data = {
            "name": child.get("name", parent.get("name")),
            "priority": child.get("priority", parent.get("priority")),
            "enforce_folder": child.get("enforce_folder", parent.get("enforce_folder")),
            "target": child.get("target") or parent.get("target"),
            "fields": fields,
            "formatting": child.get("formatting") or parent.get("formatting"),
        }
        merged[rel] = data
        chains[rel] = chains[parent_rel] + [rel]  # type: ignore[index]
        return data

    # -- lookup ------------------------------------------------------------

    def all(self) -> List[Schema]:
        return list(self.by_path.values())

    def for_note(self, path: str, frontmatter: Dict[str, Any]) -> Optional[Schema]:
        tags = tags_of(frontmatter)
        hits = [s for s in self.by_path.values() if s.matches(path, tags, frontmatter)]
        if not hits:
            return None
        hits.sort(key=lambda s: (-s.priority, -s.specificity(), -len(s.chain)))
        return hits[0]

    def for_type(self, type_name: str) -> Optional[Schema]:
        """Find a schema by its type tag (`task/default`) or manifest name."""
        wanted = type_name.lstrip("#").strip().lower()
        by_tag = [s for s in self.by_path.values() if (s.type_tag or "").lower() == wanted]
        if by_tag:
            by_tag.sort(key=lambda s: -len(s.chain))
            return by_tag[0]
        for schema in self.by_path.values():
            if schema.name.lower() == wanted:
                return schema
        return None

    def type_tags(self) -> List[str]:
        return sorted({s.type_tag for s in self.by_path.values() if s.type_tag})

    def under(self, folder: str) -> List[Schema]:
        prefix = folder.rstrip("/")
        return [s for s in self.by_path.values() if s.path.startswith(prefix)]

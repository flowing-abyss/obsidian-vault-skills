#!/usr/bin/env python3
"""
Display Obsidian vault structure as a tree.
Organizes categories with their meta-notes, problems, and hierarchies.

Vault root is resolved automatically from this script's location:
  .claude/skills/obsidian-structure/structure.py → 4 levels up = vault root
"""

import re
from pathlib import Path
from typing import Dict, List, Set


class VaultStructure:
    def __init__(self, vault_root: Path):
        self.root = Path(vault_root)
        self.files: Dict[str, Dict] = {}
        self._load_all_files()

    def _load_all_files(self) -> None:
        """Load all markdown files and parse their frontmatter."""
        for md_file in self.root.rglob("*.md"):
            if md_file.name.startswith("."):
                continue
            if any(part.startswith(".") for part in md_file.parts):
                continue

            rel_path = md_file.relative_to(self.root)
            self.files[rel_path] = self._parse_frontmatter(md_file)

    def _parse_frontmatter(self, file_path: Path) -> Dict:
        """Extract frontmatter and file metadata."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return {}

        fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if not fm_match:
            return {}

        fm_text = fm_match.group(1)
        data = self._parse_yaml(fm_text, file_path.name)

        body = content[fm_match.end() :]
        outlinks = re.findall(r"\[\[([^\]]+)\]\]", body)
        data["outlinks"] = outlinks

        return data

    def _parse_yaml(self, text: str, filename: str) -> Dict:
        """Simple YAML parser for frontmatter."""
        data = {
            "tags": [],
            "category": [],
            "meta": [],
            "problem": [],
            "filename": filename[:-3],
            "outlinks": [],
        }

        lines = text.split("\n")
        i = 0
        current_field = None

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if stripped.endswith(":"):
                field_name = stripped[:-1]
                if field_name in ("tags", "category", "meta", "problem"):
                    current_field = field_name
                    i += 1
                    continue

            if stripped.startswith("- ") and current_field:
                item = stripped[2:].strip()
                if item.startswith('"') and item.endswith('"'):
                    item = item[1:-1]
                wikilink_match = re.search(r"\[\[(.*?)\]\]", item)
                if wikilink_match:
                    item = wikilink_match.group(1)
                data[current_field].append(item)
                i += 1
                continue

            if not stripped.startswith("- ") and current_field and stripped:
                current_field = None

            i += 1

        return data

    def _normalize_tag(self, name: str) -> str:
        """Normalize category name for tag matching."""
        return name.lower().replace(" ", "_")

    def _get_files_by_tag(self, tag: str) -> List[str]:
        """Get filenames that have a specific tag."""
        return [
            fname for fname, meta in self.files.items() if tag in meta.get("tags", [])
        ]

    def _get_meta_notes(self, category: str) -> List[str]:
        """Get meta-notes for a category."""
        meta_files = self._get_files_by_tag("system/high/meta")
        result = []
        for fname in meta_files:
            meta = self.files.get(fname, {})
            cats = meta.get("category", [])
            if any(
                cat.lower().replace(" ", "_") == self._normalize_tag(category)
                for cat in cats
            ):
                result.append(meta["filename"])
        return sorted(set(result))

    def _get_problems(self, meta_note: str) -> List[str]:
        """Get problems linked to a meta-note."""
        problem_files = self._get_files_by_tag("system/high/problem")
        result = []
        for fname in problem_files:
            meta = self.files.get(fname, {})
            if any(m.lower() == meta_note.lower() for m in meta.get("meta", [])):
                result.append(meta["filename"])
        return sorted(set(result))

    def _get_hierarchies(self, parent: str) -> List[str]:
        """Get hierarchies linked to a parent (meta-note or problem)."""
        hier_files = self._get_files_by_tag("system/high/hierarchy")
        result = set()
        for fname in hier_files:
            meta = self.files.get(fname, {})
            meta_links = meta.get("meta", [])
            problem_links = meta.get("problem", [])

            if any(m.lower() == parent.lower() for m in meta_links) or any(
                p.lower() == parent.lower() for p in problem_links
            ):
                result.add(meta["filename"])

        return sorted(result)

    def _is_child_hierarchy(self, hierarchy: str) -> bool:
        """Check if this hierarchy is a child of any other hierarchy."""
        hier_files = self._get_files_by_tag("system/high/hierarchy")
        for fname in hier_files:
            meta = self.files.get(fname, {})
            if meta.get("filename") == hierarchy:
                continue
            outlinks = meta.get("outlinks", [])
            if any(link.lower() == hierarchy.lower() for link in outlinks):
                return True
        return False

    def _get_child_hierarchies(self, parent_hierarchy: str) -> List[str]:
        """Get hierarchies that are children of parent hierarchy (via outlinks)."""
        hier_files = self._get_files_by_tag("system/high/hierarchy")
        result = set()

        parent_file_meta = None
        for fname, meta in self.files.items():
            if meta.get("filename") == parent_hierarchy:
                parent_file_meta = meta
                break

        if not parent_file_meta:
            return []

        parent_outlinks = parent_file_meta.get("outlinks", [])

        for fname in hier_files:
            meta = self.files.get(fname, {})
            hierarchy_name = meta.get("filename")

            if any(link.lower() == hierarchy_name.lower() for link in parent_outlinks):
                result.add(hierarchy_name)

        return sorted(result)

    def _format_hierarchy_tree(
        self, hierarchy: str, prefix: str = "", shown: Set[str] = None
    ) -> List[str]:
        """Recursively format hierarchy with its children."""
        if shown is None:
            shown = set()

        lines = []
        child_hierarchies = self._get_child_hierarchies(hierarchy)

        for idx, child in enumerate(child_hierarchies):
            if child.lower() in shown:
                continue

            is_last = idx == len(child_hierarchies) - 1
            connector = "└── " if is_last else "├── "
            continuation = "    " if is_last else "│   "

            lines.append(f"{prefix}{connector}🧬 {child}")
            shown.add(child.lower())

            grandchildren = self._format_hierarchy_tree(
                child, prefix + continuation, shown
            )
            lines.extend(grandchildren)

        return lines

    def get_structure(self) -> str:
        """Generate and return the vault structure."""
        categories_dir = self.root / "base" / "categories"
        if not categories_dir.exists():
            return "Categories directory not found"

        output = []

        category_files = sorted([f.stem for f in categories_dir.glob("*.md")])

        for category in category_files:
            output.append(f"🗺️  {category}")

            meta_notes = self._get_meta_notes(category)

            if not meta_notes:
                continue

            for meta_idx, meta_note in enumerate(meta_notes):
                is_last_meta = meta_idx == len(meta_notes) - 1
                meta_connector = "└── " if is_last_meta else "├── "
                meta_continuation = "    " if is_last_meta else "│   "

                output.append(f"{meta_connector}🔎 {meta_note}")

                problems = self._get_problems(meta_note)
                hierarchies_from_meta = self._get_hierarchies(meta_note)

                shown_hierarchies = set()

                for prob_idx, problem in enumerate(problems):
                    is_last_item = (
                        prob_idx == len(problems) - 1
                        and len(hierarchies_from_meta) == 0
                    )
                    prob_connector = "└── " if is_last_item else "├── "
                    prob_continuation = "    " if is_last_item else "│   "

                    output.append(f"{meta_continuation}{prob_connector}⚡ {problem}")

                    hier_from_problem = self._get_hierarchies(problem)
                    root_hier_from_problem = [
                        h for h in hier_from_problem if not self._is_child_hierarchy(h)
                    ]

                    for hier_idx, hier in enumerate(root_hier_from_problem):
                        is_last_hier = hier_idx == len(root_hier_from_problem) - 1
                        hier_connector = "└── " if is_last_hier else "├── "
                        hier_continuation = "    " if is_last_hier else "│   "

                        output.append(
                            f"{meta_continuation}{prob_continuation}{hier_connector}🧬 {hier}"
                        )
                        shown_hierarchies.add(hier.lower())

                        child_lines = self._format_hierarchy_tree(
                            hier,
                            meta_continuation + prob_continuation + hier_continuation,
                            shown_hierarchies,
                        )
                        output.extend(child_lines)

                unique_hierarchies = [
                    h
                    for h in hierarchies_from_meta
                    if h.lower() not in shown_hierarchies
                ]
                root_hierarchies = [
                    h for h in unique_hierarchies if not self._is_child_hierarchy(h)
                ]

                for hier_idx, hier in enumerate(root_hierarchies):
                    is_last_hier = hier_idx == len(root_hierarchies) - 1
                    hier_connector = "└── " if is_last_hier else "├── "
                    hier_continuation = "    " if is_last_hier else "│   "

                    output.append(f"{meta_continuation}{hier_connector}🧬 {hier}")
                    shown_hierarchies.add(hier.lower())

                    child_lines = self._format_hierarchy_tree(
                        hier, meta_continuation + hier_continuation, shown_hierarchies
                    )
                    output.extend(child_lines)

        return "\n".join(output)


def main() -> None:
    """Main entry point. Vault root is resolved automatically from script location."""
    vault_root = Path(__file__).parents[4]
    structure = VaultStructure(vault_root)
    print(structure.get_structure())


if __name__ == "__main__":
    main()

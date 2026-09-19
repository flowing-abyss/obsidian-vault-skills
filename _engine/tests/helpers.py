"""Test helpers: build a small vault in a temp folder."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ENGINE_DIR))

from engine.validate import Engine  # noqa: E402
from engine.vault import Vault  # noqa: E402

RELATION_JS = (
    'return dv.pages("#system/high/meta AND -#mark/ignore").where(p => [].concat(p.category || [])'
    '.some(c => [].concat(currentPage && currentPage.category || []).map(String).includes(String(c))))'
    '.map(p => ({ value: p.file.name, label: p.file.name }))'
)

MANIFESTS = {
    "templates/create/notes/manifest.md": """---
name: note
enforce_folder: base/notes
target:
  query: "#note"
fields:
  tags:
    type: multiselect
    required: true
    strict: false
  aliases:
    type: list
    required: true
    sort: alphabetical
  status:
    type: select
    required: true
    default: 📥
    options:
      - { value: 📥, label: "📥 Inbox" }
      - { value: 🟩, label: "🟩 Done" }
  focus: { type: number, min: 0, max: 10 }
  reviewed: { type: boolean }
  published: { type: date }
  cover: { type: url }
  category:
    type: multilink
    source:
      js: 'return dv.pages("#system/category AND -#mark/ignore").map(p => ({ value: p.file.name }))'
  meta:
    type: multilink
    source:
      js: '%s'
  creator:
    type: multilink
    validate_exists: false
  created: { type: date }
  updated: { type: date }
formatting:
  property_order: [tags, aliases, status]
---
""" % RELATION_JS.replace("'", "''"),
    "templates/create/notes/basic/manifest.md": "---\nname: basic\n---\n",
    "templates/create/notes/basic/evergreen/manifest.md": """---
name: Evergreen
target:
  query: "#note/basic/evergreen"
exclude:
  - cover
fields:
  icon:
    type: text
    required: true
    fixed: 🌲
---
""",
    "templates/create/tasks/manifest.md": """---
name: Task
enforce_folder: base/tasks
target:
  query: "#task/default"
fields:
  tags: { type: select }
  id: { type: text }
  project:
    type: multilink
    source:
      query: "#project"
  related: { type: multilink }
  blockedBy: { type: multilink }
  category: { type: multilink }
  start: { type: date }
  end: { type: date }
  created: { type: date }
  updated: { type: date }
---
""",
    "templates/create/tasks/template.md": '<% "---" %>\ntags:\n  - task/default\n<% "---" %>\n\n## Plan\n\n<%* await tp.user.title() -%>💤\n',
    "templates/create/projects/manifest.md": '---\nname: project\nenforce_folder: projects\ntarget:\n  query: "#project"\nfields:\n  tags: { type: multiselect, strict: false }\n  status: { type: select, default: 🟥, options: [{ value: 🟥 }, { value: 🟩 }] }\n---\n',
    "templates/create/projects/single/manifest.md": '---\nname: Single\ntarget:\n  query: "#project/single"\n---\n',
    "templates/create/projects/longform/manifest.md": '---\nname: Longform\ntarget:\n  query: "#project/longform"\n---\n',
    "templates/create/scene/manifest.md": '---\nname: scene\ntarget:\n  query: "#mark/scene"\nfields:\n  tags: { type: multiselect, strict: false }\n  status: { type: text }\n---\n',
}

NOTES = {
    "base/categories/science.md": "---\ntags:\n  - system/category\n---\n",
    "base/categories/art.md": "---\ntags:\n  - system/category\n---\n",
    "base/_meta-notes/physics.md": '---\ntags:\n  - system/high/meta\ncategory:\n  - "[[science]]"\n---\n',
    "base/_meta-notes/painting.md": '---\ntags:\n  - system/high/meta\ncategory:\n  - "[[art]]"\n---\n',
    "projects/Open Vault.md": '---\ntags:\n  - project/single\nstatus: 🟥\nprefix: OV\ntaskCount: 4\ncategory:\n  - "[[science]]"\n---\n',
    "base/tasks/old task.md": '---\ntags:\n  - task/default\nid: OV-4\nproject:\n  - "[[Open Vault]]"\n---\n',
}

GOOD_NOTE = """---
tags:
  - note/basic/evergreen
aliases: []
status: 📥
icon: 🌲
category:
  - "[[science]]"
meta:
  - "[[physics]]"
---

Body text stays as it is.
"""


def make_vault(root, manifests=None, notes=None):
    files = dict(MANIFESTS if manifests is None else manifests)
    files.update(NOTES if notes is None else notes)
    (Path(root) / ".obsidian").mkdir(parents=True, exist_ok=True)
    for folder in ("base/notes", "base/tasks", "projects"):
        (Path(root) / folder).mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        path = Path(root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


class VaultCase(unittest.TestCase):
    manifests = None
    notes = None

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self._tmp.name)
        make_vault(self.root, self.manifests, self.notes)
        self.addCleanup(self._tmp.cleanup)

    def engine(self):
        return Engine(Vault(self.root))

    def write(self, rel, text):
        path = Path(self.root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return rel

    def read(self, rel):
        return (Path(self.root) / rel).read_text(encoding="utf-8")

    def rules(self, rel, text=None):
        if text is not None:
            self.write(rel, text)
        return sorted({f.rule for f in self.engine().check_path(rel) if f.severity != "info"})

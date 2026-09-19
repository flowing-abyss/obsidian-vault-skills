"""Conformance cases: a note goes in, rule ids come out. See fixtures/cases.json."""

import json
import re
import unittest
from pathlib import Path

from helpers import GOOD_NOTE, VaultCase

CASES = json.loads((Path(__file__).parent / "fixtures" / "cases.json").read_text(encoding="utf-8"))


class ConformanceTest(VaultCase):
    def test_cases(self):
        for case in CASES:
            with self.subTest(case=case["name"]):
                text = GOOD_NOTE if case["note"] == "GOOD" else case["note"]
                path = self.write(case["path"], text)
                findings = [f for f in self.engine().check_path(path) if f.severity != "info"]
                self.assertEqual(sorted({f.rule for f in findings}), sorted(case["expect"]))
                if case.get("hint"):
                    self.assertIn(case["hint"], " ".join(f.line() for f in findings))
                (Path(self.root) / path).unlink()


class MessageStyleTest(VaultCase):
    """Messages are plain English: ASCII punctuation, a full stop, no long dashes."""

    def test_style(self):
        for case in CASES:
            text = GOOD_NOTE if case["note"] == "GOOD" else case["note"]
            path = self.write(case["path"], text)
            for f in self.engine().check_path(path):
                with self.subTest(case=case["name"], rule=f.rule):
                    self.assertNotRegex(f.message + f.hint, "[–—…“”‘’]")
                    self.assertRegex(f.message, r"[.?]$")
                    self.assertTrue(re.match(r"^[a-z_-]+$", f.rule))
            (Path(self.root) / path).unlink()


class DescriptionTest(VaultCase):
    """Manifest descriptions are reused in hints, so skills need not repeat them."""

    def test_field_and_option_descriptions_reach_the_agent(self):
        self.write("templates/create/books/manifest.md", """---
name: Book
description: "A book you read."
target:
  query: "#book"
fields:
  summary: { type: text, required: true, description: "One line about the book." }
  state:
    type: select
    description: "Reading progress."
    options:
      - { value: todo, description: "Use this before you start." }
      - { value: done, description: "Use this when finished." }
---
""")
        path = self.write("books/b.md", "---\ntags:\n  - book\nstate: reading\n---\n")
        text = " ".join(f.line() for f in self.engine().check_path(path))
        for expected in ("Meaning: One line about the book.", "Meaning: Reading progress.",
                         "todo  Use this before you start.", "done  Use this when finished."):
            self.assertIn(expected, text)


class ConfigTest(VaultCase):
    def test_severity_override_and_off(self):
        note = GOOD_NOTE.replace("status: 📥", "status: 🟨")
        self.write("base/notes/a.md", note)
        self.write(".claude/_engine/local/config.json", '{"checks": {"options": "warning"}}')
        self.assertEqual([f.severity for f in self.engine().check_path("base/notes/a.md")], ["warning"])
        self.write(".claude/_engine/local/config.json", '{"checks": {"options": "off"}}')
        self.assertEqual(self.engine().check_path("base/notes/a.md"), [])

    def test_unknown_config_key_is_refused(self):
        from engine.vault import ConfigError

        self.write(".claude/_engine/local/config.json", '{"chekcs": {}}')
        with self.assertRaises(ConfigError) as caught:
            self.engine()
        self.assertIn("Known keys", str(caught.exception))

    def test_local_check_is_loaded(self):
        self.write(".claude/_engine/local/checks/no_todo.py",
                   'from engine.findings import Finding\nID = "no-todo"\nABOUT = "x"\n'
                   'def run(ctx):\n    return [Finding(ID, "Body has a TODO.")] if "TODO" in ctx.note.body else []\n')
        self.assertEqual(self.rules("base/notes/a.md", GOOD_NOTE + "TODO\n"), ["no-todo"])


if __name__ == "__main__":
    unittest.main()

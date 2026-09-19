import unittest

from helpers import GOOD_NOTE, VaultCase
from engine import audit


class AuditTest(VaultCase):
    def test_clean_vault_has_clean_sections(self):
        engine = self.engine()
        self.assertEqual(audit.manifests(engine), [])
        self.assertEqual(audit.sources(engine), [])
        self.assertEqual(audit.notes(engine)["files"], [])

    def test_missing_enforce_folder_and_unknown_source(self):
        self.write("templates/create/ghost/manifest.md",
                   '---\nname: Ghost\nenforce_folder: base/ghosts\ntarget:\n  query: "#ghost"\nfields:\n'
                   "  who:\n    type: multilink\n    source:\n      js: \"return fetch('x')\"\n---\n")
        engine = self.engine()
        self.assertIn('enforce_folder "base/ghosts" does not exist', " ".join(audit.manifests(engine)))
        self.assertIn("ghost/manifest.md: who", " ".join(audit.sources(engine)))

    def test_template_drift(self):
        self.write("templates/create/notes/basic/evergreen/template.md",
                   '<% "---" %>\ntags:\nmood:\n<% "---" %>\n\nbody\n')
        lines = " ".join(audit.templates(self.engine()))
        self.assertIn("has properties the manifest does not define: mood.", lines)
        self.assertIn("lacks required manifest properties: aliases", lines.replace("aliases, status", "aliases"))
        self.assertNotIn("icon", lines, "fixed fields may be left to the plugin")
        self.assertNotIn("focus", lines, "optional fields are never forced into a template")

    def test_parent_template_may_carry_child_properties(self):
        self.write("templates/create/notes/template.md", '<% "---" %>\ntags:\naliases: []\nstatus:\nicon:\n<% "---" %>\n')
        lines = [l for l in audit.templates(self.engine()) if l.startswith("templates/create/notes/template.md")]
        self.assertFalse(any("does not define" in l for l in lines), lines)

    def test_notes_filters_and_counts(self):
        self.write("base/notes/bad.md", GOOD_NOTE.replace("status: 📥", "status: 🟨").replace("icon: 🌲", "icon: 🌳"))
        engine = self.engine()
        result = audit.notes(engine)
        self.assertEqual(result["by_rule"], {"options": 1, "fixed": 1})
        self.assertEqual(audit.notes(engine, errors_only=True)["by_rule"], {"options": 1})
        self.assertEqual(audit.notes(engine, rule="fixed")["by_rule"], {"fixed": 1})
        self.assertEqual(audit.notes(engine, folder="projects/")["files"], [])
        self.assertGreater(result["by_type"]["note"], 0)

    def test_broken_body_links_skip_code_and_comments(self):
        self.write("base/notes/links.md", GOOD_NOTE + "See [[science]] and [[nowhere|alias]] and ![[missing.png]].\n"
                   "`[[in code]]`\n\n```\n[[in fence]]\n```\n%%[[in comment]]%%\n")
        lines = audit.body_links(self.engine())
        self.assertEqual(lines, ["base/notes/links.md: [[nowhere]], [[missing.png]]"])


if __name__ == "__main__":
    unittest.main()

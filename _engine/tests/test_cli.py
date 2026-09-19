"""End to end: run vault.py the way an agent or a hook does."""

import json
import subprocess
import sys
import unittest

from helpers import ENGINE_DIR, GOOD_NOTE, VaultCase

CLI = str(ENGINE_DIR / "vault.py")


class CliTest(VaultCase):
    def run_cli(self, *args, stdin=None):
        proc = subprocess.run([sys.executable, CLI, "--vault", self.root, *args],
                              input=stdin, capture_output=True, text=True, encoding="utf-8")
        return proc.returncode, proc.stdout, proc.stderr

    def hook(self, file_path, tool="Edit", event="post-tool-use"):
        payload = {"tool_name": tool, "cwd": self.root, "tool_input": {"file_path": file_path}}
        return self.run_cli("hook", "claude-code", event, stdin=json.dumps(payload))

    def test_check_exit_codes_and_json(self):
        good = self.write("base/notes/good.md", GOOD_NOTE)
        bad = self.write("base/notes/bad.md", GOOD_NOTE.replace("status: 📥", "status: 🟨"))
        self.assertEqual(self.run_cli("check", good)[0], 0)
        code, out, _ = self.run_cli("check", bad)
        self.assertEqual(code, 1)
        self.assertIn("[error] options:", out)
        self.assertIn("Rules: templates/create/notes/manifest.md", out)
        code, out, _ = self.run_cli("check", "--json", bad)
        self.assertEqual(json.loads(out)[0]["findings"][0]["rule"], "options")
        self.assertEqual(self.run_cli("check", "base/notes/none.md")[0], 1)

    def test_schema_new_set_flow(self):
        code, out, _ = self.run_cli("schema", "note/basic/evergreen")
        self.assertEqual(code, 0)
        self.assertIn("status: select | key must exist, may be empty | default 📥", out)
        self.assertIn("tags: multiselect | key must exist, may be empty | default note/basic/evergreen", out)
        self.assertIn("Allowed: 📥, 🟩.", out)
        self.assertIn("Filled for you: icon = 🌲", out)
        code, out, _ = self.run_cli("new", "note/basic/evergreen", "--title", "From CLI", "--set", "category=science")
        self.assertEqual((code, out.splitlines()[0]), (0, "Created base/notes/From CLI.md"))
        code, _, err = self.run_cli("set", "base/notes/From CLI.md", "status=🟨")
        self.assertEqual(code, 1)
        self.assertIn("Nothing was written", err)
        self.assertEqual(self.run_cli("set", "base/notes/From CLI.md", "status=🟩")[0], 0)
        self.assertEqual(self.run_cli("check", "base/notes/From CLI.md")[0], 0)

    def test_find_values_and_lookup_by_name_or_id(self):
        code, out, _ = self.run_cli("find", "#task AND id=OV-4", "--show", "id")
        self.assertEqual((code, out.strip()), (0, "base/tasks/old task.md | id: OV-4"))
        self.assertIn("No notes match.", self.run_cli("find", "#task AND id=NONE")[1])
        out = self.run_cli("values", "note/basic/evergreen", "meta", "--given", "category=science")[1]
        self.assertIn("physics", out)
        self.assertNotIn("painting", out)
        self.assertIn("📥", self.run_cli("values", "note/basic/evergreen", "status")[1])
        self.assertEqual(self.run_cli("set", "OV-4", "project=Open Vault")[0], 0)
        self.assertEqual(self.run_cli("check", "old task")[0], 0)
        code, _, err = self.run_cli("set", "no such note", "a=b")
        self.assertEqual(code, 1)
        self.assertIn("was not found", err)

    def test_hook_is_silent_for_good_and_foreign_files(self):
        good = self.write("base/notes/good.md", GOOD_NOTE)
        self.write("notes.txt", "x")
        for target in (f"{self.root}/{good}", f"{self.root}/notes.txt", "/tmp/outside.md", f"{self.root}/missing.md"):
            with self.subTest(target=target):
                self.assertEqual(self.hook(target), (0, "", ""))

    def test_hook_reports_problems_with_exit_2(self):
        bad = self.write("base/notes/bad.md", GOOD_NOTE.replace("status: 📥", "status: 🟨"))
        code, out, err = self.hook(f"{self.root}/{bad}")
        self.assertEqual((code, out), (2, ""))
        self.assertIn('"status" has a value that is not allowed', err)

    def test_hook_lists_only_what_the_edit_introduced(self):
        rel = self.write("base/notes/legacy.md", GOOD_NOTE.replace("status: 📥", "status: 🟨"))
        full = f"{self.root}/{rel}"
        self.assertEqual(self.hook(full, event="pre-tool-use"), (0, "", ""))
        code, _, err = self.hook(full)
        self.assertEqual(code, 2)
        self.assertIn("added no problems, but the note still has 1 older error(s)", err)
        self.assertNotIn("options:", err)

        self.hook(full, event="pre-tool-use")
        self.write(rel, self.read(rel).replace("icon: 🌲", "icon: 🌳"))
        code, _, err = self.hook(full)
        self.assertEqual(code, 2)
        self.assertIn("[warning, fixable] fixed:", err)
        self.assertNotIn("options:", err)
        self.assertIn("1 older finding(s)", err)
        self.assertIn("options:", self.hook(full)[2], "without a snapshot everything is listed")

    def test_old_warnings_alone_keep_the_hook_silent(self):
        rel = self.write("base/notes/legacy.md", GOOD_NOTE.replace("icon: 🌲", "icon: 🌳"))
        full = f"{self.root}/{rel}"
        self.hook(full, event="pre-tool-use")
        self.assertEqual(self.hook(full), (0, "", ""))

    def test_protected_zone_stops_once_then_lets_the_same_edit_through(self):
        target = f"{self.root}/base/categories/science.md"
        code, _, err = self.hook(target, event="pre-tool-use")
        self.assertEqual(code, 2)
        self.assertIn("Stopped once", err)
        self.assertIn("repeat the same edit", err)
        self.assertEqual(self.hook(target, event="pre-tool-use")[0], 0)
        self.assertEqual(self.hook(target)[0], 0, "already warned before the edit, no second notice")

    def test_protected_zone_notice_for_agents_without_a_pre_hook(self):
        self.write("base/categories/new.md", "---\ntags:\n  - system/category\n---\n")
        code, _, err = self.hook(f"{self.root}/base/categories/new.md", tool="Write")
        self.assertEqual(code, 2)
        self.assertIn("protected zone", err)

    def test_hook_never_crashes_the_agent(self):
        self.assertEqual(self.run_cli("hook", "claude-code", "post-tool-use", stdin="not json")[0], 0)
        self.assertEqual(self.run_cli("hook", "other-agent", "post-tool-use", stdin="{}")[0], 0)
        self.write(".claude/_engine/local/config.json", "{broken")
        good = self.write("base/notes/good.md", GOOD_NOTE)
        self.assertEqual(self.hook(f"{self.root}/{good}")[0], 0)

    def test_checks_and_config_are_self_describing(self):
        code, out, _ = self.run_cli("checks")
        self.assertEqual(code, 0)
        for check_id in ("required", "options", "link-exists", "task-id", "unknown-type"):
            self.assertIn(check_id, out)
        self.assertIn("Severity levels: off, info, warning, error", out)
        self.assertIn('"zones"', self.run_cli("config")[1])


if __name__ == "__main__":
    unittest.main()

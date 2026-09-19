import unittest

from helpers import GOOD_NOTE, VaultCase
from engine import yamlio
from engine.write import WriteError, Writer, parse_assignments


class NewTest(VaultCase):
    def new(self, type_name, title, *pairs, **kwargs):
        return Writer(self.engine()).new(type_name, title, parse_assignments(list(pairs)), **kwargs)

    def test_new_note_is_complete_and_clean(self):
        result = self.new("note/basic/evergreen", "Entropy", "category=science", "meta=physics",
                          "aliases=b", "aliases=a", body="First line.")
        self.assertEqual(result.path, "base/notes/Entropy.md")
        fm = yamlio.parse_mapping(yamlio.split_frontmatter(self.read(result.path))[0])
        self.assertEqual(list(fm)[:3], ["tags", "aliases", "status"])
        self.assertEqual(fm["tags"], ["note/basic/evergreen"])
        self.assertEqual(fm["aliases"], ["a", "b"])
        self.assertEqual(fm["status"], "📥")
        self.assertEqual(fm["icon"], "🌲")
        self.assertEqual(fm["category"], ["[[science]]"])
        self.assertRegex(fm["created"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d$")
        self.assertNotIn("cover", fm)
        self.assertIn("First line.", self.read(result.path))
        self.assertEqual(self.rules(result.path), [])

    def test_new_refuses_bad_values_and_writes_nothing(self):
        with self.assertRaises(WriteError) as caught:
            self.new("note/basic/evergreen", "Bad", "status=🟨")
        self.assertEqual([f.rule for f in caught.exception.findings], ["options"])
        self.assertFalse(self.engine().vault.exists("base/notes/Bad.md"))

    def test_new_refuses_unknown_type_property_title_and_duplicates(self):
        for args in (("note/basic/evergren", "T"), ("note/basic/evergreen", "T", "colour=x"),
                     ("note/basic/evergreen", "a/b"), ("note/basic/evergreen", "")):
            with self.subTest(args=args), self.assertRaises(WriteError):
                self.new(*args)
        self.new("note/basic/evergreen", "Once")
        with self.assertRaises(WriteError):
            self.new("note/basic/evergreen", "Once")

    def test_new_never_creates_folders(self):
        import shutil

        shutil.rmtree(f"{self.root}/base/notes")
        with self.assertRaises(WriteError) as caught:
            self.new("note/basic/evergreen", "T")
        self.assertIn("does not exist", caught.exception.message)

    def test_unknown_type_gets_a_suggestion(self):
        with self.assertRaises(WriteError) as caught:
            self.new("note/basic/evergren", "T")
        self.assertIn('Did you mean "note/basic/evergreen"?', caught.exception.message)

    def test_task_rules(self):
        with self.assertRaises(WriteError) as caught:
            self.new("task/default", "No project")
        self.assertIn("A task needs a project.", caught.exception.findings[0].message)
        task = self.new("task/default", "Loop", "project=Open Vault")
        with self.assertRaises(WriteError):
            Writer(self.engine()).change(task.path, add_values=parse_assignments(["blockedBy=Loop"]))

    def test_dry_run_writes_nothing(self):
        result = self.new("note/basic/evergreen", "Dry", dry_run=True)
        self.assertFalse(result.written)
        self.assertFalse(self.engine().vault.exists(result.path))

    def test_task_id_is_computed_and_counter_moves(self):
        first = self.new("task/default", "Write docs", "project=Open Vault")
        second = self.new("task/default", "Write tests", "project=Open Vault")
        ids = [yamlio.parse_mapping(yamlio.split_frontmatter(self.read(r.path))[0])["id"] for r in (first, second)]
        self.assertEqual(ids, ["OV-5", "OV-6"])
        project = yamlio.parse_mapping(yamlio.split_frontmatter(self.read("projects/Open Vault.md"))[0])
        self.assertEqual(project["taskCount"], 6)
        self.assertEqual(self.rules(second.path), [])

    def test_task_id_skips_taken_numbers(self):
        self.write("base/tasks/manual.md", "---\ntags:\n  - task/default\nid: OV-5\n---\n")
        result = self.new("task/default", "Next", "project=Open Vault")
        self.assertIn("id: OV-6", self.read(result.path))


    def test_body_scaffold_comes_from_the_template(self):
        empty = self.new("task/default", "No body", "project=Open Vault")
        self.assertTrue(self.read(empty.path).endswith("---\n\n## Plan\n\n💤\n"))
        full = self.new("task/default", "With body", "project=Open Vault", body="Do the thing.")
        self.assertTrue(self.read(full.path).endswith("---\n\n## Plan\n\nDo the thing.\n"))
        self.assertNotIn("<%", self.read(full.path))

    def test_task_inherits_taxonomy_and_links_back(self):
        first = self.new("task/default", "First", "project=Open Vault")
        self.assertIn('category:\n  - "[[science]]"', self.read(first.path))
        second = self.new("task/default", "Second", "project=Open Vault", "related=First", "category=art")
        self.assertIn('  - "[[art]]"', self.read(second.path))
        self.assertIn('related:\n  - "[[Second]]"', self.read(first.path))
        Writer(self.engine()).change(first.path, add_values=parse_assignments(["related=old task"]))
        self.assertIn("[[First]]", self.read("base/tasks/old task.md"))

    def test_dates(self):
        with self.assertRaises(WriteError) as caught:
            self.new("task/default", "Backwards", "project=Open Vault", "start=2024-05-02", "end=2024-05-01")
        self.assertEqual([f.rule for f in caught.exception.findings], ["date-order"])
        self.new("task/default", "Blocker", "project=Open Vault", "start=2024-05-01", "end=2024-05-10")
        blocked = self.new("task/default", "Blocked", "project=Open Vault", "blockedBy=Blocker", "start=2024-05-05")
        self.assertEqual(self.rules(blocked.path), ["task-blocked"])

    def test_longform_project_and_scene(self):
        project = self.new("project/longform", "My Book")
        self.assertEqual(project.path, "projects/My Book/My Book.md")
        scene = self.new("mark/scene", "Chapter 1", "up=My Book", "status=🟥")
        self.assertEqual(scene.path, "projects/My Book/Chapter 1.md")
        fm = yamlio.parse_mapping(yamlio.split_frontmatter(self.read(project.path))[0])
        self.assertEqual(fm["longform"]["scenes"], ["Chapter 1"])
        self.assertEqual(fm["longform"]["title"], "My Book")
        with self.assertRaises(WriteError):
            self.new("mark/scene", "Orphan", "up=Open Vault")


class ChangeTest(VaultCase):
    def setUp(self):
        super().setUp()
        self.path = self.write("base/notes/n.md", GOOD_NOTE.replace("icon: 🌲", "icon: 🌲\ncustom:   {keep: me}  # odd"))

    def change(self, **kwargs):
        values = {k: parse_assignments(v) for k, v in kwargs.items()}
        return Writer(self.engine()).change(self.path, **values)

    def test_set_touches_only_that_property(self):
        before = self.read(self.path)
        self.change(set_values=["status=🟩"])
        self.assertEqual(self.read(self.path), before.replace("status: 📥", "status: 🟩"))

    def test_set_refuses_new_errors(self):
        before = self.read(self.path)
        with self.assertRaises(WriteError):
            self.change(set_values=["status=🟨"])
        with self.assertRaises(WriteError):
            self.change(set_values=["category=nowhere"])
        self.assertEqual(self.read(self.path), before)

    def test_old_errors_do_not_block_other_edits(self):
        self.write(self.path, GOOD_NOTE.replace("status: 📥", "status: 🟨"))
        self.change(add_values=["aliases=x"])
        self.assertIn("- x", self.read(self.path))

    def test_add_and_remove(self):
        self.change(add_values=["category=art", "category=science"])
        self.assertIn('  - "[[science]]"\n  - "[[art]]"', self.read(self.path))
        self.change(remove_values=["category=art"])
        self.assertNotIn("[[art]]", self.read(self.path))

    def test_a_write_may_not_break_a_relation(self):
        with self.assertRaises(WriteError) as caught:
            self.change(remove_values=["category=science"])  # meta physics belongs to science
        self.assertEqual([f.rule for f in caught.exception.findings], ["link-relation"])
        with self.assertRaises(WriteError):
            self.change(add_values=["meta=painting"])

    def test_add_is_refused_on_a_single_value_field(self):
        with self.assertRaises(WriteError) as caught:
            self.change(add_values=["status=🟩"])
        self.assertIn("Use: set", caught.exception.message)

    def test_body_is_never_changed(self):
        self.change(set_values=["status=🟩"])
        self.assertTrue(self.read(self.path).endswith("\nBody text stays as it is.\n"))

    def test_updated_is_bumped_when_present(self):
        self.write(self.path, GOOD_NOTE.replace("status: 📥", "status: 📥\nupdated: 2020-01-01T00:00:00+00:00"))
        self.change(set_values=["status=🟩"])
        self.assertNotIn("2020-01-01", self.read(self.path))


class FixTest(VaultCase):
    def test_fix_applies_fixed_default_order_and_keeps_the_rest(self):
        path = self.write("base/notes/n.md",
                          "---\nstatus:\ncustom: 1\ntags:\n  - note/basic/evergreen\nicon: 🌳\n---\nBody\n")
        Writer(self.engine()).fix(path)
        text = self.read(path)
        fm = yamlio.parse_mapping(yamlio.split_frontmatter(text)[0])
        self.assertEqual(list(fm), ["tags", "aliases", "status", "custom", "icon"])
        self.assertEqual((fm["status"], fm["icon"], fm["aliases"], fm["custom"]), ("📥", "🌲", None, 1))
        self.assertTrue(text.endswith("---\nBody\n"))
        self.assertEqual(self.rules(path), [])

    def test_fix_quotes_bare_wikilinks(self):
        path = self.write("base/notes/n.md", GOOD_NOTE.replace('  - "[[science]]"', "  - [[science]]"))
        self.assertEqual(self.rules(path), ["type"])
        Writer(self.engine()).fix(path)
        self.assertEqual(self.read(path), GOOD_NOTE)

    def test_fix_is_idempotent(self):
        path = self.write("base/notes/n.md", GOOD_NOTE)
        Writer(self.engine()).fix(path)
        self.assertEqual(self.read(path), GOOD_NOTE)


if __name__ == "__main__":
    unittest.main()

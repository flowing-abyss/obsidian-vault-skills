import unittest

import helpers  # noqa: F401
from engine import yamlio

CASES = [
    ("a: 1", {"a": 1}),
    ("a: 1.5\nb: -2", {"a": 1.5, "b": -2}),
    ("a: true\nb: False\nc: null\nd: ~\ne:", {"a": True, "b": False, "c": None, "d": None, "e": None}),
    ("a: 2024-01-05", {"a": "2024-01-05"}),
    ("a: 2026-04-23T00:20:24+07:00", {"a": "2026-04-23T00:20:24+07:00"}),
    ("a: yes", {"a": "yes"}),
    ('a: "[[Note]]"', {"a": "[[Note]]"}),
    ("a: [[Note]]", {"a": [["Note"]]}),
    ("a: 'it''s'", {"a": "it's"}),
    ('a: "tab\\there \\u0041 \\"q\\""', {"a": 'tab\there A "q"'}),
    ("a: text # comment", {"a": "text"}),
    ("a: '#d0a570'", {"a": "#d0a570"}),
    ("a: https://x.y/z?q=1#frag", {"a": "https://x.y/z?q=1#frag"}),
    ("a:\n  - x\n  - y", {"a": ["x", "y"]}),
    ("a:\n- x\n- y\nb: 1", {"a": ["x", "y"], "b": 1}),
    ("a: []\nb: {}", {"a": [], "b": {}}),
    ("a: [x, 'y, z', 3]", {"a": ["x", "y, z", 3]}),
    ("a: { value: 📥, label: \"📥 Inbox\" }", {"a": {"value": "📥", "label": "📥 Inbox"}}),
    ("a: { b: { when: \"#x/y\" }, c: [1, 2] }", {"a": {"b": {"when": "#x/y"}, "c": [1, 2]}}),
    ("a: [\n  x,\n  y\n]", {"a": ["x", "y"]}),
    ("a:\n  b:\n    c: 1\n  d: 2", {"a": {"b": {"c": 1}, "d": 2}}),
    ("a:\n  - value: x\n    label: X\n  - value: y", {"a": [{"value": "x", "label": "X"}, {"value": "y"}]}),
    ("a:\n  - - x\n    - y\n  - z", {"a": [["x", "y"], "z"]}),
    ("a: |\n  line one\n  line two\nb: 1", {"a": "line one\nline two\n", "b": 1}),
    ("a: >-\n  folded\n  text\n\n  next", {"a": "folded text\nnext"}),
    ('"quoted key": 1', {"quoted key": 1}),
    ("# only a comment\na: 1", {"a": 1}),
    ("sr-due: 2024-01-01\nsr-ease: 250", {"sr-due": "2024-01-01", "sr-ease": 250}),
    ("js: 'return dv.pages(\"#a AND -#b\").map(p => ({ value: p.file.name }))'",
     {"js": 'return dv.pages("#a AND -#b").map(p => ({ value: p.file.name }))'}),
    ("", {}),
]

ERRORS = [
    "a: 1\na: 2",
    "a: &anchor x",
    "a: *alias",
    "a: !!str x",
    "\ta: 1",
    'a: "open',
    "a: [x, y",
    "a: 1\n   b: 2\n  c: 3",
    "- just\n- a list",
]


class ParseTest(unittest.TestCase):
    def test_cases(self):
        for text, want in CASES:
            with self.subTest(text=text):
                self.assertEqual(yamlio.parse_mapping(text), want)

    def test_errors(self):
        for text in ERRORS:
            with self.subTest(text=text):
                with self.assertRaises(yamlio.YamlError):
                    yamlio.parse_mapping(text)

    def test_error_has_line(self):
        with self.assertRaises(yamlio.YamlError) as caught:
            yamlio.parse_mapping("a: 1\nb: 2\na: 3")
        self.assertEqual(caught.exception.line, 3)
        self.assertIn("duplicate", str(caught.exception))


class SplitTest(unittest.TestCase):
    def test_split(self):
        self.assertEqual(yamlio.split_frontmatter("---\na: 1\n---\nbody\n"), ("a: 1", "body\n"))
        self.assertEqual(yamlio.split_frontmatter("no frontmatter"), (None, "no frontmatter"))
        self.assertEqual(yamlio.split_frontmatter("---\n---\nbody"), ("", "body"))
        self.assertEqual(yamlio.split_frontmatter("---\na: 1\nnever closed"), (None, "---\na: 1\nnever closed"))
        self.assertEqual(yamlio.split_frontmatter("---\r\na: 1\r\n---\r\nbody")[0], "a: 1")

    def test_body_rule_is_not_frontmatter_end(self):
        fm, body = yamlio.split_frontmatter("---\na: 1\n---\ntext\n\n---\n\nmore\n")
        self.assertEqual(fm, "a: 1")
        self.assertEqual(body, "text\n\n---\n\nmore\n")


class DumpTest(unittest.TestCase):
    VALUES = [
        "plain", "with: colon", "#hash", "[[Link]]", "[[Link|alias]]", "", " lead", "true", "12", "1.5",
        "null", "it's", 'say "hi"', "line\nbreak", "- dash", "a #b", "ends:", "📥", "кириллица", "@at",
        0, 7, -3, 2.5, True, False, None, [], ["a", "[[b]]"], {"k": "v", "n": [1, 2]}, [{"value": "x", "label": "X y"}],
        [["nested", "list"]], "2024-01-05", "https://x.y/z#frag", "*star", "&amp", "%percent", "`tick", "?q", "|pipe", ">gt",
    ]

    def test_round_trip(self):
        for value in self.VALUES:
            with self.subTest(value=value):
                text = "\n".join(yamlio.dump_property("key", value))
                self.assertEqual(yamlio.parse_mapping(text), {"key": value})

    def test_obsidian_style(self):
        self.assertEqual(yamlio.dump_property("a", ["[[x]]"]), ["a:", '  - "[[x]]"'])
        self.assertEqual(yamlio.dump_property("a", None), ["a:"])
        self.assertEqual(yamlio.dump_property("a", []), ["a: []"])
        self.assertEqual(yamlio.dump_property("color", "#2a8a40"), ['color: "#2a8a40"'])


class RewriteTest(unittest.TestCase):
    FM = 'tags:\n  - note\n# keep me\nweird:   {a: 1}\nstatus: 📥\nlast: "x"'

    def test_untouched_lines_stay(self):
        out = yamlio.rewrite_frontmatter(self.FM, {"status": "🟩"})
        self.assertEqual(out, self.FM.replace("status: 📥", "status: 🟩"))

    def test_no_change_is_identity(self):
        self.assertEqual(yamlio.rewrite_frontmatter(self.FM, {}), self.FM)

    def test_add_remove_order(self):
        out = yamlio.rewrite_frontmatter(self.FM, {"new": [1]}, remove=["weird"], order=["status", "tags"])
        self.assertEqual(list(yamlio.parse_mapping(out)), ["status", "tags", "last", "new"])
        self.assertIn("# keep me", out)

    def test_list_replaced_whole(self):
        out = yamlio.rewrite_frontmatter(self.FM, {"tags": ["a", "b"]})
        self.assertEqual(yamlio.parse_mapping(out)["tags"], ["a", "b"])
        self.assertNotIn("- note", out)


if __name__ == "__main__":
    unittest.main()

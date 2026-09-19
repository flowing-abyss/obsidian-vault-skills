import unittest

import helpers  # noqa: F401
from engine import query

FM = {"status": "🟦", "start": None, "end": "2024-03-10", "focus": 7, "project": ["[[base/x/Open Vault|OV]]"], "empty": []}
TAGS = ["note/basic/evergreen", "mark/ai"]
PATH = "base/notes/a.md"

CASES = [
    ("#note", True), ("#note/basic", True), ("#note/basic/evergreen", True), ("#not", False),
    ("#NOTE", True), ("#source", False), ("-#source", True), ("NOT #note", False), ("--#note", True),
    ("#note AND -#mark/ai", False), ("#note AND -#mark/log", True), ("#source OR #note", True),
    ("#source OR #x AND #note", False), ("#note and #mark/ai", True),
    ("(#source OR #note) AND #mark/ai", True),
    ('"base/notes/"', True), ("base/notes/", True), ('"base/tasks/" OR #task', False),
    ('"base/notes/" AND #note', True),
    ("status=🟦", True), ("status=🟩", False), ("start=", True), ("end=", False), ("empty=", True), ("missing=", True),
    ("status=🟦 AND start=", True), ("project=Open Vault", True), ("project=Other", False), ("project=[[Open Vault]]", True),
    ("focus>5", True), ("focus<=7", True), ("focus<7", False), ("focus>=8", False),
    ("end<2024-04-01", True), ("end>2024-03-10", False), ("end>=2024-03-10T00:00", True),
    ('status="🟦"', True), ("", False),
]


class QueryTest(unittest.TestCase):
    def test_cases(self):
        for text, want in CASES:
            with self.subTest(query=text):
                self.assertEqual(query.evaluate(text, PATH, TAGS, FM), want)

    def test_dataview_folder(self):
        self.assertTrue(query.evaluate('"base/notes"', PATH, TAGS, FM, dataview=True))
        self.assertFalse(query.evaluate('"base/notes"', PATH, TAGS, FM))
        self.assertFalse(query.evaluate('"base/not"', PATH, TAGS, FM, dataview=True))

    def test_first_tag(self):
        self.assertEqual(query.first_tag("#note/basic/evergreen AND -#note/discourse"), "note/basic/evergreen")
        self.assertEqual(query.first_tag('-#mark/log AND #source'), "source")
        self.assertEqual(query.first_tag('"base/contacts" OR #contact'), "contact")
        self.assertIsNone(query.first_tag('"folder/"'))


if __name__ == "__main__":
    unittest.main()

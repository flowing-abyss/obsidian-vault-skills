"""Checks against the real vault this engine is installed in.

Skipped when the engine is not inside a vault. These tests only read.
They catch what synthetic fixtures miss: real manifests, real notes.
"""

import datetime
import re
import unittest

from helpers import ENGINE_DIR  # noqa: F401
from engine import yamlio
from engine.validate import Engine
from engine.vault import Vault, find_root

ROOT = find_root()
LIVE = (ROOT / ".obsidian").is_dir() and (ROOT / "templates").is_dir()

try:
    import yaml as pyyaml  # optional, only for the differential test
except ImportError:
    pyyaml = None

_DATE = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}([Tt ]\d{1,2}:\d{2}:\d{2}(\.\d+)?\s*(Z|[-+]\d{1,2}(:\d{2})?)?)?$")


def _norm(value):
    if isinstance(value, dict):
        return {("" if k is None else str(k)): _norm(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_norm(v) for v in value]
    if isinstance(value, (datetime.date, datetime.datetime)) or (isinstance(value, str) and _DATE.match(value)):
        return "DATE"
    return value


@unittest.skipUnless(LIVE, "engine is not installed inside a vault")
class LiveVaultTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = Engine(Vault(str(ROOT), use_cache=False))
        cls.notes = sorted(cls.engine.vault.notes())

    def test_every_manifest_loads_without_problems(self):
        self.assertGreater(len(self.engine.schemas.all()), 0)
        self.assertEqual([f"{p.path}: {p.message}" for p in self.engine.schemas.problems], [])

    def test_every_javascript_source_is_recognised(self):
        unresolved = []
        for schema in self.engine.schemas.all():
            for name, field in schema.fields.items():
                options = field.get("options")
                for source in (field.get("source"), options.get("source") if isinstance(options, dict) else None):
                    if isinstance(source, dict) and source.get("js"):
                        if not self.engine.sources.resolve(source, {}).resolved:
                            unresolved.append(f"{schema.path}: {name}")
        self.assertEqual(sorted(set(unresolved)), [])

    def test_no_change_rewrite_is_byte_identical(self):
        for path in self.notes:
            note = self.engine.vault.read_note(path)
            if note.fm_text is None:
                continue
            rebuilt = yamlio.join_note(yamlio.rewrite_frontmatter(note.fm_text, {}), note.body)
            expected = note.text.replace("\r\n", "\n") if "\r\n" in note.fm_text else note.text
            if rebuilt != expected and rebuilt.rstrip("\n") != expected.rstrip("\n"):
                self.fail(f"rewrite changed {path}")

    def test_dump_then_parse_keeps_every_value(self):
        for path in self.notes:
            note = self.engine.vault.read_note(path)
            if note.error or not note.frontmatter:
                continue
            lines = []
            for key, value in note.frontmatter.items():
                lines += yamlio.dump_property(key, value)
            self.assertEqual(yamlio.parse_mapping("\n".join(lines)), note.frontmatter, path)

    def test_checks_never_raise(self):
        for path in self.notes:
            try:
                self.engine.check_path(path)
            except OSError:
                pass  # the vault is live: a note may be renamed while the test runs

    @unittest.skipUnless(pyyaml, "PyYAML is not installed (it is optional)")
    def test_reader_agrees_with_pyyaml(self):
        differences = []
        for path in self.notes:
            fm_text = self.engine.vault.read_note(path).fm_text
            if fm_text is None or "<%" in fm_text:
                continue
            try:
                mine = _norm(yamlio.parse(fm_text))
            except yamlio.YamlError as exc:
                if "duplicate key" not in str(exc):  # PyYAML keeps the last one silently
                    differences.append(f"{path}: {exc}")
                continue
            try:
                theirs = _norm(pyyaml.safe_load(fm_text + "\n"))
            except pyyaml.YAMLError:
                continue
            if mine != theirs:
                differences.append(path)
        self.assertEqual(differences, [])


if __name__ == "__main__":
    unittest.main()

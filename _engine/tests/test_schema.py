import unittest

from helpers import RELATION_JS, VaultCase


class ManifestTest(VaultCase):
    def test_inheritance_and_exclude(self):
        schemas = self.engine().schemas
        self.assertEqual(schemas.problems, [])
        leaf = schemas.for_type("note/basic/evergreen")
        self.assertEqual(leaf.name, "Evergreen")
        self.assertEqual(len(leaf.chain), 3)
        self.assertIn("status", leaf.fields)
        self.assertIn("icon", leaf.fields)
        self.assertNotIn("cover", leaf.fields)
        self.assertEqual(leaf.enforce_folder, "base/notes")
        self.assertEqual(leaf.property_order, ["tags", "aliases", "status"])
        self.assertIn("cover", schemas.for_type("note").fields)
        self.assertTrue(schemas.for_type("note").has_children)

    def test_deepest_match_wins(self):
        schemas = self.engine().schemas
        self.assertEqual(schemas.for_note("x.md", {"tags": ["note/basic/evergreen"]}).name, "Evergreen")
        # An empty middle manifest inherits the parent target, so it wins by depth.
        # The plugin does the same. Its fields equal the parent's.
        self.assertEqual(schemas.for_note("x.md", {"tags": ["note/other"]}).name, "basic")
        self.assertEqual(schemas.for_note("x.md", {"tags": "note"}).type_tag, "note")
        self.assertIsNone(schemas.for_note("x.md", {"tags": ["unrelated"]}))
        self.assertIsNone(schemas.for_note("x.md", {}))

    def test_priority_beats_depth(self):
        self.write("templates/create/special/manifest.md",
                   '---\nname: Special\npriority: 5\ntarget:\n  query: "#note"\nfields: {}\n---\n')
        self.assertEqual(self.engine().schemas.for_note("x.md", {"tags": ["note/basic/evergreen"]}).name, "Special")

    def test_bad_manifest_is_reported_not_fatal(self):
        self.write("templates/create/broken/manifest.md", "---\nname: x\nname: y\n---\n")
        self.write("templates/create/odd/manifest.md",
                   '---\nname: Odd\nfuture_key: 1\ntarget:\n  query: "#odd"\nfields:\n  a: { type: text, new_control: 1 }\n  b: { type: teleport }\n---\n')
        messages = " | ".join(p.message for p in self.engine().schemas.problems)
        self.assertIn("duplicate key", messages)
        self.assertIn('"future_key"', messages)
        self.assertIn('"new_control"', messages)
        self.assertIn('"teleport"', messages)


class SourceTest(VaultCase):
    def resolve(self, source, current=None):
        return self.engine().sources.resolve(source, current or {})

    def test_declarative(self):
        self.assertEqual(self.resolve({"query": "#system/category"}).values, {"science", "art"})
        self.assertEqual(self.resolve({"tag": "system/high"}).values, {"physics", "painting"})
        self.assertEqual(self.resolve({"folder": "projects/"}).values, {"Open Vault"})
        self.assertEqual(self.resolve({"property": {"prefix": "OV"}}).values, {"Open Vault"})

    def test_dv_pages_with_relation(self):
        res = self.resolve({"js": RELATION_JS}, {"category": ["[[science]]"]})
        self.assertEqual(res.values, {"physics"})
        self.assertEqual(res.base, {"physics", "painting"})
        self.assertEqual(self.resolve({"js": RELATION_JS}, {}).values, set())

    def test_manifest_tags_and_static_list(self):
        js = ('return [{options:"approved,ai".split(",").map(v=>({value:`mark/${v}`}))},'
              '...app.vault.getMarkdownFiles().filter(f=>f.path.startsWith("templates/create/notes") && f.basename === "manifest")]')
        self.assertEqual(self.resolve({"js": js}).values, {"mark/approved", "mark/ai", "note/basic/evergreen"})

    def test_distinct_values(self):
        js = "return Array.from(new Set(app.vault.getMarkdownFiles().flatMap(f => [].concat(app.metadataCache.getFileCache(f)?.frontmatter?.prefix || []))))"
        self.assertEqual(self.resolve({"js": js}).values, {"OV"})

    def test_unknown_js_is_unresolved_not_empty(self):
        for js in ("return fetch('x')", 'return dv.pages("#a").where(p => p.rating > 3).map(p => p.file.name)'):
            res = self.resolve({"js": js})
            self.assertFalse(res.resolved)
            self.assertTrue(res.reason)


if __name__ == "__main__":
    unittest.main()

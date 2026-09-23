import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from catalog.build import BuildError, publish
from tests.fixtures import minimal_catalog

T0 = datetime(2026, 9, 23, 10, 0, 0, tzinfo=timezone.utc)


def encode(obj) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def catalog_bytes(recipe_name="Gin Rickey"):
    taxonomy, recipes = minimal_catalog()
    recipes[0]["name"] = recipe_name
    return encode(taxonomy), encode(recipes)


class PublishTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.site = Path(self._tmp.name) / "site" / "v1"

    def tearDown(self):
        self._tmp.cleanup()

    def manifest(self):
        return json.loads((self.site / "manifest.json").read_text(encoding="utf-8"))

    def snapshot(self):
        return {p.name: p.read_bytes() for p in sorted(self.site.iterdir())}

    def test_first_publish_writes_manifest_and_hashed_files(self):
        tax, rec = catalog_bytes()
        self.assertTrue(publish(tax, rec, self.site, T0))
        m = self.manifest()
        tax_sha = hashlib.sha256(tax).hexdigest()
        rec_sha = hashlib.sha256(rec).hexdigest()
        self.assertEqual(m["schemaVersion"], 1)
        self.assertEqual(m["generatedAt"], "2026-09-23T10:00:00Z")
        self.assertEqual(m["contentVersion"], hashlib.sha256((tax_sha + rec_sha).encode()).hexdigest()[:8])
        self.assertEqual(m["taxonomy"], {"path": f"taxonomy.{tax_sha[:8]}.json", "sha256": tax_sha, "bytes": len(tax)})
        self.assertEqual(m["recipes"], {"path": f"recipes.{rec_sha[:8]}.json", "sha256": rec_sha, "bytes": len(rec)})
        self.assertEqual((self.site / m["taxonomy"]["path"]).read_bytes(), tax)
        self.assertEqual((self.site / m["recipes"]["path"]).read_bytes(), rec)

    def test_unchanged_content_is_a_byte_for_byte_no_op(self):
        tax, rec = catalog_bytes()
        publish(tax, rec, self.site, T0)
        before = self.snapshot()
        self.assertFalse(publish(tax, rec, self.site, T0 + timedelta(days=1)))
        self.assertEqual(self.snapshot(), before)

    def test_retention_keeps_the_last_three_versions(self):
        paths_per_version = []
        for i in range(4):
            tax, rec = catalog_bytes(recipe_name=f"Gin Rickey {i}")
            publish(tax, rec, self.site, T0 + timedelta(hours=i))
            m = self.manifest()
            paths_per_version.append({m["taxonomy"]["path"], m["recipes"]["path"]})
        on_disk = {p.name for p in self.site.iterdir()}
        for kept in paths_per_version[1:]:
            self.assertTrue(kept <= on_disk, f"{kept} should still be published")
        oldest_only = paths_per_version[0] - set().union(*paths_per_version[1:])
        self.assertTrue(oldest_only, "fixture should give version 0 a unique recipes file")
        self.assertFalse(oldest_only & on_disk, "version 0's unique files should be pruned")
        history = json.loads((self.site / "history.json").read_text(encoding="utf-8"))
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], self.manifest())

    def test_reverting_content_publishes_a_new_manifest(self):
        a = catalog_bytes("A")
        b = catalog_bytes("B")
        publish(*a, self.site, T0)
        first_version = self.manifest()["contentVersion"]
        publish(*b, self.site, T0 + timedelta(hours=1))
        self.assertTrue(publish(*a, self.site, T0 + timedelta(hours=2)))
        m = self.manifest()
        self.assertEqual(m["contentVersion"], first_version)
        self.assertEqual(m["generatedAt"], "2026-09-23T12:00:00Z")

    def test_invalid_content_raises_and_leaves_site_untouched(self):
        publish(*catalog_bytes(), self.site, T0)
        before = self.snapshot()
        taxonomy, recipes = minimal_catalog()
        recipes[0]["steps"] = []
        with self.assertRaises(BuildError):
            publish(encode(taxonomy), encode(recipes), self.site, T0 + timedelta(hours=1))
        self.assertEqual(self.snapshot(), before)

    def test_oversized_file_raises(self):
        tax, _ = catalog_bytes()
        with self.assertRaises(BuildError):
            publish(tax, b" " * 1_000_001, self.site, T0)
        self.assertFalse(self.site.exists())

    def test_non_json_raises_build_error(self):
        with self.assertRaises(BuildError):
            publish(b"<html>", b"[]", self.site, T0)


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from catalog.validate import validate
from tests.fixtures import STYLE_A, minimal_catalog

REPO = Path(__file__).resolve().parent.parent


class ValidateTests(unittest.TestCase):
    def assertInvalid(self, taxonomy, recipes, fragment):
        errors = validate(taxonomy, recipes)
        self.assertTrue(any(fragment in e for e in errors),
                        f"expected an error containing {fragment!r}, got {errors}")

    def test_minimal_catalog_is_valid(self):
        self.assertEqual(validate(*minimal_catalog()), [])

    def test_duplicate_id_is_rejected(self):
        taxonomy, recipes = minimal_catalog()
        recipes[0]["id"] = STYLE_A
        self.assertInvalid(taxonomy, recipes, "duplicate id")

    def test_non_uuid_id_is_rejected(self):
        taxonomy, recipes = minimal_catalog()
        taxonomy[0]["id"] = "not-a-uuid"
        self.assertInvalid(taxonomy, recipes, "invalid id")

    def test_dangling_recipe_style_reference_is_rejected(self):
        taxonomy, recipes = minimal_catalog()
        recipes[0]["ingredients"][0]["ingredientStyleId"] = "99999999-9999-5999-8999-999999999999"
        self.assertInvalid(taxonomy, recipes, "unknown style")

    def test_flavour_out_of_range_is_rejected(self):
        taxonomy, recipes = minimal_catalog()
        taxonomy[0]["families"][0]["styles"][0]["flavorProfile"]["citrus"] = 1.5
        self.assertInvalid(taxonomy, recipes, "flavorProfile.citrus")

    def test_family_category_mismatch_is_rejected(self):
        taxonomy, recipes = minimal_catalog()
        taxonomy[0]["families"][0]["categoryId"] = "99999999-9999-5999-8999-999999999999"
        self.assertInvalid(taxonomy, recipes, "categoryId does not match")

    def test_style_family_mismatch_is_rejected(self):
        taxonomy, recipes = minimal_catalog()
        taxonomy[0]["families"][0]["styles"][0]["familyId"] = "99999999-9999-5999-8999-999999999999"
        self.assertInvalid(taxonomy, recipes, "familyId does not match")

    def test_abv_min_above_max_is_rejected(self):
        taxonomy, recipes = minimal_catalog()
        taxonomy[0]["families"][0]["styles"][0]["abvMin"] = 50.0
        self.assertInvalid(taxonomy, recipes, "abvMin")

    def test_unknown_glass_type_is_rejected(self):
        taxonomy, recipes = minimal_catalog()
        recipes[0]["glassType"] = "bucket"
        self.assertInvalid(taxonomy, recipes, "glassType")

    def test_empty_steps_are_rejected(self):
        taxonomy, recipes = minimal_catalog()
        recipes[0]["steps"] = []
        self.assertInvalid(taxonomy, recipes, "steps")

    def test_empty_ingredients_are_rejected(self):
        taxonomy, recipes = minimal_catalog()
        recipes[0]["ingredients"] = []
        self.assertInvalid(taxonomy, recipes, "ingredients")

    def test_missing_name_is_rejected(self):
        taxonomy, recipes = minimal_catalog()
        recipes[0]["name"] = "  "
        self.assertInvalid(taxonomy, recipes, "name")

    def test_non_object_entries_do_not_crash(self):
        errors = validate(["oops"], [42])
        self.assertTrue(errors)

    def test_real_generated_catalog_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([sys.executable, str(REPO / "generate.py"), tmp],
                           check=True, capture_output=True)
            taxonomy = json.loads((Path(tmp) / "taxonomy.json").read_text(encoding="utf-8"))
            recipes = json.loads((Path(tmp) / "recipes.json").read_text(encoding="utf-8"))
        self.assertEqual(validate(taxonomy, recipes), [])


if __name__ == "__main__":
    unittest.main()

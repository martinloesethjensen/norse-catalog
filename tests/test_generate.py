import unittest

import generate


def _catalog():
    _, style_lookup = generate.build_taxonomy()
    names = {slug: None for slug in style_lookup}
    for category in generate.TAXONOMY:
        for family in category[2]:
            for style in family[2]:
                names[style[0]] = style[1]
    recipes = {r["name"]: r for r in generate.build_recipes(style_lookup)}
    name_by_id = {v[0]: names[slug] for slug, v in style_lookup.items()}
    return recipes, name_by_id


RECIPES, STYLE_NAME_BY_ID = _catalog()


def ingredient_names(recipe_name):
    return [STYLE_NAME_BY_ID[i["ingredientStyleId"]] for i in RECIPES[recipe_name]["ingredients"]]


def abv(recipe_name):
    return RECIPES[recipe_name]["flavorProfile"]["abv"]


class AmountTests(unittest.TestCase):
    def test_millilitres(self):
        self.assertEqual(generate.amount_ml("22ml", None, "coupe", 1), 22.0)
        self.assertEqual(generate.amount_ml("7.5ml", None, "coupe", 1), 7.5)

    def test_dashes_and_spoons(self):
        self.assertAlmostEqual(generate.amount_ml("2 dash", None, "coupe", 1), 1.6)
        self.assertEqual(generate.amount_ml("1 tsp", None, "mug", 1), 5.0)

    def test_top_depends_on_glass_and_is_split_between_tops(self):
        self.assertEqual(generate.amount_ml("top", None, "highball", 1), 120.0)
        self.assertEqual(generate.amount_ml("top", None, "highball", 2), 60.0)
        self.assertEqual(generate.amount_ml("top", None, "flute", 1), 90.0)

    def test_counted_items_are_garnish_sized_unless_muddled(self):
        self.assertEqual(generate.amount_ml("1", None, "rocks", 1), generate.GARNISH_UNIT_ML)
        self.assertEqual(generate.amount_ml("3", "wedges, muddled", "rocks", 1), 3 * generate.MUDDLED_UNIT_ML)

    def test_unknown_unit_fails_loudly(self):
        with self.assertRaises(AssertionError):
            generate.amount_ml("1 cup", None, "rocks", 1)


class StructuredAmountTests(unittest.TestCase):
    def test_parse_amount(self):
        self.assertEqual(generate.parse_amount("22ml"), (22.0, "ml"))
        self.assertEqual(generate.parse_amount("7.5ml"), (7.5, "ml"))
        self.assertEqual(generate.parse_amount("2 dash"), (2.0, "dash"))
        self.assertEqual(generate.parse_amount("8 leaves"), (8.0, "leaf"))
        self.assertEqual(generate.parse_amount("1 pinch"), (1.0, "pinch"))
        self.assertEqual(generate.parse_amount("1"), (1.0, "piece"))
        self.assertEqual(generate.parse_amount("3 wedge"), (3.0, "piece"))
        self.assertEqual(generate.parse_amount("top"), (None, "top"))

    def test_every_ingredient_carries_a_structured_amount(self):
        for name, recipe in RECIPES.items():
            for ing in recipe["ingredients"]:
                self.assertIn(ing["unit"], generate.UNITS, name)
                self.assertEqual(ing["quantity"] is None, ing["unit"] == "top", name)

    def test_structured_amount_matches_the_display_text(self):
        daiquiri = RECIPES["Daiquiri"]["ingredients"]
        self.assertEqual([(i["amount"], i["quantity"], i["unit"]) for i in daiquiri],
                         [("60ml", 60.0, "ml"), ("22ml", 22.0, "ml"), ("15ml", 15.0, "ml")])


class DilutionTests(unittest.TestCase):
    def test_shaking_dilutes_more_than_stirring(self):
        self.assertGreater(generate.dilution_ratio("shake", "coupe", 0.3),
                           generate.dilution_ratio("stir", "coupe", 0.3))

    def test_hot_drinks_take_no_ice_melt(self):
        self.assertEqual(generate.dilution_ratio("build", "mug", 0.2), 0.0)


class RecipeStrengthTests(unittest.TestCase):
    """Served ABVs should land near measured values (Liquid Intelligence, Arnold)."""

    def test_classic_sours_and_stirred_drinks(self):
        self.assertTrue(14 <= abv("Daiquiri") <= 17, abv("Daiquiri"))
        self.assertTrue(24 <= abv("Martini") <= 30, abv("Martini"))
        self.assertTrue(22 <= abv("Manhattan") <= 28, abv("Manhattan"))

    def test_juice_heavy_highballs_are_not_spirit_strength(self):
        self.assertLess(abv("Screwdriver"), 12)
        self.assertLess(abv("Whiskey Highball"), 12)

    def test_hot_water_counts_toward_volume(self):
        self.assertLess(abv("Hot Toddy"), 15)

    def test_strength_tags_agree_with_computed_abv(self):
        for name, recipe in RECIPES.items():
            tags, value = recipe["tags"], recipe["flavorProfile"]["abv"]
            self.assertEqual("no-abv" in tags, value == 0, name)
            if "low-abv" in tags:
                self.assertLessEqual(value, generate.LOW_ABV_MAX, name)

    def test_tagging_a_strong_drink_low_abv_fails_the_build(self):
        with self.assertRaises(AssertionError):
            generate.check_strength_tags("Martini", ["low-abv"], 26.0)


class FlavourTests(unittest.TestCase):
    def test_amounts_drive_the_profile(self):
        # 45ml of Angostura makes the Trinidad Sour far more bitter than a Manhattan's two dashes.
        trinidad = RECIPES["Trinidad Sour"]["flavorProfile"]["bitterness"]
        manhattan = RECIPES["Manhattan"]["flavorProfile"]["bitterness"]
        self.assertGreater(trinidad, manhattan + 0.2)

    def test_muddled_herbs_register(self):
        self.assertGreater(RECIPES["Mojito"]["flavorProfile"]["herbal"], 0.1)

    def test_a_float_flavours_more_than_its_volume(self):
        # 7.5ml of Islay on 97ml of drink: by volume alone the smoke would be ~0.16.
        self.assertGreaterEqual(RECIPES["Penicillin"]["flavorProfile"]["smokiness"], 0.2)

    def test_a_bitters_led_drink_does_not_dwarf_a_negroni(self):
        trinidad = RECIPES["Trinidad Sour"]["flavorProfile"]["bitterness"]
        negroni = RECIPES["Negroni"]["flavorProfile"]["bitterness"]
        self.assertGreater(trinidad, negroni)
        self.assertGreaterEqual(negroni / trinidad, 0.67, "the app scales notes by the catalog maximum")


class ClassicSpecTests(unittest.TestCase):
    """Guards against single-bottle stand-ins creeping back into classic specs."""

    def test_maraschino_drinks(self):
        for name in ("Aviation", "Last Word", "Martinez", "Tuxedo", "Casino", "Hemingway Daiquiri"):
            self.assertIn("Maraschino Liqueur", ingredient_names(name), name)
        self.assertIn("Crème de Violette", ingredient_names("Aviation"))

    def test_no_classic_uses_raspberry_liqueur_as_a_stand_in(self):
        users = sorted(n for n in RECIPES if "Raspberry Liqueur" in ingredient_names(n))
        self.assertEqual(users, ["French Martini"])

    def test_cream_and_mint_classics(self):
        self.assertEqual(ingredient_names("Stinger"), ["VS Cognac", "Crème de Menthe"])
        self.assertEqual(ingredient_names("Grasshopper"), ["Crème de Menthe", "Crème de Cacao", "Heavy Cream"])
        for name in ("Alexander", "Brandy Alexander", "Golden Cadillac", "Pink Squirrel"):
            self.assertIn("Crème de Cacao", ingredient_names(name), name)

    def test_specific_modifiers(self):
        self.assertIn("Stout", ingredient_names("Black Velvet"))
        self.assertIn("Galliano", ingredient_names("Harvey Wallbanger"))
        self.assertIn("Light Amaro", ingredient_names("Paper Plane"))
        self.assertIn("Dark Amaro", ingredient_names("Black Manhattan"))
        self.assertIn("Blanc Aperitif Wine", ingredient_names("Corpse Reviver No. 2"))
        self.assertIn("Hot Coffee", ingredient_names("Irish Coffee"))
        self.assertIn("Red Wine", ingredient_names("Mulled Wine"))
        for name in ("Alaska", "Naked and Famous", "Widow's Kiss"):
            self.assertIn("Yellow Chartreuse", ingredient_names(name), name)
        for name in ("Kir Royale", "El Diablo"):
            self.assertIn("Crème de Cassis", ingredient_names(name), name)
        for name in ("Blood and Sand", "Remember the Maine", "Singapore Sling"):
            self.assertIn("Cherry Liqueur", ingredient_names(name), name)


class CoverageTests(unittest.TestCase):
    """Every bottle should unlock something, or Buy next can never suggest it usefully."""

    def test_every_liqueur_and_one_off_spirit_is_used_by_a_recipe(self):
        # Gin, rum, whiskey, tequila and brandy styles also work as same-family
        # substitutes, so only bottles nothing else can stand in for must have a recipe.
        used = {generate.uid("style:" + i[0]) for r in generate.RECIPES for i in r[7]}
        unused = [style[1] for cat_slug, _, families in generate.TAXONOMY for fam_slug, _, styles in families
                  for style in styles
                  if (cat_slug == "liqueur" or fam_slug == "other_spirits") and generate.uid("style:" + style[0]) not in used]
        self.assertEqual(unused, [])

    def test_bottles_from_issue_2_unlock_several_recipes(self):
        for bottle in ("Elderflower Liqueur", "Sloe Gin", "Cynar", "Tonic Water"):
            users = [n for n in RECIPES if bottle in ingredient_names(n)]
            self.assertGreaterEqual(len(users), 3, f"{bottle}: {users}")


if __name__ == "__main__":
    unittest.main()

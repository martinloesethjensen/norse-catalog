"""Invariant checks for the generated catalog.

`validate()` returns human-readable error strings; an empty list means the
catalog is publishable. Enum sets mirror the iOS decoders exactly — a value
the app can't decode must never be published.
"""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

DIMS = ("sweetness", "bitterness", "smokiness", "citrus", "floral",
        "spice", "herbal", "fruity", "oaky")
GLASS_TYPES = {"coupe", "rocks", "highball", "martini", "collins", "hurricane",
               "flute", "mug", "wineGlass"}
METHODS = {"shake", "stir", "build", "blend", "throw"}
DIFFICULTIES = {"easy", "medium", "advanced"}
MAX_FILE_BYTES = 1_000_000


def _is_uuid(value) -> bool:
    try:
        return str(uuid.UUID(value)) == value
    except (ValueError, TypeError, AttributeError):
        return False


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_text(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _check_profile(where: str, profile, errors: list) -> None:
    if not isinstance(profile, dict):
        errors.append(f"{where}: flavorProfile missing")
        return
    for dim in DIMS:
        v = profile.get(dim)
        if not _is_number(v) or not 0.0 <= v <= 1.0:
            errors.append(f"{where}: flavorProfile.{dim} must be a number in 0-1, got {v!r}")
    abv = profile.get("abv")
    if not _is_number(abv) or not 0.0 <= abv <= 100.0:
        errors.append(f"{where}: flavorProfile.abv must be a number in 0-100, got {abv!r}")


def validate(taxonomy, recipes) -> list:
    errors: list = []
    seen_ids: set = set()
    style_ids: set = set()

    def claim(where: str, value) -> None:
        if not _is_uuid(value):
            errors.append(f"{where}: invalid id {value!r}")
            return
        if value in seen_ids:
            errors.append(f"{where}: duplicate id {value}")
        seen_ids.add(value)

    if not isinstance(taxonomy, list) or not taxonomy:
        errors.append("taxonomy: must be a non-empty list")
        taxonomy = []
    for category in taxonomy:
        if not isinstance(category, dict):
            errors.append(f"taxonomy: category must be an object, got {category!r}")
            continue
        cw = f"category {category.get('name')!r}"
        claim(cw, category.get("id"))
        if not _is_text(category.get("name")):
            errors.append(f"{cw}: name required")
        families = category.get("families")
        if not isinstance(families, list) or not families:
            errors.append(f"{cw}: families must be a non-empty list")
            continue
        for family in families:
            if not isinstance(family, dict):
                errors.append(f"{cw}: family must be an object")
                continue
            fw = f"family {family.get('name')!r}"
            claim(fw, family.get("id"))
            if not _is_text(family.get("name")):
                errors.append(f"{fw}: name required")
            if family.get("categoryId") != category.get("id"):
                errors.append(f"{fw}: categoryId does not match its parent category")
            styles = family.get("styles")
            if not isinstance(styles, list) or not styles:
                errors.append(f"{fw}: styles must be a non-empty list")
                continue
            for style in styles:
                if not isinstance(style, dict):
                    errors.append(f"{fw}: style must be an object")
                    continue
                sw = f"style {style.get('name')!r}"
                claim(sw, style.get("id"))
                style_ids.add(style.get("id"))
                if not _is_text(style.get("name")):
                    errors.append(f"{sw}: name required")
                if style.get("familyId") != family.get("id"):
                    errors.append(f"{sw}: familyId does not match its parent family")
                if style.get("categoryId") != category.get("id"):
                    errors.append(f"{sw}: categoryId does not match its parent category")
                brands = style.get("exampleBrands")
                if not isinstance(brands, list) or not all(_is_text(b) for b in brands):
                    errors.append(f"{sw}: exampleBrands must be a list of non-empty strings")
                lo, hi = style.get("abvMin"), style.get("abvMax")
                if not _is_number(lo) or not _is_number(hi) or lo > hi:
                    errors.append(f"{sw}: abvMin/abvMax must be numbers with abvMin <= abvMax")
                _check_profile(sw, style.get("flavorProfile"), errors)

    if not isinstance(recipes, list) or not recipes:
        errors.append("recipes: must be a non-empty list")
        recipes = []
    for recipe in recipes:
        if not isinstance(recipe, dict):
            errors.append(f"recipes: recipe must be an object, got {recipe!r}")
            continue
        rw = f"recipe {recipe.get('name')!r}"
        claim(rw, recipe.get("id"))
        for field in ("name", "description"):
            if not _is_text(recipe.get(field)):
                errors.append(f"{rw}: {field} required")
        if recipe.get("glassType") not in GLASS_TYPES:
            errors.append(f"{rw}: glassType {recipe.get('glassType')!r} is not one of {sorted(GLASS_TYPES)}")
        if recipe.get("method") not in METHODS:
            errors.append(f"{rw}: method {recipe.get('method')!r} is not one of {sorted(METHODS)}")
        if recipe.get("difficulty") not in DIFFICULTIES:
            errors.append(f"{rw}: difficulty {recipe.get('difficulty')!r} is not one of {sorted(DIFFICULTIES)}")
        steps = recipe.get("steps")
        if not isinstance(steps, list) or not steps or not all(_is_text(s) for s in steps):
            errors.append(f"{rw}: steps must be a non-empty list of non-empty strings")
        tags = recipe.get("tags")
        if not isinstance(tags, list) or not all(_is_text(t) for t in tags) or len(set(tags)) != len(tags):
            errors.append(f"{rw}: tags must be a list of unique non-empty strings")
        image = recipe.get("imageURL")
        if image is not None and not isinstance(image, str):
            errors.append(f"{rw}: imageURL must be a string or null")
        _check_profile(rw, recipe.get("flavorProfile"), errors)
        ingredients = recipe.get("ingredients")
        if not isinstance(ingredients, list) or not ingredients:
            errors.append(f"{rw}: ingredients must be a non-empty list")
            continue
        for i, ing in enumerate(ingredients):
            iw = f"{rw} ingredient {i}"
            if not isinstance(ing, dict):
                errors.append(f"{iw}: must be an object")
                continue
            if ing.get("ingredientStyleId") not in style_ids:
                errors.append(f"{iw}: unknown style {ing.get('ingredientStyleId')!r}")
            if not _is_text(ing.get("amount")):
                errors.append(f"{iw}: amount required")
            if not isinstance(ing.get("isOptional"), bool):
                errors.append(f"{iw}: isOptional must be a boolean")
            for field in ("preparation", "substituteNotes"):
                if ing.get(field) is not None and not isinstance(ing.get(field), str):
                    errors.append(f"{iw}: {field} must be a string or null")
    return errors


def main(argv: list) -> int:
    folder = Path(argv[1]) if len(argv) > 1 else Path(".")
    taxonomy = json.loads((folder / "taxonomy.json").read_text(encoding="utf-8"))
    recipes = json.loads((folder / "recipes.json").read_text(encoding="utf-8"))
    errors = validate(taxonomy, recipes)
    for e in errors:
        print(e, file=sys.stderr)
    print(f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

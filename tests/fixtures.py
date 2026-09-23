"""A tiny, valid catalog in the exact JSON shape generate.py emits."""
from __future__ import annotations

import copy

CAT = "11111111-1111-5111-8111-111111111111"
FAM = "22222222-2222-5222-8222-222222222222"
STYLE_A = "33333333-3333-5333-8333-333333333333"
STYLE_B = "44444444-4444-5444-8444-444444444444"
RECIPE = "55555555-5555-5555-8555-555555555555"


def _profile(**overrides):
    p = {d: 0.1 for d in ("sweetness", "bitterness", "smokiness", "citrus", "floral",
                          "spice", "herbal", "fruity", "oaky")}
    p["abv"] = 40.0
    p.update(overrides)
    return p


_TAXONOMY = [{
    "id": CAT, "name": "Spirit",
    "families": [{
        "id": FAM, "name": "Gin", "categoryId": CAT,
        "styles": [
            {"id": STYLE_A, "name": "London Dry Gin", "familyId": FAM, "categoryId": CAT,
             "exampleBrands": ["Tanqueray"], "flavorProfile": _profile(herbal=0.7),
             "abvMin": 37.5, "abvMax": 47.0},
            {"id": STYLE_B, "name": "Old Tom Gin", "familyId": FAM, "categoryId": CAT,
             "exampleBrands": [], "flavorProfile": _profile(sweetness=0.5),
             "abvMin": 40.0, "abvMax": 47.0},
        ],
    }],
}]

_RECIPES = [{
    "id": RECIPE, "name": "Gin Rickey", "description": "Gin and lime.",
    "glassType": "highball", "method": "build",
    "ingredients": [
        {"ingredientStyleId": STYLE_A, "amount": "50ml", "preparation": None,
         "isOptional": False, "substituteNotes": None},
    ],
    "steps": ["Build over ice."],
    "flavorProfile": _profile(),
    "tags": ["classic"], "difficulty": "easy", "imageURL": None,
}]


def minimal_catalog():
    """Returns fresh deep copies so tests can mutate freely."""
    return copy.deepcopy(_TAXONOMY), copy.deepcopy(_RECIPES)

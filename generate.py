#!/usr/bin/env python3
"""Generates taxonomy.json and recipes.json for Norse Mixology (Phase 1).

Deterministic UUIDs (uuid5) are derived from human-readable slugs so the
script is idempotent and recipes can reference ingredients by slug while
the emitted JSON uses real UUIDs, matching the Swift `UUID` model fields.
"""
import json
import sys
import uuid
from pathlib import Path

NS = uuid.NAMESPACE_URL


def uid(slug: str) -> str:
    return str(uuid.uuid5(NS, "norsemixology:" + slug))


DIMS = ["sweetness", "bitterness", "smokiness", "citrus", "floral", "spice", "herbal", "fruity", "oaky"]


def profile(**kwargs) -> dict:
    p = {d: 0.0 for d in DIMS}
    p.update(kwargs)
    for d in DIMS:
        assert 0.0 <= p[d] <= 1.0, f"{d} out of range: {p[d]}"
    return p


# ---------------------------------------------------------------------------
# Taxonomy: category -> family -> styles
# Each style: slug, name, brands, abv=(min,max), profile
# ---------------------------------------------------------------------------

TAXONOMY = [
    ("spirit", "Spirit", [
        ("gin", "Gin", [
            ("gin_london_dry", "London Dry Gin", ["Tanqueray", "Beefeater", "Gordon's"], (37.5, 47.0),
             profile(sweetness=.1, bitterness=.2, citrus=.3, floral=.2, spice=.1, herbal=.7, fruity=.1)),
            ("gin_contemporary", "Contemporary Gin", ["Hendrick's", "Roku", "The Botanist"], (40.0, 44.0),
             profile(sweetness=.2, bitterness=.1, citrus=.4, floral=.6, spice=.1, herbal=.5, fruity=.3)),
            ("gin_old_tom", "Old Tom Gin", ["Hayman's Old Tom", "Ransom Old Tom"], (40.0, 47.0),
             profile(sweetness=.5, bitterness=.1, citrus=.2, floral=.2, spice=.1, herbal=.5, fruity=.1, oaky=.1)),
            ("gin_navy_strength", "Navy Strength Gin", ["Plymouth Navy Strength", "Perry's Tot"], (57.0, 58.0),
             profile(sweetness=.1, bitterness=.2, citrus=.3, floral=.2, spice=.3, herbal=.7, fruity=.1)),
            ("gin_genever", "Genever", ["Bols Genever", "Boomsma"], (35.0, 40.0),
             profile(sweetness=.3, bitterness=.1, smokiness=.1, citrus=.1, floral=.1, spice=.2, herbal=.4, fruity=.2, oaky=.3)),
        ]),
        ("vodka", "Vodka", [
            ("vodka_neutral", "Neutral Vodka", ["Absolut", "Grey Goose", "Tito's"], (37.5, 40.0),
             profile(sweetness=.1, floral=.1)),
            ("vodka_citrus", "Citrus-Flavoured Vodka", ["Absolut Citron", "Ketel One Citroen"], (35.0, 40.0),
             profile(sweetness=.1, citrus=.6, floral=.1, fruity=.2)),
        ]),
        ("rum", "Rum", [
            ("rum_white", "White/Blanco Rum", ["Bacardi Superior", "Havana Club 3yr"], (37.5, 40.0),
             profile(sweetness=.3, citrus=.1, floral=.1, spice=.1, fruity=.3)),
            ("rum_gold", "Gold/Aged Rum", ["Mount Gay Eclipse", "Appleton Estate Signature"], (40.0, 40.0),
             profile(sweetness=.4, bitterness=.1, floral=.1, spice=.2, fruity=.3, oaky=.4)),
            ("rum_dark", "Dark/Molasses Rum", ["Gosling's Black Seal", "Myers's"], (40.0, 45.0),
             profile(sweetness=.5, bitterness=.1, smokiness=.1, spice=.2, fruity=.3, oaky=.5)),
            ("rum_spiced", "Spiced Rum", ["Captain Morgan", "Sailor Jerry"], (35.0, 40.0),
             profile(sweetness=.5, bitterness=.1, smokiness=.1, citrus=.1, floral=.1, spice=.5, herbal=.1, fruity=.3, oaky=.3)),
            ("rum_agricole", "Agricole Rum", ["Rhum Clément", "Neisson"], (40.0, 50.0),
             profile(sweetness=.2, citrus=.1, floral=.2, spice=.2, herbal=.3, fruity=.3, oaky=.1)),
        ]),
        ("whiskey", "Whiskey", [
            ("whiskey_bourbon", "Bourbon", ["Buffalo Trace", "Maker's Mark", "Woodford Reserve"], (40.0, 50.0),
             profile(sweetness=.6, bitterness=.1, smokiness=.1, floral=.1, spice=.3, herbal=.1, fruity=.2, oaky=.6)),
            ("whiskey_rye", "Rye Whiskey", ["Rittenhouse", "Bulleit Rye"], (40.0, 50.0),
             profile(sweetness=.3, bitterness=.2, smokiness=.1, spice=.7, herbal=.2, fruity=.1, oaky=.5)),
            ("whiskey_irish", "Irish Whiskey", ["Jameson", "Redbreast"], (40.0, 40.0),
             profile(sweetness=.3, bitterness=.1, floral=.1, spice=.1, herbal=.1, fruity=.2, oaky=.3)),
            ("whiskey_scotch_blended", "Scotch Blended Whisky", ["Johnnie Walker Black", "Famous Grouse"], (40.0, 40.0),
             profile(sweetness=.3, bitterness=.1, smokiness=.2, floral=.1, spice=.1, herbal=.1, fruity=.2, oaky=.4)),
            ("whiskey_scotch_islay", "Scotch Single Malt (Islay)", ["Laphroaig", "Lagavulin"], (43.0, 46.0),
             profile(sweetness=.1, bitterness=.2, smokiness=.9, spice=.2, herbal=.1, fruity=.1, oaky=.5)),
            ("whiskey_scotch_speyside", "Scotch Single Malt (Speyside)", ["Glenlivet", "Macallan"], (40.0, 43.0),
             profile(sweetness=.4, bitterness=.1, smokiness=.1, floral=.2, spice=.1, herbal=.1, fruity=.4, oaky=.5)),
            ("whiskey_japanese", "Japanese Whisky", ["Suntory Toki", "Nikka From The Barrel"], (40.0, 43.0),
             profile(sweetness=.3, bitterness=.1, smokiness=.1, citrus=.1, floral=.2, spice=.1, herbal=.1, fruity=.3, oaky=.4)),
            ("whiskey_tennessee", "Tennessee Whiskey", ["Jack Daniel's", "George Dickel"], (40.0, 45.0),
             profile(sweetness=.5, bitterness=.1, smokiness=.1, floral=.1, spice=.2, herbal=.1, fruity=.2, oaky=.5)),
        ]),
        ("tequila_mezcal", "Tequila & Mezcal", [
            ("tequila_blanco", "Blanco Tequila", ["Espolòn Blanco", "Patrón Silver"], (38.0, 40.0),
             profile(sweetness=.1, bitterness=.1, citrus=.2, floral=.3, spice=.2, herbal=.4, fruity=.2)),
            ("tequila_reposado", "Reposado Tequila", ["Don Julio Reposado", "Herradura Reposado"], (38.0, 40.0),
             profile(sweetness=.2, bitterness=.1, citrus=.1, floral=.2, spice=.2, herbal=.3, fruity=.2, oaky=.3)),
            ("tequila_anejo", "Añejo Tequila", ["Don Julio Añejo", "Herradura Añejo"], (38.0, 40.0),
             profile(sweetness=.3, bitterness=.1, smokiness=.1, floral=.1, spice=.2, herbal=.2, fruity=.2, oaky=.5)),
            ("mezcal", "Mezcal", ["Del Maguey Vida", "Montelobos"], (40.0, 45.0),
             profile(sweetness=.1, bitterness=.2, smokiness=.8, citrus=.1, floral=.2, spice=.2, herbal=.4, fruity=.1, oaky=.1)),
        ]),
        ("brandy_cognac", "Brandy & Cognac", [
            ("cognac_vs", "VS Cognac", ["Hennessy VS", "Martell VS"], (40.0, 40.0),
             profile(sweetness=.3, bitterness=.1, citrus=.1, floral=.2, spice=.1, fruity=.4, oaky=.3)),
            ("cognac_vsop", "VSOP Cognac", ["Hennessy VSOP", "Rémy Martin VSOP"], (40.0, 40.0),
             profile(sweetness=.3, bitterness=.1, floral=.2, spice=.1, fruity=.4, oaky=.5)),
            ("pisco", "Pisco", ["Pisco Porton", "BarSol"], (38.0, 48.0),
             profile(sweetness=.2, citrus=.2, floral=.4, spice=.1, herbal=.1, fruity=.3)),
            ("calvados", "Calvados", ["Boulard", "Christian Drouin"], (40.0, 40.0),
             profile(sweetness=.3, bitterness=.1, floral=.1, spice=.2, fruity=.6, oaky=.3)),
        ]),
        ("other_spirits", "Other Spirits", [
            ("absinthe", "Absinthe", ["Pernod Absinthe", "Lucid"], (55.0, 74.0),
             profile(sweetness=.2, bitterness=.3, floral=.2, spice=.2, herbal=.9)),
            ("aquavit", "Aquavit", ["Linie Aquavit", "Krogstad"], (40.0, 40.0),
             profile(sweetness=.1, bitterness=.1, citrus=.1, floral=.1, spice=.5, herbal=.6)),
            ("cachaca", "Cachaça", ["Leblon", "Sagatiba"], (38.0, 40.0),
             profile(sweetness=.2, citrus=.1, floral=.1, spice=.1, fruity=.4)),
        ]),
    ]),
    ("liqueur", "Liqueur", [
        ("orange_liqueur", "Orange", [
            ("triple_sec", "Orange Triple Sec", ["Cointreau", "Combier"], (30.0, 40.0),
             profile(sweetness=.8, citrus=.8, floral=.1, fruity=.3)),
            ("orange_curacao", "Orange Curaçao", ["Grand Marnier"], (40.0, 40.0),
             profile(sweetness=.7, bitterness=.1, citrus=.7, floral=.1, spice=.1, fruity=.3, oaky=.2)),
        ]),
        ("coffee_liqueur_family", "Coffee", [
            ("coffee_liqueur", "Coffee Liqueur", ["Kahlúa", "Mr. Black"], (20.0, 26.0),
             profile(sweetness=.7, bitterness=.3, spice=.1, oaky=.1)),
        ]),
        ("almond_liqueur_family", "Almond", [
            ("amaretto", "Amaretto", ["Disaronno", "Lazzaroni"], (24.0, 28.0),
             profile(sweetness=.8, bitterness=.1, floral=.1, spice=.1, fruity=.2)),
            ("creme_de_noyaux", "Crème de Noyaux", ["Tempus Fugit Crème de Noyaux", "Bols Crème de Noyaux"], (20.0, 30.0),
             profile(sweetness=.8, bitterness=.1, floral=.1, spice=.1, fruity=.3)),
        ]),
        ("herbal_liqueur_family", "Herbal", [
            ("chartreuse_green", "Green Chartreuse", ["Chartreuse Verte"], (55.0, 55.0),
             profile(sweetness=.4, bitterness=.3, citrus=.1, floral=.3, spice=.2, herbal=.9)),
            ("benedictine", "Bénédictine", ["Bénédictine D.O.M."], (40.0, 40.0),
             profile(sweetness=.6, bitterness=.1, citrus=.1, floral=.3, spice=.3, herbal=.6, fruity=.1, oaky=.1)),
            ("chartreuse_yellow", "Yellow Chartreuse", ["Chartreuse Jaune"], (40.0, 43.0),
             profile(sweetness=.6, bitterness=.1, citrus=.1, floral=.4, spice=.2, herbal=.7)),
            ("galliano", "Galliano", ["Galliano L'Autentico"], (30.0, 42.3),
             profile(sweetness=.7, citrus=.1, floral=.2, spice=.3, herbal=.6)),
            ("drambuie", "Drambuie", ["Drambuie"], (40.0, 40.0),
             profile(sweetness=.7, smokiness=.1, floral=.2, spice=.3, herbal=.4, oaky=.3)),
        ]),
        ("berry_liqueur_family", "Berry/Fruit", [
            ("chambord", "Raspberry Liqueur", ["Chambord"], (16.5, 16.5),
             profile(sweetness=.8, floral=.1, fruity=.8)),
            ("peach_schnapps", "Peach Schnapps", ["DeKuyper Peachtree"], (15.0, 20.0),
             profile(sweetness=.8, floral=.2, fruity=.7)),
            ("creme_de_cassis", "Crème de Cassis", ["Lejay", "Giffard Cassis Noir de Bourgogne"], (15.0, 20.0),
             profile(sweetness=.8, bitterness=.1, floral=.1, fruity=.9)),
            ("cherry_liqueur", "Cherry Liqueur", ["Cherry Heering", "Luxardo Sangue Morlacco"], (24.0, 30.0),
             profile(sweetness=.8, bitterness=.1, spice=.2, fruity=.8, oaky=.1)),
            ("creme_de_mure", "Blackberry Liqueur", ["Giffard Crème de Mûre", "Merlet Crème de Mûre"], (16.0, 18.0),
             profile(sweetness=.8, bitterness=.1, floral=.1, fruity=.8)),
            ("sloe_gin", "Sloe Gin", ["Plymouth Sloe Gin", "Hayman's Sloe Gin"], (26.0, 29.0),
             profile(sweetness=.6, bitterness=.2, citrus=.1, floral=.1, herbal=.2, fruity=.7)),
        ]),
        ("maraschino_liqueur_family", "Maraschino", [
            ("maraschino", "Maraschino Liqueur", ["Luxardo Maraschino", "Maraska"], (32.0, 32.0),
             profile(sweetness=.6, bitterness=.1, floral=.5, herbal=.2, fruity=.5)),
        ]),
        ("floral_liqueur_family", "Floral", [
            ("creme_de_violette", "Crème de Violette", ["Rothman & Winter", "Giffard Violette"], (16.0, 20.0),
             profile(sweetness=.7, floral=.9, fruity=.2)),
            ("elderflower_liqueur", "Elderflower Liqueur", ["St-Germain", "Fiorente"], (20.0, 20.0),
             profile(sweetness=.7, citrus=.2, floral=.8, fruity=.4)),
        ]),
        ("mint_liqueur_family", "Mint", [
            ("creme_de_menthe", "Crème de Menthe", ["Tempus Fugit Crème de Menthe", "Giffard Menthe-Pastille"], (24.0, 28.0),
             profile(sweetness=.8, spice=.1, herbal=.9)),
        ]),
        ("chocolate_liqueur_family", "Chocolate", [
            ("creme_de_cacao", "Crème de Cacao", ["Tempus Fugit Crème de Cacao", "Giffard Crème de Cacao"], (20.0, 25.0),
             profile(sweetness=.8, bitterness=.2, spice=.1, oaky=.1)),
        ]),
        ("cream_liqueur_family", "Cream", [
            ("irish_cream", "Irish Cream", ["Baileys"], (17.0, 17.0),
             profile(sweetness=.7, bitterness=.1, spice=.1, oaky=.1)),
        ]),
        ("nut_liqueur_family", "Nut", [
            ("hazelnut_liqueur", "Hazelnut Liqueur", ["Frangelico"], (20.0, 24.0),
             profile(sweetness=.8, bitterness=.1, floral=.1, fruity=.1, oaky=.1)),
        ]),
        ("anise_liqueur_family", "Anise", [
            ("sambuca", "Sambuca", ["Luxardo Sambuca"], (38.0, 42.0),
             profile(sweetness=.8, bitterness=.1, floral=.1, spice=.1, herbal=.5)),
        ]),
        ("amaro_aperitif_family", "Amaro/Aperitif", [
            ("campari_style", "Bitter Aperitif", ["Campari"], (20.0, 28.5),
             profile(sweetness=.3, bitterness=.9, citrus=.3, floral=.1, spice=.1, herbal=.4, fruity=.2)),
            ("aperol_style", "Bitter Aperitivo", ["Aperol"], (11.0, 11.0),
             profile(sweetness=.5, bitterness=.5, citrus=.5, floral=.2, spice=.1, herbal=.3, fruity=.3)),
            ("amaro_light", "Light Amaro", ["Amaro Nonino Quintessentia", "Amaro Montenegro", "Amaro Meletti"], (23.0, 35.0),
             profile(sweetness=.5, bitterness=.5, citrus=.3, floral=.2, spice=.3, herbal=.5, fruity=.2, oaky=.2)),
            ("amaro_dark", "Dark Amaro", ["Averna", "Ramazzotti"], (29.0, 32.0),
             profile(sweetness=.6, bitterness=.7, citrus=.2, spice=.3, herbal=.5, fruity=.1, oaky=.2)),
            ("cynar", "Cynar", ["Cynar"], (16.5, 16.5),
             profile(sweetness=.4, bitterness=.7, citrus=.1, spice=.1, herbal=.6)),
        ]),
    ]),
    ("wine_fortified", "Wine & Fortified", [
        ("vermouth", "Vermouth", [
            ("vermouth_dry", "Dry Vermouth", ["Dolin Dry", "Noilly Prat"], (15.0, 18.0),
             profile(sweetness=.2, bitterness=.3, citrus=.1, floral=.3, spice=.1, herbal=.6, fruity=.1)),
            ("vermouth_sweet", "Sweet/Rosso Vermouth", ["Carpano Antica", "Cocchi Storico"], (15.0, 18.0),
             profile(sweetness=.6, bitterness=.3, citrus=.1, floral=.2, spice=.2, herbal=.5, fruity=.3, oaky=.1)),
            ("vermouth_blanc", "Blanc Vermouth", ["Dolin Blanc"], (16.0, 18.0),
             profile(sweetness=.5, bitterness=.2, citrus=.1, floral=.4, spice=.1, herbal=.4, fruity=.2)),
            ("aperitif_wine_blanc", "Blanc Aperitif Wine", ["Lillet Blanc", "Cocchi Americano"], (16.5, 17.0),
             profile(sweetness=.5, bitterness=.3, citrus=.4, floral=.3, herbal=.2, fruity=.4)),
        ]),
        ("still_wine", "Still Wine", [
            ("red_wine", "Red Wine", ["Any dry red", "Côtes du Rhône"], (12.0, 14.5),
             profile(sweetness=.2, bitterness=.2, floral=.1, spice=.1, fruity=.7, oaky=.3)),
        ]),
        ("sparkling", "Sparkling", [
            ("champagne", "Champagne/Sparkling Wine", ["Veuve Clicquot", "Moët"], (12.0, 12.0),
             profile(sweetness=.2, bitterness=.1, citrus=.2, floral=.2, fruity=.3, oaky=.1)),
            ("prosecco", "Prosecco", ["La Marca", "Mionetto"], (11.0, 11.0),
             profile(sweetness=.3, citrus=.2, floral=.2, fruity=.4)),
        ]),
        ("fortified", "Fortified", [
            ("sherry_fino", "Fino Sherry", ["Tio Pepe"], (15.0, 15.0),
             profile(sweetness=.1, bitterness=.2, citrus=.2, floral=.1, herbal=.3, fruity=.1, oaky=.1)),
            ("sherry_oloroso", "Oloroso Sherry", ["Lustau Oloroso"], (18.0, 20.0),
             profile(sweetness=.4, bitterness=.1, floral=.1, spice=.2, herbal=.1, fruity=.4, oaky=.5)),
            ("port_ruby", "Ruby Port", ["Graham's Six Grapes"], (19.0, 20.0),
             profile(sweetness=.8, bitterness=.1, floral=.1, spice=.2, fruity=.7, oaky=.2)),
            ("port_tawny", "Tawny Port", ["Taylor's Tawny"], (19.0, 20.0),
             profile(sweetness=.7, bitterness=.1, floral=.1, spice=.2, fruity=.5, oaky=.5)),
        ]),
    ]),
    ("mixer", "Mixer", [
        ("carbonated", "Carbonated", [
            ("club_soda", "Club Soda", ["San Pellegrino", "Schweppes Soda"], (0.0, 0.0), profile()),
            ("tonic_water", "Tonic Water", ["Fever-Tree", "Schweppes Tonic"], (0.0, 0.0),
             profile(sweetness=.3, bitterness=.5, citrus=.2, herbal=.1)),
            ("ginger_beer", "Ginger Beer", ["Fever-Tree Ginger Beer", "Bundaberg"], (0.0, 0.0),
             profile(sweetness=.4, citrus=.1, spice=.7, fruity=.1)),
            ("ginger_ale", "Ginger Ale", ["Canada Dry", "Fever-Tree Ginger Ale"], (0.0, 0.0),
             profile(sweetness=.5, citrus=.1, spice=.4, fruity=.1)),
            ("cola", "Cola", ["Coca-Cola", "Pepsi"], (0.0, 0.0),
             profile(sweetness=.8, bitterness=.1, spice=.2, herbal=.1, fruity=.1)),
            ("lemon_lime_soda", "Lemon-Lime Soda", ["Sprite", "7UP"], (0.0, 0.0),
             profile(sweetness=.7, citrus=.5, fruity=.1)),
        ]),
        ("juice", "Juice", [
            ("lime_juice", "Lime Juice", ["Freshly squeezed"], (0.0, 0.0),
             profile(sweetness=.1, bitterness=.1, citrus=.9, fruity=.2)),
            ("lemon_juice", "Lemon Juice", ["Freshly squeezed"], (0.0, 0.0),
             profile(sweetness=.1, bitterness=.1, citrus=.9, fruity=.2)),
            ("orange_juice", "Orange Juice", ["Freshly squeezed"], (0.0, 0.0),
             profile(sweetness=.5, citrus=.7, floral=.1, fruity=.5)),
            ("grapefruit_juice", "Grapefruit Juice", ["Freshly squeezed"], (0.0, 0.0),
             profile(sweetness=.3, bitterness=.3, citrus=.8, fruity=.3)),
            ("pineapple_juice", "Pineapple Juice", ["Dole", "Freshly pressed"], (0.0, 0.0),
             profile(sweetness=.6, citrus=.2, floral=.1, fruity=.7)),
            ("cranberry_juice", "Cranberry Juice", ["Ocean Spray"], (0.0, 0.0),
             profile(sweetness=.3, bitterness=.2, citrus=.3, fruity=.5)),
            ("tomato_juice", "Tomato Juice", ["Campbell's"], (0.0, 0.0),
             profile(sweetness=.2, bitterness=.1, citrus=.1, spice=.1, herbal=.1, fruity=.2)),
        ]),
        ("dairy_cream", "Dairy & Cream", [
            ("heavy_cream", "Heavy Cream", ["Any"], (0.0, 0.0), profile(sweetness=.2)),
            ("egg_white", "Egg White", ["Fresh egg"], (0.0, 0.0), profile()),
            ("coconut_cream", "Coconut Cream", ["Coco Lopez", "Coco Reàl"], (0.0, 0.0),
             profile(sweetness=.6, fruity=.3)),
            ("butter", "Butter", ["Unsalted"], (0.0, 0.0), profile(sweetness=.1)),
        ]),
        ("other_mixer", "Other", [
            ("cold_brew", "Cold Brew Coffee", ["Any"], (0.0, 0.0),
             profile(sweetness=.1, bitterness=.5, smokiness=.1)),
            ("espresso", "Espresso", ["Freshly pulled"], (0.0, 0.0),
             profile(sweetness=.1, bitterness=.7, smokiness=.2)),
            ("hot_coffee", "Hot Coffee", ["Freshly brewed"], (0.0, 0.0),
             profile(sweetness=.1, bitterness=.5, smokiness=.1)),
        ]),
        ("tea", "Tea", [
            ("black_tea", "Black Tea", ["Any (brewed)"], (0.0, 0.0),
             profile(bitterness=.3, floral=.2, herbal=.2, oaky=.1)),
        ]),
        ("beer", "Beer", [
            ("stout", "Stout", ["Guinness"], (4.2, 7.5),
             profile(sweetness=.2, bitterness=.5, smokiness=.3, oaky=.2)),
        ]),
    ]),
    ("syrup", "Syrup", [
        ("syrup", "Syrup", [
            ("simple_syrup", "Simple Syrup", ["House-made 1:1"], (0.0, 0.0), profile(sweetness=1.0)),
            ("grenadine", "Grenadine", ["Small Hand Foods", "House-made"], (0.0, 0.0),
             profile(sweetness=.9, floral=.2, fruity=.6)),
            ("orgeat", "Orgeat", ["BG Reynolds", "House-made"], (0.0, 0.0),
             profile(sweetness=.8, floral=.3, fruity=.1)),
            ("honey_syrup", "Honey Syrup", ["House-made 1:1"], (0.0, 0.0), profile(sweetness=.9, floral=.3)),
            ("demerara_syrup", "Demerara Syrup", ["House-made"], (0.0, 0.0),
             profile(sweetness=.9, spice=.1, oaky=.2)),
            ("falernum", "Falernum", ["John D. Taylor's", "House-made"], (0.0, 0.0),
             profile(sweetness=.8, citrus=.3, floral=.1, spice=.4, herbal=.1, fruity=.2)),
            ("passion_fruit_syrup", "Passion Fruit Syrup", ["House-made"], (0.0, 0.0),
             profile(sweetness=.8, citrus=.1, floral=.2, fruity=.8)),
            ("ginger_syrup", "Ginger Syrup", ["House-made"], (0.0, 0.0),
             profile(sweetness=.8, citrus=.1, spice=.7)),
            ("raspberry_syrup", "Raspberry Syrup", ["Small Hand Foods", "House-made"], (0.0, 0.0),
             profile(sweetness=.9, floral=.1, fruity=.7)),
        ]),
    ]),
    ("fruit", "Fruit", [
        ("citrus_fresh", "Citrus", [
            ("fresh_lime", "Fresh Lime", ["Any"], (0.0, 0.0), profile(sweetness=.1, bitterness=.1, citrus=.9, fruity=.2)),
            ("fresh_lemon", "Fresh Lemon", ["Any"], (0.0, 0.0), profile(sweetness=.1, bitterness=.1, citrus=.9, fruity=.2)),
            ("fresh_orange", "Fresh Orange", ["Any"], (0.0, 0.0), profile(sweetness=.5, citrus=.6, floral=.1, fruity=.5)),
            ("fresh_grapefruit", "Fresh Grapefruit", ["Any"], (0.0, 0.0), profile(sweetness=.3, bitterness=.3, citrus=.8, fruity=.3)),
        ]),
        ("tropical_fresh", "Tropical", [
            ("fresh_pineapple", "Fresh Pineapple", ["Any"], (0.0, 0.0), profile(sweetness=.6, citrus=.2, floral=.1, fruity=.7)),
            ("fresh_mango", "Fresh Mango", ["Any"], (0.0, 0.0), profile(sweetness=.7, floral=.2, fruity=.8)),
            ("fresh_passion_fruit", "Fresh Passion Fruit", ["Any"], (0.0, 0.0), profile(sweetness=.5, bitterness=.1, citrus=.2, floral=.3, fruity=.8)),
        ]),
        ("berry_fresh", "Berry", [
            ("fresh_strawberry", "Fresh Strawberry", ["Any"], (0.0, 0.0), profile(sweetness=.6, floral=.1, fruity=.7)),
            ("fresh_raspberry", "Fresh Raspberry", ["Any"], (0.0, 0.0), profile(sweetness=.4, bitterness=.1, floral=.1, fruity=.7)),
        ]),
        ("stone_fruit_fresh", "Stone Fruit", [
            ("fresh_peach", "Fresh Peach", ["Any"], (0.0, 0.0), profile(sweetness=.6, floral=.2, fruity=.7)),
            ("fresh_cherry", "Fresh Cherry", ["Any", "Luxardo Maraschino Cherry"], (0.0, 0.0), profile(sweetness=.5, bitterness=.1, floral=.1, fruity=.7)),
        ]),
        ("other_fresh", "Other", [
            ("cucumber", "Cucumber", ["Any"], (0.0, 0.0), profile(sweetness=.1, floral=.1, herbal=.3, fruity=.1)),
            ("fresh_apple", "Fresh Apple", ["Any"], (0.0, 0.0), profile(sweetness=.4, citrus=.1, floral=.1, fruity=.6)),
        ]),
        ("herbs_fresh", "Herbs", [
            ("fresh_mint", "Fresh Mint", ["Any"], (0.0, 0.0), profile(bitterness=.1, floral=.1, spice=.1, herbal=.9)),
            ("fresh_basil", "Fresh Basil", ["Any"], (0.0, 0.0), profile(bitterness=.1, floral=.2, spice=.1, herbal=.8)),
            ("fresh_rosemary", "Fresh Rosemary", ["Any"], (0.0, 0.0), profile(bitterness=.1, floral=.1, spice=.2, herbal=.9)),
        ]),
    ]),
    ("garnish", "Garnish", [
        ("citrus_garnish", "Citrus", [
            ("lime_wedge", "Lime Wedge", ["Any"], (0.0, 0.0), profile(bitterness=.1, citrus=.6, fruity=.1)),
            ("lemon_twist", "Lemon Twist", ["Any"], (0.0, 0.0), profile(bitterness=.1, citrus=.5, floral=.2)),
            ("orange_wheel", "Orange Wheel", ["Any"], (0.0, 0.0), profile(sweetness=.2, citrus=.4, floral=.1, fruity=.3)),
            ("orange_twist", "Orange Twist", ["Any"], (0.0, 0.0), profile(bitterness=.1, citrus=.5, floral=.2, fruity=.1)),
        ]),
        ("savory_garnish", "Savory", [
            ("olive", "Olive", ["Castelvetrano", "Cocktail Olive"], (0.0, 0.0), profile(bitterness=.3, herbal=.1)),
            ("cocktail_onion", "Cocktail Onion", ["Any"], (0.0, 0.0), profile(bitterness=.1, spice=.2, herbal=.1)),
            ("worcestershire", "Worcestershire Sauce", ["Lea & Perrins"], (0.0, 0.0),
             profile(sweetness=.2, smokiness=.1, spice=.5, herbal=.2, fruity=.1)),
            ("hot_sauce", "Hot Sauce", ["Tabasco", "Cholula"], (0.0, 0.0), profile(citrus=.1, spice=.9)),
        ]),
        ("spice_garnish", "Spice", [
            ("cinnamon_stick", "Cinnamon Stick", ["Any"], (0.0, 0.0), profile(sweetness=.2, spice=.8, herbal=.1)),
        ]),
        ("salt_sugar_garnish", "Salt & Sugar", [
            ("salt_rim", "Kosher Salt Rim", ["Any"], (0.0, 0.0), profile(spice=.1)),
            ("sugar_rim", "Sugar Rim", ["Any"], (0.0, 0.0), profile(sweetness=.9)),
            ("celery_salt", "Celery Salt", ["Any"], (0.0, 0.0), profile(spice=.2, herbal=.3)),
        ]),
        ("bitters_garnish", "Bitters", [
            ("angostura_bitters", "Angostura Bitters", ["Angostura"], (44.7, 44.7),
             profile(sweetness=.1, bitterness=.8, spice=.4, herbal=.3, oaky=.1)),
            ("peychauds_bitters", "Peychaud's Bitters", ["Peychaud's"], (35.0, 35.0),
             profile(sweetness=.1, bitterness=.7, citrus=.1, floral=.3, spice=.3, herbal=.2, fruity=.1)),
            ("orange_bitters", "Orange Bitters", ["Regans' No. 6", "Angostura Orange"], (28.0, 28.0),
             profile(sweetness=.1, bitterness=.6, citrus=.6, floral=.2, spice=.1, herbal=.1, fruity=.1)),
        ]),
    ]),
]

# ---------------------------------------------------------------------------
# Recipes: (name, description, glass, method, difficulty, tags, steps, ingredients)
# ingredients: (slug, amount, prep, optional, substituteNotes)
# ---------------------------------------------------------------------------


def ing(slug, amount, prep=None, optional=False, sub=None):
    return (slug, amount, prep, optional, sub)


RECIPES = [
    # ---------------- Gin ----------------
    ("Martini", "The classic dry, spirit-forward stirred cocktail.", "martini", "stir", "medium",
     ["classic", "spirit-forward", "iba-official"],
     ["Stir gin and vermouth with ice until well-chilled.", "Strain into a chilled martini glass.", "Garnish with a lemon twist or olive."],
     [ing("gin_london_dry", "60ml"), ing("vermouth_dry", "10ml"), ing("lemon_twist", "1", optional=True), ing("olive", "1", optional=True)]),
    ("Vesper", "James Bond's gin-and-vodka martini variant.", "martini", "stir", "medium",
     ["classic", "spirit-forward"],
     ["Stir all spirits with ice until well-chilled.", "Strain into a chilled martini glass.", "Garnish with a lemon twist."],
     [ing("gin_london_dry", "45ml"), ing("vodka_neutral", "15ml"), ing("aperitif_wine_blanc", "7.5ml", sub="Fleming specified Kina Lillet; Cocchi Americano is closest to its original bitterness."), ing("lemon_twist", "1")]),
    ("Negroni", "Equal parts gin, vermouth, and bitter aperitif.", "rocks", "build", "easy",
     ["classic", "bitter", "iba-official"],
     ["Build all ingredients over ice in a rocks glass.", "Stir briefly.", "Garnish with an orange wheel."],
     [ing("gin_london_dry", "30ml"), ing("vermouth_sweet", "30ml"), ing("campari_style", "30ml"), ing("orange_wheel", "1")]),
    ("Tom Collins", "A tall, refreshing gin and lemon fizz.", "collins", "shake", "easy",
     ["classic", "tall", "refreshing", "iba-official"],
     ["Shake gin, lemon juice, and simple syrup with ice.", "Strain into a collins glass over fresh ice.", "Top with club soda.", "Garnish with a lemon twist."],
     [ing("gin_london_dry", "45ml"), ing("lemon_juice", "22ml"), ing("simple_syrup", "15ml"), ing("club_soda", "top"), ing("lemon_twist", "1")]),
    ("Gimlet", "Gin and lime cordial, shaken sharp and cold.", "coupe", "shake", "easy",
     ["classic", "sour", "iba-official"],
     ["Shake gin, lime juice, and simple syrup hard with ice.", "Double strain into a chilled coupe."],
     [ing("gin_contemporary", "60ml"), ing("lime_juice", "22ml"), ing("simple_syrup", "15ml")]),
    ("Bee's Knees", "Prohibition-era gin sour sweetened with honey.", "coupe", "shake", "easy",
     ["classic", "sour", "prohibition"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe.", "Garnish with a lemon twist."],
     [ing("gin_london_dry", "60ml"), ing("lemon_juice", "22ml"), ing("honey_syrup", "20ml"), ing("lemon_twist", "1", optional=True)]),
    ("Aviation", "Gin, maraschino, and crème de violette with a floral lift.", "coupe", "shake", "medium",
     ["classic", "sour"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe.", "Garnish with a cherry."],
     [ing("gin_london_dry", "45ml"), ing("maraschino", "15ml"), ing("creme_de_violette", "5ml"), ing("lemon_juice", "15ml"), ing("fresh_cherry", "1")]),
    ("French 75", "Gin and lemon topped with Champagne.", "flute", "shake", "easy",
     ["classic", "sparkling", "iba-official"],
     ["Shake gin, lemon juice, and simple syrup with ice.", "Strain into a flute.", "Top with Champagne.", "Garnish with a lemon twist."],
     [ing("gin_london_dry", "30ml"), ing("lemon_juice", "15ml"), ing("simple_syrup", "10ml"), ing("champagne", "top"), ing("lemon_twist", "1", optional=True)]),
    ("Gin Fizz", "A frothy gin sour lengthened with soda.", "highball", "shake", "medium",
     ["classic", "tall", "refreshing"],
     ["Dry shake gin, lemon juice, simple syrup, and egg white without ice.", "Shake again with ice.", "Strain into a highball glass.", "Top with club soda."],
     [ing("gin_london_dry", "45ml"), ing("lemon_juice", "22ml"), ing("simple_syrup", "15ml"), ing("egg_white", "15ml"), ing("club_soda", "top")]),
    ("Last Word", "An even-parts Prohibition classic of gin, Chartreuse, maraschino, and lime.", "coupe", "shake", "medium",
     ["classic", "even-parts", "prohibition"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("gin_london_dry", "22ml"), ing("chartreuse_green", "22ml"), ing("maraschino", "22ml"), ing("lime_juice", "22ml")]),
    ("Clover Club", "A pre-Prohibition gin sour with raspberry and egg white.", "coupe", "shake", "medium",
     ["classic", "sour", "prohibition"],
     ["Dry shake all ingredients without ice.", "Shake again with ice.", "Double strain into a chilled coupe.", "Garnish with a raspberry."],
     [ing("gin_london_dry", "45ml"), ing("lemon_juice", "15ml"), ing("raspberry_syrup", "15ml"), ing("egg_white", "15ml"), ing("fresh_raspberry", "1", optional=True)]),
    ("Bramble", "Modern gin classic drizzled with blackberry liqueur.", "rocks", "build", "easy",
     ["modern-classic", "sour"],
     ["Shake gin, lemon juice, and simple syrup with ice.", "Strain over crushed ice in a rocks glass.", "Drizzle crème de mûre over the top.", "Garnish with a lemon slice and a blackberry."],
     [ing("gin_london_dry", "50ml"), ing("lemon_juice", "25ml"), ing("simple_syrup", "12.5ml"), ing("creme_de_mure", "15ml", prep="drizzled"), ing("fresh_lemon", "1", prep="slice", optional=True)]),
    ("White Lady", "A gin sidecar variant with orange liqueur and lemon.", "coupe", "shake", "medium",
     ["classic", "sour"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("gin_london_dry", "45ml"), ing("triple_sec", "22ml"), ing("lemon_juice", "22ml")]),
    ("Singapore Sling", "A tall, fruity gin cocktail from Raffles Hotel.", "hurricane", "shake", "medium",
     ["classic", "tropical", "iba-official"],
     ["Shake gin, cherry liqueur, Cointreau, Bénédictine, pineapple juice, lime juice, grenadine, and bitters with ice.", "Strain into a hurricane glass over ice.", "Top with a splash of club soda.", "Garnish with a pineapple wedge and a cherry."],
     [ing("gin_london_dry", "30ml"), ing("cherry_liqueur", "15ml"), ing("triple_sec", "7.5ml"), ing("benedictine", "7.5ml"), ing("pineapple_juice", "120ml"), ing("lime_juice", "15ml"), ing("grenadine", "10ml"), ing("angostura_bitters", "1 dash"), ing("club_soda", "top", optional=True)]),
    ("Corpse Reviver No. 2", "A bracing pre-Prohibition equal-parts sour.", "coupe", "shake", "medium",
     ["classic", "even-parts"],
     ["Shake all liquid ingredients with ice.", "Double strain into a chilled coupe rinsed with absinthe."],
     [ing("gin_london_dry", "22ml"), ing("triple_sec", "22ml"), ing("aperitif_wine_blanc", "22ml"), ing("lemon_juice", "22ml"), ing("absinthe", "1 dash", prep="rinse")]),
    ("Southside", "A minty gin sour, a Prohibition-era favourite.", "coupe", "shake", "easy",
     ["classic", "sour", "herbal"],
     ["Muddle mint gently in a shaker.", "Add remaining ingredients and shake with ice.", "Double strain into a chilled coupe.", "Garnish with a mint sprig."],
     [ing("gin_london_dry", "60ml"), ing("lime_juice", "22ml"), ing("simple_syrup", "15ml"), ing("fresh_mint", "8 leaves", prep="muddled")]),
    ("Gin Rickey", "A bone-dry gin and lime highball.", "highball", "build", "easy",
     ["classic", "tall", "refreshing"],
     ["Build gin and lime juice over ice in a highball glass.", "Top with club soda.", "Garnish with a lime wedge."],
     [ing("gin_london_dry", "45ml"), ing("lime_juice", "15ml"), ing("club_soda", "top"), ing("lime_wedge", "1")]),
    ("Martinez", "A sweeter, Old Tom-based precursor to the Martini.", "coupe", "stir", "medium",
     ["classic", "spirit-forward"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe.", "Garnish with an orange twist."],
     [ing("gin_old_tom", "45ml"), ing("vermouth_sweet", "45ml"), ing("maraschino", "5ml"), ing("angostura_bitters", "2 dash"), ing("orange_twist", "1")]),
    ("Alaska", "A Martini variant sweetened with yellow Chartreuse.", "coupe", "stir", "medium",
     ["classic", "spirit-forward"],
     ["Stir gin, Chartreuse, and bitters with ice.", "Strain into a chilled coupe.", "Garnish with a lemon twist."],
     [ing("gin_london_dry", "60ml"), ing("chartreuse_yellow", "15ml"), ing("orange_bitters", "2 dash"), ing("lemon_twist", "1")]),
    ("Pegu Club", "A Burmese-colonial gin sour with orange liqueur and bitters.", "coupe", "shake", "medium",
     ["classic", "sour"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("gin_london_dry", "45ml"), ing("triple_sec", "22ml"), ing("lime_juice", "15ml"), ing("angostura_bitters", "1 dash"), ing("orange_bitters", "1 dash")]),
    ("Gin Basil Smash", "A muddled, herbaceous modern gin classic.", "rocks", "shake", "easy",
     ["modern-classic", "herbal", "refreshing"],
     ["Muddle basil with simple syrup in a shaker.", "Add gin and lemon juice, shake with ice.", "Double strain over fresh ice in a rocks glass.", "Garnish with a basil sprig."],
     [ing("gin_contemporary", "60ml"), ing("lemon_juice", "30ml"), ing("simple_syrup", "20ml"), ing("fresh_basil", "15 leaves", prep="muddled")]),
    ("Tuxedo", "An elegant, dry Martini-adjacent classic with maraschino and absinthe.", "coupe", "stir", "medium",
     ["classic", "spirit-forward"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe.", "Garnish with a lemon twist and a cherry."],
     [ing("gin_london_dry", "45ml"), ing("vermouth_dry", "45ml"), ing("maraschino", "5ml"), ing("absinthe", "1 dash"), ing("orange_bitters", "2 dash"), ing("lemon_twist", "1")]),

    # ---------------- Whiskey ----------------
    ("Old Fashioned", "The archetypal spirit-forward whiskey cocktail.", "rocks", "build", "easy",
     ["classic", "spirit-forward", "iba-official"],
     ["Stir demerara syrup and bitters in a rocks glass.", "Add bourbon and a large ice cube.", "Stir until chilled.", "Express an orange twist over the glass and drop it in."],
     [ing("whiskey_bourbon", "60ml"), ing("demerara_syrup", "7.5ml"), ing("angostura_bitters", "2 dash"), ing("orange_twist", "1")]),
    ("Manhattan", "Whiskey and sweet vermouth, stirred with bitters.", "coupe", "stir", "easy",
     ["classic", "spirit-forward", "iba-official"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe.", "Garnish with a cherry."],
     [ing("whiskey_rye", "60ml"), ing("vermouth_sweet", "30ml"), ing("angostura_bitters", "2 dash"), ing("fresh_cherry", "1")]),
    ("Whiskey Sour", "Bourbon shaken with lemon and sugar.", "rocks", "shake", "easy",
     ["classic", "sour", "iba-official"],
     ["Shake bourbon, lemon juice, and simple syrup with ice.", "Strain over fresh ice in a rocks glass.", "Garnish with an orange wheel and cherry."],
     [ing("whiskey_bourbon", "60ml"), ing("lemon_juice", "22ml"), ing("simple_syrup", "15ml"), ing("orange_wheel", "1", optional=True), ing("fresh_cherry", "1", optional=True)]),
    ("Mint Julep", "Crushed-ice bourbon classic from the American South.", "rocks", "build", "easy",
     ["classic", "herbal", "iba-official"],
     ["Muddle mint with simple syrup in a julep tin or rocks glass.", "Add bourbon and pack with crushed ice.", "Stir until frosted.", "Garnish with a mint sprig."],
     [ing("whiskey_bourbon", "60ml"), ing("demerara_syrup", "10ml"), ing("fresh_mint", "10 leaves", prep="muddled")]),
    ("Paper Plane", "An even-parts modern classic balancing bourbon, Aperol, amaro, and lemon.", "coupe", "shake", "medium",
     ["modern-classic", "even-parts"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("whiskey_bourbon", "22ml"), ing("aperol_style", "22ml"), ing("amaro_light", "22ml", sub="Amaro Nonino is the original; Montenegro is the usual stand-in."), ing("lemon_juice", "22ml")]),
    ("Sazerac", "New Orleans' rye and absinthe classic.", "rocks", "stir", "medium",
     ["classic", "spirit-forward", "iba-official"],
     ["Rinse a chilled rocks glass with absinthe and discard excess.", "Stir rye, simple syrup, and bitters with ice in a separate glass.", "Strain into the prepared glass (no ice).", "Garnish with a lemon twist."],
     [ing("whiskey_rye", "60ml"), ing("simple_syrup", "5ml"), ing("peychauds_bitters", "3 dash"), ing("absinthe", "1 dash", prep="rinse"), ing("lemon_twist", "1")]),
    ("Boulevardier", "A whiskey Negroni variant.", "rocks", "stir", "easy",
     ["classic", "bitter", "spirit-forward"],
     ["Stir all ingredients with ice.", "Strain over fresh ice in a rocks glass.", "Garnish with an orange twist."],
     [ing("whiskey_bourbon", "30ml"), ing("vermouth_sweet", "30ml"), ing("campari_style", "30ml"), ing("orange_twist", "1")]),
    ("Whiskey Smash", "A muddled bourbon and lemon refresher.", "rocks", "shake", "easy",
     ["modern-classic", "refreshing", "herbal"],
     ["Muddle lemon and mint with simple syrup in a shaker.", "Add bourbon, shake with ice.", "Double strain over fresh ice in a rocks glass.", "Garnish with a mint sprig."],
     [ing("whiskey_bourbon", "60ml"), ing("fresh_lemon", "3", prep="wedges, muddled"), ing("simple_syrup", "15ml"), ing("fresh_mint", "8 leaves", prep="muddled")]),
    ("Irish Coffee", "Hot coffee, whiskey, and cream.", "mug", "build", "easy",
     ["warm", "classic"],
     ["Warm the glass with hot water, then discard.", "Stir Irish whiskey and demerara syrup into hot coffee.", "Gently float lightly whipped cream on top."],
     [ing("whiskey_irish", "40ml"), ing("hot_coffee", "120ml"), ing("demerara_syrup", "15ml"), ing("heavy_cream", "30ml", prep="lightly whipped")]),
    ("Hot Toddy", "A warming whiskey, honey, and lemon drink.", "mug", "build", "easy",
     ["warm", "classic"],
     ["Combine whiskey, honey syrup, and lemon juice in a warmed mug.", "Top with hot water.", "Garnish with a lemon wheel and cinnamon stick."],
     [ing("whiskey_bourbon", "45ml"), ing("honey_syrup", "15ml"), ing("lemon_juice", "15ml"), ing("cinnamon_stick", "1", optional=True)]),
    ("Rob Roy", "A Scotch-based Manhattan.", "coupe", "stir", "easy",
     ["classic", "spirit-forward"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe.", "Garnish with a cherry."],
     [ing("whiskey_scotch_blended", "60ml"), ing("vermouth_sweet", "30ml"), ing("angostura_bitters", "2 dash"), ing("fresh_cherry", "1")]),
    ("Blood and Sand", "An equal-parts Scotch cocktail with cherry, vermouth, and orange.", "coupe", "shake", "medium",
     ["classic", "even-parts"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe.", "Garnish with an orange twist."],
     [ing("whiskey_scotch_blended", "22ml"), ing("cherry_liqueur", "22ml"), ing("vermouth_sweet", "22ml"), ing("orange_juice", "22ml"), ing("orange_twist", "1", optional=True)]),
    ("Penicillin", "A modern classic layering smoky Scotch over honey-ginger whiskey.", "rocks", "shake", "medium",
     ["modern-classic", "smoky"],
     ["Shake blended Scotch, lemon juice, honey syrup, and ginger syrup with ice.", "Strain over fresh ice in a rocks glass.", "Float Islay Scotch on top.", "Garnish with a candied ginger piece."],
     [ing("whiskey_scotch_blended", "45ml"), ing("lemon_juice", "22ml"), ing("honey_syrup", "15ml"), ing("ginger_syrup", "10ml"), ing("whiskey_scotch_islay", "7.5ml", prep="float")]),
    ("Whiskey Highball", "Whiskey lengthened simply with soda over ice.", "highball", "build", "easy",
     ["classic", "tall", "refreshing"],
     ["Build whiskey over ice in a highball glass.", "Top with club soda and stir gently."],
     [ing("whiskey_scotch_blended", "45ml"), ing("club_soda", "top")]),
    ("Gold Rush", "A bourbon sour sweetened with honey.", "rocks", "shake", "easy",
     ["modern-classic", "sour"],
     ["Shake all ingredients with ice.", "Strain over fresh ice in a rocks glass."],
     [ing("whiskey_bourbon", "60ml"), ing("lemon_juice", "22ml"), ing("honey_syrup", "22ml")]),
    ("Vieux Carré", "A New Orleans stirred classic blending rye, cognac, and vermouth.", "rocks", "stir", "medium",
     ["classic", "spirit-forward"],
     ["Stir all ingredients with ice.", "Strain over fresh ice in a rocks glass.", "Garnish with a lemon twist."],
     [ing("whiskey_rye", "30ml"), ing("cognac_vs", "30ml"), ing("vermouth_sweet", "30ml"), ing("benedictine", "7.5ml"), ing("peychauds_bitters", "2 dash"), ing("angostura_bitters", "1 dash")]),
    ("New York Sour", "A Whiskey Sour topped with a red wine float.", "rocks", "shake", "medium",
     ["modern-classic", "sour"],
     ["Shake bourbon, lemon juice, and simple syrup with ice.", "Strain over fresh ice in a rocks glass.", "Float red wine on top over the back of a spoon."],
     [ing("whiskey_bourbon", "60ml"), ing("lemon_juice", "22ml"), ing("simple_syrup", "15ml"), ing("red_wine", "20ml", prep="float")]),
    ("Ward 8", "A Boston Prohibition-era whiskey sour with grenadine.", "coupe", "shake", "easy",
     ["classic", "sour"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("whiskey_rye", "60ml"), ing("lemon_juice", "15ml"), ing("orange_juice", "15ml"), ing("grenadine", "10ml")]),
    ("Algonquin", "A rye, dry vermouth, and pineapple cocktail.", "coupe", "shake", "medium",
     ["classic", "sour"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("whiskey_rye", "45ml"), ing("vermouth_dry", "22ml"), ing("pineapple_juice", "22ml")]),
    ("Brown Derby", "A grapefruit and honey bourbon sour.", "rocks", "shake", "easy",
     ["modern-classic", "sour"],
     ["Shake all ingredients with ice.", "Strain over fresh ice in a rocks glass."],
     [ing("whiskey_bourbon", "60ml"), ing("grapefruit_juice", "30ml"), ing("honey_syrup", "15ml")]),
    ("Kentucky Mule", "A bourbon riff on the Moscow Mule.", "highball", "build", "easy",
     ["modern-classic", "tall", "refreshing"],
     ["Build bourbon and lime juice over ice in a copper mug or highball.", "Top with ginger beer.", "Garnish with a lime wedge."],
     [ing("whiskey_bourbon", "45ml"), ing("lime_juice", "15ml"), ing("ginger_beer", "top"), ing("lime_wedge", "1")]),
    ("Perfect Manhattan", "A Manhattan split between sweet and dry vermouth.", "coupe", "stir", "easy",
     ["classic", "spirit-forward"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe.", "Garnish with a lemon twist."],
     [ing("whiskey_rye", "60ml"), ing("vermouth_sweet", "15ml"), ing("vermouth_dry", "15ml"), ing("angostura_bitters", "2 dash"), ing("lemon_twist", "1")]),

    # ---------------- Rum ----------------
    ("Daiquiri", "Rum, lime, and sugar in perfect balance.", "coupe", "shake", "easy",
     ["classic", "sour", "iba-official"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("rum_white", "60ml"), ing("lime_juice", "22ml"), ing("simple_syrup", "15ml")]),
    ("Mojito", "Rum, lime, mint, and soda over crushed ice.", "highball", "build", "easy",
     ["classic", "tall", "refreshing", "iba-official"],
     ["Muddle mint with simple syrup and lime juice in a highball glass.", "Add rum and fill with crushed ice.", "Top with club soda and stir.", "Garnish with a mint sprig."],
     [ing("rum_white", "60ml"), ing("lime_juice", "22ml"), ing("simple_syrup", "15ml"), ing("fresh_mint", "10 leaves", prep="muddled"), ing("club_soda", "top")]),
    ("Dark 'n' Stormy", "Dark rum and spicy ginger beer.", "highball", "build", "easy",
     ["classic", "tall", "refreshing"],
     ["Fill a highball glass with ice.", "Add ginger beer.", "Float dark rum on top.", "Garnish with a lime wedge."],
     [ing("rum_dark", "50ml", prep="float"), ing("ginger_beer", "top"), ing("lime_wedge", "1")]),
    ("Mai Tai", "A tiki classic layering aged rums with orgeat and lime.", "rocks", "shake", "medium",
     ["classic", "tiki", "iba-official"],
     ["Shake rums, orange liqueur, orgeat, and lime juice with ice.", "Strain over crushed ice in a rocks glass.", "Garnish with mint and a lime shell."],
     [ing("rum_agricole", "30ml"), ing("rum_gold", "30ml"), ing("orange_curacao", "15ml"), ing("orgeat", "15ml"), ing("lime_juice", "22ml"), ing("fresh_mint", "1 sprig", optional=True)]),
    ("Piña Colada", "Blended rum, pineapple, and coconut cream.", "hurricane", "blend", "easy",
     ["classic", "tropical", "iba-official"],
     ["Blend all ingredients with a cup of ice until smooth.", "Pour into a hurricane glass.", "Garnish with a pineapple wedge and cherry."],
     [ing("rum_white", "60ml"), ing("pineapple_juice", "90ml"), ing("coconut_cream", "30ml"), ing("fresh_pineapple", "1 wedge", optional=True)]),
    ("Hurricane", "A New Orleans tiki classic loaded with fruit.", "hurricane", "shake", "medium",
     ["classic", "tiki", "tropical"],
     ["Shake all ingredients with ice.", "Strain over fresh ice in a hurricane glass.", "Garnish with an orange wheel and cherry."],
     [ing("rum_white", "45ml"), ing("rum_dark", "45ml"), ing("passion_fruit_syrup", "30ml"), ing("orange_juice", "30ml"), ing("lime_juice", "15ml"), ing("grenadine", "10ml")]),
    ("Rum Punch", "A crowd-friendly tropical rum punch.", "hurricane", "shake", "easy",
     ["tropical", "party"],
     ["Shake all ingredients with ice.", "Strain over fresh ice in a hurricane glass.", "Garnish with an orange wheel."],
     [ing("rum_gold", "60ml"), ing("orange_juice", "45ml"), ing("pineapple_juice", "45ml"), ing("grenadine", "15ml"), ing("lime_juice", "15ml")]),
    ("Zombie", "A strong, multi-rum tiki classic.", "hurricane", "shake", "advanced",
     ["classic", "tiki", "strong"],
     ["Shake all ingredients hard with ice.", "Strain over crushed ice in a hurricane glass.", "Garnish with a mint sprig."],
     [ing("rum_white", "30ml"), ing("rum_gold", "30ml"), ing("rum_dark", "30ml"), ing("lime_juice", "22ml"), ing("falernum", "15ml"), ing("grenadine", "10ml"), ing("angostura_bitters", "1 dash")]),
    ("Painkiller", "A rich, coconut-forward dark rum tiki drink.", "hurricane", "shake", "easy",
     ["tiki", "tropical"],
     ["Shake all ingredients with ice.", "Strain over crushed ice in a hurricane glass.", "Garnish with grated nutmeg."],
     [ing("rum_dark", "60ml"), ing("pineapple_juice", "60ml"), ing("orange_juice", "30ml"), ing("coconut_cream", "30ml")]),
    ("Jungle Bird", "A tiki classic balanced with bitter aperitif.", "rocks", "shake", "medium",
     ["modern-classic", "tiki", "bitter"],
     ["Shake all ingredients with ice.", "Strain over fresh ice in a rocks glass.", "Garnish with a pineapple wedge."],
     [ing("rum_dark", "45ml"), ing("campari_style", "22ml"), ing("pineapple_juice", "45ml"), ing("lime_juice", "15ml"), ing("simple_syrup", "10ml")]),
    ("Hemingway Daiquiri", "A tart, grapefruit-forward Daiquiri variant.", "coupe", "shake", "medium",
     ["modern-classic", "sour"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("rum_white", "60ml"), ing("maraschino", "15ml"), ing("grapefruit_juice", "30ml"), ing("lime_juice", "15ml")]),
    ("El Presidente", "A refined Cuban rum and vermouth classic.", "coupe", "stir", "medium",
     ["classic", "spirit-forward"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe.", "Garnish with an orange twist."],
     [ing("rum_white", "45ml"), ing("vermouth_blanc", "22ml"), ing("orange_curacao", "10ml"), ing("grenadine", "5ml")]),
    ("Rum Old Fashioned", "An Old Fashioned reimagined with aged rum.", "rocks", "build", "easy",
     ["modern-classic", "spirit-forward"],
     ["Stir demerara syrup and bitters in a rocks glass.", "Add rum and a large ice cube.", "Stir until chilled.", "Garnish with an orange twist."],
     [ing("rum_dark", "60ml"), ing("demerara_syrup", "7.5ml"), ing("angostura_bitters", "2 dash"), ing("orange_twist", "1")]),

    # ---------------- Tequila & Mezcal ----------------
    ("Margarita", "Tequila, orange liqueur, and lime — perfectly balanced.", "rocks", "shake", "easy",
     ["classic", "sour", "iba-official"],
     ["Shake all ingredients with ice.", "Strain over fresh ice in a salt-rimmed rocks glass."],
     [ing("tequila_blanco", "50ml"), ing("triple_sec", "20ml"), ing("lime_juice", "20ml"), ing("salt_rim", "1", optional=True)]),
    ("Paloma", "Tequila and grapefruit soda, Mexico's favourite highball.", "highball", "build", "easy",
     ["classic", "tall", "refreshing"],
     ["Build tequila and lime juice over ice in a salt-rimmed highball glass.", "Top with grapefruit juice and club soda.", "Garnish with a lime wheel."],
     [ing("tequila_blanco", "50ml"), ing("lime_juice", "15ml"), ing("grapefruit_juice", "60ml"), ing("club_soda", "top"), ing("salt_rim", "1", optional=True)]),
    ("Tommy's Margarita", "A Margarita variant swapping triple sec for agave syrup.", "rocks", "shake", "easy",
     ["modern-classic", "sour"],
     ["Shake all ingredients with ice.", "Strain over fresh ice in a rocks glass."],
     [ing("tequila_blanco", "60ml"), ing("lime_juice", "22ml"), ing("simple_syrup", "15ml", sub="Traditionally agave syrup; simple syrup is the nearest catalogued sweetener.")]),
    ("Oaxacan Old Fashioned", "A smoky mezcal-tequila Old Fashioned.", "rocks", "build", "medium",
     ["modern-classic", "smoky", "spirit-forward"],
     ["Stir agave syrup and bitters in a rocks glass.", "Add tequila and mezcal with a large ice cube.", "Stir until chilled.", "Flame an orange twist over the glass."],
     [ing("tequila_reposado", "45ml"), ing("mezcal", "15ml"), ing("demerara_syrup", "7.5ml", sub="Traditionally agave syrup; demerara syrup is the nearest catalogued sweetener."), ing("angostura_bitters", "2 dash"), ing("orange_twist", "1", prep="flamed")]),
    ("Tequila Sunrise", "Tequila, orange juice, and a grenadine sunrise.", "highball", "build", "easy",
     ["classic", "tall", "sweet"],
     ["Build tequila and orange juice over ice in a highball glass.", "Slowly pour grenadine down the side to settle at the bottom.", "Garnish with an orange wheel and cherry."],
     [ing("tequila_blanco", "45ml"), ing("orange_juice", "90ml"), ing("grenadine", "15ml"), ing("orange_wheel", "1", optional=True)]),
    ("Mezcal Negroni", "A smoky twist on the Negroni.", "rocks", "build", "easy",
     ["modern-classic", "bitter", "smoky"],
     ["Build all ingredients over ice in a rocks glass.", "Stir briefly.", "Garnish with an orange wheel."],
     [ing("mezcal", "30ml"), ing("vermouth_sweet", "30ml"), ing("campari_style", "30ml"), ing("orange_wheel", "1")]),
    ("El Diablo", "Tequila, cassis, lime, and ginger beer.", "highball", "build", "easy",
     ["modern-classic", "tall", "refreshing"],
     ["Build tequila and lime juice over ice in a highball glass.", "Top with ginger beer.", "Drizzle crème de cassis over the top.", "Garnish with a lime wheel."],
     [ing("tequila_blanco", "45ml"), ing("creme_de_cassis", "15ml"), ing("lime_juice", "15ml"), ing("ginger_beer", "top")]),
    ("Naked and Famous", "An even-parts smoky, bitter, herbal mezcal cocktail.", "coupe", "shake", "medium",
     ["modern-classic", "even-parts", "smoky"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("mezcal", "22ml"), ing("aperol_style", "22ml"), ing("chartreuse_yellow", "22ml"), ing("lime_juice", "22ml")]),
    ("Tequila Old Fashioned", "An Old Fashioned built on reposado tequila.", "rocks", "build", "easy",
     ["modern-classic", "spirit-forward"],
     ["Stir agave syrup and bitters in a rocks glass.", "Add tequila and a large ice cube.", "Stir until chilled.", "Garnish with an orange twist."],
     [ing("tequila_reposado", "60ml"), ing("demerara_syrup", "7.5ml", sub="Traditionally agave syrup; demerara syrup is the nearest catalogued sweetener."), ing("angostura_bitters", "2 dash"), ing("orange_twist", "1")]),

    # ---------------- Vodka ----------------
    ("Espresso Martini", "Vodka, coffee liqueur, and fresh espresso, shaken to a foam.", "coupe", "shake", "medium",
     ["modern-classic", "coffee"],
     ["Shake all ingredients hard with ice to build foam.", "Double strain into a chilled coupe.", "Garnish with three coffee beans."],
     [ing("vodka_neutral", "45ml"), ing("coffee_liqueur", "15ml"), ing("espresso", "30ml", sub="Fresh espresso gives the foam; strong cold brew works but foams less."), ing("simple_syrup", "10ml", optional=True)]),
    ("Moscow Mule", "Vodka, lime, and spicy ginger beer in a copper mug.", "highball", "build", "easy",
     ["classic", "tall", "refreshing"],
     ["Build vodka and lime juice over ice in a copper mug or highball.", "Top with ginger beer.", "Garnish with a lime wedge."],
     [ing("vodka_neutral", "45ml"), ing("lime_juice", "15ml"), ing("ginger_beer", "top"), ing("lime_wedge", "1")]),
    ("Cosmopolitan", "Vodka, orange liqueur, lime, and cranberry.", "coupe", "shake", "easy",
     ["classic", "sour"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe.", "Garnish with an orange twist."],
     [ing("vodka_citrus", "45ml"), ing("triple_sec", "15ml"), ing("cranberry_juice", "30ml"), ing("lime_juice", "15ml")]),
    ("White Russian", "Vodka, coffee liqueur, and cream over ice.", "rocks", "build", "easy",
     ["classic", "creamy"],
     ["Build vodka and coffee liqueur over ice in a rocks glass.", "Float cream on top."],
     [ing("vodka_neutral", "50ml"), ing("coffee_liqueur", "20ml"), ing("heavy_cream", "20ml", prep="float")]),
    ("Vodka Martini", "A Martini made with vodka in place of gin.", "martini", "stir", "easy",
     ["classic", "spirit-forward"],
     ["Stir vodka and vermouth with ice.", "Strain into a chilled martini glass.", "Garnish with a lemon twist or olive."],
     [ing("vodka_neutral", "60ml"), ing("vermouth_dry", "10ml"), ing("olive", "1", optional=True)]),
    ("Bloody Mary", "A savoury vodka and tomato juice brunch classic.", "highball", "build", "medium",
     ["classic", "savory", "brunch"],
     ["Roll vodka, tomato juice, lemon juice, Worcestershire, and hot sauce between two shakers with ice.", "Season with celery salt and black pepper.", "Pour into a highball glass over fresh ice.", "Garnish with a celery stalk and lemon wedge."],
     [ing("vodka_neutral", "45ml"), ing("tomato_juice", "90ml"), ing("lemon_juice", "15ml"), ing("worcestershire", "4 dash"), ing("hot_sauce", "2 dash"), ing("celery_salt", "1 pinch", optional=True)]),
    ("Vodka Gimlet", "A Gimlet made with vodka.", "coupe", "shake", "easy",
     ["classic", "sour"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("vodka_neutral", "60ml"), ing("lime_juice", "22ml"), ing("simple_syrup", "15ml")]),
    ("Sea Breeze", "Vodka with cranberry and grapefruit.", "highball", "build", "easy",
     ["classic", "tall", "refreshing"],
     ["Build all ingredients over ice in a highball glass.", "Stir gently.", "Garnish with a lime wedge."],
     [ing("vodka_neutral", "45ml"), ing("cranberry_juice", "90ml"), ing("grapefruit_juice", "30ml"), ing("lime_wedge", "1", optional=True)]),
    ("Black Russian", "Vodka and coffee liqueur, unlengthened.", "rocks", "build", "easy",
     ["classic", "spirit-forward"],
     ["Build vodka and coffee liqueur over ice in a rocks glass.", "Stir briefly."],
     [ing("vodka_neutral", "50ml"), ing("coffee_liqueur", "20ml")]),
    ("Salty Dog", "Vodka and grapefruit in a salt-rimmed glass.", "highball", "build", "easy",
     ["classic", "tall", "refreshing"],
     ["Build vodka and grapefruit juice over ice in a salt-rimmed highball glass.", "Stir gently."],
     [ing("vodka_neutral", "45ml"), ing("grapefruit_juice", "120ml"), ing("salt_rim", "1")]),
    ("Screwdriver", "Vodka and orange juice, simply built.", "highball", "build", "easy",
     ["classic", "tall", "brunch"],
     ["Build vodka and orange juice over ice in a highball glass.", "Stir gently."],
     [ing("vodka_neutral", "45ml"), ing("orange_juice", "120ml")]),
    ("Vodka Collins", "A tall vodka and lemon fizz.", "collins", "shake", "easy",
     ["classic", "tall", "refreshing"],
     ["Shake vodka, lemon juice, and simple syrup with ice.", "Strain into a collins glass over fresh ice.", "Top with club soda.", "Garnish with a lemon wheel."],
     [ing("vodka_neutral", "45ml"), ing("lemon_juice", "22ml"), ing("simple_syrup", "15ml"), ing("club_soda", "top")]),
    ("Kamikaze", "A sharp, sweet-tart vodka shooter-turned-cocktail.", "coupe", "shake", "easy",
     ["classic", "sour"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("vodka_neutral", "30ml"), ing("triple_sec", "30ml"), ing("lime_juice", "30ml")]),
    ("Harvey Wallbanger", "A Screwdriver topped with a Galliano float.", "highball", "build", "easy",
     ["classic", "tall"],
     ["Build vodka and orange juice over ice in a highball glass.", "Float Galliano on top."],
     [ing("vodka_neutral", "45ml"), ing("orange_juice", "90ml"), ing("galliano", "15ml", prep="float")]),

    # ---------------- Wine & Sparkling ----------------
    ("Aperol Spritz", "The ubiquitous low-ABV bitter aperitivo spritz.", "wine", "build", "easy",
     ["classic", "sparkling", "low-abv"],
     ["Fill a wine glass with ice.", "Add Aperol and Prosecco.", "Top with a splash of club soda.", "Garnish with an orange wheel."],
     [ing("aperol_style", "60ml"), ing("prosecco", "90ml"), ing("club_soda", "30ml"), ing("orange_wheel", "1")]),
    ("Kir Royale", "Champagne with a dash of cassis.", "flute", "build", "easy",
     ["classic", "sparkling", "low-abv"],
     ["Add crème de cassis to a chilled flute.", "Top with Champagne."],
     [ing("creme_de_cassis", "10ml"), ing("champagne", "top")]),
    ("Bellini", "White peach purée and Prosecco.", "flute", "build", "easy",
     ["classic", "sparkling", "brunch", "iba-official", "low-abv"],
     ["Add peach purée to a chilled flute.", "Top slowly with Prosecco.", "Stir gently."],
     [ing("fresh_peach", "50ml", prep="puréed"), ing("prosecco", "100ml")]),
    ("Mimosa", "Sparkling wine and orange juice, brunch's favourite.", "flute", "build", "easy",
     ["classic", "sparkling", "brunch", "low-abv"],
     ["Add orange juice to a chilled flute.", "Top with Champagne."],
     [ing("orange_juice", "60ml"), ing("champagne", "top")]),
    ("Americano", "A low-ABV precursor to the Negroni.", "highball", "build", "easy",
     ["classic", "bitter", "low-abv", "iba-official"],
     ["Build bitter aperitif and sweet vermouth over ice in a highball glass.", "Top with club soda.", "Garnish with an orange wheel."],
     [ing("campari_style", "30ml"), ing("vermouth_sweet", "30ml"), ing("club_soda", "top"), ing("orange_wheel", "1")]),
    ("Champagne Cocktail", "A sugar-and-bitters classic topped with Champagne.", "flute", "build", "easy",
     ["classic", "sparkling", "low-abv"],
     ["Place a sugar cube soaked in bitters in a flute.", "Top with Champagne.", "Garnish with a lemon twist."],
     [ing("angostura_bitters", "3 dash"), ing("simple_syrup", "5ml", sub="Traditionally a sugar cube; simple syrup is the nearest catalogued sweetener."), ing("champagne", "top"), ing("lemon_twist", "1", optional=True)]),
    ("Rossini", "A Bellini made with strawberry instead of peach.", "flute", "build", "easy",
     ["modern-classic", "sparkling", "brunch", "low-abv"],
     ["Add strawberry purée to a chilled flute.", "Top slowly with Prosecco.", "Stir gently."],
     [ing("fresh_strawberry", "50ml", prep="puréed"), ing("prosecco", "100ml")]),
    ("Poinsettia", "A festive cranberry Mimosa variant.", "flute", "build", "easy",
     ["modern-classic", "sparkling", "brunch"],
     ["Add cranberry juice and orange liqueur to a chilled flute.", "Top with Champagne."],
     [ing("cranberry_juice", "45ml"), ing("triple_sec", "10ml"), ing("champagne", "top")]),
    ("Black Velvet", "Stout and Champagne in equal measure.", "flute", "build", "easy",
     ["classic", "sparkling", "low-abv"],
     ["Pour Champagne into a chilled flute.", "Top slowly with stout, layering gently."],
     [ing("champagne", "75ml"), ing("stout", "75ml")]),

    # ---------------- Brandy & Cognac ----------------
    ("Sidecar", "Cognac, orange liqueur, and lemon in a sugar-rimmed glass.", "coupe", "shake", "medium",
     ["classic", "sour", "iba-official"],
     ["Shake all ingredients with ice.", "Double strain into a sugar-rimmed chilled coupe."],
     [ing("cognac_vs", "50ml"), ing("triple_sec", "20ml"), ing("lemon_juice", "20ml"), ing("sugar_rim", "1", optional=True)]),
    ("Brandy Alexander", "A rich, dessert-like cognac and cream cocktail.", "coupe", "shake", "easy",
     ["classic", "creamy", "dessert"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe.", "Garnish with grated nutmeg."],
     [ing("cognac_vs", "30ml"), ing("creme_de_cacao", "30ml", sub="Dark crème de cacao is traditional."), ing("heavy_cream", "30ml")]),
    ("Between the Sheets", "A cognac-rum sour in the Sidecar family.", "coupe", "shake", "medium",
     ["classic", "sour"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("cognac_vs", "22ml"), ing("rum_white", "22ml"), ing("triple_sec", "22ml"), ing("lemon_juice", "15ml")]),
    ("Pisco Sour", "Peru's national cocktail, frothed with egg white.", "coupe", "shake", "medium",
     ["classic", "sour", "iba-official"],
     ["Dry shake all ingredients without ice.", "Shake again with ice.", "Double strain into a chilled coupe.", "Garnish with bitters drops on the foam."],
     [ing("pisco", "60ml"), ing("lime_juice", "22ml"), ing("simple_syrup", "15ml"), ing("egg_white", "15ml"), ing("angostura_bitters", "2 dash", prep="garnish")]),
    ("French Connection", "Cognac and amaretto, simply built over ice.", "rocks", "build", "easy",
     ["classic", "spirit-forward"],
     ["Build both ingredients over ice in a rocks glass.", "Stir briefly."],
     [ing("cognac_vs", "45ml"), ing("amaretto", "22ml")]),
    ("Jack Rose", "A tart apple brandy sour.", "coupe", "shake", "medium",
     ["classic", "sour"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("calvados", "60ml"), ing("lime_juice", "22ml"), ing("grenadine", "15ml")]),
    ("Metropolitan", "A 19th-century brandy Manhattan, sweetened and bittered.", "coupe", "stir", "medium",
     ["classic", "spirit-forward"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe.", "Garnish with an orange twist."],
     [ing("cognac_vs", "45ml"), ing("vermouth_sweet", "30ml"), ing("simple_syrup", "5ml"), ing("angostura_bitters", "2 dash"), ing("orange_twist", "1", optional=True)]),

    # ---------------- Liqueur-forward ----------------
    ("Amaretto Sour", "A nutty, tart amaretto sour.", "rocks", "shake", "easy",
     ["classic", "sour"],
     ["Shake all ingredients with ice.", "Strain over fresh ice in a rocks glass.", "Garnish with a cherry."],
     [ing("amaretto", "60ml"), ing("lemon_juice", "22ml"), ing("simple_syrup", "10ml"), ing("egg_white", "15ml", optional=True), ing("fresh_cherry", "1", optional=True)]),
    ("Grasshopper", "A minty, dessert-like cream cocktail.", "coupe", "shake", "easy",
     ["classic", "creamy", "dessert"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("creme_de_menthe", "22ml", sub="Green crème de menthe gives the classic colour."), ing("creme_de_cacao", "22ml", sub="White crème de cacao keeps the colour bright."), ing("heavy_cream", "22ml")]),
    ("Godfather", "Scotch and amaretto, simply built.", "rocks", "build", "easy",
     ["classic", "spirit-forward"],
     ["Build both ingredients over ice in a rocks glass.", "Stir briefly."],
     [ing("whiskey_scotch_blended", "45ml"), ing("amaretto", "22ml")]),
    ("Godmother", "Vodka and amaretto, simply built.", "rocks", "build", "easy",
     ["classic", "spirit-forward"],
     ["Build both ingredients over ice in a rocks glass.", "Stir briefly."],
     [ing("vodka_neutral", "45ml"), ing("amaretto", "22ml")]),
    ("Negroni Sbagliato", "A Negroni with Prosecco standing in for gin.", "rocks", "build", "easy",
     ["modern-classic", "bitter", "sparkling"],
     ["Build sweet vermouth and bitter aperitif over ice in a rocks glass.", "Top with Prosecco.", "Garnish with an orange wheel."],
     [ing("vermouth_sweet", "30ml"), ing("campari_style", "30ml"), ing("prosecco", "30ml"), ing("orange_wheel", "1")]),
    ("French Martini", "Vodka, raspberry liqueur, and pineapple, shaken frothy.", "coupe", "shake", "easy",
     ["modern-classic", "fruity"],
     ["Shake all ingredients hard with ice.", "Double strain into a chilled coupe."],
     [ing("vodka_neutral", "45ml"), ing("chambord", "15ml"), ing("pineapple_juice", "30ml")]),
    ("Golden Cadillac", "A dessert-style cream cocktail with Galliano and cacao.", "coupe", "shake", "easy",
     ["classic", "creamy", "dessert"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("galliano", "22ml"), ing("creme_de_cacao", "22ml", sub="White crème de cacao keeps the colour golden."), ing("heavy_cream", "22ml")]),
    ("Toasted Almond", "A dessert-style coffee and amaretto cream cocktail.", "rocks", "shake", "easy",
     ["classic", "creamy", "dessert"],
     ["Shake all ingredients with ice.", "Strain over fresh ice in a rocks glass."],
     [ing("amaretto", "30ml"), ing("coffee_liqueur", "30ml"), ing("heavy_cream", "30ml")]),
    ("Stinger", "Cognac and crème de menthe, stirred sharp.", "rocks", "stir", "easy",
     ["classic", "spirit-forward"],
     ["Stir both ingredients with ice.", "Strain over crushed ice in a rocks glass."],
     [ing("cognac_vs", "60ml"), ing("creme_de_menthe", "22ml", sub="White crème de menthe is traditional.")]),

    # ---------------- Low-ABV / No-ABV ----------------
    ("Virgin Mojito", "All the mint and lime of a Mojito, no rum.", "highball", "build", "easy",
     ["no-abv", "tall", "refreshing"],
     ["Muddle mint with simple syrup and lime juice in a highball glass.", "Fill with crushed ice.", "Top with club soda and stir.", "Garnish with a mint sprig."],
     [ing("lime_juice", "22ml"), ing("simple_syrup", "15ml"), ing("fresh_mint", "10 leaves", prep="muddled"), ing("club_soda", "top")]),
    ("Shirley Temple", "Ginger ale and grenadine, a classic mocktail.", "highball", "build", "easy",
     ["no-abv", "tall", "kid-friendly"],
     ["Fill a highball glass with ice.", "Add grenadine.", "Top with ginger ale.", "Garnish with a cherry."],
     [ing("grenadine", "15ml"), ing("ginger_ale", "top"), ing("fresh_cherry", "1")]),
    ("Arnold Palmer Spritz", "Iced tea and lemonade with a sparkling top.", "highball", "build", "easy",
     ["no-abv", "tall", "refreshing"],
     ["Fill a highball glass with ice.", "Add chilled black tea, lemon juice, and simple syrup.", "Top with club soda.", "Stir gently and garnish with a lemon wedge."],
     [ing("black_tea", "90ml", prep="brewed and chilled"), ing("lemon_juice", "25ml"), ing("simple_syrup", "20ml"), ing("club_soda", "top")]),
    ("Ginger Mule (Non-Alcoholic)", "A spicy, zero-proof take on the Moscow Mule.", "highball", "build", "easy",
     ["no-abv", "tall", "refreshing"],
     ["Build lime juice over ice in a copper mug or highball.", "Top with ginger beer.", "Garnish with a lime wedge."],
     [ing("lime_juice", "15ml"), ing("ginger_beer", "top"), ing("lime_wedge", "1")]),
    ("Cucumber Cooler (Non-Alcoholic)", "A crisp, herbal cucumber refresher.", "highball", "shake", "easy",
     ["no-abv", "tall", "refreshing", "herbal"],
     ["Muddle cucumber with lime juice and simple syrup in a shaker.", "Shake with ice.", "Strain into a highball glass over fresh ice.", "Top with club soda."],
     [ing("cucumber", "4 slices", prep="muddled"), ing("lime_juice", "15ml"), ing("simple_syrup", "10ml"), ing("club_soda", "top")]),
    ("Virgin Piña Colada", "A zero-proof Piña Colada.", "hurricane", "blend", "easy",
     ["no-abv", "tropical"],
     ["Blend all ingredients with a cup of ice until smooth.", "Pour into a hurricane glass.", "Garnish with a pineapple wedge."],
     [ing("pineapple_juice", "120ml"), ing("coconut_cream", "45ml"), ing("fresh_pineapple", "1 wedge", optional=True)]),
    ("Passion Fruit Spritz (Non-Alcoholic)", "A bright, tropical zero-proof spritz.", "wine", "build", "easy",
     ["no-abv", "sparkling", "tropical"],
     ["Fill a wine glass with ice.", "Add passion fruit syrup and lime juice.", "Top with club soda.", "Garnish with a lime wheel."],
     [ing("passion_fruit_syrup", "30ml"), ing("lime_juice", "10ml"), ing("club_soda", "top")]),

    # ---------------- Warm ----------------
    ("Mulled Wine", "Red wine warmed with spice and citrus.", "mug", "build", "easy",
     ["warm", "classic", "seasonal", "low-abv"],
     ["Warm red wine gently with demerara syrup, cinnamon, and orange in a saucepan (do not boil).", "Stir in the port, if using.", "Ladle into a warmed mug.", "Garnish with a cinnamon stick."],
     [ing("red_wine", "150ml"), ing("port_ruby", "15ml", optional=True), ing("demerara_syrup", "15ml"), ing("cinnamon_stick", "1"), ing("orange_wheel", "1")]),
    ("Hot Buttered Rum", "Dark rum warmed with butter and spice.", "mug", "build", "medium",
     ["warm", "classic", "seasonal"],
     ["Combine dark rum and demerara syrup in a warmed mug.", "Top with hot water.", "Stir in the butter until melted.", "Garnish with a cinnamon stick."],
     [ing("rum_dark", "45ml"), ing("demerara_syrup", "15ml"), ing("butter", "1 tsp"), ing("cinnamon_stick", "1")]),
    ("Tom and Jerry", "A festive warm eggnog-style rum and brandy punch.", "mug", "build", "advanced",
     ["warm", "classic", "seasonal"],
     ["Whip egg white and yolk separately, then fold together with sugar into a batter.", "Add rum and cognac to a warmed mug with a spoonful of batter.", "Top with hot water or milk and stir.", "Garnish with grated nutmeg."],
     [ing("rum_dark", "30ml"), ing("cognac_vs", "30ml"), ing("egg_white", "15ml"), ing("simple_syrup", "10ml"), ing("heavy_cream", "60ml", sub="Traditionally hot milk; heavy cream is the nearest catalogued dairy ingredient — thin with hot water to taste.")]),

    # ---------------- Additional classics (gin) ----------------
    ("Bronx", "A Martini-Manhattan hybrid with orange juice.", "coupe", "shake", "medium",
     ["classic", "sour"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("gin_london_dry", "45ml"), ing("vermouth_dry", "15ml"), ing("vermouth_sweet", "15ml"), ing("orange_juice", "15ml")]),
    ("Income Tax Cocktail", "A Bronx sharpened with bitters.", "coupe", "shake", "medium",
     ["classic", "sour"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("gin_london_dry", "45ml"), ing("vermouth_dry", "15ml"), ing("vermouth_sweet", "15ml"), ing("orange_juice", "15ml"), ing("angostura_bitters", "2 dash")]),
    ("Journalist", "A layered, six-ingredient gin classic.", "coupe", "shake", "medium",
     ["classic", "spirit-forward"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("gin_london_dry", "45ml"), ing("vermouth_dry", "15ml"), ing("vermouth_sweet", "15ml"), ing("triple_sec", "7.5ml"), ing("lemon_juice", "7.5ml"), ing("angostura_bitters", "2 dash")]),
    ("Monkey Gland", "A curious gin, orange, and absinthe classic.", "coupe", "shake", "medium",
     ["classic", "sour"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("gin_london_dry", "50ml"), ing("orange_juice", "20ml"), ing("grenadine", "5ml"), ing("absinthe", "1 dash")]),
    ("Pink Lady", "A frothy pink gin sour from the Jazz Age.", "coupe", "shake", "medium",
     ["classic", "sour"],
     ["Dry shake all ingredients without ice.", "Shake again with ice.", "Double strain into a chilled coupe."],
     [ing("gin_london_dry", "45ml"), ing("calvados", "15ml", sub="Traditionally applejack; calvados is the nearest catalogued apple brandy."), ing("lemon_juice", "15ml"), ing("grenadine", "10ml"), ing("egg_white", "15ml")]),
    ("Casino", "A refined pre-Prohibition gin classic.", "coupe", "shake", "medium",
     ["classic", "spirit-forward"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe.", "Garnish with a cherry."],
     [ing("gin_old_tom", "50ml", sub="Old Tom is traditional; London Dry makes it drier."), ing("maraschino", "7.5ml"), ing("orange_bitters", "2 dash"), ing("lemon_juice", "7.5ml"), ing("fresh_cherry", "1", optional=True)]),
    ("Alexander", "A gin-based dessert cocktail, cousin to the Brandy Alexander.", "coupe", "shake", "easy",
     ["classic", "creamy", "dessert"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe.", "Garnish with grated nutmeg."],
     [ing("gin_london_dry", "30ml"), ing("creme_de_cacao", "30ml", sub="White crème de cacao is traditional."), ing("heavy_cream", "30ml")]),
    ("Suffering Bastard", "A gin-and-cognac tiki cooler with ginger beer.", "highball", "build", "medium",
     ["classic", "tiki", "tall"],
     ["Build gin, cognac, lime juice, and bitters over ice in a highball glass.", "Top with ginger beer.", "Garnish with a mint sprig and cucumber."],
     [ing("gin_london_dry", "22ml"), ing("cognac_vs", "22ml"), ing("lime_juice", "15ml"), ing("angostura_bitters", "2 dash"), ing("ginger_beer", "top")]),

    # ---------------- Additional classics (whiskey) ----------------
    ("Presbyterian", "Whiskey lengthened with ginger ale and soda.", "highball", "build", "easy",
     ["classic", "tall", "refreshing"],
     ["Build whiskey over ice in a highball glass.", "Top with equal parts ginger ale and club soda."],
     [ing("whiskey_bourbon", "45ml"), ing("ginger_ale", "top"), ing("club_soda", "top")]),
    ("Horse's Neck", "Whiskey and ginger ale with a long lemon spiral.", "highball", "build", "easy",
     ["classic", "tall"],
     ["Drape a long lemon peel spiral inside a highball glass.", "Fill with ice and add whiskey.", "Top with ginger ale."],
     [ing("whiskey_bourbon", "45ml"), ing("ginger_ale", "top"), ing("lemon_twist", "1", prep="long spiral peel")]),
    ("Whiskey Ginger", "The simplest whiskey highball.", "highball", "build", "easy",
     ["classic", "tall"],
     ["Build whiskey over ice in a highball glass.", "Top with ginger ale."],
     [ing("whiskey_bourbon", "45ml"), ing("ginger_ale", "top")]),
    ("Black Manhattan", "A Manhattan made bittersweet with Averna in place of vermouth.", "coupe", "stir", "medium",
     ["modern-classic", "spirit-forward", "bitter"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe.", "Garnish with a cherry."],
     [ing("whiskey_rye", "60ml"), ing("amaro_dark", "30ml", sub="Averna is the original."), ing("angostura_bitters", "1 dash"), ing("orange_bitters", "1 dash"), ing("fresh_cherry", "1")]),
    ("Remember the Maine", "A cherry-tinged rye Manhattan variant with an absinthe rinse.", "coupe", "stir", "medium",
     ["classic", "spirit-forward"],
     ["Rinse a chilled coupe with absinthe.", "Stir the remaining ingredients with ice.", "Strain into the coupe.", "Garnish with a cherry."],
     [ing("whiskey_rye", "60ml"), ing("vermouth_sweet", "22ml"), ing("cherry_liqueur", "10ml"), ing("absinthe", "1 dash", prep="rinse"), ing("fresh_cherry", "1", optional=True)]),
    ("Trinidad Sour", "An unconventional modern classic built on Angostura bitters.", "coupe", "shake", "medium",
     ["modern-classic", "sour", "bitter"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("angostura_bitters", "45ml"), ing("orgeat", "22ml"), ing("lemon_juice", "22ml"), ing("whiskey_rye", "15ml")]),

    # ---------------- Additional classics (rum) ----------------
    ("Bacardi Cocktail", "A pink, lime-forward Daiquiri variant.", "coupe", "shake", "easy",
     ["classic", "sour", "iba-official"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("rum_white", "60ml"), ing("lime_juice", "22ml"), ing("grenadine", "10ml")]),
    ("Corn 'n Oil", "A rich, dark rum and falernum sipper.", "rocks", "build", "easy",
     ["classic", "tiki", "spirit-forward"],
     ["Build all ingredients over ice in a rocks glass.", "Stir briefly."],
     [ing("rum_dark", "60ml"), ing("falernum", "15ml"), ing("lime_juice", "10ml"), ing("angostura_bitters", "2 dash")]),
    ("Bee's Kiss", "A honeyed, creamy rum dessert sip.", "coupe", "shake", "easy",
     ["classic", "creamy", "dessert"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("rum_white", "45ml"), ing("honey_syrup", "15ml"), ing("heavy_cream", "15ml")]),
    ("Scorpion", "A tiki punch blending rum and cognac.", "hurricane", "shake", "medium",
     ["classic", "tiki"],
     ["Shake all ingredients with ice.", "Strain over crushed ice in a hurricane glass.", "Garnish with a mint sprig."],
     [ing("rum_white", "45ml"), ing("cognac_vs", "15ml"), ing("orange_juice", "45ml"), ing("orgeat", "15ml"), ing("lime_juice", "22ml")]),
    ("Navy Grog", "A three-rum tiki grog with citrus and honey.", "hurricane", "shake", "medium",
     ["classic", "tiki"],
     ["Shake all ingredients with ice.", "Strain over crushed ice in a hurricane glass."],
     [ing("rum_white", "22ml"), ing("rum_gold", "22ml"), ing("rum_dark", "22ml"), ing("lime_juice", "15ml"), ing("grapefruit_juice", "15ml"), ing("honey_syrup", "15ml")]),
    ("Kingston Negroni", "A Negroni built on funky Jamaican-style dark rum.", "rocks", "build", "easy",
     ["modern-classic", "bitter"],
     ["Build all ingredients over ice in a rocks glass.", "Stir briefly.", "Garnish with an orange wheel."],
     [ing("rum_dark", "30ml"), ing("vermouth_sweet", "30ml"), ing("campari_style", "30ml"), ing("orange_wheel", "1")]),
    ("Air Mail", "A Cuban rum classic topped with Champagne.", "flute", "shake", "medium",
     ["classic", "sparkling"],
     ["Shake rum, lime juice, and honey syrup with ice.", "Strain into a flute.", "Top with Champagne."],
     [ing("rum_gold", "45ml"), ing("lime_juice", "15ml"), ing("honey_syrup", "15ml"), ing("champagne", "top")]),

    # ---------------- Additional classics (tequila/vodka) ----------------
    ("Matador", "A simple, tropical tequila and pineapple sour.", "coupe", "shake", "easy",
     ["modern-classic", "tropical"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("tequila_blanco", "45ml"), ing("pineapple_juice", "45ml"), ing("lime_juice", "15ml")]),
    ("Brave Bull", "Tequila and coffee liqueur, simply built.", "rocks", "build", "easy",
     ["classic", "spirit-forward", "coffee"],
     ["Build both ingredients over ice in a rocks glass.", "Stir briefly."],
     [ing("tequila_blanco", "45ml"), ing("coffee_liqueur", "22ml")]),
    ("Conquistador", "A creamy tequila and coffee dessert cocktail.", "rocks", "shake", "easy",
     ["modern-classic", "creamy", "dessert"],
     ["Shake all ingredients with ice.", "Strain over fresh ice in a rocks glass."],
     [ing("tequila_blanco", "45ml"), ing("coffee_liqueur", "22ml"), ing("heavy_cream", "22ml")]),
    ("Chi-Chi", "A vodka Piña Colada.", "hurricane", "blend", "easy",
     ["classic", "tropical"],
     ["Blend all ingredients with a cup of ice until smooth.", "Pour into a hurricane glass.", "Garnish with a pineapple wedge."],
     [ing("vodka_neutral", "45ml"), ing("pineapple_juice", "90ml"), ing("coconut_cream", "30ml")]),
    ("Vodka Sour", "A straightforward vodka sour.", "rocks", "shake", "easy",
     ["classic", "sour"],
     ["Shake all ingredients with ice.", "Strain over fresh ice in a rocks glass."],
     [ing("vodka_neutral", "60ml"), ing("lemon_juice", "22ml"), ing("simple_syrup", "15ml")]),
    ("Greyhound", "Vodka and grapefruit, unrimmed.", "highball", "build", "easy",
     ["classic", "tall"],
     ["Build both ingredients over ice in a highball glass.", "Stir gently."],
     [ing("vodka_neutral", "45ml"), ing("grapefruit_juice", "120ml")]),
    ("Cape Codder", "Vodka, cranberry, and a squeeze of lime.", "highball", "build", "easy",
     ["classic", "tall"],
     ["Build all ingredients over ice in a highball glass.", "Stir gently."],
     [ing("vodka_neutral", "45ml"), ing("cranberry_juice", "120ml"), ing("lime_juice", "10ml")]),
    ("Madras", "Vodka with cranberry and orange juice.", "highball", "build", "easy",
     ["classic", "tall"],
     ["Build all ingredients over ice in a highball glass.", "Stir gently."],
     [ing("vodka_neutral", "45ml"), ing("cranberry_juice", "60ml"), ing("orange_juice", "60ml")]),
    ("Woo Woo", "Vodka, peach schnapps, and cranberry.", "rocks", "shake", "easy",
     ["classic", "sweet"],
     ["Shake all ingredients with ice.", "Strain over fresh ice in a rocks glass."],
     [ing("vodka_neutral", "30ml"), ing("peach_schnapps", "30ml"), ing("cranberry_juice", "45ml")]),
    ("Sex on the Beach", "A fruity vodka and peach schnapps highball.", "highball", "shake", "easy",
     ["classic", "tall", "sweet"],
     ["Shake all ingredients with ice.", "Strain over fresh ice in a highball glass."],
     [ing("vodka_neutral", "30ml"), ing("peach_schnapps", "15ml"), ing("orange_juice", "45ml"), ing("cranberry_juice", "45ml")]),
    ("Fuzzy Navel", "Peach schnapps and orange juice, easygoing and sweet.", "highball", "build", "easy",
     ["classic", "tall", "sweet"],
     ["Build both ingredients over ice in a highball glass.", "Stir gently."],
     [ing("peach_schnapps", "45ml"), ing("orange_juice", "120ml")]),
    ("Pink Squirrel", "A pastel, almond-forward dessert cocktail.", "coupe", "shake", "easy",
     ["classic", "creamy", "dessert"],
     ["Shake all ingredients with ice.", "Double strain into a chilled coupe."],
     [ing("creme_de_noyaux", "22ml"), ing("creme_de_cacao", "22ml", sub="White crème de cacao keeps the pink colour."), ing("heavy_cream", "22ml")]),

    # ---------------- Additional low/no-ABV and warm ----------------
    ("Spiced Apple Cider (Warm, Non-Alcoholic)", "A warming, spiced zero-proof cider.", "mug", "build", "easy",
     ["warm", "no-abv", "seasonal"],
     ["Warm pressed apple with ginger syrup and cinnamon in a saucepan.", "Pour into a warmed mug.", "Garnish with a cinnamon stick."],
     [ing("fresh_apple", "150ml", prep="pressed to juice"), ing("ginger_syrup", "15ml"), ing("cinnamon_stick", "1")]),
    ("Grapefruit Rosemary Spritz (Non-Alcoholic)", "A bright, herbal zero-proof spritz.", "wine", "shake", "easy",
     ["no-abv", "sparkling", "herbal", "refreshing"],
     ["Muddle rosemary with honey syrup in a shaker.", "Add grapefruit juice, shake with ice.", "Strain into a wine glass over ice.", "Top with club soda.", "Garnish with a rosemary sprig."],
     [ing("grapefruit_juice", "60ml"), ing("fresh_rosemary", "1 sprig", prep="muddled"), ing("honey_syrup", "10ml"), ing("club_soda", "top")]),

    # ---------------- A few more, for margin above the 150 target ----------------
    ("Salty Chihuahua", "A tequila Greyhound, rimmed with salt.", "highball", "build", "easy",
     ["modern-classic", "tall"],
     ["Build tequila and grapefruit juice over ice in a salt-rimmed highball glass.", "Stir gently."],
     [ing("tequila_blanco", "45ml"), ing("grapefruit_juice", "120ml"), ing("salt_rim", "1")]),
    ("Batanga", "A rustic tequila and cola highball, stirred with a knife.", "highball", "build", "easy",
     ["classic", "tall"],
     ["Build tequila and lime juice over ice in a salt-rimmed highball glass.", "Top with cola and stir."],
     [ing("tequila_blanco", "45ml"), ing("lime_juice", "10ml"), ing("cola", "top"), ing("salt_rim", "1", optional=True)]),
    ("Ranch Water", "A minimal, bone-dry tequila and soda cooler.", "highball", "build", "easy",
     ["modern-classic", "tall", "refreshing"],
     ["Build tequila and lime juice over ice in a highball glass.", "Top with club soda."],
     [ing("tequila_blanco", "45ml"), ing("lime_juice", "15ml"), ing("club_soda", "top")]),
    ("Bamboo", "A dry, sherry-based aperitif classic.", "coupe", "stir", "medium",
     ["classic", "spirit-forward", "low-abv"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe.", "Garnish with a lemon twist."],
     [ing("sherry_fino", "45ml"), ing("vermouth_dry", "45ml"), ing("orange_bitters", "2 dash"), ing("lemon_twist", "1", optional=True)]),
    ("Adonis", "A sherry and sweet vermouth aperitif, gentle and dry.", "coupe", "stir", "medium",
     ["classic", "spirit-forward", "low-abv"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe.", "Garnish with an orange twist."],
     [ing("sherry_fino", "45ml"), ing("vermouth_sweet", "30ml"), ing("orange_bitters", "2 dash")]),
    ("Widow's Kiss", "An opulent apple brandy classic layered with herbal liqueurs.", "coupe", "stir", "advanced",
     ["classic", "spirit-forward"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe."],
     [ing("calvados", "45ml"), ing("benedictine", "22ml"), ing("chartreuse_yellow", "22ml"), ing("angostura_bitters", "2 dash")]),
    ("Cable Car", "A spiced-rum Sidecar variant with a cinnamon-sugar rim.", "coupe", "shake", "medium",
     ["modern-classic", "sour"],
     ["Shake all ingredients with ice.", "Double strain into a cinnamon-sugar-rimmed chilled coupe."],
     [ing("rum_spiced", "45ml"), ing("triple_sec", "15ml"), ing("lemon_juice", "15ml"), ing("cinnamon_stick", "1", optional=True)]),
    ("Jamaican Mule", "A funky dark-rum riff on the Moscow Mule.", "highball", "build", "easy",
     ["modern-classic", "tall", "refreshing"],
     ["Build dark rum and lime juice over ice in a copper mug or highball.", "Top with ginger beer.", "Garnish with a lime wedge."],
     [ing("rum_dark", "45ml"), ing("lime_juice", "15ml"), ing("ginger_beer", "top"), ing("lime_wedge", "1")]),

    # ---------------- Bottles that unlocked little (norse-catalog#2) ----------------
    ("Gin & Tonic", "The highball that needs no introduction.", "highball", "build", "easy",
     ["classic", "tall", "refreshing", "bitter"],
     ["Fill a highball glass with ice.", "Add gin, then top with tonic water.", "Stir once and garnish with a lime wedge."],
     [ing("gin_london_dry", "50ml"), ing("tonic_water", "top"), ing("lime_wedge", "1")]),
    ("Vodka Tonic", "A clean, bitter-edged vodka highball.", "highball", "build", "easy",
     ["classic", "tall", "refreshing"],
     ["Fill a highball glass with ice.", "Add vodka, then top with tonic water.", "Garnish with a lime wedge."],
     [ing("vodka_neutral", "50ml"), ing("tonic_water", "top"), ing("lime_wedge", "1")]),
    ("Espresso Tonic", "Espresso floated over tonic: bitter, bright and alcohol-free.", "highball", "build", "easy",
     ["no-abv", "tall", "refreshing", "coffee"],
     ["Fill a highball glass with ice and tonic water.", "Slowly pour fresh espresso over the top so it floats.", "Garnish with an orange twist."],
     [ing("tonic_water", "120ml"), ing("espresso", "30ml", prep="float"), ing("orange_twist", "1", optional=True)]),
    ("Hugo Spritz", "A South Tyrolean spritz of elderflower, mint and Prosecco.", "wine", "build", "easy",
     ["modern-classic", "sparkling", "refreshing", "low-abv"],
     ["Gently press the mint leaves in a wine glass.", "Add elderflower liqueur and ice.", "Top with Prosecco and a splash of soda.", "Garnish with a lime wheel."],
     [ing("elderflower_liqueur", "20ml", sub="The original uses elderflower syrup; the liqueur adds a little strength."), ing("prosecco", "90ml"),
      ing("club_soda", "30ml"), ing("fresh_mint", "6 leaves", prep="lightly pressed"), ing("lime_wedge", "1", optional=True)]),
    ("Elderflower Collins", "A Tom Collins softened with elderflower.", "collins", "shake", "easy",
     ["modern-classic", "tall", "refreshing", "sour"],
     ["Shake gin, elderflower liqueur, lemon juice and simple syrup with ice.", "Strain into a collins glass over fresh ice.", "Top with club soda.", "Garnish with a lemon twist."],
     [ing("gin_london_dry", "45ml"), ing("elderflower_liqueur", "15ml"), ing("lemon_juice", "22ml"), ing("simple_syrup", "7.5ml"),
      ing("club_soda", "top"), ing("lemon_twist", "1", optional=True)]),
    ("Elderflower G&T", "A floral twist on the Gin & Tonic.", "wine", "build", "easy",
     ["modern-classic", "tall", "refreshing"],
     ["Fill a wine glass with ice.", "Add gin and elderflower liqueur.", "Top with tonic water and stir once.", "Garnish with a lemon twist."],
     [ing("gin_london_dry", "40ml"), ing("elderflower_liqueur", "15ml"), ing("tonic_water", "top"), ing("lemon_twist", "1", optional=True)]),
    ("Sloe Gin Fizz", "Tart, jammy sloe gin lengthened with soda.", "highball", "shake", "easy",
     ["classic", "tall", "refreshing", "sour"],
     ["Shake sloe gin, lemon juice and simple syrup with ice.", "Strain into a highball glass over fresh ice.", "Top with club soda."],
     [ing("sloe_gin", "45ml"), ing("lemon_juice", "22ml"), ing("simple_syrup", "10ml"), ing("club_soda", "top")]),
    ("Sloe Gin & Tonic", "A ruby, low-strength highball for sloe gin.", "highball", "build", "easy",
     ["modern-classic", "tall", "refreshing", "low-abv"],
     ["Fill a highball glass with ice.", "Add sloe gin, then top with tonic water.", "Garnish with an orange wheel."],
     [ing("sloe_gin", "50ml"), ing("tonic_water", "top"), ing("orange_wheel", "1", optional=True)]),
    ("Blackthorn", "A Savoy-era stirred drink of sloe gin and sweet vermouth.", "coupe", "stir", "medium",
     ["classic", "spirit-forward"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe.", "Garnish with a lemon twist."],
     [ing("sloe_gin", "45ml"), ing("vermouth_sweet", "30ml"), ing("orange_bitters", "2 dash"), ing("lemon_twist", "1", optional=True)]),
    ("Rusty Nail", "Scotch sweetened with honeyed, herbal Drambuie.", "rocks", "build", "easy",
     ["classic", "spirit-forward"],
     ["Build Scotch and Drambuie over a large ice cube in a rocks glass.", "Stir until chilled.", "Garnish with a lemon twist."],
     [ing("whiskey_scotch_blended", "45ml"), ing("drambuie", "22ml"), ing("lemon_twist", "1", optional=True)]),
    ("Bobby Burns", "A Rob Roy rounded out with Bénédictine.", "coupe", "stir", "medium",
     ["classic", "spirit-forward"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe.", "Garnish with a lemon twist."],
     [ing("whiskey_scotch_blended", "45ml"), ing("vermouth_sweet", "22ml"), ing("benedictine", "7.5ml"), ing("lemon_twist", "1", optional=True)]),
    ("Cynar Spritz", "A bittersweet, vegetal take on the aperitivo spritz.", "wine", "build", "easy",
     ["modern-classic", "sparkling", "bitter", "low-abv"],
     ["Fill a wine glass with ice.", "Add Cynar and Prosecco.", "Top with a splash of club soda.", "Garnish with an orange wheel."],
     [ing("cynar", "60ml"), ing("prosecco", "90ml"), ing("club_soda", "30ml"), ing("orange_wheel", "1", optional=True)]),
    ("Little Italy", "A Manhattan deepened with Cynar.", "coupe", "stir", "medium",
     ["modern-classic", "spirit-forward", "bitter"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe.", "Garnish with a cherry."],
     [ing("whiskey_rye", "60ml"), ing("vermouth_sweet", "22ml"), ing("cynar", "15ml"), ing("fresh_cherry", "1", optional=True)]),
    ("Trident", "An equal-parts Negroni riff of aquavit, Cynar and fino sherry.", "coupe", "stir", "medium",
     ["modern-classic", "spirit-forward", "bitter", "even-parts"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe.", "Garnish with a lemon twist."],
     [ing("aquavit", "30ml"), ing("cynar", "30ml"), ing("sherry_fino", "30ml"),
      ing("orange_bitters", "2 dash", sub="The original uses peach bitters."), ing("lemon_twist", "1", optional=True)]),
    ("Danish Mary", "A Bloody Mary with caraway-scented aquavit in place of vodka.", "highball", "build", "medium",
     ["modern-classic", "savory", "brunch"],
     ["Roll aquavit, tomato juice, lemon juice, Worcestershire and hot sauce between two shakers with ice.", "Season with celery salt and black pepper.", "Pour into a highball glass over fresh ice.", "Garnish with a lemon wedge."],
     [ing("aquavit", "45ml"), ing("tomato_juice", "90ml"), ing("lemon_juice", "15ml"), ing("worcestershire", "4 dash"),
      ing("hot_sauce", "2 dash"), ing("celery_salt", "1 pinch", optional=True)]),
    ("Amaro Sour", "A rich, bittersweet sour built on a dark amaro.", "rocks", "shake", "easy",
     ["modern-classic", "sour", "bitter"],
     ["Dry shake all ingredients without ice.", "Shake again with ice.", "Strain over fresh ice in a rocks glass.", "Garnish with an orange twist."],
     [ing("amaro_dark", "45ml"), ing("lemon_juice", "22ml"), ing("simple_syrup", "10ml"), ing("egg_white", "15ml", optional=True),
      ing("orange_twist", "1", optional=True)]),
    ("Greenpoint", "A Manhattan riff with yellow Chartreuse.", "coupe", "stir", "medium",
     ["modern-classic", "spirit-forward"],
     ["Stir all ingredients with ice.", "Strain into a chilled coupe.", "Garnish with a lemon twist."],
     [ing("whiskey_rye", "60ml"), ing("vermouth_sweet", "15ml"), ing("chartreuse_yellow", "15ml"), ing("angostura_bitters", "1 dash"),
      ing("orange_bitters", "1 dash"), ing("lemon_twist", "1", optional=True)]),
    ("Caipirinha", "Brazil's national cocktail: cachaça, lime and sugar, muddled.", "rocks", "build", "easy",
     ["classic", "sour", "refreshing", "iba-official"],
     ["Cut the lime into wedges and muddle with simple syrup in a rocks glass.", "Fill with crushed ice.", "Add cachaça and stir well."],
     [ing("cachaca", "60ml"), ing("fresh_lime", "4", prep="wedges, muddled"), ing("simple_syrup", "20ml", sub="Traditionally two teaspoons of white sugar, muddled with the lime.")]),
    ("Mudslide", "A frozen-dessert-style mix of vodka, coffee liqueur and Irish cream.", "rocks", "shake", "easy",
     ["classic", "creamy", "dessert"],
     ["Shake all ingredients with ice.", "Strain over fresh ice in a rocks glass."],
     [ing("vodka_neutral", "30ml"), ing("coffee_liqueur", "30ml"), ing("irish_cream", "30ml"), ing("heavy_cream", "30ml", optional=True)]),
    ("Nutty Irishman", "Irish cream and hazelnut liqueur in hot coffee, crowned with cream.", "mug", "build", "easy",
     ["warm", "creamy", "dessert", "coffee"],
     ["Pour Irish cream and hazelnut liqueur into a warmed mug.", "Top with hot coffee and stir.", "Float lightly whipped cream on top."],
     [ing("irish_cream", "22ml"), ing("hazelnut_liqueur", "22ml"), ing("hot_coffee", "120ml"),
      ing("heavy_cream", "30ml", prep="lightly whipped", optional=True)]),
    ("Café Corretto", "Espresso \"corrected\" with a shot of sambuca.", "mug", "build", "easy",
     ["classic", "coffee", "warm"],
     ["Pull a shot of espresso into a small cup.", "Add the sambuca, or serve it alongside to pour in.", "Garnish with three coffee beans, if you like."],
     [ing("espresso", "30ml"), ing("sambuca", "15ml")]),
]


def build_taxonomy():
    categories_json = []
    style_lookup = {}  # slug -> (uuid, categoryId, familyId, flavorProfile dict)
    for cat_slug, cat_name, families in TAXONOMY:
        cat_id = uid("category:" + cat_slug)
        families_json = []
        for fam_slug, fam_name, styles in families:
            fam_id = uid("family:" + cat_slug + ":" + fam_slug)
            styles_json = []
            for style_slug, style_name, brands, abv_range, prof in styles:
                style_id = uid("style:" + style_slug)
                abv_min, abv_max = abv_range
                full_profile = dict(prof)
                full_profile["abv"] = round((abv_min + abv_max) / 2, 2)
                style_obj = {
                    "id": style_id,
                    "name": style_name,
                    "familyId": fam_id,
                    "categoryId": cat_id,
                    "exampleBrands": brands,
                    "flavorProfile": full_profile,
                    "abvMin": abv_min,
                    "abvMax": abv_max,
                }
                styles_json.append(style_obj)
                assert style_slug not in style_lookup, f"duplicate style slug {style_slug}"
                style_lookup[style_slug] = (style_id, cat_id, fam_id, full_profile, cat_name)
            families_json.append({
                "id": fam_id,
                "name": fam_name,
                "categoryId": cat_id,
                "styles": styles_json,
            })
        categories_json.append({
            "id": cat_id,
            "name": cat_name,
            "families": families_json,
        })
    return categories_json, style_lookup


# ---------------------------------------------------------------------------
# Recipe flavour profile and ABV
#
# Both are volume-weighted: each ingredient's amount is converted to millilitres
# so a 120ml pour of juice outweighs a 15ml one, and a dash of bitters barely
# moves the strength. ABV also accounts for the water that ice adds.
# ---------------------------------------------------------------------------

DASH_ML = 0.8
TSP_ML = 5.0
PINCH_ML = 0.5
LEAF_ML = 1.0
SPRIG_ML = 3.0
GARNISH_UNIT_ML = 3.0   # a wheel, twist, cherry or stick adds aroma, not volume
MUDDLED_UNIT_ML = 10.0  # a muddled wedge, slice or piece of fruit
MUDDLED_PREPS = ("muddled", "puréed", "pressed")

# What "top" means in each glass. Split evenly when a recipe has several tops.
TOP_ML_BY_GLASS = {
    "highball": 120.0, "collins": 120.0, "flute": 90.0, "wine": 90.0, "mug": 120.0,
    "hurricane": 60.0, "rocks": 60.0, "coupe": 30.0, "martini": 30.0,
}

# Bitters, seasonings and muddled herbs are concentrated: a dash or a leaf
# tastes like far more than its volume. Bitters stay below herbs so a
# bitters-led drink (Trinidad Sour) doesn't flatten every other drink's
# bitterness once the app scales notes against the catalog's maximum.
POTENCY_BY_SLUG = {
    "angostura_bitters": 3.0, "peychauds_bitters": 3.0, "orange_bitters": 3.0,
    "worcestershire": 3.0, "hot_sauce": 3.0,
    "fresh_mint": 5.0, "fresh_basil": 5.0, "fresh_rosemary": 5.0,
}

# A float sits on top and a rinse coats the glass: both reach the nose first,
# so they flavour the drink more than their volume (the Penicillin's Islay float).
AROMATIC_PREPS = ("float", "rinse")
AROMATIC_WEIGHT = 2.0

# Hot water a recipe tops with that isn't a cabinet ingredient.
EXTRA_WATER_ML = {"Hot Toddy": 90.0, "Hot Buttered Rum": 120.0}


def amount_ml(amount: str, prep, glass: str, top_count: int) -> float:
    """Approximate millilitres for an amount string such as "22ml", "2 dash" or "top"."""
    text = amount.strip().lower()
    if text == "top":
        return TOP_ML_BY_GLASS[glass] / top_count
    number, _, unit = text.partition(" ")
    if number.endswith("ml"):
        return float(number[:-2])
    qty = float(number)
    if unit == "dash":
        return qty * DASH_ML
    if unit == "tsp":
        return qty * TSP_ML
    if unit == "pinch":
        return qty * PINCH_ML
    if unit == "leaves":
        return qty * LEAF_ML
    if unit == "sprig":
        return qty * SPRIG_ML
    assert unit in ("", "wedge", "slices"), f"unknown amount unit in {amount!r}"
    muddled = prep is not None and any(p in prep for p in MUDDLED_PREPS)
    return qty * (MUDDLED_UNIT_ML if muddled else GARNISH_UNIT_ML)


def dilution_ratio(method: str, glass: str, abv_fraction: float) -> float:
    """Water from ice as a fraction of the pre-dilution volume.

    Shaken and stirred use Dave Arnold's regressions (Liquid Intelligence);
    built drinks sit on ice briefly; mugs are served hot with no ice.
    """
    x = abv_fraction
    if glass == "mug":
        return 0.0
    if method == "shake":
        return -1.567 * x * x + 1.742 * x + 0.203
    if method in ("stir", "throw"):
        return -1.21 * x * x + 1.246 * x + 0.145
    if method == "blend":
        return 0.5
    return 0.15


def compute_recipe_profile(name, glass, method, ingredients, style_lookup):
    """Volume-weighted flavour profile plus served ABV (after dilution).

    `ingredients` are (slug, amount, prep, optional) tuples; optional ones are ignored.
    """
    required = [(slug, amount, prep) for slug, amount, prep, optional in ingredients if not optional]
    top_count = sum(1 for _, amount, _ in required if amount.strip().lower() == "top") or 1

    acc = {d: 0.0 for d in DIMS}
    total_weight = 0.0
    mixed_ml = alcohol_ml = top_ml = 0.0
    for slug, amount, prep in required:
        prof = style_lookup[slug][3]
        ml = amount_ml(amount, prep, glass, top_count)
        aromatic = prep is not None and any(p in prep for p in AROMATIC_PREPS)
        weight = ml * POTENCY_BY_SLUG.get(slug, 1.0) * (AROMATIC_WEIGHT if aromatic else 1.0)
        total_weight += weight
        for d in DIMS:
            acc[d] += prof[d] * weight
        alcohol_ml += ml * prof["abv"] / 100.0
        if amount.strip().lower() == "top":
            top_ml += ml
        else:
            mixed_ml += ml

    if total_weight == 0:
        return {**{d: 0.0 for d in DIMS}, "abv": 0.0}
    result = {d: round(min(acc[d] / total_weight, 1.0), 3) for d in DIMS}

    # Tops go in after shaking/stirring, so only the mixed part takes on ice melt;
    # a built drink is poured over ice as a whole.
    if method == "build":
        diluted_ml = (mixed_ml + top_ml) * (1 + dilution_ratio(method, glass, 0.0))
    else:
        pre_abv = alcohol_ml / mixed_ml if mixed_ml else 0.0
        diluted_ml = mixed_ml * (1 + dilution_ratio(method, glass, pre_abv)) + top_ml
    final_ml = diluted_ml + EXTRA_WATER_ML.get(name, 0.0)
    result["abv"] = round(100.0 * alcohol_ml / final_ml, 2) if final_ml else 0.0
    return result


# A "low-abv" drink is at most wine/aperitivo strength once served; "no-abv" means none at all.
LOW_ABV_MAX = 15.0


def check_strength_tags(name, tags, abv):
    if abv == 0:
        assert "no-abv" in tags, f"{name}: has no alcohol but is not tagged no-abv"
    else:
        assert "no-abv" not in tags, f"{name}: tagged no-abv but computes to {abv}% ABV"
    if "low-abv" in tags:
        assert abv <= LOW_ABV_MAX, f"{name}: tagged low-abv but computes to {abv}% ABV"


GLASS_MAP = {
    "coupe": "coupe", "rocks": "rocks", "highball": "highball", "martini": "martini",
    "collins": "collins", "hurricane": "hurricane", "flute": "flute", "wine": "wineGlass",
    "mug": "mug",
}
METHOD_MAP = {"shake": "shake", "stir": "stir", "build": "build", "blend": "blend", "throw": "throw"}
DIFFICULTY_MAP = {"easy": "easy", "medium": "medium", "advanced": "advanced"}


def build_recipes(style_lookup):
    recipes_json = []
    seen_names = set()
    for (name, desc, glass, method, difficulty, tags, steps, ingredients) in RECIPES:
        assert name not in seen_names, f"duplicate recipe name {name}"
        seen_names.add(name)
        recipe_id = uid("recipe:" + name)
        ingredient_objs = []
        profile_inputs = []
        for (slug, amount, prep, optional, sub) in ingredients:
            assert slug in style_lookup, f"{name}: unknown ingredient slug {slug}"
            style_id, *_ = style_lookup[slug]
            ingredient_objs.append({
                "ingredientStyleId": style_id,
                "amount": amount,
                "preparation": prep,
                "isOptional": optional,
                "substituteNotes": sub,
            })
            profile_inputs.append((slug, amount, prep, optional))
        flavor_profile = compute_recipe_profile(name, glass, method, profile_inputs, style_lookup)
        check_strength_tags(name, tags, flavor_profile["abv"])
        recipes_json.append({
            "id": recipe_id,
            "name": name,
            "description": desc,
            "glassType": GLASS_MAP[glass],
            "method": METHOD_MAP[method],
            "ingredients": ingredient_objs,
            "steps": steps,
            "flavorProfile": flavor_profile,
            "tags": tags,
            "difficulty": DIFFICULTY_MAP[difficulty],
            "imageURL": None,
        })
    return recipes_json


def main():
    categories_json, style_lookup = build_taxonomy()
    total_styles = sum(len(f["styles"]) for c in categories_json for f in c["families"])
    print(f"Ingredient styles: {total_styles}")
    assert total_styles >= 60, f"need >=60 styles, got {total_styles}"

    recipes_json = build_recipes(style_lookup)
    print(f"Recipes: {len(recipes_json)}")
    assert len(recipes_json) >= 150, f"need >=150 recipes, got {len(recipes_json)}"

    # Referential integrity check
    valid_style_ids = {v[0] for v in style_lookup.values()}
    for r in recipes_json:
        for i in r["ingredients"]:
            assert i["ingredientStyleId"] in valid_style_ids, f"dangling ref in {r['name']}"

    # Flavour profile sanity: every style profile sums > 0 (excluding pure water-like items like club soda,
    # egg white, salt rim which are legitimately flavourless — check separately)
    zero_profile_slugs = []
    for slug, (sid, cid, fid, prof, cat_name) in style_lookup.items():
        s = sum(prof[d] for d in DIMS)
        if s == 0:
            zero_profile_slugs.append(slug)
    print(f"Zero-flavour styles (expected: neutral bases like club soda/egg white/salt/heavy cream/plain fruit): {zero_profile_slugs}")

    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "taxonomy.json").write_text(json.dumps(categories_json, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "recipes.json").write_text(json.dumps(recipes_json, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out_dir / 'taxonomy.json'} and {out_dir / 'recipes.json'}")


if __name__ == "__main__":
    main()

"""
Genererer Streger.CSV med Path ID, Path order, SVG-flag og afstand til København.

Kør fra roden af projektet:
  python exploratory/_generate_streger.py
"""

import csv
from pathlib import Path

# ---------------------------------------------------------------------------
# Kompakte SVG-flag (inline, ingen linjeskift, ingen overflødige mellemrum)
# ---------------------------------------------------------------------------
FLAGS = {
    # Tjekkiet – hvid/rød halvcirkel med blå trekant
    "CZ": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3 2">'
        '<rect width="3" height="2" fill="#d7141a"/>'
        '<rect width="3" height="1" fill="#fff"/>'
        '<polygon points="0,0 1.5,1 0,2" fill="#11457e"/>'
        "</svg>"
    ),
    # Tyskland – sort/rød/guld
    "DE": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 5 3">'
        '<rect width="5" height="1" fill="#000"/>'
        '<rect y="1" width="5" height="1" fill="#d00"/>'
        '<rect y="2" width="5" height="1" fill="#fc0"/>'
        "</svg>"
    ),
    # Danmark – rød med hvidt nordisk kors
    "DK": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 37 28">'
        '<rect width="37" height="28" fill="#c60c30"/>'
        '<rect x="12" width="5" height="28" fill="#fff"/>'
        '<rect y="11" width="37" height="6" fill="#fff"/>'
        "</svg>"
    ),
    # Island – blå med hvid/rød nordisk kors
    "IS": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 25 18">'
        '<rect width="25" height="18" fill="#003897"/>'
        '<rect x="7" width="4" height="18" fill="#fff"/>'
        '<rect y="7" width="25" height="4" fill="#fff"/>'
        '<rect x="8" width="2" height="18" fill="#d72828"/>'
        '<rect y="8" width="25" height="2" fill="#d72828"/>'
        "</svg>"
    ),
    # Ungarn – rød/hvid/grøn
    "HU": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3 2">'
        '<rect width="3" height="0.667" fill="#ce2939"/>'
        '<rect y="0.667" width="3" height="0.667" fill="#fff"/>'
        '<rect y="1.334" width="3" height="0.667" fill="#477050"/>'
        "</svg>"
    ),
    # Italien – grøn/hvid/rød lodret
    "IT": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3 2">'
        '<rect width="1" height="2" fill="#009246"/>'
        '<rect x="1" width="1" height="2" fill="#fff"/>'
        '<rect x="2" width="1" height="2" fill="#ce2b37"/>'
        "</svg>"
    ),
    # Grækenland – blå/hvide striber med kors i hjørnet
    "GR": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 27 18">'
        '<rect width="27" height="18" fill="#0d5eaf"/>'
        '<rect y="2" width="27" height="2" fill="#fff"/>'
        '<rect y="6" width="27" height="2" fill="#fff"/>'
        '<rect y="10" width="27" height="2" fill="#fff"/>'
        '<rect y="14" width="27" height="2" fill="#fff"/>'
        '<rect width="10" height="10" fill="#0d5eaf"/>'
        '<rect x="4" width="2" height="10" fill="#fff"/>'
        '<rect y="4" width="10" height="2" fill="#fff"/>'
        "</svg>"
    ),
    # Portugal – grøn/rød med gul cirkel
    "PT": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 5 3">'
        '<rect width="2" height="3" fill="#046a38"/>'
        '<rect x="2" width="3" height="3" fill="#da291c"/>'
        '<circle cx="2" cy="1.5" r="0.55" fill="#f7d117"/>'
        "</svg>"
    ),
    # Kroatien – rød/hvid/blå
    "HR": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3 2">'
        '<rect width="3" height="0.667" fill="#ff0000"/>'
        '<rect y="0.667" width="3" height="0.667" fill="#fff"/>'
        '<rect y="1.334" width="3" height="0.667" fill="#171796"/>'
        "</svg>"
    ),
    # Polen – hvid/rød
    "PL": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3 2">'
        '<rect width="3" height="1" fill="#fff"/>'
        '<rect y="1" width="3" height="1" fill="#dc143c"/>'
        "</svg>"
    ),
    # Albanien – rød med forenklet dobbeltørn
    "AL": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 7">'
        '<rect width="10" height="7" fill="#e41e20"/>'
        '<path d="M5 1L3.5 2L3 1.5L3.5 3L2.5 3.5L4 3.5L3.5 5L5 4L6.5 5L6 3.5L7.5 3.5L6.5 3L7 1.5L6.5 2Z" fill="#000"/>'
        "</svg>"
    ),
    # Norge – rød med blå/hvid nordisk kors
    "NO": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 22 16">'
        '<rect width="22" height="16" fill="#ef2b2d"/>'
        '<rect x="6" width="4" height="16" fill="#fff"/>'
        '<rect y="6" width="22" height="4" fill="#fff"/>'
        '<rect x="7" width="2" height="16" fill="#002868"/>'
        '<rect y="7" width="22" height="2" fill="#002868"/>'
        "</svg>"
    ),
    # Sverige – blå med gult nordisk kors (bruges til "Norden")
    "SE": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 10">'
        '<rect width="16" height="10" fill="#006aa7"/>'
        '<rect x="5" width="2" height="10" fill="#fecc02"/>'
        '<rect y="4" width="16" height="2" fill="#fecc02"/>'
        "</svg>"
    ),
    # UK / Skotsk saltire (Edinburgh er i Skotland)
    "GB": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 5 3">'
        '<rect width="5" height="3" fill="#003078"/>'
        '<line x1="0" y1="0" x2="5" y2="3" stroke="#fff" stroke-width="0.6"/>'
        '<line x1="5" y1="0" x2="0" y2="3" stroke="#fff" stroke-width="0.6"/>'
        "</svg>"
    ),
    # Nordmakedonien – rød med gul sol og stråler
    "MK": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2 1">'
        '<rect width="2" height="1" fill="#ce2028"/>'
        '<circle cx="1" cy="0.5" r="0.12" fill="#f7d117"/>'
        '<line x1="1" y1="0" x2="1" y2="1" stroke="#f7d117" stroke-width="0.06"/>'
        '<line x1="0.5" y1="0.5" x2="1.5" y2="0.5" stroke="#f7d117" stroke-width="0.06"/>'
        '<line x1="0.646" y1="0.146" x2="1.354" y2="0.854" stroke="#f7d117" stroke-width="0.06"/>'
        '<line x1="1.354" y1="0.146" x2="0.646" y2="0.854" stroke="#f7d117" stroke-width="0.06"/>'
        "</svg>"
    ),
}

# ---------------------------------------------------------------------------
# Destinationer: (Sted, landekode, afstand fra København i km)
# Afstande er beregnet som luftlinjestrækning (haversine).
# ---------------------------------------------------------------------------
DESTINATIONS = [
    ("Prag",          "CZ", "630 km"),
    ("Berlin",        "DE", "350 km"),
    ("Branæs",        "DK", "280 km"),
    ("Island",        "IS", "2 100 km"),
    ("Budapest",      "HU", "1 010 km"),
    ("Italien",       "IT", "1 530 km"),
    ("Grækenland",    "GR", "2 140 km"),
    ("Portugal",      "PT", "2 500 km"),
    ("Kroatien",      "HR", "1 120 km"),
    ("Krakow",        "PL", "800 km"),
    ("Tirana",        "AL", "1 680 km"),
    ("Fyn",           "DK", "140 km"),
    ("Norden",        "SE", "520 km"),
    ("Island",        "IS", "2 100 km"),
    ("Hamborg",       "DE", "290 km"),
    ("Berlin",        "DE", "350 km"),
    ("Edinburg",      "GB", "980 km"),
    ("Island",        "IS", "2 100 km"),
    ("Longyearbyen",  "NO", "2 500 km"),
    ("Samsø",         "DK", "125 km"),
    ("Prag",          "CZ", "630 km"),
    ("Skopje",        "MK", "1 650 km"),
]

OUTPUT = Path(__file__).parent / "Streger.CSV"


def main() -> None:
    rows: list[list] = [["Sted", "Path ID", "Path order", "SVG", "Afstand"]]

    for path_id, (name, flag_code, distance) in enumerate(DESTINATIONS, start=1):
        rows.append([name, path_id, 1, FLAGS[flag_code], distance])
        rows.append(["København", path_id, 0, "", ""])
        rows.append(["Aarhus",    path_id, 2, "", ""])

    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)

    print(f"Skrev {len(rows)} rækker ({len(DESTINATIONS)} destinationer) til {OUTPUT}")


if __name__ == "__main__":
    main()

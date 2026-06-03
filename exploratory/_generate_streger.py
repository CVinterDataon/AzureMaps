"""
Genererer Streger.CSV med to separate SVG-kolonner:
  - SVG_Flag   : kun landeflag (viewBox 30×20), ingen tekst
  - SVG_Afstand: kun afstandstekst som SVG (viewBox 60×14), intet flag

Branæs er i Sysslebæk, Mellemsverige → svensk flag.

Kør fra roden af projektet:
  python exploratory/_generate_streger.py
"""

import csv
from pathlib import Path

# ---------------------------------------------------------------------------
# SVG-byggere
# ---------------------------------------------------------------------------
def flag_only_svg(flag_body: str) -> str:
    """Flag uden tekst – viewBox 30×20."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 20">'
        + flag_body
        + "</svg>"
    )


def distance_only_svg(distance: str) -> str:
    """Afstandstekst uden flag – viewBox 60×14, font-size 9."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 14">'
        '<rect width="60" height="14" fill="#f7f7f7" rx="2"/>'
        f'<text x="30" y="10" text-anchor="middle" dominant-baseline="auto" '
        f'font-size="9" font-family="sans-serif" font-weight="bold" fill="#222">{distance}</text>'
        "</svg>"
    )


# ---------------------------------------------------------------------------
# Kompakte SVG-flag – kun geometri, ingen ydre <svg>-tag (tilføjes af _with_text).
# Alle koordinater er skaleret til 30×20.
# ---------------------------------------------------------------------------
_FLAGS = {
    # Tjekkiet – hvid/rød halvdel med blå trekant
    "CZ": (
        '<rect width="30" height="20" fill="#d7141a"/>'
        '<rect width="30" height="10" fill="#fff"/>'
        '<polygon points="0,0 15,10 0,20" fill="#11457e"/>'
    ),
    # Tyskland – sort/rød/guld vandrette striber
    "DE": (
        '<rect width="30" height="6.67" fill="#000"/>'
        '<rect y="6.67" width="30" height="6.67" fill="#d00"/>'
        '<rect y="13.34" width="30" height="6.66" fill="#fc0"/>'
    ),
    # Danmark – rød med hvidt nordisk kors
    "DK": (
        '<rect width="30" height="20" fill="#c60c30"/>'
        '<rect x="10" width="4" height="20" fill="#fff"/>'
        '<rect y="8" width="30" height="4" fill="#fff"/>'
    ),
    # Island – blå med hvid/rød nordisk kors
    "IS": (
        '<rect width="30" height="20" fill="#003897"/>'
        '<rect x="8" width="5" height="20" fill="#fff"/>'
        '<rect y="7.5" width="30" height="5" fill="#fff"/>'
        '<rect x="9.5" width="2" height="20" fill="#d72828"/>'
        '<rect y="9" width="30" height="2" fill="#d72828"/>'
    ),
    # Sverige – blå med gult nordisk kors (bruges til Branæs/Norden)
    "SE": (
        '<rect width="30" height="20" fill="#006aa7"/>'
        '<rect x="10" width="4" height="20" fill="#fecc02"/>'
        '<rect y="8" width="30" height="4" fill="#fecc02"/>'
    ),
    # Ungarn – rød/hvid/grøn vandrette striber
    "HU": (
        '<rect width="30" height="6.67" fill="#ce2939"/>'
        '<rect y="6.67" width="30" height="6.67" fill="#fff"/>'
        '<rect y="13.34" width="30" height="6.66" fill="#477050"/>'
    ),
    # Italien – grøn/hvid/rød lodret
    "IT": (
        '<rect width="10" height="20" fill="#009246"/>'
        '<rect x="10" width="10" height="20" fill="#fff"/>'
        '<rect x="20" width="10" height="20" fill="#ce2b37"/>'
    ),
    # Grækenland – blå/hvide striber + kors i øverste venstre hjørne
    "GR": (
        '<rect width="30" height="20" fill="#0d5eaf"/>'
        '<rect y="2.22" width="30" height="2.22" fill="#fff"/>'
        '<rect y="6.66" width="30" height="2.22" fill="#fff"/>'
        '<rect y="11.1" width="30" height="2.22" fill="#fff"/>'
        '<rect y="15.54" width="30" height="2.22" fill="#fff"/>'
        '<rect width="11" height="11.1" fill="#0d5eaf"/>'
        '<rect x="4" width="3" height="11.1" fill="#fff"/>'
        '<rect y="4.05" width="11" height="3" fill="#fff"/>'
    ),
    # Portugal – grøn 2/5, rød 3/5, gul cirkel ved grænsen
    "PT": (
        '<rect width="12" height="20" fill="#046a38"/>'
        '<rect x="12" width="18" height="20" fill="#da291c"/>'
        '<circle cx="12" cy="10" r="3.5" fill="#f7d117"/>'
    ),
    # Kroatien – rød/hvid/blå vandrette striber
    "HR": (
        '<rect width="30" height="6.67" fill="#ff0000"/>'
        '<rect y="6.67" width="30" height="6.67" fill="#fff"/>'
        '<rect y="13.34" width="30" height="6.66" fill="#171796"/>'
    ),
    # Polen – hvid/rød vandrette striber
    "PL": (
        '<rect width="30" height="10" fill="#fff"/>'
        '<rect y="10" width="30" height="10" fill="#dc143c"/>'
    ),
    # Albanien – rød med forenklet dobbeltørn
    "AL": (
        '<rect width="30" height="20" fill="#e41e20"/>'
        '<path d="M15 3L11 6L9 4.5L10.5 8.5L7.5 10.5L12 10.5'
        'L10.5 15L15 12L19.5 15L18 10.5L22.5 10.5'
        'L19.5 8.5L21 4.5L19 6Z" fill="#000"/>'
    ),
    # Norge – rød med blå/hvid nordisk kors
    "NO": (
        '<rect width="30" height="20" fill="#ef2b2d"/>'
        '<rect x="11" width="5" height="20" fill="#fff"/>'
        '<rect y="7.5" width="30" height="5" fill="#fff"/>'
        '<rect x="12" width="3" height="20" fill="#002868"/>'
        '<rect y="9" width="30" height="3" fill="#002868"/>'
    ),
    # UK / Skotsk saltire – blå med hvide diagonale kors (Edinburgh er i Skotland)
    "GB": (
        '<rect width="30" height="20" fill="#003078"/>'
        '<line x1="0" y1="0" x2="30" y2="20" stroke="#fff" stroke-width="4"/>'
        '<line x1="30" y1="0" x2="0" y2="20" stroke="#fff" stroke-width="4"/>'
    ),
    # Nordmakedonien – rød med gul sol med 8 stråler
    "MK": (
        '<rect width="30" height="20" fill="#ce2028"/>'
        '<circle cx="15" cy="10" r="3" fill="#f7d117"/>'
        '<line x1="15" y1="0" x2="15" y2="20" stroke="#f7d117" stroke-width="1.5"/>'
        '<line x1="0" y1="10" x2="30" y2="10" stroke="#f7d117" stroke-width="1.5"/>'
        '<line x1="0" y1="0" x2="30" y2="20" stroke="#f7d117" stroke-width="1.5"/>'
        '<line x1="30" y1="0" x2="0" y2="20" stroke="#f7d117" stroke-width="1.5"/>'
        '<line x1="0" y1="5" x2="30" y2="15" stroke="#f7d117" stroke-width="1.5"/>'
        '<line x1="30" y1="5" x2="0" y2="15" stroke="#f7d117" stroke-width="1.5"/>'
        '<line x1="7" y1="0" x2="23" y2="20" stroke="#f7d117" stroke-width="1.5"/>'
        '<line x1="23" y1="0" x2="7" y2="20" stroke="#f7d117" stroke-width="1.5"/>'
    ),
}


def flag_svg(code: str) -> str:
    """Bygger et komplet SVG med kun flag (30×20)."""
    return flag_only_svg(_FLAGS[code])


# ---------------------------------------------------------------------------
# Destinationer: (Sted, landekode, afstand fra København – luftlinje/haversine)
# Branæs = Sysslebæk, Mellemsverige → SE, ~480 km
# ---------------------------------------------------------------------------
DESTINATIONS = [
    ("Prag",          "CZ", "630 km"),
    ("Berlin",        "DE", "350 km"),
    ("Branæs",        "SE", "480 km"),
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
    ("Hamborg",       "DE", "290 km"),
    ("Edinburg",      "GB", "980 km"),
    ("Longyearbyen",  "NO", "2 500 km"),
    ("Samsø",         "DK", "125 km"),
    ("Skopje",        "MK", "1 650 km"),
]

OUTPUT = Path(__file__).parent / "Streger.CSV"


def main() -> None:
    rows: list[list] = [["Sted", "Path ID", "Path order", "SVG_Flag", "SVG_Afstand", "Afstand"]]

    for path_id, (name, flag_code, distance) in enumerate(DESTINATIONS, start=1):
        rows.append([name, path_id, 1, flag_svg(flag_code), distance_only_svg(distance), distance])
        rows.append(["København", path_id, 0, "", "", ""])
        rows.append(["Aarhus",    path_id, 2, "", "", ""])

    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)

    print(f"Skrev {len(rows)} rækker ({len(DESTINATIONS)} destinationer) til {OUTPUT}")


if __name__ == "__main__":
    main()

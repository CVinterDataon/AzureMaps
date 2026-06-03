"""
Beregner areal (km²) per feature i et GeoJSON-datasæt og udskriver en rangering.

Arealet beregnes ved at projicere geometrien til EPSG:25832 (UTM zone 32N),
som er standardprojektionen for Danmark og giver et godt arealanslag i meter.

Brug:
  python exploratory/geojson_area_stats.py --input data/output/kommuneinddeling_hovedstad_bornholm.geojson
  python exploratory/geojson_area_stats.py --input data/input/kommuneinddeling.geojson --label-key navn
  python exploratory/geojson_area_stats.py --input data/input/kommuneinddeling.geojson --top 10
"""

import argparse
import json
from pathlib import Path

from shapely.geometry import shape
from shapely.ops import transform
import pyproj


# EPSG:4326 → EPSG:25832 (UTM zone 32N) – velegnet til Danmark.
_WGS84 = pyproj.CRS("EPSG:4326")
_UTM32 = pyproj.CRS("EPSG:25832")
_PROJECT = pyproj.Transformer.from_crs(_WGS84, _UTM32, always_xy=True).transform

_DEFAULT_LABEL_KEYS = ["label_dk", "navn", "kommune", "name", "municipality"]


def get_label(props: dict, label_key: str | None) -> str:
    if label_key:
        return str(props.get(label_key) or "(ukendt)")
    for key in _DEFAULT_LABEL_KEYS:
        if props.get(key):
            return str(props[key])
    return "(ukendt)"


def compute_area_km2(feature: dict) -> float:
    geom = shape(feature["geometry"])
    projected = transform(_PROJECT, geom)
    return projected.area / 1_000_000  # m² → km²


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Udskriv arealstatistik (km²) per feature for et GeoJSON-datasæt."
    )
    parser.add_argument("--input", required=True, type=Path, help="GeoJSON-inputfil.")
    parser.add_argument(
        "--label-key",
        default=None,
        help="Property-nøgle, der bruges som label. Standard: forsøger label_dk, navn, kommune, name.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="Vis kun de N største features. Standard: vis alle.",
    )
    parser.add_argument(
        "--sort",
        choices=["desc", "asc"],
        default="desc",
        help="Sorteringsretning: desc (størst først) eller asc (mindst først). Standard: desc.",
    )
    args = parser.parse_args()

    input_path: Path = args.input.resolve()
    if not input_path.exists():
        parser.error(f"Inputfil ikke fundet: {input_path}")

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("type") != "FeatureCollection":
        parser.error("Inputfil er ikke en GeoJSON FeatureCollection.")

    features = data.get("features") or []
    rows: list[tuple[str, float]] = []

    for feat in features:
        if not feat.get("geometry"):
            continue
        props = feat.get("properties") or {}
        label = get_label(props, args.label_key)
        area = compute_area_km2(feat)
        rows.append((label, area))

    rows.sort(key=lambda r: r[1], reverse=(args.sort == "desc"))

    if args.top:
        rows = rows[: args.top]

    total_area = sum(r[1] for r in rows)
    col_width = max((len(r[0]) for r in rows), default=20) + 2

    print(f"\nAreal per feature – {input_path.name}")
    print(f"{'='*(col_width + 16)}")
    print(f"{'Feature':<{col_width}}{'Areal (km²)':>12}{'Andel (%)':>12}")
    print(f"{'-'*(col_width + 16)}")
    for label, area in rows:
        share = (area / total_area * 100) if total_area > 0 else 0
        print(f"{label:<{col_width}}{area:>12.1f}{share:>11.1f}%")
    print(f"{'-'*(col_width + 16)}")
    print(f"{'Total':<{col_width}}{total_area:>12.1f}{'100.0':>11}%")
    print(f"\nAntal features: {len(rows)}")


if __name__ == "__main__":
    main()

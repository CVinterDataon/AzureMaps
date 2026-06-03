"""
Forenkler geometrier i et GeoJSON-datasæt med Douglas-Peucker-algoritmen
og rapporterer fildukørelse og punkttab.

Simplificeringen sker i EPSG:25832 (meter) for at give en meningsfuld tolerance
i meter frem for grader. Outputtet konverteres tilbage til WGS84/EPSG:4326.

En høj tolerance (f.eks. 200 m) reducerer filstørrelsen markant men giver tydelig
afrunding langs kystlinjer. En lav tolerance (f.eks. 25 m) er næsten visuelt
usynlig på regionale kort.

Brug:
  # Standard: 50 m tolerance
  python exploratory/simplify_geojson.py \\
      --input data/output/kommuneinddeling_hovedstad_bornholm.geojson \\
      --output exploratory/kommuner_simplified.geojson

  # Prøv forskellige tolerancer og sammenlign filstørrelser:
  python exploratory/simplify_geojson.py \\
      --input data/input/kommuneinddeling.geojson \\
      --tolerance 200 \\
      --output exploratory/kommuner_200m.geojson
"""

import argparse
import json
from pathlib import Path

import pyproj
from shapely.geometry import mapping, shape
from shapely.ops import transform
from shapely.validation import make_valid


_WGS84 = pyproj.CRS("EPSG:4326")
_UTM32 = pyproj.CRS("EPSG:25832")
_TO_UTM = pyproj.Transformer.from_crs(_WGS84, _UTM32, always_xy=True).transform
_TO_WGS84 = pyproj.Transformer.from_crs(_UTM32, _WGS84, always_xy=True).transform


def count_coordinates(geom) -> int:
    """Tæller det totale antal koordinatpunkter i en Shapely-geometri."""
    if hasattr(geom, "exterior"):
        # Polygon
        n = len(geom.exterior.coords)
        for interior in geom.interiors:
            n += len(interior.coords)
        return n
    if hasattr(geom, "geoms"):
        return sum(count_coordinates(g) for g in geom.geoms)
    if hasattr(geom, "coords"):
        return len(geom.coords)
    return 0


def simplify_feature(feature: dict, tolerance_m: float, preserve_topology: bool) -> dict:
    geom_wgs84 = shape(feature["geometry"])
    geom_utm = transform(_TO_UTM, geom_wgs84)

    if not geom_utm.is_valid:
        geom_utm = make_valid(geom_utm)

    simplified = geom_utm.simplify(tolerance_m, preserve_topology=preserve_topology)

    if simplified.is_empty:
        # Fald tilbage til original, hvis forenkling sletter geometrien.
        simplified = geom_utm

    result_wgs84 = transform(_TO_WGS84, simplified)

    new_feature = dict(feature)
    new_feature["geometry"] = mapping(result_wgs84)
    return new_feature


def human_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / 1024 ** 2:.2f} MB"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Forenkl geometrier i et GeoJSON-datasæt og rapportér fildukørelse."
    )
    parser.add_argument("--input", required=True, type=Path, help="GeoJSON-inputfil.")
    parser.add_argument("--output", required=True, type=Path, help="GeoJSON-outputfil.")
    parser.add_argument(
        "--tolerance",
        type=float,
        default=50.0,
        help="Forenklings-tolerance i meter (Douglas-Peucker). Standard: 50.",
    )
    parser.add_argument(
        "--no-preserve-topology",
        action="store_true",
        help=(
            "Deaktivér topologi-bevarelse (hurtigere, men kan give overlappende polygoner "
            "ved kommunegrænser). Standard: topologi bevares."
        ),
    )
    args = parser.parse_args()

    input_path: Path = args.input.resolve()
    output_path: Path = args.output.resolve()

    if not input_path.exists():
        parser.error(f"Inputfil ikke fundet: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    preserve_topology = not args.no_preserve_topology

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("type") != "FeatureCollection":
        parser.error("Inputfil er ikke en GeoJSON FeatureCollection.")

    features_in = data.get("features") or []
    coords_before = 0
    coords_after = 0
    simplified_features = []

    for feat in features_in:
        if not feat.get("geometry"):
            simplified_features.append(feat)
            continue
        geom_before = shape(feat["geometry"])
        coords_before += count_coordinates(geom_before)

        simplified = simplify_feature(feat, args.tolerance, preserve_topology)
        geom_after = shape(simplified["geometry"])
        coords_after += count_coordinates(geom_after)
        simplified_features.append(simplified)

    output_data = dict(data)
    output_data["features"] = simplified_features

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, separators=(",", ":"))

    size_before = input_path.stat().st_size
    size_after = output_path.stat().st_size
    size_reduction = (1 - size_after / size_before) * 100 if size_before > 0 else 0
    coord_reduction = (1 - coords_after / coords_before) * 100 if coords_before > 0 else 0

    print(f"\nForenkling fuldført – tolerance: {args.tolerance:.0f} m")
    print(f"  Inputfil:        {human_size(size_before):>10}   ({input_path.name})")
    print(f"  Outputfil:       {human_size(size_after):>10}   ({output_path.name})")
    print(f"  Fildukørelse:    {size_reduction:>9.1f}%")
    print(f"  Punkter før:     {coords_before:>10,}")
    print(f"  Punkter efter:   {coords_after:>10,}")
    print(f"  Punktreduktion:  {coord_reduction:>9.1f}%")
    print(f"  Features:        {len(simplified_features):>10}")


if __name__ == "__main__":
    main()

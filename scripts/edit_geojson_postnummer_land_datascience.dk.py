import argparse
import json
from pathlib import Path

from shapely.geometry import GeometryCollection, MultiPolygon, Polygon, mapping, shape
from shapely.ops import unary_union
from shapely.validation import make_valid


def load_feature_collection(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as infile:
        data = json.load(infile)

    if data.get("type") != "FeatureCollection" or not isinstance(data.get("features"), list):
        raise ValueError(f"Input must be a GeoJSON FeatureCollection: {path}")

    return data


def extract_polygonal(geom):
    if geom.is_empty:
        return None

    if isinstance(geom, (Polygon, MultiPolygon)):
        return geom

    if isinstance(geom, GeometryCollection):
        polygons = []
        for child in geom.geoms:
            polygonal = extract_polygonal(child)
            if polygonal is not None and not polygonal.is_empty:
                polygons.append(polygonal)

        if not polygons:
            return None

        merged = unary_union(polygons)
        return merged if not merged.is_empty else None

    return None


def repair_geometry(geom):
    if geom.is_empty:
        return geom

    if geom.is_valid:
        return geom

    repaired = make_valid(geom)
    if repaired.is_valid:
        return repaired

    # Fallback for stubborn self-intersections/ring issues.
    buffered = repaired.buffer(0)
    return buffered


def build_land_mask(land_data: dict):
    land_geoms = []
    for feature in land_data["features"]:
        geometry = feature.get("geometry")
        if not geometry:
            continue
        land_geoms.append(repair_geometry(shape(geometry)))

    if not land_geoms:
        raise ValueError("No valid geometries found in land mask input.")

    return unary_union(land_geoms)


def clip_postnummer_features(postnr_data: dict, land_mask, min_area: float):
    output_features = []
    dropped_empty = 0
    dropped_too_small = 0

    for feature in postnr_data["features"]:
        geometry = feature.get("geometry")
        if not geometry:
            dropped_empty += 1
            continue

        source_geom = repair_geometry(shape(geometry))
        clipped = source_geom.intersection(land_mask)
        clipped_polygonal = extract_polygonal(repair_geometry(clipped))
        if clipped_polygonal is None or clipped_polygonal.is_empty:
            dropped_empty += 1
            continue

        if clipped_polygonal.area < min_area:
            dropped_too_small += 1
            continue

        new_feature = {
            "type": "Feature",
            "properties": dict(feature.get("properties") or {}),
            "geometry": mapping(clipped_polygonal),
        }
        output_features.append(new_feature)

    return output_features, dropped_empty, dropped_too_small


def transform_geojson(input_path: Path, land_mask_path: Path, output_path: Path, min_area: float) -> None:
    postnr_data = load_feature_collection(input_path)
    land_data = load_feature_collection(land_mask_path)

    land_mask = build_land_mask(land_data)
    output_features, dropped_empty, dropped_too_small = clip_postnummer_features(postnr_data, land_mask, min_area)

    output_data = {
        "type": "FeatureCollection",
        "features": output_features,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as outfile:
        json.dump(output_data, outfile, ensure_ascii=False, indent=2)
        outfile.write("\n")

    print(f"Input features: {len(postnr_data['features'])}")
    print(f"Output features: {len(output_features)}")
    print(f"Dropped (empty after clip): {dropped_empty}")
    print(f"Dropped (below min area): {dropped_too_small}")
    print(f"Output written to: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clip postnummer GeoJSON polygons to municipality land mask (remove sea areas)."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/input/postnummerinddeling.geojson"),
        help="Path to postnummer input GeoJSON.",
    )
    parser.add_argument(
        "--land-mask",
        type=Path,
        default=Path("data/input/kommuneinddeling.geojson"),
        help="Path to municipality GeoJSON used as land mask.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/output/postnummerinddeling_land.geojson"),
        help="Path to output GeoJSON.",
    )
    parser.add_argument(
        "--min-area",
        type=float,
        default=0.0,
        help="Minimum geometry area to keep after clipping.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    transform_geojson(args.input, args.land_mask, args.output, args.min_area)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
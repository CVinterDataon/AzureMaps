import argparse
import json
from pathlib import Path

import geopandas as gpd
from shapely.ops import unary_union


def strip_z_from_coordinates(coords):
    if isinstance(coords, list) and coords:
        if isinstance(coords[0], (int, float)):
            return coords[:2]
        return [strip_z_from_coordinates(item) for item in coords]
    return coords


def strip_z_from_feature_collection(geojson_obj: dict) -> int:
    stripped = 0
    for feature in geojson_obj.get("features", []):
        geometry = feature.get("geometry") or {}
        coords = geometry.get("coordinates")
        if coords is None:
            continue

        def count_3d(c):
            if isinstance(c, list) and c:
                if isinstance(c[0], (int, float)):
                    return 1 if len(c) >= 3 else 0
                return sum(count_3d(v) for v in c)
            return 0

        stripped += count_3d(coords)
        geometry["coordinates"] = strip_z_from_coordinates(coords)

    return stripped


def postnummer_is_non_standard_or_range(value) -> bool:
    txt = str(value or "").strip()
    if not txt:
        return True

    # Range values such as "1000-1499" should be excluded.
    if "-" in txt:
        return True

    # Keep only standard 4-digit postnummer values.
    return not (txt.isdigit() and len(txt) == 4)


def ensure_wgs84(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)
    return gdf.to_crs(epsg=4326)


def clip_to_municipality_land(gdf: gpd.GeoDataFrame, land_mask_path: Path) -> tuple[gpd.GeoDataFrame, int]:
    land_gdf = gpd.read_file(land_mask_path)
    if len(land_gdf) == 0:
        raise ValueError(f"Land mask has 0 rows: {land_mask_path}")

    land_gdf = ensure_wgs84(land_gdf)
    land_union = unary_union(land_gdf.geometry)

    before = len(gdf)
    gdf = gdf.copy()
    gdf["geometry"] = gdf.geometry.intersection(land_union)
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].copy()
    removed = before - len(gdf)
    return gdf, removed


def make_postnumre_unique(gdf: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, int]:
    before = len(gdf)

    agg = {}
    if "navn" in gdf.columns:
        agg["navn"] = "first"

    dissolved = gdf.dissolve(by="postnummer", aggfunc=agg if agg else "first")
    dissolved = dissolved.reset_index()
    removed = before - len(dissolved)
    return dissolved, removed


def convert_gpkg_to_geojson(
    input_path: Path,
    output_path: Path,
    simplify_tolerance: float,
    land_mask_path: Path,
) -> None:
    if str(input_path) == "dagi.gpkg":
        # Requested baseline example.
        gdf = gpd.read_file("dagi.gpkg")
    else:
        gdf = gpd.read_file(input_path)

    if len(gdf) == 0:
        fallback = Path("data/input/DAGI_V1_Postnummerinddeling_TotalDownload_gpkg_Current_645.gpkg")
        if input_path != fallback and fallback.exists():
            print(f"Input has 0 rows, using fallback source: {fallback}")
            gdf = gpd.read_file(fallback)

        if len(gdf) == 0:
            raise ValueError(
                f"Input contains 0 rows: {input_path}. "
                "The selected DAGI file/layer appears empty."
            )

    # Azure Maps expects WGS84 longitude/latitude coordinates.
    gdf = ensure_wgs84(gdf)

    if simplify_tolerance > 0:
        gdf["geometry"] = gdf.geometry.simplify(simplify_tolerance, preserve_topology=True)

    source_rows = len(gdf)
    if "postnummer" in gdf.columns:
        keep_mask = ~gdf["postnummer"].apply(postnummer_is_non_standard_or_range)
        gdf = gdf.loc[keep_mask].copy()

    # Defensive fallback: some dataframe operations can drop GeoDataFrame typing.
    if not isinstance(gdf, gpd.GeoDataFrame) and "geometry" in gdf.columns:
        gdf = gpd.GeoDataFrame(gdf, geometry="geometry", crs="EPSG:4326")

    removed_non_standard_or_range = source_rows - len(gdf)

    if "postnummer" not in gdf.columns:
        raise ValueError("Missing required 'postnummer' column after filtering.")

    gdf, removed_non_land = clip_to_municipality_land(gdf, land_mask_path)
    gdf, removed_duplicates = make_postnumre_unique(gdf)

    keep_columns = [col for col in ["postnummer", "navn", "geometry"] if col in gdf.columns]
    if keep_columns:
        gdf = gdf[keep_columns]

    geojson_obj = json.loads(gdf.to_json(drop_id=True))
    geojson_obj.pop("crs", None)
    stripped_count = strip_z_from_feature_collection(geojson_obj)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as outfile:
        json.dump(geojson_obj, outfile, ensure_ascii=False, indent=2)
        outfile.write("\n")

    print(f"Input rows: {source_rows}")
    print(f"Removed rows (range/non-standard postnummer): {removed_non_standard_or_range}")
    print(f"Removed rows (empty after land clip): {removed_non_land}")
    print(f"Removed duplicate rows (after postnummer union): {removed_duplicates}")
    print(f"Output rows: {len(gdf)}")
    print(f"Stripped 3D coordinate tuples: {stripped_count}")
    print(f"Output written to: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read DAGI GPKG postnummer data and export GeoJSON."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/input/DAGI_V2_Postnummerinddeling_500000_TotalDownload_gpkg_Current_118.gpkg"),
        help="Path to DAGI .gpkg input file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/output/postnummerinddeling_dagi.geojson"),
        help="Path to output GeoJSON file.",
    )
    parser.add_argument(
        "--land-mask",
        type=Path,
        default=Path("data/input/kommuneinddeling.geojson"),
        help="Path to municipality GeoJSON used as land mask for water clipping.",
    )
    parser.add_argument(
        "--simplify-tolerance",
        type=float,
        default=0.0001,
        help="Geometry simplify tolerance in degrees after reprojection to EPSG:4326.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    convert_gpkg_to_geojson(args.input, args.output, args.simplify_tolerance, args.land_mask)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
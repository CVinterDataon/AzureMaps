import argparse
from pathlib import Path

import geopandas as gpd


def convert_gpkg_to_geojson(input_path: Path, output_path: Path) -> None:
    if str(input_path) == "dagi.gpkg":
        # Requested baseline example.
        gdf = gpd.read_file("dagi.gpkg")
    else:
        gdf = gpd.read_file(input_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(output_path, driver="GeoJSON")
    print(f"Input rows: {len(gdf)}")
    print(f"Output written to: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read DAGI GPKG postnummer data and export GeoJSON."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/input/DAGI_V1_Postnummerinddeling_TotalDownload_gpkg_Current_645.gpkg"),
        help="Path to DAGI .gpkg input file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/output/postnummerinddeling_dagi.geojson"),
        help="Path to output GeoJSON file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    convert_gpkg_to_geojson(args.input, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
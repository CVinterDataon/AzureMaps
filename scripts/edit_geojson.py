import json
import sys
from pathlib import Path


def load_geojson(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as infile:
        data = json.load(infile)

    if not isinstance(data, dict):
        raise ValueError("GeoJSON root must be an object.")

    if data.get("type") != "FeatureCollection":
        raise ValueError("GeoJSON must have type='FeatureCollection'.")

    features = data.get("features")
    if not isinstance(features, list):
        raise ValueError("GeoJSON FeatureCollection must contain a 'features' array.")

    return data


def save_geojson(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=2)
        outfile.write("\n")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: python scripts/edit_geojson.py <input.geojson> <output.geojson>")
        return 1

    input_path = Path(argv[1])
    output_path = Path(argv[2])

    if not input_path.exists():
        print(f"Input file does not exist: {input_path}")
        return 1

    try:
        geojson_data = load_geojson(input_path)
        save_geojson(geojson_data, output_path)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Wrote GeoJSON to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

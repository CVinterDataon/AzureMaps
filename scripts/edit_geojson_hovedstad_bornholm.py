import argparse
import copy
import json
import unicodedata
from pathlib import Path
from typing import Iterable


SCALE = 2.4  # Skaleringsfaktor for kopien af hovedstadskommunerne.
GAP_NORTH_OF_CAPITAL = -0.4  # Lodret afstand mellem original Hovedstaden og den forstørrede kopi.
GAP_BORNHOLM_ABOVE_COPY = 0.20  # Lodret afstand mellem forstørret Hovedstaden og flyttet Bornholm.
EXTRA_EAST_SHIFT = 0.45  # Ekstra forskydning mod øst for kopien af hovedstadskommunerne.
EXTRA_NORTH_SHIFT = 0.75  # Ekstra forskydning mod nord for at undgå overlap med Nordsjælland.
FRAME_PADDING = 0.08  # Margin mellem geometri og ramme.

# Brugerdefinerede hovedstadskommuner.
CAPITAL_MUNICIPALITY_NAMES = {
    "København",
    "Frederiksberg",
    "Dragør",
    "Tårnby",
    "Gentofte",
    "Lyngby-Tårbæk",
    "Rudersdal",
    "Hørsholm",
    "Furesø",
    "Gladsaxe",
    "Herlev",
    "Ballerup",
    "Albertslund",
    "Glostrup",
    "Rødovre",
    "Vallensbæk",
    "Brøndby",
    "Hvidovre",
}

# Bornholm-navne.
BORNHOLM_NAME_VALUES = {
    "Bornholm",
    "Christiansø",
}

NAME_KEYS = ["label_dk", "navn", "kommune", "municipality", "name"]

MANUAL_NAME_FIXES = {
    "nordfyns": "Nordfyn",
    "vesthimmerlands": "Vesthimmerland",
}

REGION_BY_CODE = {
    "1085": "Sjælland",
    "1084": "Hovedstaden",
    "1083": "Syddanmark",
    "1082": "Midtjylland",
    "1081": "Nordjylland",
}

def normalize_text(value: str) -> str:
    txt = (value or "").strip().lower()
    txt = txt.replace("æ", "ae").replace("ø", "oe").replace("å", "aa")
    txt = "".join(ch for ch in unicodedata.normalize("NFKD", txt) if not unicodedata.combining(ch))
    allowed = []
    for ch in txt:
        if ch.isalnum() or ch in {" ", "-"}:
            allowed.append(ch)
    return "".join(allowed)

CAPITAL_MUNICIPALITIES = {normalize_text(name) for name in CAPITAL_MUNICIPALITY_NAMES}
BORNHOLM_NAMES = {normalize_text(name) for name in BORNHOLM_NAME_VALUES}

def apply_manual_name_fixes(feature: dict) -> None:
    props = feature.get("properties") or {}
    source_value = ""
    source_key = ""

    for key in NAME_KEYS:
        if props.get(key):
            source_key = key
            source_value = str(props[key])
            break

    if not source_value:
        return

    fixed = MANUAL_NAME_FIXES.get(normalize_text(source_value))
    if not fixed:
        return

    props[source_key] = fixed
    if "label_dk" in props:
        props["label_dk"] = fixed
    if "navn" in props:
        props["navn"] = fixed
    if "kommune" in props:
        props["kommune"] = fixed
    if "name" in props:
        props["name"] = fixed
    if "label_en" in props:
        props["label_en"] = fixed

def apply_region_name(feature: dict) -> None:
    props = feature.get("properties") or {}
    code = str(props.get("regionskode") or "").strip()
    if not code:
        return

    region_name = REGION_BY_CODE.get(code)
    if region_name:
        props["Region"] = region_name

def get_feature_name(feature: dict) -> str:
    props = feature.get("properties") or {}
    for key in NAME_KEYS:
        if props.get(key):
            return str(props[key])
    return ""

def is_capital_feature(feature: dict) -> bool:
    normalized_name = normalize_text(get_feature_name(feature))
    if not normalized_name:
        return False

    tokens = normalized_name.replace("-", " ").split()
    if tokens and tokens[0] == "koebenhavn":
        return True

    normalized_with_hyphen = "-".join(tokens)
    return normalized_with_hyphen in CAPITAL_MUNICIPALITIES


def is_bornholm_feature(feature: dict) -> bool:
    normalized_name = normalize_text(get_feature_name(feature))
    if not normalized_name:
        return False

    tokens = normalized_name.replace("-", " ").split()
    normalized_with_hyphen = "-".join(tokens)
    return normalized_with_hyphen in BORNHOLM_NAMES or (tokens and tokens[0] in BORNHOLM_NAMES)


def iter_geometry_points(geometry: dict) -> Iterable[list[float]]:
    gtype = geometry.get("type")
    coords = geometry.get("coordinates")
    if coords is None:
        return

    if gtype == "Point":
        yield coords
    elif gtype == "MultiPoint" or gtype == "LineString":
        for pt in coords:
            yield pt
    elif gtype == "MultiLineString" or gtype == "Polygon":
        for ring in coords:
            for pt in ring:
                yield pt
    elif gtype == "MultiPolygon":
        for poly in coords:
            for ring in poly:
                for pt in ring:
                    yield pt


def bbox_of_features(features: list[dict]) -> tuple[float, float, float, float]:
    xs = []
    ys = []
    for feature in features:
        geometry = feature.get("geometry")
        if not geometry:
            continue
        for pt in iter_geometry_points(geometry):
            if isinstance(pt, list) and len(pt) >= 2:
                xs.append(pt[0])
                ys.append(pt[1])

    if not xs or not ys:
        raise ValueError("No coordinates found in selected features.")

    return min(xs), min(ys), max(xs), max(ys)


def scale_and_move_geometry(geometry: dict, xmin: float, ymin: float, scale: float, dx: float, dy: float) -> None:
    for pt in iter_geometry_points(geometry):
        x = pt[0]
        y = pt[1]
        scaled_x = (x - xmin) * scale + xmin
        scaled_y = (y - ymin) * scale + ymin
        pt[0] = scaled_x + dx
        pt[1] = scaled_y + dy


def move_geometry(geometry: dict, dx: float, dy: float) -> None:
    for pt in iter_geometry_points(geometry):
        pt[0] = pt[0] + dx
        pt[1] = pt[1] + dy


def make_bbox_frame_feature(min_x: float, min_y: float, max_x: float, max_y: float, name: str, frame_type: str) -> dict:
    # A closed rectangle as a LineString (LinearRing) – lightweight and universally
    # supported by GeoJSON consumers including Power BI Azure Maps.
    ring = [
        [min_x, min_y],
        [max_x, min_y],
        [max_x, max_y],
        [min_x, max_y],
        [min_x, min_y],
    ]

    return {
        "type": "Feature",
        "properties": {
            "navn": name,
            "label_dk": name,
            "label_en": name,
            "is_frame": True,
            "frame_type": frame_type,
            "frame_visual": "linestring",
        },
        "geometry": {
            "type": "LineString",
            "coordinates": ring,
        },
    }


def transform_geojson(input_path: Path, output_path: Path) -> None:
    with input_path.open("r", encoding="utf-8") as infile:
        data = json.load(infile)

    if data.get("type") != "FeatureCollection" or not isinstance(data.get("features"), list):
        raise ValueError("Input must be a GeoJSON FeatureCollection.")

    original_features = data["features"]
    for feature in original_features:
        apply_manual_name_fixes(feature)
        apply_region_name(feature)

    capital_features = [f for f in original_features if is_capital_feature(f)]
    bornholm_features = [f for f in original_features if is_bornholm_feature(f)]

    if not capital_features:
        raise ValueError("No capital municipality features found in input data.")

    cap_xmin, cap_ymin, cap_xmax, cap_ymax = bbox_of_features(capital_features)

    scaled_min_x = cap_xmin
    scaled_min_y = cap_ymin
    scaled_max_x = cap_xmin + (cap_xmax - cap_xmin) * SCALE
    scaled_max_y = cap_ymin + (cap_ymax - cap_ymin) * SCALE

    source_center_x = (cap_xmin + cap_xmax) / 2.0
    scaled_center_x = (scaled_min_x + scaled_max_x) / 2.0

    dx_copy = source_center_x - scaled_center_x + EXTRA_EAST_SHIFT
    dy_copy = (cap_ymax + GAP_NORTH_OF_CAPITAL + EXTRA_NORTH_SHIFT) - scaled_min_y

    copied_capital_features = []
    for feature in capital_features:
        feature_copy = copy.deepcopy(feature)
        geom = feature_copy.get("geometry")
        if geom:
            scale_and_move_geometry(geom, cap_xmin, cap_ymin, SCALE, dx_copy, dy_copy)

        props = feature_copy.setdefault("properties", {})
        props["is_hovedstad_copy"] = True
        props["copy_source"] = "hovedstad"
        copied_capital_features.append(feature_copy)

    copied_bbox = bbox_of_features(copied_capital_features)

    moved_bornholm_features = []
    if bornholm_features:
        bh_xmin, bh_ymin, bh_xmax, bh_ymax = bbox_of_features(bornholm_features)
        bh_center_x = (bh_xmin + bh_xmax) / 2.0
        copied_center_x = (copied_bbox[0] + copied_bbox[2]) / 2.0

        dx_bh = copied_center_x - bh_center_x
        dy_bh = (copied_bbox[3] + GAP_BORNHOLM_ABOVE_COPY) - bh_ymin

        for feature in original_features:
            if is_bornholm_feature(feature) and feature.get("geometry"):
                move_geometry(feature["geometry"], dx_bh, dy_bh)
                moved_bornholm_features.append(feature)

    copied_frame = make_bbox_frame_feature(
        copied_bbox[0] - FRAME_PADDING,
        copied_bbox[1] - FRAME_PADDING,
        copied_bbox[2] + FRAME_PADDING,
        copied_bbox[3] + FRAME_PADDING,
        "Ramme - Forstørret Hovedstad",
        "capital_copy",
    )
    frame_features = [copied_frame]

    if moved_bornholm_features:
        bh_box = bbox_of_features(moved_bornholm_features)
        bornholm_frame = make_bbox_frame_feature(
            bh_box[0] - FRAME_PADDING,
            bh_box[1] - FRAME_PADDING,
            bh_box[2] + FRAME_PADDING,
            bh_box[3] + FRAME_PADDING,
            "Ramme - Bornholm",
            "bornholm",
        )
        frame_features.append(bornholm_frame)

    data["features"].extend(copied_capital_features)
    data["features"].extend(frame_features)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False)

    print(f"Capital features copied: {len(copied_capital_features)}")
    print(f"Bornholm features moved: {len(bornholm_features)}")
    print(f"Frames added: {1 + (1 if moved_bornholm_features else 0)}")
    print(f"Output written to: {output_path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create enlarged copied capital-area features north of Copenhagen and move Bornholm above them."
    )
    parser.add_argument(
        "--input",
        default=str(Path("data/input/kommuneinddeling.geojson")),
        help="Input GeoJSON path",
    )
    parser.add_argument(
        "--output",
        default=str(Path("data/output/kommuneinddeling_hovedstad_bornholm.geojson")),
        help="Output GeoJSON path",
    )

    args = parser.parse_args()
    transform_geojson(Path(args.input), Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Genererer en selvstændig HTML-fil, der viser et GeoJSON-lag i Azure Maps Web SDK.

Features:
  - Indlæser GeoJSON inline i HTML'en (ingen serverafhængighed).
  - Klikpopup med alle feature-properties.
  - Valgfri choropleth-farvelagdeling baseret på en numerisk property.
  - Automatisk centrering og zoom til datasættes bounding box.

Brug:
  python exploratory/generate_azure_maps_html.py \\
      --input data/output/kommuneinddeling_hovedstad_bornholm.geojson \\
      --key <din-azure-maps-nøgle> \\
      --output exploratory/kort.html

  # Med choropleth-farve baseret på en numerisk kolonne:
  python exploratory/generate_azure_maps_html.py \\
      --input data/output/kommuneinddeling_hovedstad_bornholm.geojson \\
      --key <din-azure-maps-nøgle> \\
      --color-property areal_km2 \\
      --output exploratory/kort_areal.html
"""

import argparse
import json
from pathlib import Path


_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="da">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <link rel="stylesheet" href="https://atlas.microsoft.com/sdk/javascript/mapcontrol/3/atlas.min.css" />
  <script src="https://atlas.microsoft.com/sdk/javascript/mapcontrol/3/atlas.min.js"></script>
  <style>
    html, body {{ margin: 0; padding: 0; height: 100%; }}
    #map {{ width: 100%; height: 100vh; }}
    .popup-content {{ font-family: sans-serif; font-size: 13px; max-width: 260px; }}
    .popup-content table {{ border-collapse: collapse; width: 100%; }}
    .popup-content td {{ padding: 3px 6px; vertical-align: top; }}
    .popup-content tr:nth-child(even) {{ background: #f4f4f4; }}
    .popup-content td:first-child {{ font-weight: bold; color: #555; white-space: nowrap; }}
  </style>
</head>
<body>
<div id="map"></div>
<script>
const GEOJSON = {geojson_json};
const COLOR_PROPERTY = {color_property_js};

const map = new atlas.Map("map", {{
  authOptions: {{
    authType: "subscriptionKey",
    subscriptionKey: "{subscription_key}"
  }},
  language: "da-DK",
  style: "road"
}});

map.events.add("ready", function () {{
  const source = new atlas.source.DataSource();
  map.sources.add(source);
  source.add(GEOJSON);

  // Centrér kortet på datasættets bounding box.
  const bbox = atlas.data.BoundingBox.fromData(GEOJSON);
  map.setCamera({{ bounds: bbox, padding: 40 }});

  // Choropleth-farvelagdeling – kun aktiv, hvis COLOR_PROPERTY er sat.
  let fillColor = "#0078d4";
  if (COLOR_PROPERTY) {{
    const values = GEOJSON.features
      .map(f => f.properties && f.properties[COLOR_PROPERTY])
      .filter(v => typeof v === "number" && isFinite(v));
    const minVal = Math.min(...values);
    const maxVal = Math.max(...values);
    fillColor = [
      "interpolate", ["linear"],
      ["get", COLOR_PROPERTY],
      minVal, "#cce5ff",
      maxVal, "#003d80"
    ];
  }}

  const polygonLayer = new atlas.layer.PolygonLayer(source, null, {{
    fillColor: fillColor,
    fillOpacity: 0.55
  }});
  const lineLayer = new atlas.layer.LineLayer(source, null, {{
    strokeColor: "#004a99",
    strokeWidth: 1
  }});
  map.layers.add([polygonLayer, lineLayer]);

  // Klikpopup med feature-properties.
  const popup = new atlas.Popup({{ pixelOffset: [0, -10] }});

  map.events.add("click", polygonLayer, function (e) {{
    if (!e.shapes || e.shapes.length === 0) return;
    const props = e.shapes[0].getProperties();
    const rows = Object.entries(props)
      .filter(([, v]) => v !== null && v !== undefined && v !== "")
      .map(([k, v]) => `<tr><td>${{k}}</td><td>${{v}}</td></tr>`)
      .join("");
    popup.setOptions({{
      position: e.position,
      content: `<div class="popup-content"><table>${{rows}}</table></div>`
    }});
    popup.open(map);
  }});

  map.events.add("mouseover", polygonLayer, function () {{
    map.getCanvas().style.cursor = "pointer";
  }});
  map.events.add("mouseleave", polygonLayer, function () {{
    map.getCanvas().style.cursor = "";
  }});
}});
</script>
</body>
</html>
"""


def build_title(input_path: Path) -> str:
    return f"Azure Maps – {input_path.stem}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generér en selvstændig HTML-fil med et Azure Maps-kort for et GeoJSON-datasæt."
    )
    parser.add_argument("--input", required=True, type=Path, help="GeoJSON-inputfil.")
    parser.add_argument("--key", required=True, help="Azure Maps-abonnementsnøgle.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="HTML-outputfil. Standard: samme mappe som --input med .html-endelse.",
    )
    parser.add_argument(
        "--color-property",
        default=None,
        help=(
            "Numerisk feature-property, der bruges til choropleth-farvelagdeling. "
            "Udelad for ensartet blå farve."
        ),
    )
    args = parser.parse_args()

    input_path: Path = args.input.resolve()
    if not input_path.exists():
        parser.error(f"Inputfil ikke fundet: {input_path}")

    output_path: Path = args.output.resolve() if args.output else input_path.with_suffix(".html")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    geojson_json = json.dumps(geojson_data, ensure_ascii=False)
    color_property_js = f'"{args.color_property}"' if args.color_property else "null"

    html = _HTML_TEMPLATE.format(
        title=build_title(input_path),
        geojson_json=geojson_json,
        subscription_key=args.key,
        color_property_js=color_property_js,
    )

    output_path.write_text(html, encoding="utf-8")
    print(f"HTML-fil skrevet til: {output_path}")
    print(f"Åbn filen i en browser for at se kortet.")


if __name__ == "__main__":
    main()

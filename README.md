# AzureMaps

Minimal workspace til scripts, der redigerer JSON/GeoJSON-filer.

## Struktur

- `scripts/`: Python scripts til databehandling og redigering
- `data/input/`: inputfiler (GeoJSON)
- `data/output/`: genererede outputfiler
- `tests/`: testfiler

## Hurtig start

1. Læg en GeoJSON fil i `data/input/`, fx `sample.geojson`.
2. Kør scriptet:

```powershell
python scripts/edit_geojson.py data/input/sample.geojson data/output/sample_out.geojson
```

Scriptet validerer, at input er en GeoJSON `FeatureCollection`, og skriver derefter filen ud igen i formatteret JSON.

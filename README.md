# AzureMaps

Minimal workspace til scripts, der redigerer JSON/GeoJSON-filer.

Alt indhold i dette repository er genereret med GitHub Copilot i Auto-mode.

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

## Fjern hav-arealer fra postnumre

Scriptet `scripts/edit_geojson_postnummer_land_datascience.dk.py` klipper postnummergeometrier med kommunegeometrier som landmaske.
Det fjerner de store udtræk i havet, som ellers kan give unaturlige polygoner.

Eksempel:

```powershell
python scripts/edit_geojson_postnummer_land_datascience.dk.py --input data/input/postnummerinddeling.geojson --land-mask data/input/kommuneinddeling.geojson --output data/output/postnummerinddeling_land.geojson
```

## Konverter DAGI GPKG til GeoJSON

Scriptet `scripts/edit_geojson_postnummer_land_DAGI.py` laeser DAGI GPKG-filen og gemmer en GeoJSON-fil i `data/output/`.

Eksempel:

```powershell
python scripts/edit_geojson_postnummer_land_DAGI.py --input data/input/DAGI_V1_Postnummerinddeling_TotalDownload_gpkg_Current_645.gpkg --output data/output/postnummerinddeling_dagi.geojson
```

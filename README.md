# AzureMaps

Minimal workspace til scripts, der redigerer JSON/GeoJSON-filer.

Alt indhold i dette repository er genereret med GitHub Copilot i Auto-mode.

## Struktur

- `scripts/`: Python scripts til databehandling og redigering
- `data/input/`: inputfiler (GeoJSON og GPKG) — store filer er ikke inkluderet i repo, se nedenfor
- `data/output/`: genererede outputfiler
- `tests/`: testfiler

## Opsætning

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Inputfiler du selv skal downloade

Store inputfiler er ikke inkluderet i Git. Læg dem i `data/input/` med præcis de filnavne, der er angivet herunder.

### Kommuneredigering

Bruges af: `edit_geojson_hovedstad_bornholm.py`, `edit_geojson_postnummer_land_datascience.dk.py`, `create_trip_locations.py`

| Fil | Kilde |
|-----|-------|
| `kommuneinddeling.geojson` | [datascience.dk – Kommuner](https://www.datascience.dk/kommuneinddeling-i-geojson) |

### Postnummerredigering (datascience.dk-kilde)

Bruges af: `edit_geojson_postnummer_land_datascience.dk.py`

| Fil | Kilde |
|-----|-------|
| `postnummerinddeling.geojson` | [datascience.dk – Postnumre](https://www.datascience.dk/postnummerinddeling-i-geojson) |
| `kommuneinddeling.geojson` | Se ovenfor |

### Postnummerredigering (DAGI-kilde)

Bruges af: `edit_geojson_postnummer_land_DAGI.py`

| Fil | Kilde | Download-navn |
|-----|-------|---------------|
| `DAGI_V2_Postnummerinddeling_500000_TotalDownload_gpkg_Current_118.gpkg` | [Dataforsyningen – DAGI](https://dataforsyningen.dk/data/3978) → *Postnummerinddeling* → *GeoPackage* | Omdøb til det præcise filnavn |
| `kommuneinddeling.geojson` | Se ovenfor | |

> **Tip:** scriptet falder automatisk tilbage til `DAGI_V1_...` hvis V2-filen ikke findes.

---

## Fjern hav-arealer fra postnumre

Scriptet `scripts/edit_geojson_postnummer_land_datascience.dk.py` klipper postnummergeometrier med kommunegeometrier som landmaske.
Det fjerner de store udtræk i havet, som ellers kan give unaturlige polygoner.

```powershell
python scripts/edit_geojson_postnummer_land_datascience.dk.py --input data/input/postnummerinddeling.geojson --land-mask data/input/kommuneinddeling.geojson --output data/output/postnummerinddeling_land.geojson
```

## Konverter DAGI GPKG til GeoJSON

Scriptet `scripts/edit_geojson_postnummer_land_DAGI.py` læser DAGI GPKG-filen og gemmer en GeoJSON-fil i `data/output/`.

```powershell
python scripts/edit_geojson_postnummer_land_DAGI.py --input data/input/DAGI_V2_Postnummerinddeling_500000_TotalDownload_gpkg_Current_118.gpkg --output data/output/postnummerinddeling_dagi.geojson
```

## Udtræk hovedstadsregion og Bornholm

```powershell
python scripts/edit_geojson_hovedstad_bornholm.py
```

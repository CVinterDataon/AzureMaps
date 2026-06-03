# AzureMaps

Minimal workspace til scripts, der redigerer JSON/GeoJSON-filer.

Alt indhold i dette repository er genereret med GitHub Copilot i Auto-mode.

## Struktur

- `scripts/`: Python scripts til databehandling og redigering
- `data/input/`: inputfiler (GeoJSON) — store filer er ikke inkluderet i repo, se nedenfor
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

| Fil | Bruges af | Kilde |
|-----|-----------|-------|
| `kommuneinddeling.geojson` | alle scripts | [datascience.dk – Kommuner](https://www.datascience.dk/kommuneinddeling-i-geojson) |
| `postnummerinddeling.geojson` | `edit_geojson_postnummer_land_datascience.dk.py` | [datascience.dk – Postnumre](https://www.datascience.dk/postnummerinddeling-i-geojson) |

---

## Fjern hav-arealer fra postnumre

`scripts/edit_geojson_postnummer_land_datascience.dk.py` klipper postnummergeometrier med kommunegeometrier som landmaske og fjerner de store vandarealer på kystpostnumre.

```powershell
python scripts/edit_geojson_postnummer_land_datascience.dk.py --input data/input/postnummerinddeling.geojson --land-mask data/input/kommuneinddeling.geojson --output data/output/postnummerinddeling_land.geojson
```

## Udtræk hovedstadsregion og Bornholm

`scripts/edit_geojson_hovedstad_bornholm.py` udtrækker kommunerne i Hovedstadsregionen og Bornholm fra `kommuneinddeling.geojson` og tilføjer normaliserede navne og regionslabels.

```powershell
python scripts/edit_geojson_hovedstad_bornholm.py
```

# Exploratory scripts

Disse scripts er **ikke beskrevet i LinkedIn-artiklen**. Det er ting, jeg har undersøgt undervejs – sidespor og eksperimenter, der ikke passede ind i den røde tråd.

Tag det, hvis det er sjovt.

---

Der er desuden en Power BI-fil i denne mappe, som illustrerer de Azure Maps-funktioner, der beskrives i artiklen, direkte i et rapport-format.

## Scripts

| Fil | Hvad den gør |
|-----|-------------|
| `generate_azure_maps_html.py` | Genererer en selvstændig HTML-fil, der viser et GeoJSON-lag i Azure Maps Web SDK med klikpopup og farvelagdeling. |
| `geojson_area_stats.py` | Beregner areal (km²) per feature og udskriver en rangering. Nyttigt til at forstå datasættets størrelsesfordeling. |
| `simplify_geojson.py` | Forenkler geometrier med en konfigurerbar toleranceparameter og rapporterer fildukørelse. |

## Opsætning

Samme virtuelle miljø som de øvrige scripts – se roden af repositoryet.

```powershell
.venv\Scripts\Activate.ps1
```

De tre scripts bruger kun `shapely` og `geopandas`, som allerede er installeret via `requirements.txt`.  
`generate_azure_maps_html.py` kræver desuden en gyldig **Azure Maps-abonnementsnøgle** (`--key`).

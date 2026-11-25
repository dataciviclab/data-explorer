# Data Loader

Ogni file `.json.py` in questa directory è un **data loader** per una pagina specifica: produce JSON consumato dalle pagine Observable. Due regimi:

- **mart** (preferito) — legge una tabella mart dichiarata nella pipeline, nessuna SQL nel frontend;
- **clean** (legacy) — aggrega dal clean con DuckDB, per i dataset senza mart equivalente.

Il loader resta un file per pagina: il contratto dati condiviso è in `_views.py`.

## Naming

Il nome del file segue lo slug URL della pagina (con trattini), eventualmente con un suffisso che specifica la vista:

- `<slug-url>.json.py` — loader principale per una pagina
- `<slug-url>-<vista>.json.py` — loader per una vista specifica (es. per regione, per comune)

Esempi:
- `aifa-spesa.json.py` — loader per la pagina "Spesa farmaceutica"
- `irpef-regioni.json.py` — vista aggregata per regione
- `ispra-comuni.json.py` — vista aggregata per comune

Lo slug interno (con underscore, es. `aifa_spesa_consumo`) che identifica il parquet su GCS viene passato come parametro `slug=` a `load_dataset()` — non ha relazione col nome del file.

## Contratto dati: `_views.py` (mart, non SQL)

I loader nuovi leggono i **mart** dichiarati nel registry del repo e non
scrivono SQL: l'aggregazione vive nella pipeline, dove è testata.

```python
import sys
sys.path.insert(0, "src/data")
from _views import group_rows, mart_rows, write

trend = mart_rows(
    "anac_bandi_gara__mart_annuale",          # <dataset>__<table> del registry
    select={"anno": "anno", "n_lotti": "n_lotti"},
    since=2016,                                # perimetro editoriale
    until="last_complete",                     # anno corrente escluso: partizione parziale
)
write({"trend": trend})
```

Regole:

- il path del mart viene dal registry (`marts[].location`), non costruito a mano;
- gli anni vengono dal dato (`since`/`until`, o `available_years(slug)`), mai `range(YYYY, YYYY)`;
- un mart assente è un errore leggibile, non una pagina vuota;
- per un mart partizionato per anno il loader deve avere successo in < 10 s
  (lettura unica via DuckDB, glob espanso una volta).

I loader che restano su `clean` (perché non hanno un mart equivalente) usano
ancora `_util.load_dataset()` / `safe_connect()`: migrano quando il mart
corrispondente esiste.

### Due regole non negoziabili

1. **Niente anni hardcoded.** `years=[2023]` con un commento «il file contiene
   1990-2023» è il modo in cui `ispra-emissioni-ghg` si è rotto quando la
   pipeline ha pubblicato il 2024: `_parquet_exists` confrontava l'anno del
   path, non trovava il 2023 e il loader scriveva `[]`. Gli anni vengono dal
   mart (`mart_rows`) o dal registry (`available_years`).
2. **Niente output vuoto.** `load_dataset`/`raw_sample` ora **falliscono** se
   nessun anno richiesto ha un parquet: un `[]` produce una pagina che va in
   errore nel browser senza che il build se ne accorga. Se un dataset è
   davvero senza dati, l'errore deve dirlo nel job.

`npm run audit` (step CI dopo il build) verifica output vuoti, path GCS
hardcoded, `published` senza superficie e copertura regioni delle mappe.

## Utility condivisa (`_util.py`)

`_util.py` fornisce `load_dataset()`, `_parquet_exists()` e `_parquet_refs()`
per evitare di replicare logica GCS/DuckDB in ogni loader.

Per i dataset di repo dominio (siope, eurostat, conto-annuale, ...) il path
GCS reale può divergere dal pattern canonico (prefix per repo, layout flat):
passa il `location` dal registry a `load_dataset()` e le refs HTTPS vengono
derivate dal path reale invece che dallo slug.

## Catalogo e temi (dal registry)

`catalog.json.py` e `themes.json.py` sono data loader "di sistema" che leggono
i registry fusion di TUTTI i repo del Lab (dataset-incubator, open-politica,
open-conto-annuale, eurostat, dcl-bologna, open-siope, rna-aiuti-stato) e
alimentano index, pagine tema e sidebar:

- `_registry.py` — logica condivisa e testata: `fuse_registries()` (dedup per
  slug, priorità = ordine `REGISTRY_REPOS`, entry con `registry_source`),
  `resolve_url_slug()` → `lab_connectors.registry.to_url_slug`, `build_catalog()`, `build_themes()`
- `catalog/themes.json` (repo root) — config editoriale dei temi: mappa `categories`
  del registry → tema pubblico. Single source of truth, consumata da `_registry.py`.

I temi sono **dinamici**: un dataset entra in un tema se ha una pagina explorer
(`src/dataset/<url-slug>.md`) e la sua `category` è mappata in `catalog/themes.json`.

I dataset senza pagina explorer restano nel catalogo (index "Tutti i dataset")
ma non entrano nei temi né nella sidebar.

## Moduli JS condivisi (`src/import/`)

Dalla Fase 1 (2026-06), le pagine dataset possono importare moduli condivisi da `src/import/`:

- `geo-utils.js` — `normalizzaReg()`, `loadItalianRegions()`, `buildMapLookup()`, `buildRegLookupWithTrentino()`
- `format-utils.js` — `num()`, `euro()`, `euroCompact()`, `pct()`, `unit()`, `numFix()`, `tableFormat()`

`tableFormat()` supporta `decimals: N` per campi con virgola (es. indici, Gini, densità).

Vedi `src/dataset/entrate-stato.md` come esempio di pagina che li usa.

# Data Loader

Ogni file `.json.py` in questa directory è un **data loader** creato a mano per una pagina specifica. Legge i clean parquet su GCS via DuckDB e produce JSON aggregato, consumato dalle pagine Observable.

**Roadmap**: in una fase successiva (Fase 3) valuteremo un unico loader generico parametrizzato dallo slug, per ridurre i 22 loader attuali a 1 + override per eccezioni. Nel frattempo, ogni nuovo dataset ha il suo loader.

## Naming

Il nome del file segue lo slug URL della pagina (con trattini), eventualmente con un suffisso che specifica la vista:

- `<slug-url>.json.py` — loader principale per una pagina
- `<slug-url>-<vista>.json.py` — loader per una vista specifica (es. per regione, per comune)

Esempi:
- `aifa-spesa.json.py` — loader per la pagina "Spesa farmaceutica"
- `irpef-regioni.json.py` — vista aggregata per regione
- `ispra-comuni.json.py` — vista aggregata per comune

Lo slug interno (con underscore, es. `aifa_spesa_consumo`) che identifica il parquet su GCS viene passato come parametro `slug=` a `load_dataset()` — non ha relazione col nome del file.

## Utility condivisa

`_util.py` fornisce `load_dataset()` e `_parquet_exists()` per evitare di replicare logica GCS/DuckDB in ogni loader.

## Catalogo e temi (dal registry)

`catalog.json.py` e `themes.json.py` sono data loader "di sistema" che leggono il
[fusion registry](https://github.com/dataciviclab/dataset-incubator/blob/main/registry/registry.json)
di dataset-incubator e alimentano index, pagine tema e sidebar:

- `_registry.py` — logica condivisa e testata: `load_registry()`, `resolve_url_slug()`
  (URL_SLUG_OVERRIDES), `build_catalog()`, `build_themes()`
- `catalog/themes.json` (repo root) — config editoriale dei temi: mappa `categories`
  del registry → tema pubblico. Single source condivisa con `scripts/generate_catalog.mjs`

I temi sono **dinamici**: un dataset entra in un tema se ha una pagina explorer
(`src/dataset/<url-slug>.md`) e la sua `category` è mappata in `catalog/themes.json`.

## Moduli JS condivisi (`src/import/`)

Dalla Fase 1 (2026-06), le pagine dataset possono importare moduli condivisi da `src/import/`:

- `geo-utils.js` — `normalizzaReg()`, `loadItalianRegions()`, `buildRegLookup()`, `buildRegLookupWithTrentino()`
- `format-utils.js` — `num()`, `euro()`, `euroCompact()`, `pct()`, `unit()`, `numFix()`, `tableFormat()`

Vedi `src/dataset/rifiuti-urbani.md` come esempio di pagina che li usa.

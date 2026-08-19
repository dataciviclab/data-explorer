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
  `resolve_url_slug()` (URL_SLUG_OVERRIDES), `build_catalog()`, `build_themes()`
- `catalog/themes.json` (repo root) — config editoriale dei temi: mappa `categories`
  del registry → tema pubblico. Single source of truth, consumata da `_registry.py`.

I temi sono **dinamici**: un dataset entra in un tema se ha una pagina explorer
(`src/dataset/<url-slug>.md`) e la sua `category` è mappata in `catalog/themes.json`.

I dataset senza pagina explorer restano nel catalogo (index "Tutti i dataset")
ma non entrano nei temi né nella sidebar.

## Moduli JS condivisi (`src/import/`)

Dalla Fase 1 (2026-06), le pagine dataset possono importare moduli condivisi da `src/import/`:

- `geo-utils.js` — `normalizzaReg()`, `loadItalianRegions()`, `buildRegLookup()`, `buildRegLookupWithTrentino()`
- `format-utils.js` — `num()`, `euro()`, `euroCompact()`, `pct()`, `unit()`, `numFix()`, `tableFormat()`

Vedi `src/dataset/rifiuti-urbani.md` come esempio di pagina che li usa.

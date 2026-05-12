# data-explorer

Frontend pubblico dati del Lab, basato su Evidence.dev, DuckDB e clean parquet pubblici su GCS.

Il catalogo dataset viene generato automaticamente da `dataset-incubator/registry/clean_catalog.json`.
I source SQL leggono i parquet direttamente da GCS via HTTP (nessuna cache locale).

## Stato

Bootstrap v0 locale completato con:

- catalogo generato dal registry DI (23+ dataset disponibili)
- 5 dataset `featured` con pagine curate
- 4 temi attivi
- build statica Evidence verde

## Setup locale

Node 20:

```bash
fnm use 20
node --version
```

Install:

```bash
npm install --legacy-peer-deps
```

Genera catalogo:

```bash
npm run generate:catalog
```

Valida catalogo:

```bash
npm run validate:catalog
```

Build:

```bash
npm run build
```

Preview locale:

```bash
npm run preview
```

## Struttura

- `scripts/generate_catalog.mjs` — genera `catalog/datasets.json` da DI + themes.json
- `catalog/themes.json` — unico file editoriale manuale (temi + featured dataset)
- `catalog/datasets.json` — GENERATO (non versionato come source of truth)
- `sources/` — query SQL Evidence per i parquet pubblici (lettura GCS diretta)
- `pages/` — homepage, temi e pagine dataset

## Catalogo

Il catalogo si genera a build time:

1. `generate_catalog.mjs` fetcha `dataset-incubator/registry/clean_catalog.json`
2. Lo fonde con `catalog/themes.json` (scelta editoriale)
3. Produce `catalog/datasets.json` usato dalla navigazione

Tutti gli slug usano il formato DI (underscore, es. `ispra_ru_base`).

## Note

- i dati letti dalle pagine arrivano dal bucket pubblico `dataciviclab-clean` via HTTP
- la cache GCS locale e' stata rimossa -- i source SQL leggono direttamente da GCS
- per aggiungere un dataset: 1) themes.json se featured, 2) pagina dataset se serve
- il deploy si triggera su push a main

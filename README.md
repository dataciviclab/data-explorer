# data-explorer

Frontend pubblico dati del Lab, basato su **Observable Framework**, DuckDB e clean parquet pubblici su GCS.

**Live**: [explorer.dataciviclab.org](https://explorer.dataciviclab.org)

## Setup

```bash
npm install --legacy-peer-deps
pip install -r requirements.txt
npm run dev
```

Apri http://localhost:3000

## Documentazione

- [`docs/explorer-ready-checklist.md`](docs/explorer-ready-checklist.md) — criteri per pubblicare un dataset nel catalogo
- [`docs/dataset-page-standard.md`](docs/dataset-page-standard.md) — principi guida di una pagina dataset
- [`docs/TEMPLATE-dataset-page.md`](docs/TEMPLATE-dataset-page.md) — template operativo per nuove pagine

## Pagine

Il catalogo completo è sulla [home page live](https://explorer.dataciviclab.org). Al momento sono pubblicati 13 dataset su 5 temi.

## Data loader

Gli script Python in `src/data/` leggono i parquet da GCS via DuckDB a build time e producono JSON aggregato. La utility `_util.py` gestisce GROUP BY, WHERE e skip anni mancanti.

## Deploy

Su **GitHub Pages** via workflow CI: `npm run build` → `observable build` → deploy su `explorer.dataciviclab.org`.

## Stack

- **Observable Framework** — static site generator
- **Observable Plot** — chart
- **DuckDB** — query engine per parquet su GCS
- **Python** — data loader

## Contribuire

Guarda [`CONTRIBUTING.md`](CONTRIBUTING.md) per aggiungere una pagina dataset o contribuire al frontend.

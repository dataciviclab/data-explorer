# data-explorer — I dati del DataCivicLab, esplorabili

**Il catalogo pubblico dei dati del Lab: cerca, filtra e interroga i dataset puliti del DataCivicLab.**

**Live**: [explorer.dataciviclab.org](https://explorer.dataciviclab.org)

## Cosa trovi

Dataset puliti (clean parquet) pubblicati dal Lab, organizzati per tema:

| Tema | Esempi |
|---|---|
| **Territorio e ambiente** | rifiuti urbani, capacità rinnovabile, emissioni, incidentalità |
| **Finanza pubblica** | IRPEF comunale, entrate stato, FSC, coesione, partecipate |
| **Sanità** | spesa farmaceutica, strutture ASL, posti letto |
| **Welfare e lavoro** | dipendenti pubblici, pensioni, popolazione |
| **Giustizia** | flussi civili |
| **Terzo settore** | cinque per mille |

Il catalogo completo è sulla [home page live](https://explorer.dataciviclab.org), con ricerca per tema e stato di pubblicazione.

## Per chi è

- **Cittadini e giornalisti** — esplorano i dati pubblici senza scrivere codice
- **Analisti** — interrogano i parquet con DuckDB
- **Contributor** — aggiungono pagine dataset al catalogo

## Setup (per sviluppatori)

```bash
npm install --legacy-peer-deps
pip install -r requirements.txt
npm run dev
```

Apri http://localhost:3000

## Come funziona

- **Data loader**: script Python in `src/data/` leggono i parquet da GCS via DuckDB a build time e producono JSON aggregato
- **Deploy**: GitHub Pages via CI (`npm run build` → `observable build` → `explorer.dataciviclab.org`)

## Stack

- **Observable Framework** — static site generator
- **Observable Plot** — chart
- **DuckDB** — query engine per parquet su GCS
- **Python** — data loader

## Contribuire

- [CONTRIBUTING.md](CONTRIBUTING.md) — come aggiungere una pagina dataset
- [docs/explorer-ready-checklist.md](docs/explorer-ready-checklist.md) — criteri per pubblicare un dataset nel catalogo
- [docs/dataset-page-standard.md](docs/dataset-page-standard.md) — principi guida di una pagina dataset
- [docs/TEMPLATE-dataset-page.md](docs/TEMPLATE-dataset-page.md) — template operativo per nuove pagine

Parte del [DataCivicLab](https://github.com/dataciviclab).

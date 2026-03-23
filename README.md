# data-explorer

Frontend pubblico dati del Lab, basato su Evidence.dev, DuckDB e clean parquet pubblici su GCS.

## Stato

Bootstrap v0 locale completato con:

- catalogo minimo
- 3 dataset `explorer-ready`
- 2 temi attivi
- build statica Evidence verde

Dataset v0:

- `ispra_ru_base`
- `civile_flussi_2014_2024`
- `terna_electricity_by_source`

## Setup locale

Node 20:

```powershell
fnm use 20
node --version
```

Install:

```powershell
npm install --legacy-peer-deps
```

Verifica sources:

```powershell
npm run sources
```

Build:

```powershell
npm run build
```

Preview locale:

```powershell
npm run preview
```

## Struttura

- `catalog/` = catalogo dataset e temi
- `sources/` = query SQL Evidence per i parquet pubblici
- `pages/` = homepage, temi e pagine dataset

## Note

- il repo puo partire privato per il bootstrap
- prima di GitHub Pages dovra essere reso pubblico
- i dati letti dalle pagine arrivano dal bucket pubblico `dataciviclab-clean`

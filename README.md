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

Validazione catalogo:

```powershell
npm run validate:catalog
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

## Contratto del catalogo

Il catalogo vive in:

- `catalog/datasets.json`
- `catalog/themes.json`

I due file sono la fonte di verità minima per:

- navigazione pubblica
- relazione tra dataset e temi
- metadata leggibili del v0

### `datasets.json`

Ogni dataset è un oggetto JSON.

Campi obbligatori:

- `slug`
  - slug pubblico usato nelle route del sito
- `technical_slug`
  - slug tecnico usato nel data lake e nei path GCS
- `name`
  - nome leggibile del dataset
- `theme`
  - slug del tema pubblico di riferimento
- `status`
  - stato di readiness del dataset nel Data Explorer
- `years`
  - lista degli anni disponibili nel v0
- `source`
  - ente o fonte del dataset

Campi opzionali futuri:

- descrizione breve
- coverage territoriale
- note sullo schema
- query consigliate
- link pubblici aggiuntivi

Regole:

- `slug` deve essere unico nel repo
- `theme` deve esistere in `themes.json`
- `technical_slug` può differire dallo slug pubblico
- `years` deve riflettere gli anni realmente esposti nel sito, non necessariamente tutti quelli disponibili fuori dal v0

### `themes.json`

Ogni tema è un oggetto JSON.

Campi obbligatori:

- `slug`
  - slug pubblico del tema
- `name`
  - nome leggibile del tema
- `datasets`
  - lista degli slug pubblici dei dataset inclusi nel tema

Regole:

- `slug` deve essere unico
- ogni dataset elencato deve esistere in `datasets.json`
- un dataset del v0 deve comparire sia nel proprio `theme` in `datasets.json`, sia nella lista `datasets` del tema corrispondente

### Metadata tecnici vs pubblici

Nel catalogo convivono due livelli diversi:

- metadata pubblici:
  - `slug`
  - `name`
  - `theme`
  - `source`
- metadata tecnici:
  - `technical_slug`
  - `years`
  - `status`

Il principio è:

- lo slug pubblico guida le route e la navigazione
- lo slug tecnico collega il sito al data lake del Lab
- i temi sono l'identità pubblica
- i dataset restano l'unità tecnica di base

## Note

- il repo può partire privato per il bootstrap
- prima di GitHub Pages dovrà essere reso pubblico
- i dati letti dalle pagine arrivano dal bucket pubblico `dataciviclab-clean`

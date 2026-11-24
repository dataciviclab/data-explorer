# Scheda dataset — modello e flusso

Stato: **pilota** (3 schede, route `/schede/[slug]`). Non sostituisce ancora
`/dataset/*`.

## Perché esiste

Una scheda deve costare ~0 in codice e non deve far interrogare GCS al build:

```
pipeline → registry + mart
               │
     catalog/cards/<url_slug>.yml   (editoriale, opzionale, DE)
               │
     scripts/build_cards.py         (1 query per blocco, fuori dal build)
               │
     src/data/cards.json            (artefatto, gitignored)
               │
     build OF → /schede/<url_slug>  (route dinamica, nessuna query)
```

## Il file editoriale (opzionale)

`catalog/cards/<url_slug>.yml` contiene **solo ciò che il catalogo non ha**.
Se il file manca, non c'è scheda. Se c'è, i campi presenti vincono sul catalogo.

```yaml
dataset: anac_bandi_gara        # obbligatorio: slug DI
title: Bandi di gara pubblici ANAC
description: "..."              # override; default = catalogo
source: ANAC — Autorità Nazionale Anticorruzione
source_url: https://dati.anticorruzione.it/
license: CC-BY-SA 4.0
intro: "Testo di apertura."     # opzionale

blocks:                         # la pagina è la composizione di questi blocchi
  - type: kpi
    measures:
      - {mart: anac_bandi_gara__mart_annuale, x: anno, y: n_lotti,
         label: Lotti pubblicati, format: num, delta: true}

  - type: series
    mart: anac_bandi_gara__mart_annuale
    x: anno
    y: n_lotti
    y_label: Lotti pubblicati
    y_format: num
    title: Lotti pubblicati per anno
    note: "Dal 2007 all'ultimo anno completo."

  - type: ranking
    mart: anac_bandi_gara__mart_top_stazioni
    x: anno
    dimension: denominazione_amministrazione_appaltante
    dimension_label: Stazione appaltante
    measure: importo_totale
    measure_label: Importo dei lotti
    measure_format: euroCompact
    top: 20
    title: Top 20 stazioni appaltanti

notes:
  - "Gli importi escludono i lotti con importo sospetto."
```

### Blocchi disponibili (v0)

| Tipo | Campi | Note |
|---|---|---|
| `kpi` | `measures[{mart,x,y,label,format,delta}]` | `delta` aggiunge la variazione primo→ultimo anno |
| `series` | `mart,x,y,x_label,y_label,y_format,title,note` | linea + punti, anno corrente escluso |
| `composition` | `mart,x,y,by,by_label,y_label,normalize,title,note` | barre stacked per anno; `normalize: true` (default) = quote 100% |
| `map` | `mart,x,dimension,dimension_label,measure,measure_label,measure_format,title,note` | coropletica regioni; ultimo anno completo |
| `ranking` | `mart,x,dimension,dimension_label,measure,measure_label,measure_format,top,title,note` | ultimo anno completo, ordina per misura |

`view` resta come **scorciatoia legacy**: `view: {mart,x,y,...}` equivale a un
blocco `kpi` (y e y2) + un blocco `series`. Non si possono usare `view` e
`blocks` nello stesso file.

### Campi vietati

Vivono nel catalogo, copiarli crea drift: `name`, `period`, `rows`,
`clean_rows`, `columns`, `stage`, `category`, `registry_source`, `source_id`,
`mart_refs`, `location`, `slug`, `url_slug`. Il produttore fallisce se li
trova. Fallisce anche se: `dataset` non esiste in ACB, il nome del file non è
lo `url_slug`, lo stesso dataset è in due file, un `mart` non è tra i
`mart_refs`, un blocco è incompleto o di tipo sconosciuto.

## Componenti e pagina

- `src/import/blocks.js` — componenti condivisi (`renderBlocks`): KPI, serie,
  ranking. Non importano npm (limite delle pagine dinamiche OF); ricevono
  `html`, `plot`, `width`, `fmt` dalla pagina.
- `src/schede/[slug].md` — assemblaggio: header, intro, avvisi, blocchi,
  dizionario, provenienza, limiti. ~100 righe, non si tocca per dataset.
- `scripts/build_cards.py` — risolve i dati dei blocchi dai mart e li scrive
  nel card JSON. È l'unico punto che parla con GCS.

## Comandi

```bash
npm run cards:dry        # tabella slug → blocchi/mart/punti, non scrive
npm run cards            # scrive src/data/cards.json
npm run card:new <slug>  # crea lo stub editoriale
npm run build            # legge cards.json, nessuna query GCS
```

In CI `npm run cards` è uno step prima del build (`deploy.yml`).

## Migrare le pagine curate

- **Strutturali** (KPI + 1-2 viste + tabella + limiti): si esprimono in blocchi
  e la pagina `.md` sparisce.
- **Analisi bespoke** (calcoli, confronti, ipotesi: es. `chi-cattura-la-crescita`,
  `mit-incidentalita`): restano `.md` e vengono linkate dalla scheda.
- Un blocco nuovo diventa un tipo solo se serve **3+ pagine**. Altrimenti è
  codice in quella pagina.

## Cosa manca (qualità, non tecnica)

- **Licenza**: assente in tutti i registry; senza, la scheda dice "non dichiarata".
- **Descrizioni colonne**: ~10% compilate nel catalogo.
- **Periodo**: il registry può essere più stretto dei file pubblicati
  (ANAC: `period` 2016–2025, mart 2007–2026). La scheda mostra entrambi.
- **Vista automatica**: oggi va dichiarata (blocchi o `view`); il resolver
  mart+anno+misura è il passo successivo, il file resta come override.

## Limiti tecnici noti

- Le pagine **dinamiche** di OF non iniettano `Inputs`/import `npm:`: le
  tabelle sono HTML statico.
- Le serie sono a punti annuali; niente filtri o drill-down (restano Streamlit
  / Query SQL).

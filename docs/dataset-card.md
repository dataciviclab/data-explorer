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
     scripts/build_cards.py         (1 query per scheda, fuori dal build)
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
view:                           # opzionale: senza, scheda senza grafico
  mart: anac_bandi_gara__mart_annuale
  x: anno
  y: n_lotti
  y_label: Lotti pubblicati
  y_format: num                 # num | euroCompact | pct
  y2: importo_totale            # seconda misura, opzionale
  y2_label: Importo stimato
  y2_format: euroCompact
notes:                          # opzionale: finisce in "Limiti"
  - "Gli importi escludono i lotti con importo sospetto."
```

Campi **vietati** (vivono nel catalogo, copiarli crea drift): `name`, `period`,
`rows`, `clean_rows`, `columns`, `stage`, `category`, `registry_source`,
`source_id`, `mart_refs`, `location`, `slug`, `url_slug`. Il produttore
fallisce se li trova. Fallisce anche se: `dataset` non esiste in ACB, il nome
del file non è lo `url_slug`, lo stesso dataset è in due file, `view.mart` non
è tra i `mart_refs`, `view` è incompleta.

## Comandi

```bash
npm run cards:dry        # tabella slug → mart/x/y/punti, non scrive
npm run cards            # scrive src/data/cards.json
npm run card:new <slug>  # crea lo stub editoriale (solo `dataset:`)
npm run build            # legge cards.json, nessuna query GCS
```

`card:new` accetta slug DI o URL. In CI `npm run cards` è uno step prima del
build (`deploy.yml`).

## Nuovo dataset: cosa succede

1. Il dataset è `published` in ACB.
2. `npm run card:new <slug>` crea lo stub (2 righe utili).
3. L'editor compila `title`, `description`, `source`, `license`, e `view` se
   vuole il grafico.
4. `npm run cards && npm run build`; in CI la PR contiene il file e il build
   lo consuma.

Un dataset senza file non compare in `/schede`: nessuna scheda inventata.

## Cosa manca (qualità, non tecnica)

- **Licenza**: assente in tutti i registry; senza, la scheda mostra "non dichiarata".
- **Descrizioni colonne**: ~10% compilate nel catalogo.
- **Periodo**: il registry può essere più stretto dei file pubblicati
  (ANAC: `period` 2016–2025, mart 2007–2026). La scheda mostra entrambi.
- **Vista automatica**: oggi va dichiarata nel file; il resolver (mart + anno +
  misura) è il passo successivo, e il file resta come override.

## Limiti tecnici noti

- Le pagine **dinamiche** di OF non iniettano `Inputs`/import `npm:`: la
  tabella del dizionario è HTML statico.
- La serie è a punti annuali; niente filtri o drill-down (restano Streamlit /
  Query SQL).

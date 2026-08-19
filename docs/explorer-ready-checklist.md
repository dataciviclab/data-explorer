# Checklist Explorer-Ready

Questa checklist serve a decidere se un dataset puo' entrare nel `Data Explorer` e con quale livello di esposizione.

## Classi di readiness

I dataset si allineano agli stati del catalogo `dataset-incubator`:

| Stato DI | Visibilita' DE | Requisiti |
|---|---|---|
| `clean_ready` | Dataset compare nel catalogo tecnico, navigabile da URL diretto | Clean parquet pubblico su GCS, schema stabile |
| `public_catalog_ready` | Pagina dataset pubblica completa | Query curate, copy pubblico, tema assegnato, `data_driven: true` |

## Checklist per pagina pubblica

Prima di aggiungere un dataset al tema, verificare:

- slug DI e slug DE coincidono (usa lo slug DI)
- il clean parquet pubblico esiste ed e' interrogabile da GCS diretto
- il dataset ha un tema pubblico chiaro in `catalog/themes.json`
- le colonne usate dalle query sono stabili e comprensibili
- la pagina puo' essere letta anche da un utente non tecnico
- le `section-note` e `method-note` sono davvero minime
- il link al dato grezzo (clean parquet) e' disponibile e corretto
- le query non fanno promesse piu' forti dei dati disponibili

## Standard tecnici obbligatori

Per ogni pagina con `data_driven: true`:

- **Frontmatter**: `data_driven: true` presente
- **Intro narrativa**: numeri interpolati da variabili calcolate, mai hardcoded
- **KPI cards**: almeno 2-4 metriche con valori dinamici
- **Primo blocco**: stock/distribuzione/base (forma naturale del dataset)
- **Colori Plot**: literal (`fill: "#4e79a7"`) — mai `fill: "NomeCampo"`
- **Decimali**: `decimals: N` in `tableFormat()` per campi con virgola
- **Tabelle**: `tableFormat()` e `Inputs.table` in celle separate
- **Sezione Limiti**: almeno 2-3 punti sulle limitazioni del dataset

## Query curate

Una query e' abbastanza buona per il Data Explorer se:

- risponde a una domanda pubblica chiara
- usa campi comprensibili o ben etichettati
- non dipende da interpretazioni troppo fragili
- produce un output leggibile come tabella o grafico

## Copy minimo richiesto

Ogni pagina dataset dovrebbe avere almeno:

- una frase iniziale che spiega cosa contiene il dataset (con numeri dal dato)
- una frase che esplicita la domanda guida della pagina
- se serve, una breve nota di lettura sul blocco piu' importante
- `source` e `last_modified` nel frontmatter
- un link al clean parquet pubblico

## Principio guida

Nel Data Explorer entrano prima i dataset che si leggono bene, non quelli semplicemente disponibili.

## Riferimento

- `docs/dataset-page-standard.md` — formato pagina
- `docs/TEMPLATE-dataset-page.md` — template operativo
- `dataset-incubator/registry/registry.schema.json` — schema registry (fusion)

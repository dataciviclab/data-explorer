# Contribuire a data-explorer

Questa guida vale per la repo `data-explorer`, il frontend pubblico dei dataset puliti del Lab.

## A cosa serve questa repo

`data-explorer` espone i dataset del Lab in pagine navigabili, basate su [Observable Framework](https://observablehq.com/framework/), con dati letti dai clean parquet su GCS.

Ogni pagina dataset ha:
- un **data loader** Python che interroga il parquet e produce JSON aggregato
- un **file `.md`** Observable che definisce layout, grafici e tabelle
- una **voce nel config** `observablehq.config.js` per la navigazione

Qui **non** stanno:
- pipeline o trasformazione dati (vedi [`dataset-incubator`](https://github.com/dataciviclab/dataset-incubator))
- analisi o notebook (vedi [`dataciviclab/analisi/`](https://github.com/dataciviclab/dataciviclab/tree/main/analisi))

## Setup locale

```bash
npm install --legacy-peer-deps
pip install -r requirements.txt
npm run dev
```

Apri http://localhost:3000

## Aggiungere una pagina dataset

1. **Data loader**: crea `src/data/<slug>.json.py` con la logica di aggregazione per la tua pagina
   - usa `load_dataset()` da `src/data/_util.py` per leggere i parquet GCS
   - il nome del file usa slug URL con trattini (es. `bdap-lea-regioni.json.py`)
   - lo slug DI (con underscore, es. `bdap_lea`) va come parametro `slug=` a `load_dataset()`
   - vedi `src/data/_util.py` e i loader esistenti come riferimento
2. **Pagina**: crea `src/dataset/<slug-url>.md`
   - segui la struttura definita in `docs/dataset-page-standard.md`
   - i data loader sono referenziati come `FileAttachment("../data/<nome>.json")`
3. **Registra** la pagina in `observablehq.config.js` nella sezione `pages`
4. **Tema**: se il dataset introduce un nuovo tema, aggiungilo in `src/data/themes.json.py`
5. **Verifica** con `npm run dev` che la pagina sia navigabile e i dati si carichino

## Standard e criteri

Prima di proporre una nuova pagina, controlla:
- [`docs/explorer-ready-checklist.md`](docs/explorer-ready-checklist.md) — classi di readiness
- [`docs/dataset-page-standard.md`](docs/dataset-page-standard.md) — struttura standard della pagina

Il principio guida: *nel Data Explorer entrano prima i dataset che si leggono bene, non quelli semplicemente disponibili.*

## PR e review

Prima di aprire una PR:
- verifica che il data loader produca output sensati
- controlla che la pagina sia leggibile da un utente non tecnico
- assicurati che slug e naming siano consistenti con il catalogo DI
- mantieni il perimetro stretto: una PR = un dataset o un fix

## Riferimenti

- [`docs/`](docs/) — documentazione del repo
- [`dataset-incubator`](https://github.com/dataciviclab/dataset-incubator) — pipeline e contratto tecnico
- [`clean_catalog.json`](https://github.com/dataciviclab/dataset-incubator/blob/main/registry/clean_catalog.json) — catalogo dataset disponibili

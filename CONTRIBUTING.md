# Contribuire a data-explorer

Questa guida vale per la repo `data-explorer`, il frontend pubblico dei dataset puliti del Lab.

Per le regole GitHub condivise dell'organizzazione, parti prima da
[`.github`](https://github.com/dataciviclab/.github).

## A cosa serve questa repo

`data-explorer` espone i dataset del Lab in pagine navigabili, basate su [Observable Framework](https://observablehq.com/framework/), con dati letti dai clean parquet su GCS.

Ogni pagina dataset ha:
- un **data loader** Python che interroga il parquet e produce JSON aggregato
- un **file `.md`** Observable (modello *narrativo data-driven*) che definisce KPI, grafici e tabelle
- la navigazione è **auto-generata** dal registry: la sidebar nasce da `scripts/generate-config.mjs`
  (legge `src/dataset/*.md` + catalog) — **non si modifica** `observablehq.config.js` a mano

Qui **non** stanno:
- pipeline o trasformazione dati (vedi [`dataset-incubator`](https://github.com/dataciviclab/dataset-incubator))
- notebook estesi ("quaderni" lunghi): la forma notebook resta nel repo hub; nel Data Explorer le analisi diventano **pagine vivaci data-driven** (vedi "Standard pagina" sotto)

## Setup locale

```bash
npm install --legacy-peer-deps
pip install -r requirements.txt
npm run dev
```

Apri http://localhost:3000

## Aggiungere una pagina dataset

1. **Data loader**: crea `src/data/<slug>.json.py` con la logica di aggregazione
   - usa `load_dataset()` da `src/data/_util.py` (o `safe_connect()` per query custom)
   - **non usare** `duckdb.connect()` diretto — preferisci `safe_connect()`
   - il nome del file usa slug URL con trattini (es. `bdap-lea-regioni.json.py`)
   - lo slug DI (con underscore) va come parametro `slug=` a `load_dataset()`
2. **Pagina**: copia il [template `docs/TEMPLATE-dataset-page.md`](docs/TEMPLATE-dataset-page.md)
   in `src/dataset/<slug-url>.md` e compila ogni sezione
   - **frontmatter**: obbligatorio `title`, `description`, `source`, `source_url`, `period`,
     `last_modified`, `dataset_slug`, `data_driven: true`
   - **formattazione**: usa `num()`, `euro()`, `pct()` da `format-utils.js` — **mai `toLocaleString`**
   - **decimali**: usa `decimals: N` nel spec di `tableFormat()` per campi con virgola (es. Gini, indici)
   - **colori nei grafici**: usa colori literal (`fill: "#4e79a7"`) — **mai** `fill: "NomeCampo"` (Plot interpreta come field name, non colore)
   - **mappe**: usa `buildMapLookup()` con `loadItalianRegions()` — **mai `buildRegLookup` diretto**
   - **tabelle**: `tableFormat` e `Inputs.table` in **celle separate** (bug noto OF altrimenti)
   - primo blocco: distribuzione o stock base, non ranking o delta
   - sezione **Limiti** obbligatoria in fondo
3. **Tema**: i temi sono **dinamici** — derivano dalla `category` del registry.
   Per assegnare/creare un tema modifica `catalog/themes.json` (mappa
   `categories` → tema). La sidebar e le pagine tema si auto-generano —
   **non modificare** `observablehq.config.js` a mano.
4. **Verifica**: `npm run lint && npm test && npm run build`
5. **Checklist pre-pub** nel template PR: verificare slug, parquet, frontmatter,
   moduli condivisi, `tableFormat` in cella separata.

### Standard verificati automaticamente

`npm run lint` include `node scripts/lint-standards.mjs` che controlla:

| Controllo | Cosa blocca |
|-----------|-------------|
| `toLocaleString` | Uso diretto di formattazione locale (usare `format-utils.js`) |
| `tableFormat` + `Inputs.table` stessa cella | Tabella non renderizzata per bug OF |
| `buildRegLookup` in pagine con mappa | Usare `buildMapLookup()` che include fuzzy matching |
| `duckdb.connect()` nei loader | Usare `safe_connect()` da lab-connectors |
| Cifre hardcoded in pagine `data_driven` | Numeri devono essere variabili calcolate dal dato |

### Moduli condivisi (`src/import/`)

| Modulo | Funzioni principali | Quando usarlo |
|--------|-------------------|---------------|
| `geo-utils.js` | `normalizzaReg()`, `loadItalianRegions()`, `buildMapLookup()`, `buildRegLookupWithTrentino()` | Pagine con mappe coropletiche |
| `format-utils.js` | `num()`, `euro()`, `euroCompact()`, `pct()`, `unit()`, `numFix()`, `tableFormat()` | Qualsiasi pagina (formattazione) |

`tableFormat()` supporta `decimals: N` nel spec per campi con decimali:
```js
const { header, format } = tableFormat({
  gini: { label: "Gini", fmt: "num", decimals: 3 },
  popolazione: { label: "Popolazione", fmt: "num" },  // intero, senza decimals
});
```

Esempio import:
```js
import { normalizzaReg, loadItalianRegions, buildMapLookup } from "../import/geo-utils.js";
import { num, euro, pct, tableFormat } from "../import/format-utils.js";
```

Riferimenti canonici: `src/dataset/entrate-stato.md`, `src/dataset/cinque-per-mille.md`, `src/dataset/dipendenti-pubblici.md`.

## Standard e criteri

Prima di proporre una nuova pagina, controlla:
- [`docs/explorer-ready-checklist.md`](docs/explorer-ready-checklist.md) — classi di readiness
- [`docs/dataset-page-standard.md`](docs/dataset-page-standard.md) — principi guida della pagina
- [`docs/TEMPLATE-dataset-page.md`](docs/TEMPLATE-dataset-page.md) — template operativo

Il principio guida: *nel Data Explorer entrano prima i dataset che si leggono bene, non quelli semplicemente disponibili.*

### Modello narrativo data-driven (standard pagina)

Le pagine non riportano **numeri scritti a mano**: KPI e frasi con dati citano variabili calcolate dai data loader, così la pagina si aggiorna da sola quando si ripubblica il parquet. Esempio: `Nel ${last} le entrate valgono ${euroCompact(totaleLast)}`.

Struttura tipo (dataset-first, in quest'ordine):
1. frontmatter con `data_driven: true`
2. data loader + import moduli condivisi + filtro anno
3. computazione variabili (KPI, aggregazioni)
4. intro narrativa con template literal (usa variabili computate)
5. KPI cards
6. blocco **base**: la distribuzione naturale del dataset nell'anno più recente
7. blocco **derivato**: trend/confronti (es. soglie, pre/post evento)
8. eventuale blocco secondario di lettura
9. tabella finale ricercabile + `Limiti` + `Risorse`

Pagine di riferimento (canoniche):
- `src/dataset/entrate-stato.md` — serie, KPI, soglia 50%, confronto pre/post
- `src/dataset/cinque-per-mille.md` — mappa coropletica + categorie + concentrazione
- `src/dataset/dipendenti-pubblici.md` — stock + trend + composizione (genere)

## Quando aprire una issue

Apri una issue in `data-explorer` se il lavoro riguarda:

- aggiungere la pagina di un nuovo dataset
- bug o miglioramenti al frontend (data loader, layout, performance)
- aggiornamento della configurazione o del catalogo
- cambio di struttura dei dati upstream

## PR e review

Prima di aprire una PR:
- verifica che il data loader produca output sensati
- controlla che la pagina sia leggibile da un utente non tecnico
- assicurati che slug e naming siano consistenti con il catalogo DI
- mantieni il perimetro stretto: una PR = un dataset o un fix

## Riferimenti

- [`docs/`](docs/) — documentazione del repo
- [`dataset-incubator`](https://github.com/dataciviclab/dataset-incubator) — pipeline e contratto tecnico
- [`registry/registry.json`](https://github.com/dataciviclab/dataset-incubator/blob/main/registry/registry.json) — registry dataset disponibili (fusion, con `category` per i temi)
- [`lab-connectors`](https://github.com/dataciviclab/lab-connectors) — dipendenza per GCS e HTTP
- [`.github`](https://github.com/dataciviclab/.github) — policy condivise

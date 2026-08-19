---
# Template pagina dataset — DataCivicLab Explorer
# Copia in src/dataset/{slug}.md e compila ogni sezione.
# I principi guida: docs/dataset-page-standard.md
# La procedura completa: CONTRIBUTING.md → "Aggiungere una pagina dataset"
#
# FRONTMATTER — tutto obbligatorio
title: Nome leggibile del dataset
description: Una frase che dice cosa contiene e perché è utile (max 150 caratteri)
source: Ente che pubblica il dato originale (es. "ISTAT", "MEF — Dipartimento delle Finanze")
source_url: URL della fonte originale
period: "YYYY–YYYY"  # intervallo di anni coperto dal dataset
last_modified: YYYY-MM-DD  # data dell'ultimo aggiornamento del parquet pulito
dataset_slug: slug_del_dataset_su_gcs  # slug DI (con underscore) per data loader
data_driven: true  # OBBLIGATORIO — attiva il lint per numeri hardcoded
---

# Nome leggibile del dataset

<!--
  DATA LOADER + IMPORT
  Prima di tutto: import moduli condivisi e carica i dati.
  Le variabili computate qui vengono usate nell'intro narrativa sotto.
-->
```js
import { normalizzaReg, loadItalianRegions, buildMapLookup } from "../import/geo-utils.js";
import { num, numFix, euro, euroCompact, pct, unit, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/{slug-url}.json").json();
```

<!--
  SE SERVE UNA MAPPA
  Carica regioni.topojson con FileAttachment e passa a loadItalianRegions().
-->
```js
// const regTopo = await FileAttachment("../data/regioni.topojson").json();
// const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
```

<!--
  FILTRO ANNO + COMPUTAZIONE VARIABILI
  Calcola tutte le variabili usate nell'intro e nei KPI.
  In Observable Framework le celle sono reattive: quando annoSel cambia, tutto si aggiorna.
-->
```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel);
// + metriche riassuntive (usa d3.sum, d3.mean)
// es. const totale = d3.sum(filtered, d => d.valore);
// es. const media = d3.mean(filtered, d => d.valore);
```

<!--
  INTRO NARRATIVA DATA-DRIVEN
  Usa template literal con le variabili computate sopra.
  MAI numeri hardcoded — il lint li blocca.
  Esempio: "Nel ${String(annoSel)} il totale è ${euroCompact(totale)}."
-->
**Nel ${String(annoSel)} il totale è ${euroCompact(totale)}.**

Breve descrizione del dataset: cosa contiene, a che livello di dettaglio, qual è il periodo coperto. Ogni numero di questa pagina è calcolato dal dato a build-time.

**Fonte**: [Nome ente](URL) · **Periodo**: {period}

<!--
  KPI CARDS
  2-4 metriche chiave. Usa num(), euro(), pct() per la formattazione.
-->
<div class="grid grid-cols-3">
  <div class="card">
    <h3>Metrica 1</h3>
    <span class="big">${euroCompact(totale)}</span>
  </div>
  <div class="card">
    <h3>Metrica 2</h3>
    <span class="big">${num(conteggio)}</span>
  </div>
  <div class="card">
    <h3>Metrica 3</h3>
    <span class="big">${pct(quota)}</span>
  </div>
</div>

---

<!--
  BLOCCO 1 — STOCK / DISTRIBUZIONE / BASE
  La forma più naturale del dataset nell'anno più recente.
  Mappa coropletica, bar chart, composizione — NON trend o delta.
-->
## 1. Titolo blocco base — ${String(annoSel)}

Breve nota di lettura (max 2 righe). Cosa mostra questo grafico? Come leggerlo?

```js
// Mappa coropletica:
// Plot.plot({
//   projection: {type: "mercator", domain: regioniGeo},
//   ...
//   marks: [
//     Plot.geo(regioniGeo, {
//       fill: d => lookup.get(normalizzaReg(d.properties.DEN_REG)),
//       ...
//     }),
//     Plot.geo(confiniReg, ...)
//   ]
// })

// Bar chart (USARE COLORI LITERAL, mai field names):
// Plot.plot({
//   marks: [
//     Plot.barX(filtered, { y: "categoria", x: "metrica", fill: "#4e79a7", sort: {y: "-x"} })
//   ]
// })
```

> **Nota di lettura**: se serve, nota breve su perimetro o metrica.

---

<!--
  BLOCCO 2 — TREND / CONFRONTO / LETTURA DERIVATA
  Deve essere diverso dal primo. Trend, confronto pre/post, delta.
-->
## 2. Titolo blocco derivato ${primoAnno}–${ultimoAnno}

Breve nota su cosa mostra questo secondo blocco.

```js
// secondo grafico o tabella
```

---

<!--
  TABELLA FINALE
  tableFormat() e Inputs.table in CELLE SEPARATE (bug noto OF).
  Usa decimals: N per campi con virgola.
-->
## Dettaglio

```js
const { header, format } = tableFormat({
  col1: { label: "Nome leggibile", fmt: "string" },
  col2: { label: "Nome leggibile", fmt: "num" },            // intero
  col3: { label: "Nome leggibile", fmt: "num", decimals: 2 }, // con decimali
  col4: { label: "Nome leggibile", fmt: "euro" },
  col5: { label: "Nome leggibile", fmt: "pct" },
});
```

```js
Inputs.table(filtered, {
  columns: ["col1", "col2", "col3", "col4", "col5"],
  header,
  format,
  rows: 20,
  width: "100%"
})
```

---

## Limiti

<!--
  SEZIONE OBBLIGATORIA. Elenca cosa il dataset NON permette di dire.
  Tre punti massimi, linguaggio pubblico.
-->
- **Copertura**: il dataset copre {periodo}, non sono disponibili dati precedenti
- **Granularità**: i dati sono aggregati per {livello}, non è possibile scendere a dettaglio {X}
- **Nota metodologica**: {eventuale caveat sul significato delle metriche, doppi conteggi, cambi di classificazione}

---

## Risorse

- [Fonte originale]({source_url})
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/{slug_gcs}/{anno}/{slug_gcs}_{anno}_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/{slug_candidate})

<!--
  CHECKLIST PRE-PUBBLICAZIONE
  [ ] data_driven: true nel frontmatter
  [ ] Slug DE e slug DI coincidono
  [ ] Clean parquet pubblico esiste su GCS
  [ ] Data loader funziona (npm run dev)
  [ ] Intro narrativa con template literal (numeri non hardcoded)
  [ ] Primo blocco mostra stock/distribuzione base
  [ ] Colori Plot sono literal (non field names)
  [ ] tableFormat usa decimals per campi con virgola
  [ ] tableFormat e Inputs.table in celle separate
  [ ] Usa moduli condivisi da src/import/
  [ ] Sezione Limiti compilata
  [ ] Link a fonte originale e parquet funzionanti
  [ ] Pagina leggibile da un utente non tecnico
-->

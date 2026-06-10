---
title: Partecipazioni pubbliche
description: Partecipazioni delle PA in società per categoria e settore — MEF, 2020-2023
source: MEF — Dipartimento dell'Economia
source_url: https://www.mef.gov.it/
period: "2020–2023"
last_modified: 2026-06-03
dataset_slug: mef_partecipazioni
---

# Partecipazioni pubbliche

Partecipazioni delle pubbliche amministrazioni italiane in società, per categoria di amministrazione e settore di attività. I dati mostrano quante società sono controllate dalla PA, quanto costano e quanti addetti impiegano.

**Fonte**: [MEF](https://www.mef.gov.it/) · **Periodo**: 2020–2023

```js
import { num, euroCompact, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/mef-partecipazioni.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel);
const totPartecipate = d3.sum(filtered, d => d.num_partecipate);
const totOneri = d3.sum(filtered, d => d.totale_oneri);
const totAddetti = d3.sum(filtered, d => d.totale_addetti);
```

```js
// Per categoria PA
const perCategoria = Array.from(
  d3.rollup(filtered, v => ({
    num: d3.sum(v, d => d.num_partecipate),
    oneri: d3.sum(v, d => d.totale_oneri),
    addetti: d3.sum(v, d => d.totale_addetti),
  }), d => d.categoria),
  ([categoria, v]) => ({categoria, ...v})
).sort((a, b) => b.num - a.num);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Partecipazioni</h3>
    <span class="big">${num(totPartecipate)}</span>
    <small style="opacity:0.6">società distinte</small>
  </div>
  <div class="card">
    <h3>Oneri totali</h3>
    <span class="big">${euroCompact(totOneri)}</span>
  </div>
  <div class="card">
    <h3>Addetti</h3>
    <span class="big">${num(totAddetti)}</span>
  </div>
</div>

---

## Partecipazioni per categoria PA

I Comuni detengono la maggior parte delle partecipazioni pubbliche, seguiti dalle Regioni. Le Università e le Camere di Commercio completano il quadro.

```js
Plot.plot({
  title: `Partecipazioni per categoria PA — ${String(annoSel)}`,
  width: 800,
  height: 350,
  marginLeft: 160,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(perCategoria, {
      y: "categoria",
      x: "num",
      fill: "categoria",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Oneri per categoria PA

L'onere finanziario maggiore è sostenuto dalle Regioni, nonostante abbiano meno partecipazioni dei Comuni — segno che le partecipazioni regionali sono in società più grandi e costose.

```js
const perOneri = [...perCategoria].filter(d => d.oneri > 0).sort((a, b) => b.oneri - a.oneri);
```

```js
Plot.plot({
  title: `Oneri per categoria PA — ${String(annoSel)}`,
  width: 800,
  height: 350,
  marginLeft: 160,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Oranges"},
  marks: [
    Plot.barX(perOneri, {
      y: "categoria",
      x: "oneri",
      fill: "oneri",
      sort: {y: "-x"},
      tip: {format: {x: d => euroCompact(d)}}
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Trend 2020-2023

```js
const trend = Array.from(
  d3.rollup(data, v => ({
    num: d3.sum(v, d => d.num_partecipate),
    oneri: d3.sum(v, d => d.totale_oneri),
  }), d => d.anno),
  ([anno, v]) => ({anno, ...v})
).sort((a, b) => a.anno - b.anno);
```

```js
Plot.plot({
  title: "Totale partecipazioni e oneri per anno",
  width: 800,
  height: 300,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, tickFormat: "~s", label: "Partecipazioni"},
  marks: [
    Plot.barY(trend, {x: "anno", y: "num", fill: "#4e79a7", tip: true}),
    Plot.text(trend, {x: "anno", y: "num", text: d => num(d.num), dy: -6, fontSize: 11})
  ]
})
```

---

## Dettaglio per categoria

```js
const { header, format } = tableFormat({
  categoria: { label: "Categoria PA", fmt: "string" },
  num: { label: "Partecipazioni", fmt: "num" },
  oneri: { label: "Oneri (€)", fmt: "euroCompact" },
  addetti: { label: "Addetti", fmt: "num" },
});
Inputs.table(perCategoria, {
  columns: ["categoria", "num", "oneri", "addetti"],
  header,
  format,
  rows: 20,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie copre il periodo 2020-2023. Dati precedenti non sono disponibili.
- **Partecipazioni**: il numero indica società distinte in cui la PA detiene quote (deduplicate per denominazione).
- **Addetti**: il totale addetti è deduplicato per società (MAX per partecipata) per evitare il doppio conteggio quando più enti detengono quote della stessa azienda. Il dato potrebbe comunque includere alcune duplicazioni residue.
- **Oneri**: gli oneri impegnati sono quelli dichiarati dalle amministrazioni. La metodologia di rendicontazione può variare tra enti.
- **Fonte**: i dati provengono dal MEF — Dipartimento dell'Economia, portale Partecipazioni Pubbliche.

---

## Risorse

- [MEF — Partecipazioni Pubbliche](https://www.mef.gov.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/mef_partecipazioni/2023/mef_partecipazioni_2023_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/mef-partecipazioni)

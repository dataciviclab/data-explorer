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

Quante società sono controllate dalla PA italiana, quanto costano e quanti addetti impiegano? I dati MEF mostrano le partecipazioni pubbliche per categoria di amministrazione (Comuni, Regioni, Università, ecc.) e settore economico.

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
const mediaQuota = d3.mean(filtered, d => d.quota_media);
```

```js
// Per categoria (aggregato)
const perCategoria = Array.from(
  d3.rollup(filtered, v => ({
    num: d3.sum(v, d => d.num_partecipate),
    oneri: d3.sum(v, d => d.totale_oneri),
    addetti: d3.sum(v, d => d.totale_addetti),
    quota_media: d3.mean(v, d => d.quota_media),
  }), d => d.categoria),
  ([categoria, v]) => ({categoria, ...v})
).sort((a, b) => b.num - a.num);
```

```js
// Per categoria + settore (per stacked bar)
const perCatSett = Array.from(
  d3.rollup(filtered, v => ({
    num: d3.sum(v, d => d.num_partecipate),
    oneri: d3.sum(v, d => d.totale_oneri),
    addetti: d3.sum(v, d => d.totale_addetti),
  }), d => d.categoria, d => d.settore),
  ([categoria, settori]) => Array.from(settori, ([settore, v]) => ({categoria, settore, ...v}))
).flat().sort((a, b) => b.num - a.num);
```

```js
// Trend per categoria (evoluzione 2020-2023)
const trendPerCat = Array.from(
  d3.rollup(data, v => d3.sum(v, d => d.num_partecipate), d => d.anno, d => d.categoria),
  ([anno, cats]) => Array.from(cats, ([categoria, num]) => ({anno, categoria, num}))
).flat().sort((a, b) => a.anno - b.anno);

// Top 7 categorie per trend (raggruppa il resto in "Altre")
const topCats = perCategoria.slice(0, 7).map(d => d.categoria);
const trendChart = trendPerCat.map(d => ({
  ...d,
  categoria: topCats.includes(d.categoria) ? d.categoria : "Altre"
}));
```

<div class="grid grid-cols-4">
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
  <div class="card">
    <h3>Quota media</h3>
    <span class="big">${Math.round(mediaQuota * 10) / 10}%</span>
    <small style="opacity:0.6">partecipazione media</small>
  </div>
</div>

---

## Partecipazioni per categoria e settore

I Comuni detengono la maggior parte delle partecipazioni, concentrate nel settore secondario (municipalizzate, utilities, società strumentali). Le Regioni hanno meno società ma con oneri molto più alti (sanità, trasporti). Le Università e le Camere di Commercio completano il quadro con partecipazioni prevalentemente nel terziario.

```js
Plot.plot({
  title: `Partecipazioni per categoria e settore — ${String(annoSel)}`,
  width: 800,
  height: 350,
  marginLeft: 160,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {legend: true, scheme: "Set2"},
  marks: [
    Plot.barX(perCatSett, {
      y: "categoria",
      x: "num",
      fill: "settore",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Oneri per categoria PA

L'onere finanziario maggiore è sostenuto dalle Regioni (sanità e trasporti), nonostante abbiano meno partecipazioni dei Comuni. Il dato è invertito rispetto al numero di società: poche ma costose.

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

## Evoluzione 2020-2023

Come cambia il numero di partecipazioni per categoria nel tempo? Le linee mostrano l'evoluzione annuale delle principali categorie. Le partecipazioni dei Comuni sono in lieve calo, mentre Regioni e Università restano stabili.

```js
Plot.plot({
  title: "Partecipazioni per categoria — trend 2020-2023",
  width: 800,
  height: 350,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, tickFormat: "~s", label: "Partecipazioni"},
  color: {legend: true, scheme: "Set2"},
  marks: [
    Plot.line(trendChart, {x: "anno", y: "num", z: "categoria", stroke: "categoria", tip: true}),
    Plot.dot(trendChart, {x: "anno", y: "num", z: "categoria", fill: "categoria", r: 3}),
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
  quota_media: { label: "Quota media", fmt: "pct" },
});
```

```js
Inputs.table(perCategoria, {
  columns: ["categoria", "num", "oneri", "addetti", "quota_media"],
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
- **Quota media**: la quota di partecipazione media è calcolata come media semplice tra le partecipazioni, non ponderata per oneri o addetti.
- **Fonte**: i dati provengono dal MEF — Dipartimento dell'Economia, portale Partecipazioni Pubbliche.

---

## Risorse

- [MEF — Partecipazioni Pubbliche](https://www.mef.gov.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/mef_partecipazioni/2023/mef_partecipazioni_2023_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/mef-partecipazioni)

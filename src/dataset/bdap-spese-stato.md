---
title: Spese dello Stato
description: Previsioni definitive di spesa per amministrazione e missione — BDAP, 2008-2024
source: MEF — BDAP
source_url: https://www.rgs.mef.gov.it/
period: "2008–2024"
last_modified: 2026-06-10
dataset_slug: bdap_spese_stato
---

# Spese dello Stato

Previsioni definitive di spesa delle amministrazioni statali italiane, per amministrazione e missione. I dati mostrano chi spende e in cosa, dal 2008 al 2024.

**Fonte**: [MEF — BDAP](https://www.rgs.mef.gov.it/) · **Periodo**: 2008–2024

```js
import { num, euroCompact, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/bdap-spese-stato.json").json();
```

```js
const anni = [...new Set(data.map(d => d.esercizio_finanziario))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.esercizio_finanziario === annoSel);
const totSpesa = d3.sum(filtered, d => d.previsioni_definitive_cp);
const nAmm = new Set(filtered.map(d => d.amministrazione)).size;
const nMissioni = new Set(filtered.map(d => d.missione)).size;

// Spesa per amministrazione
const perAmm = Array.from(
  d3.rollup(filtered, v => d3.sum(v, d => d.previsioni_definitive_cp), d => d.amministrazione),
  ([amministrazione, spesa]) => ({amministrazione, spesa})
).sort((a, b) => b.spesa - a.spesa);

// Spesa per missione
const perMissione = Array.from(
  d3.rollup(filtered, v => d3.sum(v, d => d.previsioni_definitive_cp), d => d.missione),
  ([missione, spesa]) => ({missione, spesa})
).sort((a, b) => b.spesa - a.spesa).slice(0, 15);

// Trend totale
const trend = Array.from(
  d3.rollup(data, v => d3.sum(v, d => d.previsioni_definitive_cp), d => d.esercizio_finanziario),
  ([esercizio_finanziario, spesa]) => ({esercizio_finanziario, spesa})
).sort((a, b) => a.esercizio_finanziario - b.esercizio_finanziario);

// Delta 2008→2024
const spesa2008 = trend.find(d => d.esercizio_finanziario === 2008)?.spesa || 0;
const spesa2024 = trend.find(d => d.esercizio_finanziario === 2024)?.spesa || 0;
const deltaPct = spesa2008 ? Math.round((spesa2024 - spesa2008) / spesa2008 * 1000) / 10 : 0;
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Spesa totale</h3>
    <span class="big">${euroCompact(totSpesa)}</span>
    <small style="opacity:0.6">${String(annoSel)}</small>
  </div>
  <div class="card">
    <h3>Amministrazioni</h3>
    <span class="big">${nAmm}</span>
  </div>
  <div class="card">
    <h3>Missioni</h3>
    <span class="big">${nMissioni}</span>
  </div>
</div>

---

## Evoluzione della spesa 2008-2024

La spesa statale totale è cresciuta da €748 mld nel 2008 a oltre €1.245 mld nel 2024 (+${deltaPct}%). Il salto del 2020 riflette le misure pandemiche.

```js
Plot.plot({
  title: "Previsioni definitive di spesa — 2008-2024",
  width: 800,
  height: 350,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, tickFormat: "~s", label: "Spesa (€)"},
  marks: [
    Plot.lineY(trend, {x: "esercizio_finanziario", y: "spesa", tip: {format: {y: d => euroCompact(d)}}}),
    Plot.dot(trend, {x: "esercizio_finanziario", y: "spesa", fill: "steelblue", r: 3}),
    Plot.areaY(trend, {x: "esercizio_finanziario", y: "spesa", fill: "steelblue", fillOpacity: 0.05}),
    Plot.ruleY([0])
  ]
})
```

---

## Spesa per amministrazione — ${String(annoSel)}

```js
Plot.plot({
  title: `Spesa per amministrazione — ${String(annoSel)}`,
  width: 800,
  height: 400,
  marginLeft: 220,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Blues"},
  marks: [
    Plot.barX(perAmm, {
      y: "amministrazione",
      x: "spesa",
      fill: "spesa",
      sort: {y: "-x"},
      tip: {format: {x: d => euroCompact(d)}}
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Spesa per missione — ${String(annoSel)}

```js
Plot.plot({
  title: `Spesa per missione — ${String(annoSel)}`,
  width: 800,
  height: 400,
  marginLeft: 220,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Oranges"},
  marks: [
    Plot.barX(perMissione, {
      y: "missione",
      x: "spesa",
      fill: "spesa",
      sort: {y: "-x"},
      tip: {format: {x: d => euroCompact(d)}}
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Dettaglio per amministrazione e missione

```js
const { header, format } = tableFormat({
  amministrazione: { label: "Amministrazione", fmt: "string" },
  missione: { label: "Missione", fmt: "string" },
  previsioni_definitive_cp: { label: "Spesa (cp)", fmt: "euroCompact" },
  previsioni_definitive_cs: { label: "Spesa (cs)", fmt: "euroCompact" },
});
```

```js
Inputs.table(filtered, {
  columns: ["amministrazione", "missione", "previsioni_definitive_cp", "previsioni_definitive_cs"],
  header,
  format,
  rows: 20,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie copre il periodo 2008-2024. Tutti i dati provengono da un unico file BDAP.
- **Previsioni definitive**: i dati sono previsioni di spesa definitive, non spese effettivamente sostenute. Possono differire dai consuntivi.
- **Amministrazioni**: la denominazione delle amministrazioni può cambiare nel periodo (es. fusioni, scissioni di ministeri). I dati riflettono la denominazione al momento della previsione.
- **Missioni**: la classificazione per missione segue il COFOG (Classificazione delle Funzioni di Governo). Alcune missioni hanno denominazioni leggermente variabili negli anni.

---

## Risorse

- [MEF — BDAP](https://www.rgs.mef.gov.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/bdap_spese_stato/2024/bdap_spese_stato_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/bdap-spese-stato)

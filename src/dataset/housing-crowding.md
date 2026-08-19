---
title: Densità abitativa
description: Indice di densità abitativa per titolo di godimento — ISTAT, 2004-2025
source: ISTAT — Dataflow 33_179
source_url: https://esploradati.istat.it/
period: "2004–2025"
last_modified: 2026-06-02
dataset_slug: istat_housing_crowding
data_driven: true
---

# Densità abitativa

```js
import { num, numFix, pct, unit, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/housing-crowding.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel);
const totale = d3.mean(filtered, d => d.componenti_per_100mq);
const minVal = d3.min(filtered, d => d.componenti_per_100mq);
const maxVal = d3.max(filtered, d => d.componenti_per_100mq);
const densityGap = maxVal - minVal;
```

**Nel ${String(annoSel)} la densità abitativa media è di ${numFix(totale, 1)} componenti per 100 mq, con un divario di ${numFix(densityGap, 1)} punti tra chi affitta (${numFix(maxVal, 1)}) e chi possiede (${numFix(minVal, 1)}).**

Indice di densità abitativa (componenti per 100 mq) per titolo di godimento. I dati mostrano come evolve l'affollamento abitativo in Italia e le differenze tra proprietà e affitto. Ogni numero di questa pagina è calcolato dal dato a build-time.

**Fonte**: [ISTAT](https://esploradati.istat.it/) · **Periodo**: 2004–2025

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Densità media</h3>
    <span class="big">${numFix(totale, 1)}</span>
    <small style="opacity:0.6">componenti/100mq</small>
  </div>
  <div class="card">
    <h3>Divario affitto/proprietà</h3>
    <span class="big">${numFix(densityGap, 1)}</span>
    <small style="opacity:0.6">punti di densità</small>
  </div>
  <div class="card">
    <h3>Periodo</h3>
    <span class="big">${String(anni[anni.length - 1])}–${String(anni[0])}</span>
    <small style="opacity:0.6">${anni.length} osservazioni</small>
  </div>
</div>

---

## 1. Densità per titolo di godimento — ${String(annoSel)}

Chi vive in case più affollate? Chi affitta ha una densità abitativa maggiore rispetto a chi possiede l'abitazione.

```js
Plot.plot({
  title: `Componenti per 100 mq per titolo di godimento — ${String(annoSel)}`,
  width: 800,
  height: 250,
  marginLeft: 120,
  y: {label: null, tickSize: 0},
  x: {grid: true},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(filtered, {
      y: "titolo_godimento",
      x: "componenti_per_100mq",
      fill: "titolo_godimento",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

> **Nota di lettura**: il grafico mostra lo **stock** del ${String(annoSel)}: la densità per ciascuna tipologia di godimento. La tendenza temporale è nel grafico successivo.

---

## 2. Evoluzione 2004–2025

Come cambia la densità abitativa nel tempo? Il divario tra proprietà e affitto si è ridotto negli ultimi vent'anni.

```js
const trend = data.sort((a, b) => a.anno - b.anno);
```

```js
Plot.plot({
  title: "Componenti per 100 mq — tendenza 2004-2025",
  width: 800,
  height: 350,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, label: "Componenti per 100 mq"},
  color: {legend: true},
  marks: [
    Plot.line(trend, {
      x: "anno",
      y: "componenti_per_100mq",
      z: "titolo_godimento",
      stroke: "titolo_godimento",
      tip: true
    }),
    Plot.dot(trend, {
      x: "anno",
      y: "componenti_per_100mq",
      z: "titolo_godimento",
      fill: "titolo_godimento",
      r: 1.5
    })
  ]
})
```

---

## Dettaglio per anno

```js
const { header, format } = tableFormat({
  anno: { label: "Anno", fmt: "string" },
  titolo_godimento: { label: "Titolo godimento", fmt: "string" },
  componenti_per_100mq: { label: "Comp./100mq", fmt: "num", decimals: 2 },
});
```

```js
Inputs.table(trend, {
  columns: ["anno", "titolo_godimento", "componenti_per_100mq"],
  header,
  format,
  rows: 25,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie copre il periodo 2004-2025. Dati precedenti non sono disponibili.
- **Indice**: la densità abitativa misura i componenti del nucleo familiare ogni 100 mq di abitazione. Valori più alti indicano maggiore affollamento.
- **Nazionale**: i dati sono a livello nazionale. Non è disponibile la disaggregazione regionale in questo dataset.

---

## Risorse

- [ISTAT — Esplora dati](https://esploradati.istat.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/istat_housing_crowding/2024/istat_housing_crowding_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/istat-housing-crowding)

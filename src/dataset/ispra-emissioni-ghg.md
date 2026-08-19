---
title: Emissioni GHG da processi energetici
description: Emissioni di gas serra da processi energetici per settore — ISPRA Inventario Nazionale UNFCCC/EEA, 1990-2023
source: ISPRA — Indicatori Ambientali
source_url: https://indicatoriambientali.isprambiente.it/
period: "1990–2023"
last_modified: 2026-07-12
dataset_slug: ispra_emissioni_ghg
data_driven: true
---

# Emissioni GHG da processi energetici

**Nel ${String(annoMax)} le emissioni da processi energetici ammontano a ${unit(ultimoAnno.totale, "Mt CO₂eq")}, in ${varPct > 0 ? "aumento" : "diminuzione"} del ${Math.abs(varPct)}% rispetto al ${String(annoMin)}. I trasporti sono il settore più stabile, mentre industrie energetiche e manifatturiere sono in calo strutturale.**

Emissioni di gas serra da processi energetici in Italia, per settore economico: industrie energetiche, industrie manifatturiere, residenziale e servizi, trasporti. Ogni numero di questa pagina è calcolato dal dato a build-time.

**Fonte**: [ISPRA](https://indicatoriambientali.isprambiente.it/) · **Periodo**: 1990–2023

```js
import { num, numFix, pct, unit, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/ispra-emissioni-ghg.json").json();
```

```js
const settori = ["industrie_energetiche", "industrie_manifatturiere", "residenziale_e_servizi", "trasporti"];
const settoreLabel = {
  industrie_energetiche: "Industrie energetiche",
  industrie_manifatturiere: "Industrie manifatturiere",
  residenziale_e_servizi: "Residenziale e servizi",
  trasporti: "Trasporti",
};
```

```js
const annoMin = d3.min(data, d => d.anno);
const annoMax = d3.max(data, d => d.anno);
const ultimoAnno = data.find(d => d.anno === annoMax);
const primoAnno = data.find(d => d.anno === annoMin);
const varPct = Math.round((ultimoAnno.totale - primoAnno.totale) / primoAnno.totale * 1000) / 10;
```

```js
const trendPerSettore = data.flatMap(d =>
  settori.map(s => ({anno: d.anno, settore: settoreLabel[s], emissioni: d[s]}))
);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Emissioni totali (${String(annoMax)})</h3>
    <span class="big">${unit(ultimoAnno.totale, "Mt CO₂eq")}</span>
  </div>
  <div class="card">
    <h3>Settori</h3>
    <span class="big">${settori.length}</span>
  </div>
  <div class="card">
    <h3>Variazione ${String(annoMin)}→${String(annoMax)}</h3>
    <span class="big">${varPct > 0 ? "+" : ""}${varPct}%</span>
  </div>
</div>

---

## 1. Mix settoriale — ${String(annoMax)}

La composizione delle emissioni per settore nel ${String(annoMax)}. I trasporti e le industrie energetiche sono le due voci principali; residenziale e servizi risente della variabilità climatica invernale.

```js
const mixUltimoAnno = settori.map(s => ({settore: settoreLabel[s], emissioni: ultimoAnno[s], pct: ultimoAnno[s] / ultimoAnno.totale * 100}));
```

```js
Plot.plot({
  title: `Emissioni per settore — ${String(annoMax)}`,
  width: 800,
  height: 250,
  marginLeft: 180,
  y: {label: null, tickSize: 0},
  x: {grid: true, label: "Emissioni (Mt CO₂eq)"},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(mixUltimoAnno, {
      y: "settore",
      x: "emissioni",
      fill: "settore",
      sort: {y: "-x"},
      tip: {format: {x: d => `${d.toFixed(1)} Mt CO₂eq`}}
    }),
    Plot.text(mixUltimoAnno, {
      y: "settore",
      x: "emissioni",
      text: d => `${d.pct.toFixed(1)}%`,
      dx: 6,
      textAnchor: "start",
      fill: "var(--theme-foreground-muted)",
      fontSize: 12
    }),
    Plot.ruleX([0])
  ]
})
```

> **Nota di lettura**: il grafico mostra lo **stock** del ${String(annoMax)}: quante emissioni per ciascun settore. La lettura del trend è nel grafico successivo.

---

## 2. Evoluzione per settore ${String(annoMin)}–${String(annoMax)}

Le emissioni da industrie energetiche e manifatturiere sono in calo strutturale dagli anni 2000. Il settore trasporti resta il più stabile, mentre residenziale e servizi risente della variabilità climatica invernale.

```js
Plot.plot({
  title: "Emissioni GHG per settore — 1990-2023",
  width: 800,
  height: 350,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, label: "Emissioni (Mt CO₂eq)"},
  color: {legend: true, scheme: "Set2"},
  marks: [
    Plot.areaY(trendPerSettore, {x: "anno", y: "emissioni", fill: "settore", order: "sum", fillOpacity: 0.7}),
    Plot.ruleY([0]),
  ]
})
```

---

## 3. Serie storica emissioni totali

```js
Plot.plot({
  title: "Emissioni totali per anno",
  width: 800,
  height: 300,
  x: {tickFormat: d => String(d)},
  y: {grid: true, label: "Emissioni (Mt CO₂eq)"},
  marks: [
    Plot.lineY(data, {x: "anno", y: "totale", tip: true}),
    Plot.dot(data, {x: "anno", y: "totale", fill: "steelblue"}),
    Plot.areaY(data, {x: "anno", y: "totale", fill: "steelblue", fillOpacity: 0.05}),
  ]
})
```

---

## Dettaglio per anno

```js
const { header, format } = tableFormat({
  anno: { label: "Anno", fmt: "string" },
  industrie_energetiche: { label: "Ind. energetiche", fmt: "num", decimals: 1 },
  industrie_manifatturiere: { label: "Ind. manifatturiere", fmt: "num", decimals: 1 },
  residenziale_e_servizi: { label: "Residenziale e servizi", fmt: "num", decimals: 1 },
  trasporti: { label: "Trasporti", fmt: "num", decimals: 1 },
  totale: { label: "Totale", fmt: "num", decimals: 1 },
});
```

```js
Inputs.table(data.slice().sort((a, b) => b.anno - a.anno), {
  columns: ["anno", ...settori, "totale"],
  header,
  format,
  rows: 34,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie copre il periodo 1990-2023. I dati più recenti possono essere soggetti a revisione da parte di ISPRA nell'ambito dell'Inventario Nazionale UNFCCC/EEA.
- **Perimetro**: le emissioni riguardano esclusivamente i processi energetici (combustione), non l'intero inventario nazionale GHG (che include anche processi industriali non energetici, agricoltura e rifiuti).
- **Totale**: la colonna "totale" è la somma dei quattro settori riportati e non coincide con il totale nazionale delle emissioni GHG.

---

## Risorse

- [ISPRA — Indicatori Ambientali (fonte originale)](https://indicatoriambientali.isprambiente.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/ispra_emissioni_ghg/2023/ispra_emissioni_ghg_2023_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/ispra-emissioni-ghg)

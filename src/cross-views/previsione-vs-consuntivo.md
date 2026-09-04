---
title: "Previsione vs Consuntivo per Missione"
description: "Quanto è stato previsto nel bilancio dello Stato vs quanto è stato effettivamente pagato, per missione di spesa — tasso di esecuzione 2014–2025"
source: MEF — RGS · BDAP
source_url: https://bdap.rgs.mef.gov.it/
period: "2014–2025"
data_driven: true
cross_view: true
datasets:
  - bdap_spese_stato
  - bdap_pagamenti_stato
---

# Previsione vs Consuntivo — quante spese vengono effettivamente pagate?

**Nel ${lastYear} lo Stato ha previsto ${euroCompact(totalePrevisto)} di spese, ma ne ha pagate solo ${euroCompact(totalePagato)}: ${euroCompact(totalePrevisto - totalePagato)} restano non spesi. Il tasso di esecuzione complessivo è del ${pct(tassoComplessivo)}. Le missioni con il tasso più basso sono quelle con maggiori vincoli burocratici o fondi pluriennali.**

Questa cross-view incrocia i dati di **previsione** (bilancio dello Stato, BDAP) con quelli di **consuntivo** (pagamenti effettivi, BDAP) per missione di spesa. Mostra quanto del budget previsto viene realmente speso.

```js
import { euroCompact, pct, numFix, tableFormat } from "../import/format-utils.js";
```

```js
const rows = await FileAttachment("../data/previsione-vs-consuntivo.json").json();
```

```js
// Capitalizza i nomi delle missioni (lowercase nel data)
// In italiano, articoli/preposizioni/congiunzioni restano minuscoli
const _lower = new Set(["di","a","da","in","con","su","per","tra","fra","e","o","ma","che","il","lo","la","i","gli","le","un","uno","una","del","dello","della","dei","degli","delle","al","allo","alla","ai","agli","alle","dal","dallo","dalla","dai","dagli","dalle","nel","nello","nella","nei","negli","nelle","sul","sullo","sulla","sui","sugli","sulle","l","s"]);
const cap = (s) => s.split(" ").map((w, i) => i === 0 || !_lower.has(w.toLowerCase()) ? w.charAt(0).toUpperCase() + w.slice(1) : w.toLowerCase()).join(" ");

// Ultimo anno con consuntivo disponibile
const withPagato = rows.filter(d => d.pagato != null);
const years = [...new Set(withPagato.map(d => d.anno))].sort();
const lastYear = years[years.length - 1];

const dataLast = withPagato
  .filter(d => d.anno === lastYear)
  .map(d => ({
    missione: cap(d.missione),
    previsto: d.previsto,
    pagato: d.pagato,
    tasso: d.tasso_esecuzione,
    delta: d.previsto - d.pagato,
  }))
  .sort((a, b) => b.previsto - a.previsto);

const totalePrevisto = dataLast.reduce((s, d) => s + d.previsto, 0);
const totalePagato = dataLast.reduce((s, d) => s + d.pagato, 0);
const tassoComplessivo = totalePrevisto > 0 ? (totalePagato / totalePrevisto) * 100 : null;
```

<div class="grid grid-cols-3">
  <div class="card"><h3>Previsto ${lastYear}</h3><span class="big">${euroCompact(totalePrevisto)}</span></div>
  <div class="card"><h3>Pagato ${lastYear}</h3><span class="big">${euroCompact(totalePagato)}</span></div>
  <div class="card"><h3>Tasso esecuzione</h3><span class="big">${pct(tassoComplessivo)}</span></div>
</div>

## 1. Le missioni con il tasso di esecuzione più basso — ${lastYear}

Non tutte le spese vengono pagate alla stessa velocità. Le missioni con fondi destinate a investimenti o trasferimenti hanno spesso tassi di esecuzione più bassi rispetto al funzionamento corrente.

```js
const plot = await import("npm:@observablehq/plot");
const bottom10 = dataLast.filter(d => d.tasso != null).sort((a, b) => a.tasso - b.tasso).slice(0, 10);
display(plot.plot({
  title: `Missioni con tasso di esecuzione più basso — ${lastYear}`,
  width: 800, height: 320, marginLeft: 320, marginRight: 70,
  x: {grid: true, domain: [0, 0.85], tickFormat: ".0%"},
  y: {label: null, tickSize: 0},
  marks: [
    plot.barX(bottom10, {x: "tasso", y: "missione", fill: "#d62728", tip: true}),
    plot.text(bottom10, {x: "tasso", y: "missione", text: d => ` ${(d.tasso * 100).toFixed(1)}%`, dx: 6, textAnchor: "start", fontSize: 11}),
    plot.ruleX([1], {stroke: "#888", strokeDasharray: "4 4"})
  ]
}))
```

## 2. Trend del tasso di esecuzione complessivo

Il tasso di esecuzione complessivo è la fotografia di quanto lo Stato è in grado di spendere rispetto a quanto previsto. Un tasso basso non è necessariamente negativo: può riflettere vincoli normativi o ritardi strutturali.

```js
const trendData = years.map(y => {
  const yr = withPagato.filter(d => d.anno === y);
  const prev = yr.reduce((s, d) => s + d.previsto, 0);
  const pag = yr.reduce((s, d) => s + d.pagato, 0);
  return { anno: y, tasso: prev > 0 ? pag / prev : null };
}).filter(d => d.tasso != null);

display(plot.plot({
  title: "Tasso di esecuzione complessivo del bilancio — previsione vs pagato",
  width: 800, height: 300,
  x: {tickFormat: String},
  y: {grid: true, domain: [0.8, 1.05], label: "rapporto pagato / previsto"},
  marks: [
    plot.ruleY([1], {stroke: "#888", strokeDasharray: "4 4"}),
    plot.line(trendData, {x: "anno", y: "tasso", stroke: "#2c7fb8", strokeWidth: 2}),
    plot.dot(trendData, {x: "anno", y: "tasso", fill: "#fff", stroke: "#2c7fb8"}),
    plot.text(trendData.filter(d => d.anno === lastYear), {x: "anno", y: "tasso", text: d => " " + pct(d.tasso * 100), dx: 8, dy: -8, fontSize: 11})
  ]
}))
```

## 3. Previsione vs Consuntivo per missione — ${lastYear}

Il confronto diretto tra quanto previsto e quanto pagato per ogni missione.

```js
const top10 = dataLast.slice(0, 10);
const barData = top10.flatMap(d => [
  {missione: d.missione, tipo: "Previsto", value: d.previsto},
  {missione: d.missione, tipo: "Pagato", value: d.pagato}
]);
display(plot.plot({
  title: `Previsione vs Pagato per missione — ${lastYear}`,
  width: 800, height: 400, marginLeft: 340,
  x: {grid: true, tickFormat: d => `${(d / 1e9).toFixed(0)} B€`, label: null},
  y: {label: null, tickSize: 0, domain: top10.map(d => d.missione)},
  color: {domain: ["Previsto", "Pagato"], range: ["#9ecae1", "#2c7fb8"]},
  marks: [
    plot.barX(barData, {x: "value", y: "missione", fill: "tipo"}),
    plot.text(barData, {x: "value", y: "missione", text: d => `${(d.value / 1e9).toFixed(0)} B€`, dx: 4, textAnchor: "start", fontSize: 10, fill: "currentColor"}),
    plot.ruleX([0])
  ]
}))
```

---

## Dettaglio per missione

<small>Tutte le missioni con previsione, consuntivo e tasso di esecuzione. Ordina per qualsiasi colonna.</small>

```js
const { header, format } = tableFormat({
  missione: { label: "Missione", fmt: "string" },
  previsto: { label: "Previsto", fmt: "euroCompact" },
  pagato: { label: "Pagato", fmt: "euroCompact" },
  tasso: { label: "Tasso esecuzione", fmt: "pct" },
  delta: { label: "Differenza", fmt: "euroCompact" },
});
```

```js
const table = dataLast.map(d => ({
  missione: d.missione,
  previsto: d.previsto,
  pagato: d.pagato,
  tasso: d.tasso * 100,
  delta: d.delta,
}));
```

```js
Inputs.table(table, {
  columns: ["missione", "previsto", "pagato", "tasso", "delta"],
  header,
  format,
  rows: dataLast.length,
  width: "100%",
  sort: "previsto",
  reverse: true
})
```

---

## Limiti

- **Tempistica**: il consuntivo dei pagamenti ha un ritardo di circa un anno rispetto alla previsione; i dati più recenti potrebbero non avere ancora il consuntivo completo.
- **Copertura**: i pagamenti coprono il 2014–2025; la previsione parte dal 2008. L'overlap effettivo è 2014–2025.
- **Classificazione**: la missione di spesa segue la classificazione funzionale del bilancio, soggetta a riclassificazioni tra esercizi.

## Risorse

- [Cross-view definition](https://github.com/dataciviclab/data-explorer/blob/main/cross-views/defs/previsione-vs-consuntivo.sql) — SQL riutilizzabile da MCP, dashboard, notebook
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Entrate dello Stato](/dataset/entrate-stato) — il complemento di questa vista
- [Pipeline spese](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/bdap-spese-stato) · [Pipeline pagamenti](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/bdap-pagamenti-stato)

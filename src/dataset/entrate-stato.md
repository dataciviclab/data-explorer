---
title: Entrate dello Stato
description: Previsioni definitive di entrata dello Stato per titolo (BDAP — RGS MEF)
---

# Entrate dello Stato

Previsioni definitive di entrata dello Stato per titolo, dal bilancio dello Stato (BDAP — RGS MEF).

**Fonte**: RGS · BDAP · **Periodo**: 2008–2024

```js
const data = await FileAttachment("../data/bdap-entrate.json").json();
```

```js
const anni = [...new Set(data.map(d => d.esercizio_finanziario))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(anni, {label: "Anno", value: anni[0]}));
```

```js
const filtered = data
  .filter(d => d.esercizio_finanziario === annoSel && d.previsioni_definitive_cp > 0)
  .sort((a, b) => b.previsioni_definitive_cp - a.previsioni_definitive_cp);
```

```js
const totaleEntrate = d3.sum(filtered, d => d.previsioni_definitive_cp);
```

<div class="grid grid-cols-2">
  <div class="card">
    <h3>Entrate totali</h3>
    <span class="big">€ ${(totaleEntrate / 1e9).toFixed(1)} <small style="opacity:0.6">mld</small></span>
  </div>
  <div class="card">
    <h3>Titoli</h3>
    <span class="big">${filtered.length}</span>
  </div>
</div>

---

## Entrate per titolo

```js
Plot.plot({
  title: `Previsioni definitive entrata per titolo — ${annoSel}`,
  width: 800,
  height: 300,
  marginLeft: 200,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Blues"},
  marks: [
    Plot.barX(filtered, {
      y: "titolo",
      x: "previsioni_definitive_cp",
      fill: "previsioni_definitive_cp",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Serie storica entrate totali

```js
const trend = Array.from(d3.rollup(data, v => d3.sum(v, d => d.previsioni_definitive_cp), d => d.esercizio_finanziario), ([esercizio_finanziario, previsioni_definitive_cp]) => ({esercizio_finanziario, previsioni_definitive_cp})).sort((a,b) => a.esercizio_finanziario - b.esercizio_finanziario);
```

```js
Plot.plot({
  title: "Entrate totali dello Stato per anno",
  width: 800,
  height: 350,
  y: {grid: true, tickFormat: "~s"},
  marks: [
    Plot.lineY(trend, {x: "esercizio_finanziario", y: "previsioni_definitive_cp", tip: true}),
    Plot.dot(trend, {x: "esercizio_finanziario", y: "previsioni_definitive_cp", fill: "steelblue"}),
    Plot.areaY(trend, {x: "esercizio_finanziario", y: "previsioni_definitive_cp", fill: "steelblue", fillOpacity: 0.05}),
  ]
})
```

---

## Dettaglio

```js
Inputs.table(filtered, {
  columns: ["titolo", "previsioni_definitive_cp", "previsioni_definitive_cs"],
  header: {titolo: "Titolo", previsioni_definitive_cp: "Competenza (€)", previsioni_definitive_cs: "Cassa (€)"},
  format: {previsioni_definitive_cp: x => `€ ${(x / 1e9).toFixed(2)} mld`, previsioni_definitive_cs: x => `€ ${(x / 1e9).toFixed(2)} mld`},
  rows: 10,
  width: "100%"
})
```

---

## Risorse

- [RGS · BDAP](https://bdap.rgs.mef.gov.it/)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/bdap-entrate-stato)

---
title: Entrate dello Stato
description: Previsioni definitive di entrata dello Stato per titolo, natura e tipologia — BDAP RGS MEF, 2008-2024
source: RGS · BDAP — Banca Dati delle Amministrazioni Pubbliche
source_url: https://bdap.rgs.mef.gov.it/
period: "2008–2024"
last_modified: 2026-05-26
dataset_slug: bdap_entrate_stato
---

# Entrate dello Stato

Previsioni definitive di entrata dello Stato per titolo, dal bilancio dello Stato (BDAP — RGS MEF).

**Fonte**: RGS · BDAP · **Periodo**: 2008–2024

```js
const data = await FileAttachment("../data/bdap-entrate.json").json();
```

```js
const anni = [...new Set(data.map(d => d.esercizio_finanziario))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
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

---

## Limiti

- **Previsioni**: i dati si riferiscono alle previsioni definitive di bilancio, non agli effettivi incassi. La differenza tra previsioni e consuntivo può essere significativa.
- **Copertura**: la serie parte dal 2008, anno di introduzione della contabilità armonizzata per lo Stato. Anni precedenti non sono comparabili.
- **Classificazione**: la disaggregazione per titolo segue la classificazione economica del bilancio dello Stato, che può variare tra esercizi finanziari.

---

## Risorse

- [RGS · BDAP (fonte originale)](https://bdap.rgs.mef.gov.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/bdap_entrate_stato/2024/bdap_entrate_stato_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/bdap-entrate-stato)

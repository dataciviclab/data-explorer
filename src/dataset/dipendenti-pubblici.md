---
title: Dipendenti pubblici per comparto
description: Dati BDAP/RGS sul pubblico impiego, crescita e composizione dei comparti (2010-2023)
---

# Dipendenti pubblici per comparto

Dati BDAP/RGS sui dipendenti pubblici italiani per comparto nel periodo 2010-2023.

**Fonte**: MEF · RGS · BDAP · **Periodo**: 2010–2023

```js
const data = await FileAttachment("../data/dipendenti-pubblici.json").json();
```

```js
const comparti = [...new Set(data.map(d => d.comparto))].sort();
const compartoSel = view(Inputs.select(
  [{label: "Tutti i comparti", value: "Tutti"}, ...comparti.map(c => ({label: c, value: c}))],
  {label: "Comparto", value: "Tutti", key: "comp"}
));
```

```js
const filtered = compartoSel === "Tutti" ? data : data.filter(d => d.comparto === compartoSel);
```

```js
const tot2023 = data.filter(d => d.anno === 2023).reduce((s, d) => s + d.totale, 0);
const tot2010 = data.filter(d => d.anno === 2010).reduce((s, d) => s + d.totale, 0);
const delta = tot2023 - tot2010;
const pctDonne2023 = Math.round(data.filter(d => d.anno === 2023).reduce((s, d) => s + d.donne, 0) / tot2023 * 1000) / 10;
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Dipendenti 2023</h3>
    <span class="big">${tot2023.toLocaleString("it-IT")}</span>
  </div>
  <div class="card">
    <h3>Variazione 2010→2023</h3>
    <span class="big">${(delta > 0 ? "+" : "")}${delta.toLocaleString("it-IT")}</span>
  </div>
  <div class="card">
    <h3>Donne %</h3>
    <span class="big">${pctDonne2023}%</span>
  </div>
</div>

---

## Andamento per comparto

```js
Plot.plot({
  title: compartoSel === "Tutti" ? "Dipendenti totali per anno" : `Dipendenti — ${compartoSel}`,
  width: 800,
  height: 400,
  y: {grid: true, tickFormat: "~s"},
  color: compartoSel === "Tutti" ? {legend: true} : {scheme: "Blues"},
  marks: [
    Plot.lineY(filtered, {
      x: "anno",
      y: "totale",
      ...(compartoSel === "Tutti" ? {stroke: "comparto"} : {}),
      tip: true
    }),
    Plot.dot(filtered, {
      x: "anno",
      y: "totale",
      ...(compartoSel === "Tutti" ? {stroke: "comparto"} : {}),
    }),
  ]
})
```

---

## Stock 2023 per comparto

```js
const stock2023 = data
  .filter(d => d.anno === 2023)
  .sort((a, b) => b.totale - a.totale);
```

```js
Plot.plot({
  title: "Dipendenti per comparto — 2023",
  width: 800,
  height: 400,
  marginLeft: 140,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Blues"},
  marks: [
    Plot.barX(stock2023, {
      y: "comparto",
      x: "totale",
      fill: "totale",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Tabella per comparto

```js
Inputs.table(filtered, {
  columns: ["anno", "comparto", "donne", "uomini", "totale"],
  header: {comparto: "Comparto", donne: "Donne", uomini: "Uomini", totale: "Totale"},
  format: {donne: x => x.toLocaleString("it-IT"), uomini: x => x.toLocaleString("it-IT"), totale: x => x.toLocaleString("it-IT")},
  rows: 20,
  width: "100%"
})
```

---

## Risorse

- [MEF · RGS · BDAP](https://www.rgs.mef.gov.it/)
- [Analisi](https://github.com/dataciviclab/dataciviclab/tree/main/analisi/dipendenti-pubblici)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/dipendenti-pubblici)

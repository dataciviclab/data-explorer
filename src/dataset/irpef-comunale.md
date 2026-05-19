---
title: IRPEF comunale
description: Lettura pubblica dei dati IRPEF comunali del MEF, 2019-2023
---

# IRPEF comunale

Lettura pubblica dei dati IRPEF comunali del MEF. Contribuenti, reddito imponibile e confronto tra regioni.

**Fonte**: MEF · **Periodo**: 2019–2023

```js
const regioni = await FileAttachment("../data/irpef-regioni.json").json();
const capoluoghi = await FileAttachment("../data/irpef-capoluoghi.json").json();
```

```js
const anni = [...new Set(regioni.map(d => d.anno_di_imposta))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(anni, {label: "Anno", value: anni[0]}));
```

```js
const regFiltered = regioni
  .filter(d => d.anno_di_imposta === annoSel)
  .sort((a, b) => b.reddito_imponibile_eur - a.reddito_imponibile_eur);
```

```js
const capFiltered = capoluoghi
  .filter(d => d.anno === annoSel)
  .sort((a, b) => (b.reddito_imponibile_eur / b.numero_contribuenti) - (a.reddito_imponibile_eur / a.numero_contribuenti));
```

```js
const totContribuenti = regFiltered.reduce((s, d) => s + d.numero_contribuenti, 0);
const totReddito = regFiltered.reduce((s, d) => s + d.reddito_imponibile_eur, 0);
const nRegioni = new Set(regFiltered.map(d => d.regione)).size;
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Contribuenti</h3>
    <span class="big">${totContribuenti.toLocaleString("it-IT")}</span>
  </div>
  <div class="card">
    <h3>Reddito medio</h3>
    <span class="big">€ ${Math.round(totReddito / totContribuenti).toLocaleString("it-IT")}</span>
  </div>
  <div class="card">
    <h3>Regioni</h3>
    <span class="big">${nRegioni}</span>
  </div>
</div>

---

## Reddito imponibile per regione

```js
Plot.plot({
  title: `Reddito imponibile per regione — ${annoSel}`,
  width: 800,
  height: 450,
  marginLeft: 120,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Blues"},
  marks: [
    Plot.barX(regFiltered, {
      y: "regione",
      x: "reddito_imponibile_eur",
      fill: "reddito_imponibile_eur",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Reddito medio per contribuente — capoluoghi

```js
Plot.plot({
  title: `Reddito medio per contribuente — capoluoghi ${annoSel}`,
  width: 800,
  height: 350,
  marginLeft: 100,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Turbo"},
  marks: [
    Plot.barX(capFiltered, {
      y: "comune",
      x: d => Math.round(d.reddito_imponibile_eur / d.numero_contribuenti),
      fill: d => Math.round(d.reddito_imponibile_eur / d.numero_contribuenti),
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Dettaglio capoluoghi

```js
Inputs.table(capFiltered, {
  columns: ["comune", "regione", "numero_contribuenti", "reddito_imponibile_eur", "imposta_netta_eur"],
  header: {
    comune: "Comune",
    regione: "Regione",
    numero_contribuenti: "Contribuenti",
    reddito_imponibile_eur: "Reddito imponibile (€)",
    imposta_netta_eur: "Imposta netta (€)"
  },
  format: {
    reddito_imponibile_eur: x => `€ ${x.toLocaleString("it-IT")}`,
    imposta_netta_eur: x => `€ ${x.toLocaleString("it-IT")}`,
    numero_contribuenti: x => x.toLocaleString("it-IT")
  },
  rows: 20,
  width: "100%"
})
```

---

## Risorse

- [MEF — Finanze](https://www1.finanze.gov.it/)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/irpef-comunale)

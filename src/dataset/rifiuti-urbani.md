---
title: Rifiuti urbani nei comuni
description: Dati ISPRA su rifiuti urbani, raccolta differenziata e volumi per comune e regione
---

# Rifiuti urbani nei comuni

Dati ISPRA sui rifiuti urbani dei comuni italiani. Produzione totale, raccolta differenziata e percentuale per regione.

**Fonte**: ISPRA · **Periodo**: 2020–2024

```js
const regioni = await FileAttachment("../data/ispra-regioni.json").json();
const comuni = await FileAttachment("../data/ispra-comuni.json").json();
```

```js
const anni = [...new Set(regioni.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(anni, {label: "Anno", value: anni[0]}));
```

```js
const regFiltered = regioni
  .filter(d => d.anno === annoSel)
  .sort((a, b) => b.totale_ru_tonnellate - a.totale_ru_tonnellate)
  .map(d => ({
    ...d,
    quota_rd: Math.round(d.totale_rd_tonnellate / d.totale_ru_tonnellate * 100 * 10) / 10
  }));
```

```js
const totRU = regFiltered.reduce((s, d) => s + d.totale_ru_tonnellate, 0);
const totRD = regFiltered.reduce((s, d) => s + d.totale_rd_tonnellate, 0);
const mediaRd = Math.round(totRD / totRU * 1000) / 10;
```

```js
const comuniFiltrati = comuni
  .filter(d => d.anno === annoSel)
  .map(d => ({...d, percentuale_rd: Math.round(d.totale_rd_tonnellate / d.totale_ru_tonnellate * 1000) / 10}))
  .sort((a, b) => b.percentuale_rd - a.percentuale_rd);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Rifiuti totali</h3>
    <span class="big">${Math.round(totRU / 1000000).toLocaleString("it-IT")} <small style="opacity:0.6">t</small></span>
  </div>
  <div class="card">
    <h3>Quota RD</h3>
    <span class="big">${mediaRd}%</span>
  </div>
  <div class="card">
    <h3>Regioni</h3>
    <span class="big">${regFiltered.length}</span>
  </div>
</div>

---

## Raccolta differenziata per regione

```js
Plot.plot({
  title: `Quota raccolta differenziata per regione — ${annoSel}`,
  width: 800,
  height: 450,
  marginLeft: 120,
  y: {label: null, tickSize: 0},
  x: {grid: true, label: "% RD"},
  color: {scheme: "RdYlGn"},
  marks: [
    Plot.barX(regFiltered, {
      y: "regione",
      x: "quota_rd",
      fill: "quota_rd",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0]),
    Plot.ruleX([mediaRd], {stroke: "var(--theme-foreground-muted)", strokeDasharray: "4,4"})
  ]
})
```

---

## Grandi comuni (popolazione ≥ 100.000)

```js
Plot.plot({
  title: `Percentuale RD nei grandi comuni — ${annoSel}`,
  width: 800,
  height: 350,
  marginLeft: 120,
  y: {label: null, tickSize: 0},
  x: {grid: true, label: "% RD"},
  color: {scheme: "RdYlGn"},
  marks: [
    Plot.barX(comuniFiltrati, {
      y: "comune",
      x: "percentuale_rd",
      fill: "percentuale_rd",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Regioni — dettaglio

```js
Inputs.table(regFiltered, {
  columns: ["regione", "totale_ru_tonnellate", "totale_rd_tonnellate", "quota_rd"],
  header: {regione: "Regione", totale_ru_tonnellate: "RU totali (t)", totale_rd_tonnellate: "RD totale (t)", quota_rd: "% RD"},
  format: {totale_ru_tonnellate: x => Math.round(x).toLocaleString("it-IT"), totale_rd_tonnellate: x => Math.round(x).toLocaleString("it-IT"), quota_rd: x => `${x}%`},
  rows: 25, width: "100%"
})
```

---

## Risorse

- [ISPRA — Rifiuti Urbani](https://www.isprambiente.gov.it/it/dati/dati-sui-rifiuti-urbani)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/ispra-ru-base)

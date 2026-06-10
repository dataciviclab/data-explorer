---
title: Dipendenti pubblici per comparto
description: Dati BDAP/RGS sul pubblico impiego per comparto, genere e orario di lavoro, 2010-2023
source: MEF — RGS · BDAP
source_url: https://www.rgs.mef.gov.it/
period: "2010–2023"
last_modified: 2026-05-26
dataset_slug: dipendenti_pubblici
---

# Dipendenti pubblici per comparto

Dati BDAP/RGS sui dipendenti pubblici italiani per comparto nel periodo 2010-2023.

**Fonte**: MEF · RGS · BDAP · **Periodo**: 2010–2023

```js
import { num, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/dipendenti-pubblici.json").json();
```

```js
const comparti = [...new Set(data.map(d => d.comparto))].sort();
const opzioni = ["Tutti i comparti", ...comparti];
const compartoSel = view(Inputs.select(opzioni, {label: "Comparto", value: "Tutti i comparti"}));
```

```js
const filtered = compartoSel === "Tutti i comparti" ? data : data.filter(d => d.comparto === compartoSel);
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
    <span class="big">${num(tot2023)}</span>
  </div>
  <div class="card">
    <h3>Variazione 2010→2023</h3>
    <span class="big">${(delta > 0 ? "+" : "")}${num(delta)}</span>
  </div>
  <div class="card">
    <h3>Donne %</h3>
    <span class="big">${pctDonne2023}%</span>
  </div>
</div>

---

## Andamento

```js
const trendData = compartoSel === "Tutti i comparti"
  ? Array.from(d3.rollup(data, v => d3.sum(v, d => d.totale), d => d.anno), ([anno, totale]) => ({anno, totale})).sort((a,b) => a.anno - b.anno)
  : filtered;
```

```js
Plot.plot({
  title: `Dipendenti ${compartoSel === "Tutti i comparti" ? "totali" : compartoSel}`,
  width: 800,
  height: 400,
  x: {tickFormat: d => String(d)},
  y: {grid: true, tickFormat: "~s"},
  marks: [
    Plot.lineY(trendData, {x: "anno", y: "totale", tip: true}),
    Plot.dot(trendData, {x: "anno", y: "totale", fill: "steelblue"}),
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
const { header, format } = tableFormat({
  anno: { label: "Anno", fmt: "string" },
  comparto: { label: "Comparto", fmt: "string" },
  donne: { label: "Donne", fmt: "num" },
  uomini: { label: "Uomini", fmt: "num" },
  totale: { label: "Totale", fmt: "num" },
});
Inputs.table(filtered, {
  columns: ["anno", "comparto", "donne", "uomini", "totale"],
  header,
  format,
  rows: 20,
  width: "100%"
})
```

---

---

## Limiti

- **Copertura**: i dati coprono il periodo 2010-2023. I dati 2024 non sono ancora disponibili.
- **Genere**: il totale donne/uomini è calcolato sommando tempo pieno e part time (sopra e sotto 50%). Non include eventuali contratti atipici non ricompresi nelle categorie del dataset.
- **Comparti**: la classificazione per comparto può variare nel periodo considerato a seguito di riforme del pubblico impiego.

---

## Risorse

- [MEF · RGS · BDAP (fonte originale)](https://www.rgs.mef.gov.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/dipendenti_pubblici/2023/dipendenti_pubblici_2023_clean.parquet)
- [Analisi](https://github.com/dataciviclab/dataciviclab/tree/main/analisi/dipendenti-pubblici)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/dipendenti-pubblici)

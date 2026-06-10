---
title: Popolazione italiana per età
description: Popolazione residente italiana per fascia d'età e anno — ISTAT, 2019-2025
source: ISTAT — POSAS (Popolazione residente per sesso, età e comune)
source_url: https://esploradati.istat.it/
period: "2019–2025"
last_modified: 2026-06-01
dataset_slug: popolazione_istat_comunale_2019_2025
---

# Popolazione italiana per età

Popolazione residente italiana per fascia d'età, sesso e anno. I dati mostrano la struttura demografica del paese e la sua evoluzione nel tempo.

**Fonte**: [ISTAT](https://esploradati.istat.it/) · **Periodo**: 2019–2025

```js
import { num, pct, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/popolazione-istat.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel).sort((a, b) => {
  const order = {"0-14": 1, "15-29": 2, "30-44": 3, "45-59": 4, "60-74": 5, "75+": 6};
  return (order[a.fascia_eta] || 0) - (order[b.fascia_eta] || 0);
});

const totale = d3.sum(filtered, d => d.popolazione_residente);
const pctFemmine = d3.sum(filtered, d => d.totale_femmine) / totale * 100;
const nFasce = filtered.length;
```

```js
// Trend per fascia
const trend = Array.from(
  d3.rollup(data, v => d3.sum(v, d => d.popolazione_residente), d => d.anno, d => d.fascia_eta),
  ([anno, fasce]) => ({anno, ...Object.fromEntries(fasce)})
).sort((a, b) => a.anno - b.anno);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Popolazione</h3>
    <span class="big">${(totale / 1e6).toFixed(1)} <small style="opacity:0.6">mln</small></span>
  </div>
  <div class="card">
    <h3>Femmine</h3>
    <span class="big">${pct(pctFemmine, 1)}</span>
    <small style="opacity:0.6">maschi ${pct(100 - pctFemmine, 1)}</small>
  </div>
  <div class="card">
    <h3>Fasce d'età</h3>
    <span class="big">${nFasce}</span>
  </div>
</div>

---

## Popolazione per fascia d'età

Come si distribuisce la popolazione italiana tra le fasce d'età? Il grafico mostra la composizione per classe di età, divisa tra maschi e femmine.

```js
// Gender split per fascia
const fasciaGenere = data
  .filter(d => d.anno === annoSel)
  .sort((a, b) => {
    const order = {"0-14": 1, "15-29": 2, "30-44": 3, "45-59": 4, "60-74": 5, "75+": 6};
    return (order[a.fascia_eta] || 0) - (order[b.fascia_eta] || 0);
  });
```

```js
Plot.plot({
  title: `Popolazione per fascia d'età — ${String(annoSel)}`,
  width: 800,
  height: 350,
  marginLeft: 80,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {legend: true},
  marks: [
    Plot.barX(fasciaGenere, {
      y: "fascia_eta",
      x: "totale_maschi",
      fill: "#4e79a7",
      tip: {title: "Maschi"}
    }),
    Plot.barX(fasciaGenere, {
      y: "fascia_eta",
      x: d => -d.totale_femmine,
      fill: "#e15759",
      tip: {title: "Femmine"}
    }),
    Plot.text(fasciaGenere, {
      y: "fascia_eta",
      x: "totale_maschi",
      text: d => Math.round(d.totale_maschi / 1000000 * 10) / 10 + "M",
      dx: 4,
      textAnchor: "start",
      fill: "var(--theme-foreground-muted)",
      fontSize: 10
    }),
    Plot.ruleX([0])
  ]
})
```

Il grafico a specchio mostra la distribuzione maschi (destra, blu) e femmine (sinistra, rossa) per fascia d'età. Le fasce più giovani tendono ad avere più maschi, quelle più anziane più femmine (maggiore speranza di vita femminile).

---

## Evoluzione per fascia d'età

Come cambia la popolazione nelle diverse fasce d'età? I giovani (0-14 e 15-29) sono in calo, gli over 60 in crescita.

```js
const trendOrder = ["0-14", "15-29", "30-44", "45-59", "60-74", "75+"];
const trendLong = trend.flatMap(d =>
  trendOrder.map(f => ({anno: d.anno, fascia: f, pop: d[f] || 0}))
);
```

```js
Plot.plot({
  title: "Andamento per fascia d'età — 2019-2025",
  width: 800,
  height: 400,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, tickFormat: "~s", label: "Popolazione"},
  color: {legend: true},
  marks: [
    Plot.line(trendLong, {
      x: "anno",
      y: "pop",
      z: "fascia",
      stroke: "fascia",
      tip: true
    }),
    Plot.dot(trendLong, {
      x: "anno",
      y: "pop",
      z: "fascia",
      fill: "fascia",
      r: 2
    })
  ]
})
```

---

## Dettaglio per fascia

```js
const { header, format } = tableFormat({
  fascia_eta: { label: "Fascia d'età", fmt: "string" },
  popolazione_residente: { label: "Totale", fmt: "num" },
  totale_maschi: { label: "Maschi", fmt: "num" },
  totale_femmine: { label: "Femmine", fmt: "num" },
});
Inputs.table(filtered, {
  columns: ["fascia_eta", "popolazione_residente", "totale_maschi", "totale_femmine"],
  header,
  format,
  rows: 10,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie copre il periodo 2019-2025. Dati precedenti non sono disponibili in questo dataset.
- **Fasce d'età**: la classificazione per fascia d'età segue la definizione ISTAT. I dati per singola età (0-100) sono disponibili nel dataset originale.
- **Stato civile**: il dataset include anche la disaggregazione per stato civile (celibi, coniugati, ecc.) non mostrata in questa pagina.
- **Popolazione residente**: i dati si riferiscono alla popolazione residente in Italia al 1° gennaio di ogni anno. Non include italiani all'estero (AIRE) né stranieri non residenti.
- **Dettaglio territoriale**: i dati sono aggregati a livello nazionale. La disaggregazione comunale e regionale è disponibile nel dataset originale.

---

## Risorse

- [ISTAT — Esplora dati](https://esploradati.istat.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/popolazione_istat_comunale_2019_2025/2025/popolazione_istat_comunale_2019_2025_2025_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/popolazione-istat-comunale-2019-2025)

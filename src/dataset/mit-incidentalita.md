---
title: Incidenti stradali
description: Incidenti stradali, morti e feriti in Italia — serie mensile MIT, 2001-2018
source: MIT — Ministero delle Infrastrutture e dei Trasporti
source_url: https://www.mit.gov.it/
period: "2001–2018"
last_modified: 2026-06-02
dataset_slug: mit_incidentalita_mensile
---

# Incidenti stradali

Serie mensile di incidenti stradali, morti e feriti in Italia. I dati mostrano l'evoluzione della sicurezza stradale dal 2001 al 2018 e gli effetti delle campagne di prevenzione.

**Fonte**: [MIT](https://www.mit.gov.it/) · **Periodo**: 2001–2018 · Dati mensili

```js
import { num, numFix } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/mit-incidentalita.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel);
const totIncidenti = d3.sum(filtered, d => d.incidenti);
const totMorti = d3.sum(filtered, d => d.morti);
const totFeriti = d3.sum(filtered, d => d.feriti);
```

```js
// Trend annuale
const annuale = Array.from(
  d3.rollup(data, v => ({
    incidenti: d3.sum(v, d => d.incidenti),
    morti: d3.sum(v, d => d.morti),
    feriti: d3.sum(v, d => d.feriti),
  }), d => d.anno),
  ([anno, v]) => ({anno, ...v})
).sort((a, b) => a.anno - b.anno);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Incidenti</h3>
    <span class="big">${num(totIncidenti)}</span>
    <small style="opacity:0.6">${String(annoSel)}</small>
  </div>
  <div class="card">
    <h3>Morti</h3>
    <span class="big">${num(totMorti)}</span>
  </div>
  <div class="card">
    <h3>Feriti</h3>
    <span class="big">${num(totFeriti)}</span>
  </div>
</div>

---

## Trend 2001-2018

Incidenti, morti e feriti sono in costante calo dal 2001. Il miglioramento della sicurezza stradale è visibile su tutti e tre gli indicatori, con una riduzione particolarmente marcata dei morti (-60%).

```js
Plot.plot({
  title: "Incidenti stradali in Italia — trend annuale 2001-2018",
  width: 800,
  height: 400,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, tickFormat: "~s"},
  marks: [
    Plot.lineY(annuale, {x: "anno", y: "incidenti", tip: true, stroke: "#4e79a7"}),
    Plot.dot(annuale, {x: "anno", y: "incidenti", fill: "#4e79a7", r: 2}),
    Plot.areaY(annuale, {x: "anno", y: "incidenti", fill: "#4e79a7", fillOpacity: 0.05})
  ]
})
```

---

## Calo percentuale dal 2001

Per confrontare la riduzione di morti e feriti — che hanno scale molto diverse — il grafico mostra la variazione percentuale rispetto al 2001 (base 100). Entrambi gli indicatori sono in forte calo, ma i morti sono diminuiti molto più rapidamente dei feriti (-58% contro -36% al 2018).

```js
const base2001 = annuale.find(d => d.anno === 2001);
const indicizzato = annuale.map(d => ({
  anno: d.anno,
  incidenti: Math.round(d.incidenti / base2001.incidenti * 100),
  morti: Math.round(d.morti / base2001.morti * 100),
  feriti: Math.round(d.feriti / base2001.feriti * 100)
}));

const trendLines = indicizzato.flatMap(d => [
  {anno: d.anno, tipo: "Incidenti", valore: d.incidenti},
  {anno: d.anno, tipo: "Morti", valore: d.morti},
  {anno: d.anno, tipo: "Feriti", valore: d.feriti}
]);
```

```js
Plot.plot({
  title: "Incidenti, morti e feriti — base 2001 = 100",
  width: 800,
  height: 350,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, label: "% rispetto al 2001"},
  color: {legend: true, scheme: "Set1"},
  marks: [
    Plot.line(trendLines, {x: "anno", y: "valore", z: "tipo", stroke: "tipo", tip: true}),
    Plot.dot(trendLines, {x: "anno", y: "valore", z: "tipo", fill: "tipo", r: 1.5}),
    Plot.ruleY([100], {stroke: "var(--theme-foreground-muted)", strokeDasharray: "4,4"})
  ]
})
```

---

## Dettaglio mensile

```js
Inputs.table(filtered, {
  columns: ["mese", "incidenti", "morti", "feriti", "indice_mortalita", "indice_gravita"],
  header: {mese: "Mese", incidenti: "Incidenti", morti: "Morti", feriti: "Feriti", indice_mortalita: "Mort.%", indice_gravita: "Grav.%"},
  format: {
    incidenti: x => num(x),
    morti: x => num(x),
    feriti: x => num(x),
    indice_mortalita: x => numFix(x, 2) + "%",
    indice_gravita: x => numFix(x, 2) + "%"
  },
  rows: 15,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie copre il periodo 2001-2018. Dati successivi al 2018 non sono disponibili in questo dataset (la fonte MIT ha cambiato metodologia).
- **Nazionale**: i dati sono aggregati a livello nazionale. Non è disponibile la disaggregazione regionale o provinciale.
- **Indicatori**: l'indice di mortalità (morti/incidenti × 100) e l'indice di gravità sono calcolati dal MIT sulla base dei dati mensili.
- **Metodologia**: la rilevazione degli incidenti stradali ha subito cambiamenti metodologici nel periodo considerato. I dati pre e post 2010 potrebbero non essere perfettamente confrontabili.

---

## Risorse

- [MIT — Open Data](https://www.mit.gov.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/mit_incidentalita_mensile/2001/mit_incidentalita_mensile_2001_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/mit-incidentalita-mensile-2001-2018)

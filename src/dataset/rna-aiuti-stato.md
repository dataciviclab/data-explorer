---
title: "Aiuti di Stato — Registro Nazionale Aiuti (RNA)"
description: "Oltre 480 miliardi alle imprese italiane in 10 anni: trend, distribuzione regionale, strumenti e beneficiari degli aiuti pubblici (MIMIT)"
source: MIMIT — Registro Nazionale Aiuti di Stato
source_url: https://www.rna.gov.it/
period: "2017–2026"
data_driven: true
dataset_slug: rna_aiuti_stato
---

# Aiuti di Stato: la mappa del denaro pubblico alle imprese italiane

**Tra il ${first} e il ${last} lo Stato italiano ha concesso ${euroCompact(totale)} in aiuti alle imprese. Il biennio ${covidAnni}, da solo, vale il ${pct(covidShare)} del totale: lo shock COVID ha moltiplicato l'erogazione annuale, passando da ${euroCompact(trendFirst.importo)} (${trendFirst.anno}) a ${euroCompact(trendCovid[1]?.importo ?? 0)} (${trendCovid[1]?.anno}).**

```js
import { euroCompact, pct, numFix, tableFormat } from "../import/format-utils.js";
```

```js
const raw = await FileAttachment("../data/rna-aiuti-stato.json").json();
```

```js
const byAnno = Array.from(
  d3.rollup(raw, v => ({
    importo: d3.sum(v, d => d.elemento_aiuto),
  }), d => d.anno),
  ([anno, v]) => ({ anno, ...v })
).sort((a, b) => a.anno - b.anno);

const trendFirst = byAnno[0];
const trendLast = byAnno[byAnno.length - 1];
const first = trendFirst.anno;
const last = trendLast.anno;
const totale = d3.sum(byAnno, d => d.importo);

const trendCovid = byAnno.filter(d => d.anno >= 2020 && d.anno <= 2021);
const covidAnni = `${trendCovid[0]?.anno}–${trendCovid[1]?.anno}`;
const covidImporto = d3.sum(trendCovid, d => d.importo);
const covidShare = totale ? (covidImporto / totale) * 100 : null;

const byRegione = Array.from(
  d3.rollup(raw, v => ({ importo: d3.sum(v, d => d.elemento_aiuto), n: v.length }), d => d.regione_beneficiario),
  ([regione, v]) => ({ regione, ...v })
).sort((a, b) => b.importo - a.importo);

const byStrumento = Array.from(
  d3.rollup(raw, v => ({ importo: d3.sum(v, d => d.elemento_aiuto), n: v.length }), d => d.strumento),
  ([strumento, v]) => ({ strumento, ...v })
).sort((a, b) => b.importo - a.importo);

const byTipoAnno = Array.from(
  d3.rollup(raw, v => ({ importo: d3.sum(v, d => d.elemento_aiuto) }), d => d.anno, d => d.tipo_beneficiario),
  ([anno, m]) => Array.from(m, ([tipo, v]) => ({ anno, tipo, ...v }))
).flat().sort((a, b) => a.anno - b.anno);

const byProcedimento = Array.from(
  d3.rollup(raw, v => ({ importo: d3.sum(v, d => d.elemento_aiuto), n: v.length }), d => d.procedimento),
  ([procedimento, v]) => ({ procedimento, ...v })
).sort((a, b) => b.importo - a.importo);

const byConcedente = Array.from(
  d3.rollup(raw, v => ({ importo: d3.sum(v, d => d.elemento_aiuto), n: v.length }), d => d.soggetto_concedente),
  ([concedente, v]) => ({ concedente, ...v })
).sort((a, b) => b.importo - a.importo);
```

<div class="grid grid-cols-2">
  <div class="card"><h3>Aiuti totali ${first}–${last}</h3><span class="big">${euroCompact(totale)}</span></div>
  <div class="card"><h3>Picco COVID</h3><span class="big">${euroCompact(trendCovid[1]?.importo ?? 0)}</span></div>
</div>

## 1. Trend annuale — l'onda COVID e il rientro

```js
const plot = await import("npm:@observablehq/plot");
display(plot.plot({
  title: `Importo aiuti per anno — ${first}–${last}`,
  width: 800, height: 320,
  x: {tickFormat: String},
  y: {grid: true, tickFormat: d => (d / 1e9).toFixed(0) + " B€"},
  marks: [
    plot.barY(byAnno, {x: "anno", y: "importo", fill: d => d.anno >= 2020 && d.anno <= 2021 ? "#d62728" : "#3182bd", tip: true}),
    plot.ruleY([0])
  ]
}))
```

L'andamento mostra tre fasi: il regime **pre-COVID** (2017-2019, sotto i ${euroCompact(trendFirst.importo)} annui), l'**emergenza** (2020-2021, oltre ${(covidImporto / 1e9).toFixed(0)} miliardi in due anni) e il **rientro graduale** (2022-2026), con volumi ancora 5-10 volte superiori al pre-pandemia.

## 2. Distribuzione regionale — dove vanno i soldi

```js
const topRegioni = byRegione.slice(0, 10);
display(plot.plot({
  title: `Top 10 regioni per importo aiuti — ${first}–${last}`,
  width: 800, height: 340, marginLeft: 100, marginRight: 50,
  x: {grid: true, tickFormat: d => (d / 1e9).toFixed(0) + " B€"},
  y: {label: null, tickSize: 0},
  marks: [
    plot.barX(topRegioni, {x: "importo", y: "regione", fill: "#3182bd", sort: {y: "-x"}, tip: true}),
    plot.text(topRegioni, {x: "importo", y: "regione", text: d => ` ${euroCompact(d.importo)}`, dx: 6, textAnchor: "start", fontSize: 11}),
    plot.ruleX([0])
  ]
}))
```

La **Lombardia** assorbe ${euroCompact(byRegione[0].importo)}, un quinto del totale nazionale. Le prime 5 regioni totalizzano circa il ${pct(d3.sum(byRegione.slice(0, 5), d => d.importo) / totale * 100)} delle erogazioni.

## 3. Strumenti — garanzie, sovvenzioni e agevolazioni

```js
const topStrumenti = byStrumento.slice(0, 5);
display(plot.plot({
  title: "Distribuzione per strumento",
  width: 800, height: 300, marginLeft: 300, marginRight: 50,
  x: {grid: true, tickFormat: d => (d / 1e9).toFixed(0) + " B€"},
  y: {label: null, tickSize: 0},
  marks: [
    plot.barX(topStrumenti, {x: "importo", y: "strumento", fill: "#2ca02c", sort: {y: "-x"}, tip: true}),
    plot.text(topStrumenti, {x: "importo", y: "strumento", text: d => ` ${euroCompact(d.importo)} (${pct(d.importo / totale * 100)})`, dx: 6, textAnchor: "start", fontSize: 11}),
    plot.ruleX([0])
  ]
}))
```

## 4. PMI vs Grande Impresa — come cambia nel tempo

```js
const tipoDomains = [...new Set(byTipoAnno.map(d => d.tipo))].filter(t => t !== "-");
display(plot.plot({
  title: "Importo per tipo di beneficiario",
  width: 800, height: 320,
  x: {tickFormat: String},
  y: {grid: true, tickFormat: d => (d / 1e9).toFixed(0) + " B€"},
  color: {domain: tipoDomains, range: ["#2c7fb8", "#d62728", "#999"]},
  marks: [
    plot.barY(byTipoAnno.filter(d => tipoDomains.includes(d.tipo)), {
      x: "anno", y: "importo", fill: "tipo", stack: "normalize", tip: true
    }),
  ]
}))
```

## 5. Procedimenti — Notifica, Esenzione, De Minimis

```js
const topProc = byProcedimento.slice(0, 5);
display(plot.plot({
  title: "Distribuzione per procedimento",
  width: 800, height: 260, marginLeft: 130, marginRight: 50,
  x: {grid: true, tickFormat: d => (d / 1e9).toFixed(0) + " B€"},
  y: {label: null, tickSize: 0},
  marks: [
    plot.barX(topProc, {x: "importo", y: "procedimento", fill: "#e67e22", sort: {y: "-x"}, tip: true}),
    plot.text(topProc, {x: "importo", y: "procedimento", text: d => ` ${euroCompact(d.importo)} (${pct(d.importo / totale * 100)})`, dx: 6, textAnchor: "start", fontSize: 11}),
    plot.ruleX([0])
  ]
}))
```

## 6. Top concedenti — chi eroga

```js
const topConc = byConcedente.slice(0, 10);
display(plot.plot({
  title: "Top 10 soggetti concedenti",
  width: 800, height: 340, marginLeft: 200, marginRight: 50,
  x: {grid: true, tickFormat: d => (d / 1e9).toFixed(0) + " B€"},
  y: {label: null, tickSize: 0},
  marks: [
    plot.barX(topConc, {x: "importo", y: "concedente", fill: "#8e44ad", sort: {y: "-x"}, tip: true}),
    plot.text(topConc, {x: "importo", y: "concedente", text: d => ` ${euroCompact(d.importo)}`, dx: 6, textAnchor: "start", fontSize: 11}),
    plot.ruleX([0])
  ]
}))
```

Solo **${byConcedente[0]?.concedente}** ha erogato ${euroCompact(byConcedente[0]?.importo)}, il ${pct(byConcedente[0]?.importo / totale * 100)} del totale.

---

## Limiti

- **Dati misti**: includono sia aiuti effettivamente erogati che impegni formali.
- **ESL**: gli importi sono in "elemento aiuto" (equivalente sovvenzione lordo), non flussi di cassa.
- **Aggiornamento**: i dati 2026 sono parziali (estratti a giugno 2026).

## Risorse

- [MIMIT — RNA](https://www.rna.gov.it/) — fonte originale
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/rna-aiuti-stato)

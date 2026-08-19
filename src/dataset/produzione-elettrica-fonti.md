---
title: Produzione elettrica per fonte
description: "Produzione netta di energia elettrica per fonte e regione, 2015-2024 — il mix cambia: rinnovabili in salita (Terna)"
source: Terna S.p.A. — dati.terna.it
source_url: https://www.terna.it/
period: "2015–2024"
last_modified: 2026-08-19
dataset_slug: terna_electricity_by_source
data_driven: true
---

# Produzione elettrica per fonte — come cambia il mix

**In ${last - first} anni la quota di elettricità da fonti rinnovabili è passata dal ${pct(rS2015)} al ${pct(rSLast)} (${dRinn >= 0 ? "+" : ""}${numFix(dRinn, 1)} punti). Il termoelettrico è calato in volume (da ${numFix(g(first, "Termoelettrico") / 1000, 0)} a ${numFix(g(last, "Termoelettrico") / 1000, 0)} TWh, ${numFix(termoD, 0)}%), il fotovoltaico è quasi raddoppiato (${numFix(fvD, 0)}%) e la produzione totale è scesa da ${numFix(tot2015 / 1000, 0)} a ${numFix(totLast / 1000, 0)} TWh.**

Produzione netta di energia elettrica in **GWh per fonte e regione** (Terna). Ogni numero è calcolato dal dato a build-time: se si ripubblica il parquet, KPI e grafici si aggiornano da soli.

```js
import { num, pct, numFix, tableFormat } from "../import/format-utils.js";
import { normalizzaReg, loadItalianRegions, buildMapLookup } from "../import/geo-utils.js";
```

```js
const data = await FileAttachment("../data/produzione-elettrica-fonti.json").json();
// 2017 escluso: anomalie nelle rilevazioni Terna (vedi Limiti)
const valid = data.filter(d => d.anno !== 2017);
```

```js
const stackData = Array.from(
  d3.rollup(valid, v => d3.sum(v, d => d.produzione_gwh), d => d.anno, d => d.fonte),
  ([anno, m]) => Array.from(m, ([fonte, gwh]) => ({ anno, fonte, gwh }))
).flat();
const byAnno = Array.from(d3.rollup(valid, v => d3.sum(v, d => d.produzione_gwh), d => d.anno))
  .map(([anno, gwh]) => ({ anno, gwh })).sort((a, b) => a.anno - b.anno);
const first = byAnno[0].anno;
const last = byAnno[byAnno.length - 1].anno;
const tot2015 = byAnno[0].gwh;
const totLast = byAnno[byAnno.length - 1].gwh;
const deltaTot = tot2015 ? ((totLast - tot2015) / tot2015) * 100 : null;
const g = (anno, fonte) => stackData.find(d => d.anno === anno && d.fonte === fonte)?.gwh ?? 0;
const REN = ["Idrico", "Fotovoltaico", "Eolico", "Geotermoelettrico"];
const share = (anno) => { const t = byAnno.find(p => p.anno === anno)?.gwh ?? 0; return t ? (REN.reduce((s, f) => s + g(anno, f), 0) / t) * 100 : null; };
const rS2015 = share(first);
const rSLast = share(last);
const dRinn = (rSLast != null && rS2015 != null) ? rSLast - rS2015 : null;
const pctD = (f) => g(first, f) ? ((g(last, f) - g(first, f)) / g(first, f)) * 100 : null;
const termoD = pctD("Termoelettrico");
const fvD = pctD("Fotovoltaico");
const eolD = pctD("Eolico");

const mixLast = stackData.filter(d => d.anno === last).sort((a, b) => b.gwh - a.gwh);
const perRegione = Array.from(
  d3.rollup(valid.filter(d => d.anno === last), v => d3.sum(v, d => d.produzione_gwh), d => d.regione),
  ([regione, gwh]) => ({ regione, gwh })
).sort((a, b) => b.gwh - a.gwh);
```

<div class="grid grid-cols-4">
  <div class="card"><h3>Produzione totale ${last}</h3><span class="big">${numFix(totLast / 1000, 0)} TWh</span></div>
  <div class="card"><h3>Quota rinnovabili</h3><span class="big">${pct(rSLast)}</span></div>
  <div class="card"><h3>Δ quota rinnovabili</h3><span class="big">${dRinn >= 0 ? "+" : ""}${numFix(dRinn, 1)} pp</span></div>
  <div class="card"><h3>Termoelettrico</h3><span class="big">${termoD >= 0 ? "+" : ""}${numFix(termoD, 0)}%</span></div>
</div>

## 1. Il mix di oggi — produzione per fonte (${last})

La composizione della produzione netta nel ${last} è ancora dominata dal termoelettrico, ma le rinnovabili valgono ormai ${pct(rSLast)} del totale. Questa è la "fotografia" del mix; come è cambiata nel tempo lo mostra il blocco seguente.

```js
const plot = await import("npm:@observablehq/plot");
display(plot.plot({
  title: `Produzione netta per fonte — ${last}`,
  width: 800, height: 320, marginLeft: 180,
  x: {grid: true, tickFormat: (d) => numFix(d / 1000, 0) + " T"}, y: {label: null, tickSize: 0},
  color: {scheme: "Set2"},
  marks: [
    plot.barX(mixLast, {x: "gwh", y: "fonte", fill: "fonte", sort: {y: "-x"}}),
    plot.text(mixLast, {x: "gwh", y: "fonte", text: (d) => ` ${numFix(d.gwh / 1000, 0)} TWh — ${pct((d.gwh / totLast) * 100)}`, dx: 6, textAnchor: "start", fontSize: 10}),
    plot.ruleX([0])
  ]
}))
```

## 2. Come cambia il mix nel tempo (${first}–${last})

Qui vediamo la **composizione a 100% anno per anno**: la quota di ciascuna fonte sul totale (escluso il 2017, anomalo). Il termoelettrico cede progressivamente terreno alle rinnovabili, con l'idrico che oscilla per il clima e il fotovoltaico che sale in modo costante.

```js
display(plot.plot({
  title: `Mix elettrico per anno (100%) — ${first}–${last}`,
  width: 800, height: 360,
  x: {tickFormat: String, label: "Anno"},
  y: {grid: true, percent: true, label: "Quota sul totale"},
  color: {legend: true, scheme: "Set2"},
  marks: [
    plot.barY(stackData, {x: "anno", y: "gwh", fill: "fonte", stack: "normalize", tip: true, sort: null})
  ]
}))
```

> **Nota di lettura**: ogni barra (anno) è altezza totale 100%; i segmenti colorati mostrano il peso relativo di ciascuna fonte. Fuori dal grafico il 2017 (dato Terna anomalo). La quota rinnovabili sale da ${pct(rS2015)} a ${pct(rSLast)}.

## 3. Dove si produce — per regione (${last})

Chiude il quadro la distribuzione territoriale della produzione nell'ultimo anno.

```js
const regTopo = await FileAttachment("../data/regioni.topojson").json();
const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
const regLookup = buildMapLookup(perRegione, regioniGeo, "regione", "gwh");
```

```js
display(plot.plot({
  title: `Produzione elettrica per regione — ${last}`,
  projection: {type: "mercator", domain: regioniGeo},
  width: 800, height: 600,
  color: {scheme: "Oranges", legend: true, label: "Produzione (GWh)", type: "quantile"},
  marks: [
    plot.geo(regioniGeo, {fill: (d) => regLookup.get(normalizzaReg(d.properties.DEN_REG)), stroke: "#888", strokeWidth: 0.25, tip: true}),
    plot.geo(confiniReg, {stroke: "#888", strokeWidth: 0.7})
  ]
}))
```
---

## Dettaglio ${last} per regione e fonte

<small>Produzione netta in GWh, per regione e fonte, anno più recente (${last}).</small>

```js
const lastRows = valid.filter(d => d.anno === last);
const { header, format } = tableFormat({
  regione: { label: "Regione", fmt: "string" },
  fonte: { label: "Fonte", fmt: "string" },
  produzione_gwh: { label: "Produzione (GWh)", fmt: "num" }
});
```

```js
const searchQuery = view(Inputs.search(lastRows, {placeholder: "cerca regione o fonte…", label: "Cerca"}));
```

```js
Inputs.table(searchQuery, {
  columns: ["regione", "fonte", "produzione_gwh"],
  header, format, rows: 20, width: "100%", sort: "produzione_gwh", reverse: true
})
```

---

## Limiti

- **2017 escluso**: i dati 2017 presentano anomalie nelle rilevazioni Terna (probabile cambio metodologico) e sono esclusi da trend e mix per non distorcerli; riconosciuti sia qui sia nell'analisi hub.
- **Copertura**: serie 2015-2024; i dati 2024 sono preliminari e potrebbero essere rivisti.
- **Produzione, non capacità**: i valori sono produzione effettiva (GWh), non capacità installata (MW). Per la capacità vedi [Capacità rinnovabile](/dataset/capacita-rinnovabile).
- **Idrico = clima**: la produzione idroelettrica oscilla sensibilmente con la piovosità; le fluttuazioni nel trend riflettono condizioni meteorologiche, non cambiamenti strutturali.
- **Mappa a quantili**: ogni colore contiene lo stesso numero di regioni; i valori precisi sono nella tabella.

## Risorse

- [Terna (fonte originale)](https://www.terna.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/terna_electricity_by_source/2024/terna_electricity_by_source_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/terna-electricity-by-source)
Dal **${first}** al **${last}** la produzione totale è passata da **${numFix(tot2015 / 1000, 0)} a ${numFix(totLast / 1000, 0)} TWh** (${deltaTot >= 0 ? "+" : ""}${numFix(deltaTot, 1)}%). Al netto dell'oscillazione idrica (clima), la composizione è cambiata in modo strutturale: <strong>il termoelettrico perde 12 punti di quota</strong>, il fotovoltaico (${numFix(fvD, 0)}%) e l'eolico (${numFix(eolD, 0)}%) guadagnano.

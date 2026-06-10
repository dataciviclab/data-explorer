---
title: Produzione elettrica per fonte
description: Produzione di energia elettrica in GWh per fonte, regione e tipo — Terna, 2015-2024
source: Terna S.p.A. — dati.terna.it
source_url: https://www.terna.it/
period: "2015–2024"
last_modified: 2026-06-10
dataset_slug: terna_electricity_by_source
---

# Produzione elettrica per fonte

Produzione netta di energia elettrica in GWh per fonte e regione. La produzione totale oscilla tra i **270 e i 290 TWh annui**, con il mix che cambia sensibilmente: calo del termoelettrico, crescita del fotovoltaico e dell'eolico.

**Fonte**: [Terna](https://www.terna.it/) · **Periodo**: 2015–2024

```js
import { normalizzaReg, loadItalianRegions, buildRegLookup } from "../import/geo-utils.js";
import { num, unit } from "../import/format-utils.js";
```

```js
const regTopo = await FileAttachment("../data/regioni.topojson").json();
const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
```

```js
const data = await FileAttachment("../data/produzione-elettrica-fonti.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel);
```

```js
const perFonte = Array.from(
  d3.rollup(filtered, v => d3.sum(v, d => d.produzione_gwh), d => d.fonte),
  ([fonte, produzione_gwh]) => ({fonte, produzione_gwh})
).sort((a, b) => b.produzione_gwh - a.produzione_gwh);

const perRegione = Array.from(
  d3.rollup(filtered, v => d3.sum(v, d => d.produzione_gwh), d => d.regione),
  ([regione, produzione_gwh]) => ({regione, produzione_gwh})
).sort((a, b) => b.produzione_gwh - a.produzione_gwh);
```

```js
const totaleGWh = d3.sum(perFonte, d => d.produzione_gwh);
const nFonti = perFonte.length;
const nRegioni = perRegione.length;
```

```js
// Trend per fonte 2015-2024
const trendFonti = Array.from(
  d3.rollup(data, v => d3.sum(v, d => d.produzione_gwh), d => d.anno, d => d.fonte),
  ([anno, fonti]) => Array.from(fonti, ([fonte, produzione_gwh]) => ({anno, fonte, produzione_gwh}))
).flat().sort((a, b) => a.anno - b.anno);

// Lookup per mappa
const regLookup = buildRegLookup(perRegione, "regione", "produzione_gwh");
```

```js
// Variazione totale 2015→2024
const annoMin = d3.min(data, d => d.anno);
const annoMax = d3.max(data, d => d.anno);
const tot2015 = d3.sum(data.filter(d => d.anno === annoMin), d => d.produzione_gwh);
const tot2024 = d3.sum(data.filter(d => d.anno === annoMax), d => d.produzione_gwh);
const varPct = Math.round((tot2024 - tot2015) / tot2015 * 1000) / 10;
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Produzione totale</h3>
    <span class="big">${unit(totaleGWh, "GWh")}</span>
  </div>
  <div class="card">
    <h3>Fonti</h3>
    <span class="big">${nFonti}</span>
  </div>
  <div class="card">
    <h3>Variazione ${String(annoMin)}→${String(annoMax)}</h3>
    <span class="big">${varPct > 0 ? "+" : ""}${varPct}%</span>
  </div>
</div>

---

## Evoluzione per fonte 2015-2024

La produzione termoelettrica è in calo strutturale, mentre il fotovoltaico e l'eolico crescono progressivamente. L'idroelettrico fluttua in base alla piovosità annuale. La produzione totale resta stabile intorno ai 280 TWh annui.

```js
Plot.plot({
  title: "Produzione elettrica per fonte — 2015-2024",
  width: 800,
  height: 350,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, tickFormat: "~s", label: "Produzione (GWh)"},
  color: {legend: true, scheme: "Set2"},
  marks: [
    Plot.line(trendFonti, {x: "anno", y: "produzione_gwh", z: "fonte", stroke: "fonte", tip: true}),
    Plot.dot(trendFonti, {x: "anno", y: "produzione_gwh", z: "fonte", fill: "fonte", r: 1.5}),
  ]
})
```

---

## Mix per fonte — ${String(annoSel)}

La distribuzione della produzione tra le fonti mostra il peso ancora dominante del termoelettrico, seguito da idroelettrico, fotovoltaico ed eolico.

```js
const totMix = d3.sum(perFonte, d => d.produzione_gwh);
const fonteConPct = perFonte.map(d => ({...d, pct: d.produzione_gwh / totMix * 100}));
```

```js
Plot.plot({
  title: `Produzione netta per fonte — ${String(annoSel)}`,
  width: 800,
  height: 300,
  marginLeft: 160,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(fonteConPct, {
      y: "fonte",
      x: "produzione_gwh",
      fill: "fonte",
      sort: {y: "-x"},
      tip: {format: {x: d => `${(d / 1000).toFixed(0)} TWh`}}
    }),
    Plot.text(fonteConPct, {
      y: "fonte",
      x: "produzione_gwh",
      text: d => `${d.pct.toFixed(1)}%`,
      dx: 6,
      textAnchor: "start",
      fill: "var(--theme-foreground-muted)",
      fontSize: 12
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Distribuzione regionale — ${String(annoSel)}

```js
Plot.plot({
  title: `Produzione elettrica per regione — ${String(annoSel)}`,
  projection: {type: "mercator", domain: regioniGeo},
  width: 800,
  height: 600,
  color: {scheme: "Oranges", legend: true, label: "Produzione (GWh)", type: "quantile"},
  marks: [
    Plot.geo(regioniGeo, {
      fill: d => regLookup.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#888",
      strokeWidth: 0.25,
      tip: {format: {fill: d => unit(d, "GWh")}}
    }),
    Plot.geo(confiniReg, {
      stroke: "#888",
      strokeWidth: 0.7
    })
  ]
})
```

---

## Dettaglio per regione e fonte

```js
Inputs.table(filtered, {
  columns: ["regione", "fonte", "produzione_gwh"],
  header: {regione: "Regione", fonte: "Fonte", produzione_gwh: "Produzione (GWh)"},
  format: {produzione_gwh: x => unit(x, "GWh")},
  rows: 30,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie copre il periodo 2015-2024. I dati 2024 sono preliminari e potrebbero essere rivisti da Terna.
- **Produzione**: i dati si riferiscono alla produzione effettiva di energia elettrica (GWh), non alla capacità installata (MW). Per la capacità installata, vedi il dataset [Capacità rinnovabile](/dataset/capacita-rinnovabile).
- **Idroelettrico**: la produzione idroelettrica varia sensibilmente in base alla piovosità annuale; le fluttuazioni nel grafico di trend riflettono condizioni meteorologiche, non cambiamenti strutturali.
- **Mappa**: scala quantile — ogni colore contiene lo stesso numero di regioni. I valori precisi sono nella tabella.

---

## Risorse

- [Terna (fonte originale)](https://www.terna.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/terna_electricity_by_source/2024/terna_electricity_by_source_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/terna-electricity-by-source)

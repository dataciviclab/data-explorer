---
title: Spesa sanitaria regionale LEA
description: Dati BDAP sui costi dei Livelli Essenziali di Assistenza per regione, macro-area e voce contabile, 2019-2024
source: BDAP — Banca Dati delle Amministrazioni Pubbliche (RGS MEF)
source_url: https://bdap-opendata.rgs.mef.gov.it/
period: "2019–2024"
last_modified: 2026-06-10
dataset_slug: bdap_lea
---

# Spesa sanitaria regionale LEA

I costi sostenuti dalle regioni italiane per garantire i Livelli Essenziali di Assistenza (LEA), disaggregati per regione, macro-area (prevenzione, distrettuale, ospedaliera, ricerca) e voce contabile.

**Fonte**: [BDAP](https://bdap-opendata.rgs.mef.gov.it/) · **Periodo**: 2019–2024

```js
import { normalizzaReg, loadItalianRegions, buildMapLookup } from "../import/geo-utils.js";
import { num, euroCompact, tableFormat } from "../import/format-utils.js";
```

```js
const regTopo = await FileAttachment("../data/regioni.topojson").json();
const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
```

```js
const regioni = await FileAttachment("../data/bdap-lea-regioni.json").json();
const macro = await FileAttachment("../data/bdap-lea-macro.json").json();
```

```js
const anni = [...new Set(regioni.map(d => d.anno_riferimento))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const regFiltered = regioni.filter(d => d.anno_riferimento === annoSel);
const macroFiltered = macro.filter(d => d.anno === annoSel);

const totSpesa = d3.sum(regFiltered, d => d.importo_totale);
const nRegioni = regFiltered.length;

// Per la mappa
const regLookup = buildMapLookup(regFiltered, regioniGeo, "descrizione_regione", "importo_totale");

// Trend spesa totale 2019-2024
const trend = Array.from(
  d3.rollup(regioni, v => d3.sum(v, d => d.importo_totale), d => d.anno_riferimento),
  ([anno, spesa]) => ({anno, spesa})
).sort((a, b) => a.anno - b.anno);

// Delta
const annoMin = d3.min(regioni, d => d.anno_riferimento);
const spesaMin = trend.find(d => d.anno === annoMin)?.spesa || 0;
const spesaMax = trend.find(d => d.anno === annoSel)?.spesa || 0;
const deltaPct = spesaMin ? Math.round((spesaMax - spesaMin) / spesaMin * 1000) / 10 : 0;
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Spesa totale LEA</h3>
    <span class="big">${euroCompact(totSpesa)}</span>
    <small style="opacity:0.6">${String(annoSel)}</small>
  </div>
  <div class="card">
    <h3>Media per regione</h3>
    <span class="big">${euroCompact(totSpesa / nRegioni)}</span>
  </div>
  <div class="card">
    <h3>Variazione dal ${String(annoMin)}</h3>
    <span class="big">${deltaPct > 0 ? "+" : ""}${deltaPct}%</span>
  </div>
</div>

---

## Evoluzione della spesa 2019-2024

La spesa sanitaria LEA è in crescita costante, passando da ${euroCompact(spesaMin)} a ${euroCompact(spesaMax)} nel ${String(annoSel)} (+${deltaPct}%). L'incremento riflette sia l'inflazione sanitaria sia l'ampliamento progressivo dei LEA.

```js
Plot.plot({
  title: "Spesa LEA totale — 2019-2024",
  width: 800,
  height: 300,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, tickFormat: "~s", label: "Spesa (€)"},
  marks: [
    Plot.lineY(trend, {x: "anno", y: "spesa", tip: {format: {y: d => euroCompact(d)}}}),
    Plot.dot(trend, {x: "anno", y: "spesa", fill: "steelblue", r: 4}),
    Plot.areaY(trend, {x: "anno", y: "spesa", fill: "steelblue", fillOpacity: 0.05}),
    Plot.ruleY([0])
  ]
})
```

---

## Composizione per macro-area — ${String(annoSel)}

L'assistenza distrettuale e ospedaliera assorbono oltre l'85% della spesa. La prevenzione e la ricerca pesano per meno del 5%.

```js
const totMacro = d3.sum(macroFiltered, d => d.importo_totale);
const macroAggr = Array.from(
  d3.rollup(macroFiltered, v => d3.sum(v, d => d.importo_totale), d => d.descrizione_voce_contabile),
  ([area, importo]) => ({area, importo, pct: importo / totMacro * 100})
).sort((a, b) => b.importo - a.importo);
```

```js
Plot.plot({
  title: `Composizione spesa LEA per macro-area — ${String(annoSel)}`,
  width: 800,
  height: 300,
  marginLeft: 200,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(macroAggr, {
      y: "area",
      x: "importo",
      fill: "area",
      sort: {y: "-x"},
      tip: {format: {x: d => euroCompact(d)}}
    }),
    Plot.text(macroAggr, {
      y: "area",
      x: "importo",
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

> **Nota**: la spesa include le transazioni inter-ente per mobilità sanitaria (prestazioni acquistate da altri enti SSN), contate sia dall'ente pagante sia dall'ente erogante. Il costo operativo diretto è inferiore di circa il valore delle prestazioni sanitarie.

---

## Distribuzione regionale — ${String(annoSel)}

Le regioni più popolose guidano la spesa assoluta, ma il dato pro capite — non ancora presente in questo dataset — darebbe un quadro più preciso dell'efficienza.

```js
Plot.plot({
  title: `Spesa LEA per regione — ${String(annoSel)}`,
  projection: {type: "mercator", domain: regioniGeo},
  width: 800,
  height: 600,
  color: {scheme: "Blues", legend: true, label: "Spesa (€)", type: "quantile"},
  marks: [
    Plot.geo(regioniGeo, {
      fill: d => regLookup.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#888",
      strokeWidth: 0.25,
      tip: {format: {fill: d => euroCompact(d)}}
    }),
    Plot.geo(confiniReg, {
      stroke: "#888",
      strokeWidth: 0.7
    })
  ]
})
```

---

## Dettaglio regioni

```js
const { header, format } = tableFormat({
  descrizione_regione: { label: "Regione", fmt: "string" },
  importo_totale: { label: "Spesa totale", fmt: "euroCompact" },
  prestazioni_sanitarie: { label: "Prestazioni", fmt: "euroCompact" },
  personale_sanitario: { label: "Personale", fmt: "euroCompact" },
  consumi_sanitari: { label: "Consumi", fmt: "euroCompact" },
  servizi_sanitari: { label: "Servizi", fmt: "euroCompact" },
  ammortamenti: { label: "Ammortam.", fmt: "euroCompact" },
});
```

```js
Inputs.table(regFiltered, {
  columns: ["descrizione_regione", "importo_totale", "prestazioni_sanitarie", "personale_sanitario", "consumi_sanitari", "servizi_sanitari", "ammortamenti"],
  header,
  format,
  sort: "importo_totale",
  rows: 25,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie copre il periodo 2019-2024. I dati 2024 sono preliminari.
- **Doppia contabilizzazione**: la spesa totale include le prestazioni sanitarie tra enti SSN (mobilità sanitaria), contate sia dall'ente pagante sia dall'ente erogante.
- **Enti esclusi**: le voci aggregate (codice ente '000' e '999') sono escluse per evitare duplicazioni contabili.
- **Pro capite**: il dato di spesa pro capite non è ancora disponibile in questo dataset (richiederebbe un join con la popolazione ISTAT).

---

## Risorse

- [BDAP — Open Data (fonte originale)](https://bdap-opendata.rgs.mef.gov.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/bdap_lea/2024/bdap_lea_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/bdap-lea)

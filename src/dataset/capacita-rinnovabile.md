---
title: Capacità rinnovabile per regione
description: Dati Terna sulla capacità di generazione rinnovabile installata per regione e fonte (potenza netta), 2015-2024
source: Terna S.p.A.
source_url: https://www.terna.it/
period: "2015–2024"
last_modified: 2026-06-10
dataset_slug: terna_capacita_rinnovabile
data_driven: true
---

# Capacità rinnovabile per regione

**In ${annoMax - annoMin} anni la potenza rinnovabile italiana è cresciuta del ${numFix(crescitaPct)}%, passando da ${unit(tot2015, "MW")} a ${unit(tot2024, "MW")}. Il fotovoltaico traina la crescita, ma la distribuzione geografica è tutt'altro che uniforme: le regioni del Sud e delle Isole concentrano una quota crescente della capacità installata.**

Dati Terna sulla capacità di generazione rinnovabile installata per regione e fonte (potenza netta). Ogni numero di questa pagina è calcolato dal dato a build-time: se si ripubblica il parquet, KPI e grafici si aggiornano da soli.

**Fonte**: [Terna](https://www.terna.it/) · **Periodo**: 2015–2024

```js
import { normalizzaReg, loadItalianRegions, buildMapLookup } from "../import/geo-utils.js";
import { num, numFix, unit, tableFormat } from "../import/format-utils.js";
```

```js
const regTopo = await FileAttachment("../data/regioni.topojson").json();
const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
```

```js
const data = await FileAttachment("../data/terna-fonti.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel);
```

```js
const totNazionale = d3.sum(filtered, d => d.potenza_mw);
const fontiNazionali = Array.from(
  d3.rollup(filtered, v => d3.sum(v, d => d.potenza_mw), d => d.fonti),
  ([fonti, potenza_mw]) => ({fonti, potenza_mw})
).sort((a, b) => b.potenza_mw - a.potenza_mw);
const nRegioni = new Set(filtered.map(d => d.regione)).size;
```

```js
// Trend per fonte 2015-2024
const trendFonti = Array.from(
  d3.rollup(data, v => d3.sum(v, d => d.potenza_mw), d => d.anno, d => d.fonti),
  ([anno, fonti]) => Array.from(fonti, ([fonti, potenza_mw]) => ({anno, fonti, potenza_mw}))
).flat().sort((a, b) => a.anno - b.anno);

// Capacità per regione (per la mappa)
const perRegione = Array.from(
  d3.rollup(filtered, v => d3.sum(v, d => d.potenza_mw), d => d.regione),
  ([regione, potenza_mw]) => ({regione, potenza_mw})
).sort((a, b) => b.potenza_mw - a.potenza_mw);
const regLookup = buildMapLookup(perRegione, regioniGeo, "regione", "potenza_mw");
```

```js
// Crescita totale 2015→2024
const annoMin = d3.min(data, d => d.anno);
const annoMax = d3.max(data, d => d.anno);
const tot2015 = d3.sum(data.filter(d => d.anno === annoMin), d => d.potenza_mw);
const tot2024 = d3.sum(data.filter(d => d.anno === annoMax), d => d.potenza_mw);
const crescitaPct = Math.round((tot2024 - tot2015) / tot2015 * 1000) / 10;
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Potenza totale</h3>
    <span class="big">${unit(totNazionale, "MW")}</span>
  </div>
  <div class="card">
    <h3>Fonti</h3>
    <span class="big">${fontiNazionali.length}</span>
  </div>
  <div class="card">
    <h3>Crescita ${String(annoMin)}→${String(annoMax)}</h3>
    <span class="big">+${crescitaPct}%</span>
  </div>
</div>

---

## 1. Distribuzione regionale — ${String(annoSel)}

La mappa mostra come si distribuisce la potenza rinnovabile installata tra le regioni italiane. Ogni colore rappresenta una fascia di potenza (scala quantile): le regioni con più capacità sono quelle del Sud e delle Isole, dove fotovoltaico ed eolico hanno trovato le condizioni più favorevoli.

```js
Plot.plot({
  title: `Potenza rinnovabile per regione — ${String(annoSel)}`,
  projection: {type: "mercator", domain: regioniGeo},
  width: 800,
  height: 600,
  color: {scheme: "Greens", legend: true, label: "Potenza (MW)", type: "quantile"},
  marks: [
    Plot.geo(regioniGeo, {
      fill: d => regLookup.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#888",
      strokeWidth: 0.25,
      tip: {format: {fill: d => unit(d, "MW")}}
    }),
    Plot.geo(confiniReg, {
      stroke: "#888",
      strokeWidth: 0.7
    })
  ]
})
```

> **Nota di lettura**: la scala quantile divide le regioni in gruppi di pari dimensione. I valori precisi sono nella tabella in fondo alla pagina.

---

## 2. Evoluzione per fonte ${String(annoMin)}–${String(annoMax)}

La capacità rinnovabile italiana è cresciuta da ${unit(tot2015, "MW")} a ${unit(tot2024, "MW")} (+${crescitaPct}%). Il fotovoltaico è la tecnologia che è cresciuta di più in termini assoluti, seguito dall'eolico. L'idroelettrico e le bioenergie restano sostanzialmente stabili.

```js
Plot.plot({
  title: "Capacità rinnovabile per fonte — 2015-2024",
  width: 800,
  height: 350,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, tickFormat: "~s", label: "Potenza (MW)"},
  color: {legend: true, scheme: "Set2"},
  marks: [
    Plot.line(trendFonti, {x: "anno", y: "potenza_mw", z: "fonti", stroke: "fonti", tip: true}),
    Plot.dot(trendFonti, {x: "anno", y: "potenza_mw", z: "fonti", fill: "fonti", r: 1.5}),
  ]
})
```

---

## 3. Mix per fonte — ${String(annoSel)}

```js
const totMix = d3.sum(fontiNazionali, d => d.potenza_mw);
const fontiConPct = fontiNazionali.map(d => ({...d, pct: d.potenza_mw / totMix * 100}));
```

```js
Plot.plot({
  title: `Mix capacità rinnovabile — ${String(annoSel)}`,
  width: 800,
  height: 300,
  marginLeft: 140,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(fontiConPct, {
      y: "fonti",
      x: "potenza_mw",
      fill: "fonti",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.text(fontiConPct, {
      y: "fonti",
      x: "potenza_mw",
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

## Dettaglio per regione e fonte

```js
const { header, format } = tableFormat({
  regione: { label: "Regione", fmt: "string" },
  fonti: { label: "Fonte", fmt: "string" },
  potenza_mw: { label: "Potenza (MW)", fmt: "num" },
});
```

```js
Inputs.table(filtered, {
  columns: ["regione", "fonti", "potenza_mw"],
  header,
  format,
  rows: 30,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie copre il periodo 2015-2024. I dati 2024 sono preliminari e potrebbero essere rivisti da Terna.
- **Tipo capacità**: i dati si riferiscono alla potenza netta installata (tipo_capacita = 'Netta'). Non include capacità lorda o eventuale capacità autorizzata ma non ancora installata.
- **Map**: la mappa usa una scala quantile — ogni colore contiene lo stesso numero di regioni. I valori precisi sono nella tabella sottostante.

---

## Risorse

- [Terna (fonte originale)](https://www.terna.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/terna_capacita_rinnovabile/2024/terna_capacita_rinnovabile_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/terna-capacita-rinnovabile)

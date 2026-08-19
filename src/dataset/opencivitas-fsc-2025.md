---
title: Fondo di Solidarietà Comunale
description: FSC 2022-2025 — capacità fiscale, fondo perequativo e dotazione finale per comune — OpenCivitas
source: OpenCivitas / Sogei
source_url: https://www.opencivitas.it/
period: "2022–2025"
last_modified: 2026-05-28
dataset_slug: opencivitas_fsc_2025_rso
data_driven: true
---

# Fondo di Solidarietà Comunale

```js
import { normalizzaReg, loadItalianRegions, buildMapLookup } from "../import/geo-utils.js";
import { num, numFix, pct, unit, euroCompact, tableFormat } from "../import/format-utils.js";
```

```js
const regTopo = await FileAttachment("../data/regioni.topojson").json();
const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
```

```js
const data = await FileAttachment("../data/opencivitas-fsc-2025.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel);
const totaleFsc = d3.sum(filtered, d => d.dotazione_finale_fsc);
const totalePerequativo = d3.sum(filtered, d => d.fondo_perequativo);
const totalePopolazione = d3.sum(filtered, d => d.popolazione);
const nComuni = filtered.length;
```

```js
const perRegione = Array.from(
  d3.rollup(filtered, v => ({
    fsc: d3.sum(v, d => d.dotazione_finale_fsc),
    perequativo: d3.sum(v, d => d.fondo_perequativo),
    capacita: d3.sum(v, d => d.capacita_fiscale),
    comuni: v.length,
    popolazione: d3.sum(v, d => d.popolazione)
  }), d => d.regione),
  ([regione, v]) => ({regione, ...v})
).sort((a, b) => b.fsc - a.fsc);
```

```js
// Contribuenti netti (fondo_perequativo negativo) vs beneficiari
const contribNetti = filtered.filter(d => d.fondo_perequativo < 0).length;
const percContribNetti = contribNetti / nComuni * 100;
```

```js
// Trend FSC totale per anno
const trendFsc = Array.from(
  d3.rollup(data, v => ({
    fsc: d3.sum(v, d => d.dotazione_finale_fsc),
    perequativo: d3.sum(v, d => d.fondo_perequativo),
    comuni: v.length
  }), d => d.anno),
  ([anno, v]) => ({anno, ...v})
).sort((a, b) => a.anno - b.anno);
```

**Nel ${String(annoSel)} il Fondo di Solidarietà Comunale distribuisce ${euroCompact(totaleFsc)} tra ${num(nComuni)} comuni delle RSO. Il ${pct(percContribNetti)} dei comuni è contribuente netto: la capacità fiscale del fondo perequativo supera il fabbisogno standard.**

Fondo di Solidarietà Comunale (FSC) per comune: capacità fiscale, fondo perequativo, dotazione finale e risorse storiche. I dati mostrano come si distribuiscono le risorse tra i comuni italiani e quali territori contribuiscono o ricevono dalla perequazione. Ogni numero di questa pagina è calcolato dal dato a build-time.

**Fonte**: [OpenCivitas](https://www.opencivitas.it/) · **Periodo**: 2022–2025

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Dotazione FSC</h3>
    <span class="big">${euroCompact(totaleFsc)}</span>
  </div>
  <div class="card">
    <h3>Comuni</h3>
    <span class="big">${num(nComuni)}</span>
  </div>
  <div class="card">
    <h3>Contribuenti netti</h3>
    <span class="big">${pct(percContribNetti)}</span>
    <small style="opacity:0.6">${num(contribNetti)} comuni</small>
  </div>
</div>

---

## 1. Dotazione FSC per regione — ${String(annoSel)}

La mappa mostra la distribuzione territoriale della dotazione FSC. Solo le Regioni a Statuto Ordinario (RSO) sono incluse; le regioni in grigio non sono nel dataset.

```js
const fscLookup = buildMapLookup(perRegione, regioniGeo, "regione", "fsc");
```

```js
Plot.plot({
  title: `Dotazione FSC per regione — ${String(annoSel)}`,
  projection: {type: "mercator", domain: regioniGeo},
  width: 800,
  height: 600,
  color: {scheme: "Blues", legend: true, label: "Dotazione FSC (€)", type: "quantile"},
  marks: [
    Plot.geo(regioniGeo, {
      filter: d => fscLookup.has(normalizzaReg(d.properties.DEN_REG)),
      fill: d => fscLookup.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#888",
      strokeWidth: 0.25,
      tip: true
    }),
    Plot.geo(regioniGeo, {
      filter: d => !fscLookup.has(normalizzaReg(d.properties.DEN_REG)),
      fill: "#e0e0e0",
      stroke: "#888",
      strokeWidth: 0.25,
      tip: {format: {fill: () => "Dato non disponibile (RSO)"}}
    }),
    Plot.geo(confiniReg, {
      stroke: "#888",
      strokeWidth: 0.7
    })
  ]
})
```

---

## 2. Evoluzione della dotazione FSC ${trendFsc[0].anno}–${trendFsc[trendFsc.length - 1].anno}

Come è cambiata la dotazione totale nel tempo? Il grafico mostra l'andamento della dotazione FSC e del fondo perequativo a livello nazionale.

```js
Plot.plot({
  title: "Dotazione FSC e fondo perequativo — andamento nazionale",
  width: 800,
  height: 350,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, tickFormat: "~s", label: "€"},
  color: {legend: true, domain: ["Dotazione FSC", "Perequativo"], range: ["#4e79a7", "#e15759"]},
  marks: [
    Plot.line(trendFsc, {x: "anno", y: "fsc", stroke: "#4e79a7", tip: true}),
    Plot.dot(trendFsc, {x: "anno", y: "fsc", fill: "#4e79a7", r: 3}),
    Plot.line(trendFsc, {x: "anno", y: "perequativo", stroke: "#e15759", tip: true}),
    Plot.dot(trendFsc, {x: "anno", y: "perequativo", fill: "#e15759", r: 3}),
  ]
})
```

---

## 3. Contribuenti netti vs beneficiari — ${String(annoSel)}

Il fondo perequativo è negativo per i comuni che contribuiscono e positivo per chi riceve. Il ${pct(percContribNetti)} dei comuni è contribuente netto.

```js
const perComune = filtered
  .map(d => ({...d, fsc_procapite: d.dotazione_finale_fsc / d.popolazione}))
  .sort((a, b) => b.fondo_perequativo - a.fondo_perequativo);
const top10 = perComune.slice(0, 10);
const bottom10 = perComune.slice(-10).reverse();
```

```js
Plot.plot({
  title: "Fondo perequativo pro capite — top 10 comuni beneficiari e contribuenti",
  width: 800,
  height: 350,
  marginLeft: 200,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "PiYG"},
  marks: [
    Plot.barX([...top10, ...bottom10], {
      y: "comune",
      x: "fondo_perequativo",
      fill: d => d.fondo_perequativo > 0 ? "beneficiario" : "contribuente",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Dettaglio regioni

```js
const { header, format } = tableFormat({
  regione: { label: "Regione", fmt: "string" },
  comuni: { label: "Comuni", fmt: "num" },
  popolazione: { label: "Popolazione", fmt: "num" },
  fsc: { label: "Dotazione FSC (€)", fmt: "euroCompact" },
  perequativo: { label: "Perequativo (€)", fmt: "euroCompact" },
  capacita: { label: "Capacità fiscale (€)", fmt: "euroCompact" },
});
```

```js
Inputs.table(perRegione, {
  columns: ["regione", "comuni", "popolazione", "fsc", "perequativo", "capacita"],
  header,
  format,
  rows: 25,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: il dataset copre il periodo 2022-2025. Anni precedenti non sono disponibili.
- **Comuni RSO**: i dati si riferiscono ai comuni delle Regioni a Statuto Ordinario. Non include comuni delle Regioni a Statuto Speciale.
- **Perequativo**: il fondo perequativo con segno negativo indica un comune contribuente netto (la sua capacità fiscale supera il fabbisogno standard).

---

## Risorse

- [OpenCivitas (fonte originale)](https://www.opencivitas.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/opencivitas_fsc_2025_rso/2025/opencivitas_fsc_2025_rso_2025_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/opencivitas-fsc-rso)

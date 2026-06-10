---
title: Consumo di suolo
description: Consumo di suolo per regione — stock e incremento annuale, ISPRA 2024
source: ISPRA
source_url: https://www.isprambiente.gov.it/
period: "2024"
last_modified: 2026-06-03
dataset_slug: ispra_consumo_suolo
---

# Consumo di suolo

Stock di suolo consumato e incremento netto annuale per regione. I dati ISPRA mostrano la cementificazione del territorio e la sua distribuzione geografica.

**Fonte**: [ISPRA](https://www.isprambiente.gov.it/) · **Periodo**: 2024

```js
import { normalizzaReg, loadItalianRegions, buildRegLookup } from "../import/geo-utils.js";
import { num, numFix, tableFormat } from "../import/format-utils.js";
```

```js
const regTopo = await FileAttachment("../data/regioni.topojson").json();
const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
```

```js
const data = await FileAttachment("../data/consumo-suolo.json").json();
```

```js
const ordinato = [...data].sort((a, b) => b.stock_pct_2024 - a.stock_pct_2024);
const mediaNaz = d3.mean(data, d => d.stock_pct_2024);
const totHa = d3.sum(data, d => d.stock_ha_2024);
const totInc = d3.sum(data, d => d.incremento_netto_ha_2023_2024);
```

```js
// Lookup con fallback automatici per match TopoJSON
const stockLookup = buildRegLookup(data, "regione", "stock_pct_2024");
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Suolo consumato</h3>
    <span class="big">${numFix(mediaNaz, 1)}%</span>
    <small style="opacity:0.6">media regionale</small>
  </div>
  <div class="card">
    <h3>Stock totale</h3>
    <span class="big">${(totHa / 1000).toFixed(0)} <small style="opacity:0.6">k ha</small></span>
  </div>
  <div class="card">
    <h3>Incremento 2023-24</h3>
    <span class="big">${num(totInc)} <small style="opacity:0.6">ha</small></span>
  </div>
</div>

---

## Stock suolo consumato per regione

Quali regioni hanno più suolo consumato? La percentuale di territorio cementificato è molto più alta in Lombardia e Veneto, mentre Basilicata e Valle d'Aosta registrano i valori più bassi.

```js
Plot.plot({
  title: "Stock suolo consumato per regione — 2024",
  projection: {type: "mercator", domain: regioniGeo},
  width: 800,
  height: 600,
  color: {scheme: "Reds", legend: true, label: "% suolo consumato", type: "quantile"},
  marks: [
    Plot.geo(regioniGeo, {
      fill: d => stockLookup.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#888",
      strokeWidth: 0.25,
      tip: {format: {fill: d => numFix(d, 1) + "%"}}
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
  regione: { label: "Regione", fmt: "string" },
  stock_pct_2024: { label: "Stock %", fmt: "pct" },
  stock_ha_2024: { label: "Stock (ha)", fmt: "num" },
  incremento_netto_ha_2023_2024: { label: "Incr. 23-24 (ha)", fmt: "num" },
});
```

```js
Inputs.table(ordinato, {
  columns: ["regione", "stock_pct_2024", "stock_ha_2024", "incremento_netto_ha_2023_2024"],
  header,
  format,
  rows: 25,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: il dataset copre il solo 2024. Dati precedenti non sono disponibili in questo dataset (le serie storiche sono disponibili nel dato originale ISPRA).
- **Stock**: la percentuale di suolo consumato è calcolata sul territorio comunale. I valori regionali sono medie dei comuni, non ponderate per superficie.
- **Incremento netto**: differenza tra consumo lordo e ripristino nell'ultimo periodo disponibile (2023-2024).
- **Fonte**: i dati provengono da ISPRA — monitoraggio del consumo di suolo.

---

## Risorse

- [ISPRA — Consumo di suolo](https://www.isprambiente.gov.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/ispra_consumo_suolo/2024/ispra_consumo_suolo_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/ispra-consumo-suolo)

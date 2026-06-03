---
title: Rifiuti urbani nei comuni
description: Dati ISPRA su rifiuti urbani, raccolta differenziata e volumi per comune e regione, 2020-2024
source: ISPRA
source_url: https://www.isprambiente.gov.it/it/dati/dati-sui-rifiuti-urbani
period: "2020–2024"
last_modified: 2026-05-26
dataset_slug: ispra_ru_base
---

# Rifiuti urbani nei comuni

Dati ISPRA sui rifiuti urbani dei comuni italiani. Produzione totale, raccolta differenziata e percentuale per regione.

**Fonte**: ISPRA · **Periodo**: 2020–2024

```js
import * as topojson from "npm:topojson-client";

const regTopo = await FileAttachment("../data/regioni.topojson").json();
const regioniGeo = topojson.feature(regTopo, regTopo.objects.regioni);
const confiniReg = topojson.mesh(regTopo, regTopo.objects.regioni, (a, b) => a !== b);
```

```js
const rifiutiData = await FileAttachment("../data/ispra-regioni.json").json();
const comuni = await FileAttachment("../data/ispra-comuni.json").json();
```

```js
const anni = [...new Set(rifiutiData.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const regFiltered = rifiutiData
  .filter(d => d.anno === annoSel)
  .sort((a, b) => b.totale_ru_tonnellate - a.totale_ru_tonnellate)
  .map(d => ({
    ...d,
    quota_rd: Math.round(d.totale_rd_tonnellate / d.totale_ru_tonnellate * 100 * 10) / 10
  }));
```

```js
const totRU = regFiltered.reduce((s, d) => s + d.totale_ru_tonnellate, 0);
const totRD = regFiltered.reduce((s, d) => s + d.totale_rd_tonnellate, 0);
const mediaRd = Math.round(totRD / totRU * 1000) / 10;
```

```js
const comuniFiltrati = comuni
  .filter(d => d.anno === annoSel)
  .map(d => ({...d, percentuale_rd: Math.round(d.totale_rd_tonnellate / d.totale_ru_tonnellate * 1000) / 10}))
  .sort((a, b) => b.percentuale_rd - a.percentuale_rd);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Rifiuti totali</h3>
    <span class="big">${Math.round(totRU).toLocaleString("it-IT")} <small style="opacity:0.6">t</small></span>
  </div>
  <div class="card">
    <h3>Quota RD</h3>
    <span class="big">${mediaRd}%</span>
  </div>
  <div class="card">
    <h3>Regioni</h3>
    <span class="big">${regFiltered.length}</span>
  </div>
</div>

---

## Raccolta differenziata per regione

```js
// Normalizzazione nomi regione
function normalizzaReg(nome) {
  return nome.toUpperCase().replace(/ \/ /g, '/').replace(/ /g, '-');
}

const rdLookup = new Map(regFiltered.map(d => [normalizzaReg(d.regione), d.quota_rd]));
// Fallback per nomi regione non standard (ISPRA vs TopoJSON)
const rdFALLBACKS = {"VALLE-DAOSTA": "VALLE-D'AOSTA/VALLÉE-D'AOSTE", "TRENTINO-ALTO-ADIGE": "TRENTINO-ALTO-ADIGE/SÜDTIROL"};
for (const [short, full] of Object.entries(rdFALLBACKS)) {
  if (rdLookup.has(short) && !rdLookup.has(full)) rdLookup.set(full, rdLookup.get(short));
}
```

```js
Plot.plot({
  title: `Quota raccolta differenziata per regione — ${String(annoSel)}`,
  projection: {type: "mercator", domain: regioniGeo},
  width: 800,
  height: 600,
  color: {scheme: "YlGn", legend: true, label: "% RD", type: "quantile"},
  marks: [
    Plot.geo(regioniGeo, {
      fill: d => rdLookup.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#888",
      strokeWidth: 0.25,
      tip: true
    }),
    Plot.geo(confiniReg, {
      stroke: "#888",
      strokeWidth: 0.7
    })
  ]
})
```

---

## Grandi comuni (popolazione ≥ 100.000)

```js
Plot.plot({
  title: `Percentuale RD nei grandi comuni — ${String(annoSel)}`,
  width: 800,
  height: 350,
  marginLeft: 120,
  y: {label: null, tickSize: 0},
  x: {grid: true, label: "% RD"},
  color: {scheme: "RdYlGn"},
  marks: [
    Plot.barX(comuniFiltrati, {
      y: "comune",
      x: "percentuale_rd",
      fill: "percentuale_rd",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Regioni — dettaglio

```js
Inputs.table(regFiltered, {
  columns: ["regione", "totale_ru_tonnellate", "totale_rd_tonnellate", "quota_rd"],
  header: {regione: "Regione", totale_ru_tonnellate: "RU totali (t)", totale_rd_tonnellate: "RD totale (t)", quota_rd: "% RD"},
  format: {totale_ru_tonnellate: x => Math.round(x).toLocaleString("it-IT"), totale_rd_tonnellate: x => Math.round(x).toLocaleString("it-IT"), quota_rd: x => `${x}%`},
  rows: 25, width: "100%"
})
```

---

---

## Limiti

- **Copertura**: i dati coprono il periodo 2020-2024. I dati 2024 sono preliminari e potrebbero essere rivisti da ISPRA.
- **Popolazione**: i dati comunali con popolazione ≥ 100.000 abitanti sono un sottoinsieme dei comuni italiani; non rappresentano l'intero territorio nazionale.
- **Percentuale RD**: calcolata come rapporto tra totale RD e totale RU. Variazioni nella metodologia di calcolo ISPRA tra anni possono influenzare il dato.

---

## Risorse

- [ISPRA — Rifiuti Urbani (fonte originale)](https://www.isprambiente.gov.it/it/dati/dati-sui-rifiuti-urbani)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/ispra_ru_base/2024/ispra_ru_base_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/ispra-ru-base)

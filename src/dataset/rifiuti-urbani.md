---
title: Rifiuti urbani nei comuni
description: Dati ISPRA su rifiuti urbani, raccolta differenziata e volumi per comune e regione, 2020-2024
source: ISPRA
source_url: https://www.isprambiente.gov.it/it/dati/dati-sui-rifiuti-urbani
period: "2020–2024"
last_modified: 2026-05-26
dataset_slug: ispra_ru_base
data_driven: true
---

# Rifiuti urbani nei comuni

**Nel ${String(annoSel)} i comuni italiani hanno prodotto ${unit(totRU, "t")} di rifiuti urbani, con una quota di raccolta differenziata del ${pct(mediaRd)}. Ma il divario tra regioni è enorme: dalla Val d'Aosta con oltre ${pct(maxRd)} al Sud dove si resta spesso sotto ${pct(minRd)}.**

Dati ISPRA sui rifiuti urbani dei comuni italiani. Produzione totale, raccolta differenziata e percentuale per regione. Ogni numero di questa pagina è calcolato dal dato a build-time.

**Fonte**: [ISPRA](https://www.isprambiente.gov.it/it/dati/dati-sui-rifiuti-urbani) · **Periodo**: 2020–2024

```js
import { normalizzaReg, loadItalianRegions, buildMapLookup } from "../import/geo-utils.js";
import { num, pct, unit, tableFormat } from "../import/format-utils.js";
```

```js
const regTopo = await FileAttachment("../data/regioni.topojson").json();
const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
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
const maxRd = d3.max(regFiltered, d => d.quota_rd);
const minRd = d3.min(regFiltered, d => d.quota_rd);
```

```js
const comuniFiltrati = comuni
  .filter(d => d.anno === annoSel)
  .map(d => ({...d, percentuale_rd: Math.round(d.totale_rd_tonnellate / d.totale_ru_tonnellate * 1000) / 10}))
  .sort((a, b) => b.percentuale_rd - a.percentuale_rd);
const maxRdComuni = d3.max(comuniFiltrati, d => d.percentuale_rd);
const minRdComuni = d3.min(comuniFiltrati, d => d.percentuale_rd);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Rifiuti totali</h3>
    <span class="big">${unit(totRU, "t")}</span>
  </div>
  <div class="card">
    <h3>Quota RD</h3>
    <span class="big">${pct(mediaRd, 1)}</span>
  </div>
  <div class="card">
    <h3>Regioni</h3>
    <span class="big">${regFiltered.length}</span>
  </div>
</div>

---

## 1. Raccolta differenziata per regione — ${String(annoSel)}

La mappa mostra la quota di raccolta differenziata su totale rifiuti urbani per regione. Le regioni settentrionali e la Val d'Aosta guidano la classifica; al Sud e nelle Isole la differenziazione resta più bassa.

```js
const rdLookup = buildMapLookup(regFiltered, regioniGeo, "regione", "quota_rd");
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

> **Nota di lettura**: la scala quantile divide le regioni in gruppi di pari dimensione. I valori precisi sono nella tabella in fondo alla pagina.

---

## 2. Grandi comuni — ${String(annoSel)}

Nei grandi comuni (popolazione ≥ 100000) il divario è ancora più netto. Alcuni comuni del Nord superano il ${pct(maxRdComuni)} di differenziata, mentre altri restano sotto il ${pct(minRdComuni)}.

```js
Plot.plot({
  title: `Percentuale RD nei grandi comuni — ${String(annoSel)}`,
  width: 800,
  height: 450,
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

## Dettaglio per regione

```js
const { header, format } = tableFormat({
  regione: { label: "Regione", fmt: "string" },
  totale_ru_tonnellate: { label: "RU totali (t)", fmt: "num" },
  totale_rd_tonnellate: { label: "RD totale (t)", fmt: "num" },
  quota_rd: { label: "% RD", fmt: "pct" },
});
```

```js
Inputs.table(regFiltered, {
  columns: ["regione", "totale_ru_tonnellate", "totale_rd_tonnellate", "quota_rd"],
  header,
  format,
  rows: 25, width: "100%"
})
```

---

## Limiti

- **Copertura**: i dati coprono il periodo 2020-2024. I dati 2024 sono preliminari e potrebbero essere rivisti da ISPRA.
- **Popolazione**: i dati comunali con popolazione ≥ 100000 abitanti sono un sottoinsieme dei comuni italiani; non rappresentano l'intero territorio nazionale.
- **Percentuale RD**: calcolata come rapporto tra totale RD e totale RU. Variazioni nella metodologia di calcolo ISPRA tra anni possono influenzare il dato.

---

## Risorse

- [ISPRA — Rifiuti Urbani (fonte originale)](https://www.isprambiente.gov.it/it/dati/dati-sui-rifiuti-urbani)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/ispra_ru_base/2024/ispra_ru_base_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/ispra-ru-base)

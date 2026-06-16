---
title: Pensioni Pubblica Amministrazione — DAG
description: Numero e importo delle pensioni della PA per microqualifica, regione e anno, 2017-2022
source: MEF — Dipartimento dell'Amministrazione Generale
source_url: https://www.dag.mef.gov.it/aree-tematiche/dati-amministrativi/index.html
period: "2017–2022"
last_modified: 2026-05-20
dataset_slug: pensioni_pa_dag
---

# Pensioni Pubblica Amministrazione — DAG

Numero di partite pensionistiche e importo mensile erogato per la PA, disaggregati per microqualifica professionale, regione e anno. I dati coprono pensioni dirette, di reversibilità e altri trattamenti erogati dal Dipartimento dell'Amministrazione Generale.

**Fonte**: MEF — Dipartimento dell'Amministrazione Generale · **Periodo**: 2017–2022

```js
import { num, euro, pct, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/pensioni-pa-dag.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel);
```

```js
const totalePartite = d3.sum(filtered, d => d.numero_partite);
const totaleImporti = d3.sum(filtered, d => d.importi_mensili_pagati_eur);
const importoMedio = totalePartite > 0 ? totaleImporti / totalePartite : 0;
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Partite pensionistiche</h3>
    <span class="big">${num(totalePartite)}</span>
  </div>
  <div class="card">
    <h3>Importo mensile totale</h3>
    <span class="big">${euro(totaleImporti)}</span>
  </div>
  <div class="card">
    <h3>Importo medio</h3>
    <span class="big">${euro(importoMedio)}</span>
  </div>
</div>

---

## Per microqualifica

Distribuzione delle pensioni PA per microqualifica professionale. Le microqualifiche coprono i ruoli del personale della PA (docenti, impiegati, forze armate, ecc.).

```js
const TOP_K = 15;
const perQualificaRaw = d3.rollups(
  filtered,
  v => ({
    partite: d3.sum(v, d => d.numero_partite),
    importi: d3.sum(v, d => d.importi_mensili_pagati_eur),
  }),
  d => d.descrizione_microqualifica
).map(([key, val]) => ({
  microqualifica: key,
  partite: val.partite,
  importo_medio: val.partite > 0 ? val.importi / val.partite : 0
})).sort((a, b) => b.partite - a.partite);

const perQualifica = perQualificaRaw.length > TOP_K
  ? [
      ...perQualificaRaw.slice(0, TOP_K),
      {
        microqualifica: `Altre (${perQualificaRaw.length - TOP_K})`,
        partite: d3.sum(perQualificaRaw.slice(TOP_K), d => d.partite),
        importo_medio: null,
      }
    ]
  : perQualificaRaw;
```

```js
Plot.plot({
  title: `Partite pensionistiche PA per microqualifica — ${annoSel} (top ${Math.min(TOP_K, perQualificaRaw.length)})`,
  width: 800,
  height: Math.min(450, perQualifica.length * 28 + 40),
  marginLeft: 220,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Blues"},
  marks: [
    Plot.barX(perQualifica, {
      y: "microqualifica",
      x: "partite",
      fill: "partite",
      sort: {y: "-x"},
      tip: {format: {x: d => num(d)}}
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Per regione

Numero di partite pensionistiche per regione di residenza del pensionato.

```js
const perRegione = d3.rollups(
  filtered,
  v => ({
    partite: d3.sum(v, d => d.numero_partite),
  }),
  d => d.regione
).map(([key, val]) => ({regione: key, partite: val.partite}))
 .sort((a, b) => b.partite - a.partite);
```

```js
Plot.plot({
  title: `Partite pensionistiche PA per regione — ${annoSel}`,
  width: 800,
  height: 350,
  marginLeft: 150,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Greens"},
  marks: [
    Plot.barX(perRegione.slice(0, 15), {
      y: "regione",
      x: "partite",
      fill: "partite",
      sort: {y: "-x"},
      tip: {format: {x: d => num(d)}}
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Dettaglio completo

```js
const { header, format } = tableFormat({
  anno: { label: "Anno", fmt: "string" },
  descrizione_microqualifica: { label: "Microqualifica", fmt: "string" },
  regione: { label: "Regione", fmt: "string" },
  numero_partite: { label: "Partite", fmt: "num" },
  importi_mensili_pagati_eur: { label: "Importo mensile (€)", fmt: "euro" },
});
```

```js
Inputs.table(data.filter(d => d.anno >= 2019), {
  columns: ["anno", "descrizione_microqualifica", "regione", "numero_partite", "importi_mensili_pagati_eur"],
  header,
  format,
  rows: 20,
  width: "100%"
})
```

---

## Limiti

- **Copertura geografica**: la regione si riferisce alla residenza del pensionato, non alla sede dell'amministrazione che eroga la pensione.
- **Microqualifiche**: la classificazione delle microqualifiche segue le categorie ufficiali del DAG. Alcune voci possono essere aggregate o variare nel tempo.
- **Periodo**: il dataset copre 2017–2022. Anni precedenti o successivi non sono disponibili in questo snapshot.
- **Importo medio**: l'importo medio è calcolato come rapporto tra importo totale mensile pagato e numero di partite. Non include tredicesime, arretrati o ratei.

---

## Risorse

- [Fonte originale — MEF DAG](https://www.dag.mef.gov.it/aree-tematiche/dati-amministrativi/index.html)
- [Dati statistici spesa pensioni](https://datipensioni.mef.gov.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/pensioni_pa_dag/2024/pensioni_pa_dag_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/pensioni-pa-dag)

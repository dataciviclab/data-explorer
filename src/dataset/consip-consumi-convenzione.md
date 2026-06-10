---
title: Consumi in convenzione Consip
description: Dati Consip sugli acquisti della PA attraverso convenzioni, per regione e tipologia di amministrazione, 2023-2025
source: Consip S.p.A. / MEF
source_url: https://dati.consip.it/
period: "2023–2025"
last_modified: 2025-12-31
dataset_slug: consip_consumi_convenzione
---

# Consumi in convenzione Consip

La spesa della Pubblica Amministrazione per beni e servizi acquistati attraverso le convenzioni Consip. I dati sono disaggregati per regione della PA, tipologia di amministrazione e fornitore.

**Fonte**: Consip · **Periodo**: 2023–2025

```js
import { num, euro, tableFormat } from "../import/format-utils.js";
import { normalizzaReg, loadItalianRegions, buildMapLookup } from "../import/geo-utils.js";
```

```js
const regTopo = await FileAttachment("../data/regioni.topojson").json();
const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
```

```js
const regioni = await FileAttachment("../data/consip-consumi-convenzione-regioni.json").json();
const tipologie = await FileAttachment("../data/consip-consumi-convenzione-tipologie.json").json();
```

```js
const anni = [...new Set(regioni.map(d => d.anno_riferimento))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const totAnno = regioni
  .filter(d => d.anno_riferimento === annoSel)
  .reduce((s, d) => s + d.valore_economico_consumi, 0);
const totOrdini = regioni
  .filter(d => d.anno_riferimento === annoSel)
  .reduce((s, d) => s + d.numero_ordini_con_consumi, 0);
```

<div class="grid grid-cols-2">
  <div class="card">
    <h3>Spesa totale</h3>
    <span class="big">€ ${(totAnno / 1e6).toFixed(0)} <small style="opacity:0.6">mln</small></span>
  </div>
  <div class="card">
    <h3>Ordini</h3>
    <span class="big">${num(totOrdini)}</span>
  </div>
</div>

---

## Spesa per regione della PA

Quali regioni concentrano la spesa in convenzione? Il Lazio e la Lombardia guidano la classifica, trainate rispettivamente dagli apparati centrali dello Stato e dagli enti territoriali.

```js
const regFiltered = regioni
  .filter(d => d.anno_riferimento === annoSel)
  .sort((a, b) => b.valore_economico_consumi - a.valore_economico_consumi);
const lookup = buildMapLookup(regFiltered, regioniGeo, "regione_pa", "valore_economico_consumi");
```

```js
Plot.plot({
  title: `Spesa Consip per regione della PA — ${annoSel}`,
  projection: {type: "mercator", domain: regioniGeo},
  width: 800,
  height: 600,
  color: {scheme: "Blues", legend: true, label: "Spesa (€)", type: "quantile"},
  marks: [
    Plot.geo(regioniGeo, {
      fill: d => lookup.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#888",
      strokeWidth: 0.25,
      tip: {format: {fill: d => euro(d)}}
    }),
    Plot.geo(confiniReg, {
      stroke: "#888",
      strokeWidth: 0.7
    })
  ]
})
```

---

## Spesa per tipo di amministrazione

Chi spende di più attraverso Consip? Comuni, aziende di servizi pubblici e ministeri sono le prime tre categorie per volume di acquisti.

```js
const tipFiltered = tipologie
  .filter(d => d.anno_riferimento === annoSel)
  .sort((a, b) => b.valore_economico_consumi - a.valore_economico_consumi)
  .slice(0, 12);
```

```js
Plot.plot({
  title: `Spesa per tipologia di amministrazione — ${annoSel} (top 12)`,
  width: 800,
  height: 380,
  marginLeft: 180,
  y: {label: null, tickSize: 0},
  x: {grid: true, label: "milioni di €", tickFormat: d => (d / 1e6).toFixed(0)},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(tipFiltered, {
      y: "tipologia_amministrazione",
      x: "valore_economico_consumi",
      fill: "valore_economico_consumi",
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
  regione_pa: { label: "Regione PA", fmt: "string" },
  valore_economico_consumi: { label: "Spesa (€)", fmt: "euro" },
  numero_ordini_con_consumi: { label: "Ordini", fmt: "num" },
});
```

```js
Inputs.table(regFiltered, {
  columns: ["regione_pa", "valore_economico_consumi", "numero_ordini_con_consumi"],
  header,
  format,
  rows: 25,
  width: "100%"
})
```

---

---

## Limiti

- **Copertura**: i dati coprono il periodo 2023-2025. Anni precedenti non sono disponibili in questo dataset.
- **Regione PA**: la regione indicata è quella della PA acquirente, non quella del fornitore né quella di utilizzo del bene/servizio. Per le amministrazioni centrali, la sede legale è spesso nel Lazio indipendentemente dalla destinazione d'uso.
- **Convenzioni**: il dato include solo acquisti attraverso convenzioni Consip attive. Acquisti diretti o attraverso altri strumenti (MEPA, accordi quadro) non sono inclusi.

---

## Risorse

- [Consip — Dati (fonte originale)](https://dati.consip.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/consip_consumi_convenzione/2025/consip_consumi_convenzione_2025_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/consip-consumi-convenzione)

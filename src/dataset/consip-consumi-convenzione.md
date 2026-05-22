---
title: Consumi in convenzione Consip
description: Dati Consip sugli acquisti della PA attraverso convenzioni, per regione, tipologia di amministrazione e fornitore
---

# Consumi in convenzione Consip

La spesa della Pubblica Amministrazione per beni e servizi acquistati attraverso le convenzioni Consip. I dati sono disaggregati per regione della PA, tipologia di amministrazione e fornitore.

**Fonte**: Consip · **Periodo**: 2023–2025

```js
const regioni = await FileAttachment("../data/consip-consumi-convenzione-regioni.json").json();
const tipologie = await FileAttachment("../data/consip-consumi-convenzione-tipologie.json").json();
```

```js
const anni = [...new Set(regioni.map(d => d.anno_riferimento))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(anni, {label: "Anno", value: anni[0]}));
```

```js
const totAnno = regioni
  .filter(d => d.anno_riferimento === annoSel)
  .reduce((s, d) => s + d.valore_economico_consumi, 0);
const totOrdini = regioni
  .filter(d => d.anno_riferimento === annoSel)
  .reduce((s, d) => s + d.numero_ordini_con_consumi, 0);
const totPa = regioni
  .filter(d => d.anno_riferimento === annoSel)
  .reduce((s, d) => s + d.n_pa_con_consumi, 0);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Spesa totale</h3>
    <span class="big">€ ${(totAnno / 1e6).toFixed(0)} <small style="opacity:0.6">mln</small></span>
  </div>
  <div class="card">
    <h3>Ordini</h3>
    <span class="big">${totOrdini.toLocaleString("it-IT")}</span>
  </div>
  <div class="card">
    <h3>Amministrazioni</h3>
    <span class="big">${totPa.toLocaleString("it-IT")}</span>
  </div>
</div>

---

## Spesa per regione della PA

Quali regioni concentrano la spesa in convenzione? Il Lazio e la Lombardia guidano la classifica, trainate rispettivamente dagli apparati centrali dello Stato e dagli enti territoriali.

```js
const regFiltered = regioni
  .filter(d => d.anno_riferimento === annoSel)
  .sort((a, b) => b.valore_economico_consumi - a.valore_economico_consumi);
```

```js
Plot.plot({
  title: `Spesa Consip per regione della PA — ${annoSel}`,
  width: 800,
  height: 420,
  marginLeft: 140,
  y: {label: null, tickSize: 0},
  x: {grid: true, label: "milioni di €", tickFormat: d => (d / 1e6).toFixed(0)},
  color: {scheme: "Oranges"},
  marks: [
    Plot.barX(regFiltered, {
      y: "regione_pa",
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
Inputs.table(regFiltered, {
  columns: ["regione_pa", "valore_economico_consumi", "numero_ordini_con_consumi", "n_pa_con_consumi", "n_po_con_consumi"],
  header: {
    regione_pa: "Regione PA",
    valore_economico_consumi: "Spesa (€)",
    numero_ordini_con_consumi: "Ordini",
    n_pa_con_consumi: "PA coinvolte",
    n_po_con_consumi: "Fornitori"
  },
  format: {
    valore_economico_consumi: x => `€ ${Math.round(x).toLocaleString("it-IT")}`,
    numero_ordini_con_consumi: x => x.toLocaleString("it-IT"),
    n_pa_con_consumi: x => x.toLocaleString("it-IT"),
    n_po_con_consumi: x => x.toLocaleString("it-IT")
  },
  rows: 25,
  width: "100%"
})
```

---

## Risorse

- [Consip — Dati](https://dati.consip.it/)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/consip-consumi-convenzione)

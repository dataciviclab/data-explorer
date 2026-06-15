---
title: Pensioni Pubblica Amministrazione — DAG
description: Numero e importo delle pensioni della Pubblica Amministrazione per qualifica, regione e anno
source: MEF — Dipartimento dell'Amministrazione Generale
source_url: https://www.dag.mef.gov.it/aree-tematiche/dati-amministrativi/index.html
period: "2014–2024"
last_modified: 2026-05-20
dataset_slug: pensioni_pa_dag
---

# Pensioni Pubblica Amministrazione — DAG

Numero e importo mensile medio delle pensioni della Pubblica Amministrazione per qualifica, regione e anno. I dati coprono pensioni dirette, di reversibilità e assegni vitalizi erogati dal Dipartimento dell'Amministrazione Generale.

**Fonte**: MEF — Dipartimento dell'Amministrazione Generale · **Periodo**: 2014–2024

```js
const data = await FileAttachment("../data/pensioni-pa-dag.json").json();
```

```js
import { normalizzaReg, loadItalianRegions, buildRegLookup } from "../import/geo-utils.js";
import { num, euro, pct, unit } from "../import/format-utils.js";
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel);
```

```js
const totale_pensioni = d3.sum(filtered, d => d.numero_pensioni);
const importo_medio = d3.mean(filtered, d => d.importo_medio_mensile);
const perQualifica = Array.from(d3.rollup(filtered, v => ({
  numero: d3.sum(v, d => d.numero_pensioni),
  importo_medio: d3.mean(v, d => d.importo_medio_mensile)
}), d => d.qualifica), ([qualifica, agg]) => ({
  qualifica, 
  numero: agg.numero,
  importo_medio: agg.importo_medio
})).sort((a,b) => b.numero - a.numero);

const perRegione = Array.from(d3.rollup(filtered, v => ({
  numero: d3.sum(v, d => d.numero_pensioni),
  importo_medio: d3.mean(v, d => d.importo_medio_mensile)
}), d => d.regione), ([regione, agg]) => ({
  regione,
  numero: agg.numero,
  importo_medio: agg.importo_medio
})).sort((a,b) => b.numero - a.numero);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Pensioni totali</h3>
    <span class="big">${(totale_pensioni / 1e3).toFixed(1)} <small style="opacity:0.6">mila</small></span>
  </div>
  <div class="card">
    <h3>Importo medio</h3>
    <span class="big">${euro(importo_medio)}</span>
  </div>
  <div class="card">
    <h3>Qualifiche</h3>
    <span class="big">${perQualifica.length}</span>
  </div>
</div>

---

## Per qualifica

Numero di pensioni e importo medio mensile della Pubblica Amministrazione, disaggregati per qualifica del pensionato. Le qualifiche variano in base al ruolo ricoperto al momento della decorrenza della pensione.

```js
Plot.plot({
  title: `Pensioni PA per qualifica — ${annoSel}`,
  width: 800,
  height: 400,
  marginLeft: 250,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  marks: [
    Plot.barX(perQualifica, {
      y: "qualifica",
      x: "numero",
      fill: "numero",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ],
  color: {type: "linear", scheme: "Blues"}
})
```

---

## Per regione

Numero di pensioni per regione di residenza del pensionato. Molte pensioni risultano concentrate in alcune regioni, riflettendo la distribuzione geografica della sede centrale dei ministeri e degli enti della Pubblica Amministrazione.

```js
Plot.plot({
  title: `Pensioni PA per regione — ${annoSel}`,
  width: 800,
  height: 350,
  marginLeft: 150,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  marks: [
    Plot.barX(perRegione.slice(0, 15), {
      y: "regione",
      x: "numero",
      fill: "numero",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ],
  color: {type: "linear", scheme: "Greens"}
})
```

---

## Dettaglio completo

```js
const columns = ["anno", "qualifica", "regione", "numero_pensioni", "importo_medio_mensile"];
const header = {
  anno: "Anno",
  qualifica: "Qualifica",
  regione: "Regione",
  numero_pensioni: "Numero pensioni",
  importo_medio_mensile: "Importo medio mensile (€)"
};
const format = {
  numero_pensioni: x => String(Math.round(x)),
  importo_medio_mensile: x => euro(x)
};
```

```js
Inputs.table(data.filter(d => d.anno >= 2020), {
  columns,
  header,
  format,
  rows: 20,
  width: "100%"
})
```

---

## Limiti

- **Copertura geografica**: i dati si riferiscono alla regione di residenza del pensionato, non alla sede dell'amministrazione che eroga la pensione. Una parte significativa di pensioni è concentrata a Roma (sede centrale di numerosi ministeri).
- **Qualifiche**: la classificazione delle qualifiche può variare nel tempo. L'aggregazione per qualifica segue le categorie ufficiali del DAG.
- **Periodo**: il dataset copre dal 2014 al 2024. Alcuni anni potrebbero avere dati incompleti o essere soggetti a revisioni successive.
- **Importo medio**: l'importo medio mensile è calcolato su base annuale e rappresenta una stima della pensione media nel periodo considerato.

---

## Risorse

- [Fonte originale — MEF DAG](https://www.dag.mef.gov.it/aree-tematiche/dati-amministrativi/index.html)
- [Dati statistici spesa pensioni](https://datipensioni.mef.gov.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/pensioni_pa_dag/2024/pensioni_pa_dag_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/pensioni-pa-dag)

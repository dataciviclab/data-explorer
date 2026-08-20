---
title: Pensioni INPS — da quali gestioni arrivano?
description: Numero di pensioni INPS per gestione previdenziale, area geografica e anno, 2020-2024
source: INPS — Open Data
source_url: https://www.inps.it/open-data
period: "2020–2024"
last_modified: 2026-05-26
dataset_slug: inps_pensioni_trimestrale
data_driven: true
---

# Pensioni INPS — da quali gestioni arrivano?

```js
import { num, numFix, pct, euroCompact, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/inps-pensioni.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel);

const perGestione = Array.from(d3.rollup(filtered, v => d3.sum(v, d => d.numero_pensioni), d => d.gestione), ([gestione, numero_pensioni]) => ({gestione, numero_pensioni})).sort((a,b) => b.numero_pensioni - a.numero_pensioni);

const perArea = Array.from(d3.rollup(filtered, v => d3.sum(v, d => d.numero_pensioni), d => d.area_geografica), ([area_geografica, numero_pensioni]) => ({area_geografica, numero_pensioni})).sort((a,b) => b.numero_pensioni - a.numero_pensioni);

const totale = d3.sum(filtered, d => d.numero_pensioni);
const topGestione = perGestione[0];
const quotaTop = topGestione ? (topGestione.numero_pensioni / totale * 100) : 0;
```

Il sistema previdenziale italiano è frammentato in gestioni separate — e questa frammentazione si vede nei numeri. Nel ${String(annoSel)} le ${perGestione.length} gestioni INPS gestivano complessivamente ${num(totale)} pensioni nel dataset, con la **${topGestione?.gestione}** che da sola ne concentrava il ${pct(quotaTop)}.

**Fonte**: INPS · **Periodo**: 2020–2024 · Le righe del dataset rappresentano pensioni per gestione, area geografica e trimestre — non l'intero stock nazionale.

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Pensioni nel dataset</h3>
    <span class="big">${num(totale)}</span>
  </div>
  <div class="card">
    <h3>Gestione principale</h3>
    <span class="big">${pct(quotaTop)}</span>
    <small style="opacity:0.6">${topGestione?.gestione}</small>
  </div>
  <div class="card">
    <h3>Aree geografiche</h3>
    <span class="big">${perArea.length}</span>
  </div>
</div>

---

## 1. Da quali gestioni arrivano — ${String(annoSel)}

La FPLD (Fondo Pensioni Lavoratori Dipendenti) domina con ${num(topGestione?.numero_pensioni)} pensioni. Seguono assegni sociali, artigiani e dipendenti pubblici. Le gestioni separate (commercianti, parasubordinati, cdcm) coprono la quota restante.

```js
Plot.plot({
  title: `Pensioni per gestione — ${String(annoSel)}`,
  width: 800,
  height: 350,
  marginLeft: 200,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  marks: [
    Plot.barX(perGestione, {
      y: "gestione",
      x: "numero_pensioni",
      fill: "#4e79a7",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

> **Nota**: il dataset include solo le righe per gestione × area × trimestre. L'intero stock nazionale non è in questo dataset.

---

## 2. Come si distribuiscono per area — ${String(annoSel)}

Il Sud e le Isole hanno la quota più alta di pensioni nel dataset, ma è proporzionale alla popolazione residente. La differenza non è nel numero, ma nella distribuzione per gestione.

```js
Plot.plot({
  title: `Pensioni per area geografica — ${String(annoSel)}`,
  width: 800,
  height: 250,
  marginLeft: 120,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  marks: [
    Plot.barX(perArea, {
      y: "area_geografica",
      x: "numero_pensioni",
      fill: "#6baed6",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Dettaglio gestioni

```js
const { header, format } = tableFormat({
  gestione: { label: "Gestione", fmt: "string" },
  numero_pensioni: { label: "Pensioni", fmt: "num" },
});
```

```js
Inputs.table(perGestione, {
  columns: ["gestione", "numero_pensioni"],
  header,
  format,
  rows: 20,
  width: "100%"
})
```

---

## Limiti

- **Sottoinsieme**: il dataset non contiene l'intero stock nazionale di pensioni. Le righe rappresentano aggregazioni per gestione, area e trimestre.
- **Cadenza trimestrale**: i dati sono pubblicati con cadenza trimestrale da INPS. Il totale mostrato è la somma dei trimestri dell'anno.
- **Stock vs flusso**: il numero di pensioni è uno stock (pensioni in essere alla fine del trimestre), non un flusso di nuove decorrenze.
- **Gestioni**: la disaggregazione segue la classificazione INPS. Alcune gestioni minori potrebbero essere aggregate.

---

## Risorse

- [INPS Open Data (fonte originale)](https://www.inps.it/open-data)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/inps_pensioni_trimestrale/2024/inps_pensioni_trimestrale_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/inps-pensioni)

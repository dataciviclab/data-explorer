---
title: Elezioni Regionali
description: "Presidenti e liste regionali 2018-2024: affluenza e risultati"
source: open-politica / Ministero dell'Interno
source_url: https://dait.interno.gov.it/
period: "2018-2024"
last_modified: 2026-08-21
dataset_slug: elezioni_regionali
data_driven: true
---

```js
const data = await FileAttachment("../data/elezioni-regionali.json").json();
const plot = await import("npm:@observablehq/plot");
import { num, numFix, pct } from "../import/format-utils.js";
```

# Elezioni Regionali — chi governa le 20 regioni?

**${data.kpi.tot_regioni} regioni con elezioni dal ${data.kpi.first_year} al ${data.kpi.last_year}. Affluenza media: ${data.kpi.aff_media}%.** Le regionali sono il voto che decide chi amministra le regioni — e spesso anticipa le tendenze nazionali.

Risultati delle elezioni regionali per presidente: candidati, liste, voti e affluenza. I dati coprono le elezioni del 2018, 2020 e 2024.

---

## 1. Affluenza per regione

<div class="grid grid-cols-3">
  <div class="card"><h3>Regioni</h3><span class="big">${data.kpi.tot_regioni}</span></div>
  <div class="card"><h3>Periodo</h3><span class="big">${data.kpi.first_year}–${data.kpi.last_year}</span></div>
  <div class="card"><h3>Affluenza media</h3><span class="big">${data.kpi.aff_media}%</span></div>
</div>

```js
display(plot.plot({
  title: "Affluenza per regione (ultima elezione)",
  width: 800, height: 400,
  marginLeft: 140,
  x: {grid: true, label: "% affluenza"},
  y: {label: null},
  marks: [
    plot.barX(data.per_regione, {
      y: "regione", x: "affluenza",
      fill: d => d.affluenza >= 60 ? "#2ca02c" : d.affluenza >= 50 ? "#ff7f0e" : "#d62728",
      tip: true
    }),
    plot.text(data.per_regione, {
      y: "regione", x: "affluenza",
      text: d => `${d.affluenza}%`,
      dx: 5, textAnchor: "start", fontSize: 11
    }),
    plot.ruleX([50])
  ]
}))
```

---

## 2. Le liste che vincono

```js
const ultimeElezioni = [...new Set(data.per_lista.map(d => d.anno))].sort();
const datiPlot = data.per_lista
  .filter(d => ultimeElezioni.includes(d.anno))
  .map(d => ({...d, annoStr: String(d.anno)}));

const rankMap = {};
ultimeElezioni.forEach(a => {
  const items = datiPlot.filter(d => d.anno === a).sort((x, y) => y.voti - x.voti).slice(0, 5);
  items.forEach((d, i) => { rankMap[`${d.anno}_${d.lista}`] = i; });
});
const filtered = datiPlot.filter(d => rankMap[`${d.anno}_${d.lista}`] !== undefined);

display(plot.plot({
  title: "Top 5 liste per elezione regionale (voti)",
  width: 800, height: 350,
  fx: {label: null, padding: 0.2},
  x: {label: "Voti", tickFormat: "~s"},
  y: {label: null},
  marginLeft: 140,
  marks: [
    plot.barX(filtered, {
      y: d => d.lista.length > 18 ? d.lista.slice(0, 18) + "…" : d.lista,
      x: "voti",
      fx: "annoStr",
      fill: "#e6550d",
      tip: true
    }),
    plot.ruleX([0])
  ]
}))
```

---

## Vedi anche

<div style="display:flex; flex-wrap:wrap; gap:0.5em">
  <a href="/dataset/elezioni-politiche" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Politiche</a>
  <a href="/dataset/elezioni-comunali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Comunali</a>
  <a href="/dataset/elezioni-europee" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Europee</a>
  <a href="/dataset/elezioni-referendum" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Referendum</a>
</div>

---

## Limiti

- **Fonte**: open-politica / Ministero dell'Interno
- **Copertura**: solo elezioni regionali ordinarie (2018, 2020, 2024)
- **Presidenti**: il presidente eletto è quello con più voti al primo turno; non include ballottaggi
- **Liste**: le coalizioni cambiano; le liste locali non sono sempre presenti

---

## Risorse

- [open-politica](https://github.com/dataciviclab/open-politica)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/elezioni_regionali/2024/elezioni_regionali_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/open-politica/tree/main/datasets/elezioni-regionali)

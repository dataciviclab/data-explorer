---
title: Elezioni Europee
description: "Risultati europei 1979-2024: affluenza, liste e tendenze euroscettiche"
source: open-politica / Ministero dell'Interno
source_url: https://dait.interno.gov.it/
period: "1979-2024"
last_modified: 2026-08-21
dataset_slug: elezioni_europee
data_driven: true
---

```js
const data = await FileAttachment("../data/elezioni-europee.json").json();
const plot = await import("npm:@observablehq/plot");
import { num, numFix, pct, tableFormat } from "../import/format-utils.js";
```

```js
const delta = data.kpi.affluenza_first - data.kpi.affluenza_last;
```

# Elezioni Europee — l'Italia si disinteressa all'Europa?

**Dal ${data.kpi.first_year} al ${data.kpi.last_year}, ${data.trend.length} elezioni europee. L'affluenza è crollata dal ${data.kpi.affluenza_first}% al ${data.kpi.affluenza_last}%: ${numFix(delta, 0)} punti in quasi 50 anni.** L'Italia è il paese europeo dove il voto per il Parlamento europeo ha perso più terreno.

Risultati delle elezioni europee per lista: voti, affluenza e tendenze per circoscrizione. I dati coprono tutte le elezioni dal 1979 al 2024.

---

## 1. L'affluenza in free fall

<div class="grid grid-cols-4">
  <div class="card"><h3>Elezioni</h3><span class="big">${data.trend.length}</span>
</div>
  <div class="card"><h3>Periodo</h3><span class="big">${data.kpi.first_year}–${data.kpi.last_year}</span>
</div>
  <div class="card"><h3>Affluenza ${data.kpi.first_year}</h3><span class="big">${data.kpi.affluenza_first}%</span>
</div>
  <div class="card"><h3>Affluenza ${data.kpi.last_year}</h3><span class="big">${data.kpi.affluenza_last}%</span>
</div>
</div>

```js
display(plot.plot({
  title: "Affluenza alle elezioni europee (%)",
  width: 800, height: 300,
  x: {tickFormat: String, label: null},
  y: {domain: [30, 100], grid: true, label: "% affluenza"},
  marks: [
    plot.lineY(data.trend, {x: "anno", y: "affluenza", stroke: "#e6550d", strokeWidth: 2}),
    plot.dot(data.trend, {x: "anno", y: "affluenza", fill: "#e6550d", r: 5}),
    plot.tip(data.trend.filter(d => [1979, 1994, 2004, 2014, 2024].includes(d.anno)), {x: "anno", y: "affluenza", title: d => `${d.anno}: ${d.affluenza}%`}),
    plot.ruleY([50])
  ]
}))
```

```js
const affMax = data.trend.reduce((a, b) => b.affluenza > a.affluenza ? b : a);
const affMin = data.trend.reduce((a, b) => b.affluenza < a.affluenza ? b : a);
```

> Il picco è stato nel ${affMax.anno} (${affMax.affluenza}%), il minimo nel ${affMin.anno} (${affMin.affluenza}%). Nel 2024 c'è stata una leggera ripresa, ma siamo ancora sotto il 50%.

---

## 2. Le liste che contano

I partiti italiani alle europee: chi cresce e chi crolla?

```js
const ultimeElezioni = [...new Set(data.per_lista.map(d => d.anno))].sort().slice(-5);
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
  title: "Top 5 liste per elezione europea (voti)",
  width: 800, height: 400,
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
      tip: true,
      title: d => `${d.lista}: ${num(d.voti)} voti`
    }),
    plot.ruleX([0])
  ]
}))
```

---

## 3. Affluenza per circoscrizione

Le circoscrizioni europee raggruppano più regioni. Il Nord-Ovest ha sempre avuto più affluenza.

```js
display(plot.plot({
  title: "Affluenza per circoscrizione (ultima elezione)",
  width: 800, height: 280,
  marginLeft: 250,
  x: {grid: true, label: "% affluenza"},
  y: {label: null},
  marks: [
    plot.barX(data.per_circoscrizione, {
      y: "circoscrizione", x: "affluenza",
      fill: d => d.affluenza >= 50 ? "#2ca02c" : d.affluenza >= 40 ? "#ff7f0e" : "#d62728",
      tip: true
    }),
    plot.text(data.per_circoscrizione, {
      y: "circoscrizione", x: "affluenza",
      text: d => `${d.affluenza}%`,
      dx: 5, textAnchor: "start", fontSize: 11
    }),
    plot.ruleX([50])
  ]
}))
```

---

## Vedi anche

<div style="display:flex; flex-wrap:wrap; gap:0.5em">
  <a href="/dataset/elezioni-politiche" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Politiche</a>
  <a href="/dataset/elezioni-comunali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Comunali</a>
  <a href="/dataset/elezioni-referendum" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Referendum</a>
  <a href="/dataset/elezioni-regionali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Regionali</a>
</div>

---

## Limiti

- **Fonte**: open-politica / Ministero dell'Interno
- **Circoscrizioni**: 5 circoscrizioni europee (Nord-Ovest, Nord-Est, Centro, Sud, Isole)
- **Liste**: le coalizioni cambiano ogni elezione; le liste europee (PPE, S&D) non sono sempre presenti
- **Non include**: elezioni suppletive

---

## Risorse

- [open-politica](https://github.com/dataciviclab/open-politica)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/elezioni_europee/2024/elezioni_europee_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/open-politica/tree/main/datasets/elezioni-europee)

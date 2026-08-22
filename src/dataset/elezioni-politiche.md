---
title: Elezioni Politiche Italiane
description: "Risultati elettorali Camera e Senato 1948-2022: affluenza, liste e candidati"
source: open-politica / Ministero dell'Interno
source_url: https://dait.interno.gov.it/
period: "1948-2022"
last_modified: 2026-08-21
dataset_slug: elezioni_politiche
data_driven: true
---

```js
const data = await FileAttachment("../data/elezioni-politiche.json").json();
const plot = await import("npm:@observablehq/plot");
import { num, numFix, pct } from "../import/format-utils.js";
```

```js
const affC = data.trend_affluenza.filter(d => d.camera_senato === "C");
const affS = data.trend_affluenza.filter(d => d.camera_senato === "S");
const delta = data.kpi.affluenza_first - data.kpi.affluenza_last;
```

# Elezioni Politiche — 75 anni di voto italiano

**Dal ${data.kpi.first} al ${data.kpi.last}, ${data.kpi.tot_anni} elezioni politiche. L'affluenza Camera è scesa dal ${data.kpi.affluenza_first}% al ${data.kpi.affluenza_last}%: ${numFix(delta, 0)} punti in 75 anni.** Come è cambiato il voto italiano? Quali partiti sono nati e quali sono scomparsi?

Risultati delle elezioni politiche per Camera dei Deputati e Senato della Repubblica. Ogni riga è un candidato/lista in un comune. I dati coprono tutti i collegi plurinominali e uninominali dal 1948 al 2022.

---

## 1. L'affluenza in calo

<div class="grid grid-cols-4">
  <div class="card"><h3>Elezioni</h3><span class="big">${data.kpi.tot_anni}</span>  <a href="/dataset/elezioni-regionali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Regionali</a>
</div>
  <div class="card"><h3>Periodo</h3><span class="big">${data.kpi.first}–${data.kpi.last}</span>  <a href="/dataset/elezioni-regionali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Regionali</a>
</div>
  <div class="card"><h3>Affluenza ${data.kpi.first}</h3><span class="big">${data.kpi.affluenza_first}%</span>  <a href="/dataset/elezioni-regionali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Regionali</a>
</div>
  <div class="card"><h3>Affluenza ${data.kpi.last}</h3><span class="big">${data.kpi.affluenza_last}%</span>  <a href="/dataset/elezioni-regionali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Regionali</a>
</div>
  <a href="/dataset/elezioni-regionali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Regionali</a>
</div>

L'Italia vota sempre meno. Nel 1948 quasi 9 italiani su 10 andavano alle urne; nel 2022 meno di 2 su 3. Il calo è costante, con qualche inversione temporanea (2006, 2013).

```js
display(plot.plot({
  title: "Affluenza alle elezioni politiche (%)",
  width: 800, height: 350,
  x: {tickFormat: String, label: null},
  y: {domain: [50, 100], grid: true, label: "% affluenza"},
  color: {domain: ["Camera", "Senato"], range: ["#3182bd", "#e6550d"], legend: true},
  marks: [
    plot.lineY(affC, {x: "anno", y: "affluenza", stroke: "#3182bd", strokeWidth: 2}),
    plot.lineY(affS, {x: "anno", y: "affluenza", stroke: "#e6550d", strokeWidth: 2, strokeDasharray: "5,3"}),
    plot.dot(affC, {x: "anno", y: "affluenza", fill: "#3182bd", r: 4}),
    plot.dot(affS, {x: "anno", y: "affluenza", fill: "#e6550d", r: 4}),
    plot.tip(affC.filter(d => [1948, 1972, 1992, 2006, 2013, 2022].includes(d.anno)), {x: "anno", y: "affluenza", title: d => `Camera ${d.anno}: ${d.affluenza}%`}),
    plot.tip(affS.filter(d => [1948, 1972, 1992, 2006, 2013, 2022].includes(d.anno)), {x: "anno", y: "affluenza", title: d => `Senato ${d.anno}: ${d.affluenza}%`}),
    plot.ruleY([50])
  ]
}))
```

> La Camera (linea continua) ha sempre avuto affluenza leggermente superiore al Senato (tratteggiato). Il divario si riduce negli ultimi decenni.

---

## 2. La mappa dei partiti — chi vince e chi perde

Ogni elezione racconta una storia diversa. I dati mostrano i voti delle principali liste alla Camera. Le sigle cambiano, ma ilGioco del potere rimane.

```js
// Top 5 liste per le ultime 5 elezioni
const ultimeElezioni = [...new Set(data.per_lista.map(d => d.anno))].sort().slice(-5);
const datiPlot = data.per_lista
  .filter(d => ultimeElezioni.includes(d.anno))
  .map(d => ({...d, annoStr: String(d.anno)}));

// Rank per anno per top 5
const rankMap = {};
ultimeElezioni.forEach(a => {
  const items = datiPlot.filter(d => d.anno === a).sort((x, y) => y.voti - x.voti).slice(0, 5);
  items.forEach((d, i) => { rankMap[`${d.anno}_${d.lista}`] = i; });
});
const filtered = datiPlot.filter(d => rankMap[`${d.anno}_${d.lista}`] !== undefined);

display(plot.plot({
  title: "Top 5 liste per elezione (Camera, voti)",
  width: 800, height: 400,
  fx: {label: null, padding: 0.2},
  x: {label: "Voti", tickFormat: "~s"},
  y: {label: null},
  marginLeft: 120,
  marks: [
    plot.barX(filtered, {
      y: d => d.lista.length > 15 ? d.lista.slice(0, 15) + "\u2026" : d.lista,
      x: "voti",
      fx: "annoStr",
      fill: "steelblue",
      tip: true,
      title: d => `${d.lista}: ${num(d.voti)} voti`
    }),
    plot.ruleX([0])
  ]
}))
```

> Le sigle cambiano ogni elezione. La storia è una costante ridefinizione dell'arco parlamentare: dal Bipolarismo (DC vs PCI) al Tri-polarismo (Berlusconi vs Prodi vs Lega) fino alla frammentazione attuale.

---

## 3. Affluenza per circoscrizione

Le circoscrizioni con più elettori non sono quelle con più affluenza. Il Sud vota meno del Nord nelle ultime elezioni.

```js
display(plot.plot({
  title: "Affluenza per circoscrizione (ultime elezioni)",
  width: 800, height: 340,
  marginLeft: 130,
  x: {grid: true, label: "% affluenza"},
  y: {label: null},
  marks: [
    plot.barX(data.per_circoscrizione, {
      y: d => d.circoscrizione.length > 25 ? d.circoscrizione.slice(0, 25) + "…" : d.circoscrizione,
      x: "affluenza",
      fill: d => d.affluenza >= 70 ? "#2ca02c" : d.affluenza >= 60 ? "#ff7f0e" : "#d62728",
      tip: true
    }),
    plot.text(data.per_circoscrizione, {
      y: d => d.circoscrizione.length > 25 ? d.circoscrizione.slice(0, 25) + "…" : d.circoscrizione,
      x: "affluenza",
      text: d => `${d.affluenza}%`,
      dx: 5, textAnchor: "start", fontSize: 11
    }),
    plot.ruleX([60])
  ]
}))
```

> Le circoscrizioni del Nord (Milano, Torino, Bologna) mantengono affluenza più alta; quelle del Sud (Napoli, Calabria, Sicilia) sono sotto la media nazionale.

---

## Vedi anche

<div style="display:flex; flex-wrap:wrap; gap:0.5em">
  <a href="/dataset/elezioni-comunali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Comunali</a>
  <a href="/dataset/elezioni-europee" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Europee</a>
  <a href="/dataset/elezioni-referendum" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Referendum</a>
  <a href="/dataset/votazioni-camera" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Votazioni Camera</a>
  <a href="/dataset/elezioni-regionali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Regionali</a>
</div>

---

## Limiti

- **Fonte**: open-politica / Ministero dell'Interno — dati storici delle elezioni
- **Granularità**: dati a livello di comune e lista; i candidati sono disponibili solo per le elezioni recenti
- **Liste**: le sigle delle liste cambiano nel tempo (fusioni, scissioni, riciclaggi)
- **Non include**: elezioni regionali e amministrative (hanno pagine separate)

---

## Risorse

- [open-politica](https://github.com/dataciviclab/open-politica)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/elezioni_politiche/2022/elezioni_politiche_2022_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/open-politica/tree/main/datasets/elezioni-politiche)

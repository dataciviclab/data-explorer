---
title: Elezioni Comunali
description: "Sindaci e liste comunali 2016-2024: affluenza, candidati e risultati"
source: open-politica / Ministero dell'Interno
source_url: https://dait.interno.gov.it/
period: "2016-2024"
last_modified: 2026-08-21
dataset_slug: elezioni_comunali
data_driven: true
---

```js
const data = await FileAttachment("../data/elezioni-comunali.json").json();
const plot = await import("npm:@observablehq/plot");
import { num, numFix, pct, tableFormat } from "../import/format-utils.js";
```

# Elezioni Comunali — cosa votano i comuni italiani?

**${num(data.kpi.tot_comuni)} comuni con elezioni dal ${data.kpi.first_year} al ${data.kpi.last_year}. L'affluenza è passata dal ${data.kpi.affluenza_first}% al ${data.kpi.affluenza_last}%.** Le comunali sono il voto più vicino ai cittadini — ma anche quello meno seguito.

Risultati delle elezioni comunali per sindaco: candidati, liste, voti, seggi e affluenza. I dati coprono turno 1 e turno 2, tutti i comuni italiani con elezioni nei periodi indicati.

---

## 1. L'affluenza comunale

<div class="grid grid-cols-4">
  <div class="card"><h3>Comuni</h3><span class="big">${num(data.kpi.tot_comuni)}</span>  <a href="/dataset/elezioni-regionali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Regionali</a>
</div>
  <div class="card"><h3>Periodo</h3><span class="big">${data.kpi.first_year}–${data.kpi.last_year}</span>  <a href="/dataset/elezioni-regionali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Regionali</a>
</div>
  <div class="card"><h3>Affluenza ${data.kpi.first_year}</h3><span class="big">${data.kpi.affluenza_first}%</span>  <a href="/dataset/elezioni-regionali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Regionali</a>
</div>
  <div class="card"><h3>Affluenza ${data.kpi.last_year}</h3><span class="big">${data.kpi.affluenza_last}%</span>  <a href="/dataset/elezioni-regionali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Regionali</a>
</div>
  <a href="/dataset/elezioni-regionali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Regionali</a>
</div>

```js
display(plot.plot({
  title: "Affluenza comunale per anno (turno 1)",
  width: 800, height: 300,
  x: {tickFormat: String, label: null},
  y: {grid: true, label: "% affluenza"},
  marks: [
    plot.lineY(data.trend, {x: "anno", y: "affluenza", stroke: "#3182bd", strokeWidth: 2}),
    plot.dot(data.trend, {x: "anno", y: "affluenza", fill: "#3182bd", r: 4}),
    plot.tip(data.trend, {x: "anno", y: "affluenza", title: d => `${d.anno}: ${d.affluenza}%`}),
    plot.ruleY([0])
  ]
}))
```

---

## 2. Affluenza per regione

Il Nord vota più del Sud? Le regioni con più affluenza sono quelle con più tradizione civica.

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

## 3. I sindaci più votati

I candidati sindaco con più voti assoluti — i numeri della democrazia locale.

```js
const { header, format } = tableFormat({
  comune: { label: "Comune", fmt: "string" },
  regione: { label: "Regione", fmt: "string" },
  candidato: { label: "Candidato", fmt: "string" },
  lista: { label: "Lista", fmt: "string" },
  voti: { label: "Voti", fmt: "num" },
  elettori: { label: "Elettori", fmt: "num" }
});
```

```js
Inputs.table(data.top_sindaci, {
  columns: ["comune", "regione", "candidato", "lista", "voti", "elettori"],
  header, format, rows: 20, width: "100%", sort: "voti", reverse: true
})
```

---

## Vedi anche

<div style="display:flex; flex-wrap:wrap; gap:0.5em">
  <a href="/dataset/elezioni-politiche" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Politiche</a>
  <a href="/dataset/elezioni-europee" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Europee</a>
  <a href="/dataset/elezioni-referendum" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Referendum</a>
  <a href="/dataset/elezioni-regionali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Regionali</a>
</div>

---

## Limiti

- **Fonte**: open-politica / Ministero dell'Interno
- **Copertura**: solo comuni con elezioni nei periodi indicati
- **Turno 1 e 2**: i dati includono entrambi i turni; l'affluenza si riferisce al turno 1
- **Non include**: elezioni suppletive e ballotaggi spareggio

---

## Risorse

- [open-politica](https://github.com/dataciviclab/open-politica)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/elezioni_comunali/2024/elezioni_comunali_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/open-politica/tree/main/datasets/elezioni-comunali)

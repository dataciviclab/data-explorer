---
title: Elezioni Referendum
description: "Referendum italiani 1995-2022: affluenza, esiti SI/NO e differenze regionali"
source: open-politica / Ministero dell'Interno
source_url: https://dait.interno.gov.it/
period: "1995-2022"
last_modified: 2026-08-21
dataset_slug: elezioni_referendum
data_driven: true
---

```js
const data = await FileAttachment("../data/elezioni-referendum.json").json();
const plot = await import("npm:@observablehq/plot");
import { num, numFix, pct, tableFormat } from "../import/format-utils.js";
```

```js
// Primo quesito di ogni referendum per il trend
const primoQuesito = data.trend.filter(d => d.quesito === 1);
const last = primoQuesito[primoQuesito.length - 1];
const first = primoQuesito[0];
```

# Referendum — Sì o No? L'Italia decide

**${data.kpi.tot_referendum} quesiti referendari dal ${data.kpi.first_year} al ${data.kpi.last_year}. L'affluenza ai referendum è sempre più alta delle elezioni politiche — ma non basta a fermare il calo.** I referendum sono lo strumento diretto della democrazia italiana: dalla cancellazione della Finanziaria (2011) al taglio dei parlamentari (2020).

Risultati dei referendum abrogativi e costituzionali per comune: voti SI/NO, affluenza, schede bianche e nulle. I dati coprono tutti i quesiti dal 1995 al 2022.

---

## 1. Affluenza e esito

<div class="grid grid-cols-3">
  <div class="card"><h3>Quesiti</h3><span class="big">${data.kpi.tot_referendum}</span>
</div>
  <div class="card"><h3>Periodo</h3><span class="big">${data.kpi.first_year}–${data.kpi.last_year}</span>
</div>
  <div class="card"><h3>Affluenza ultima</h3><span class="big">${last ? last.affluenza : "?"}%</span>
</div>
</div>

I referendum hanno affluenza più alta delle politiche — ma non sempre il Sì prevale. Il grafico mostra l'affluenza e la quota SI per ogni quesito.

```js
display(plot.plot({
  title: "Affluenza e quota SI per referendum",
  width: 800, height: 350,
  x: {tickFormat: String, label: "Anno"},
  y: {grid: true, label: "%", domain: [0, 100]},
  color: {domain: ["Affluenza", "Quota SI"], range: ["#3182bd", "#2ca02c"], legend: true},
  marks: [
    plot.lineY(primoQuesito, {x: "anno", y: "affluenza", stroke: "#3182bd", strokeWidth: 2}),
    plot.dot(primoQuesito, {x: "anno", y: "affluenza", fill: "#3182bd", r: 4}),
    plot.lineY(primoQuesito, {x: "anno", y: "pct_si", stroke: "#2ca02c", strokeWidth: 2}),
    plot.dot(primoQuesito, {x: "anno", y: "pct_si", fill: "#2ca02c", r: 4}),
    plot.tip(primoQuesito.filter(d => [1995, 2001, 2006, 2011, 2020, 2022].includes(d.anno)), {x: "anno", y: "affluenza", title: d => `${d.anno}: affluenza ${d.affluenza}%, SI ${d.pct_si}%`}),
    plot.ruleY([50])
  ]
}))
```

> L'affluenza (blu) è sempre superiore al 50%; la quota SI (verde) oscilla. Quando il Sì supera il 60%, il referendum passa quasi sempre.

---

## 2. SI vs NO per regione

Il Nord e il Sud non votano allo stesso modo. Le regioni con più affluenza non sono quelle con più SI.

```js
const regioniPlot = data.per_regione.map(d => ({...d, pct_no: 100 - d.pct_si}));

display(plot.plot({
  title: "Quota SI/NO per regione (ultimo referendum)",
  width: 800, height: 400,
  marginLeft: 140,
  x: {grid: true, label: "% dei voti validi"},
  y: {label: null},
  color: {domain: ["SI", "NO"], range: ["#2ca02c", "#d62728"], legend: true},
  marks: [
    plot.barX(regioniPlot.flatMap(d => [
      {regione: d.regione, pct: d.pct_si, tipo: "SI"},
      {regione: d.regione, pct: d.pct_no, tipo: "NO"}
    ]), {
      y: "regione", x: "pct", fill: "tipo", stack: true, tip: true
    }),
    plot.ruleX([50])
  ]
}))
```

---

## 3. Tutti i quesiti

```js
const { header: tblHeader, format: tblFormat } = tableFormat({
  anno: { label: "Anno", fmt: "num" },
  quesito: { label: "Quesito", fmt: "num" },
  affluenza: { label: "Affluenza", fmt: "pct" },
  si: { label: "Voti SI", fmt: "num" },
  no: { label: "Voti NO", fmt: "num" },
  pct_si: { label: "% SI", fmt: "pct" }
});
```

```js
Inputs.table(primoQuesito.map(d => ({
  anno: d.anno, quesito: d.quesito,
  affluenza: d.affluenza, si: d.si, no: d.no, pct_si: d.pct_si
})), {
  columns: ["anno", "quesito", "affluenza", "si", "no", "pct_si"],
  header: tblHeader, format: tblFormat,
  rows: 20, width: "100%", sort: "anno", reverse: true
})
```

---

## Vedi anche

<div style="display:flex; flex-wrap:wrap; gap:0.5em">
  <a href="/dataset/elezioni-politiche" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Politiche</a>
  <a href="/dataset/elezioni-comunali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Comunali</a>
  <a href="/dataset/elezioni-europee" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Europee</a>
  <a href="/dataset/elezioni-regionali" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Elezioni Regionali</a>
</div>

---

## Limiti

- **Fonte**: open-politica / Ministero dell'Interno
- **Referendum**: solo abrogativi e costituzionali; non include referendum regionali
- **Quesiti**: ogni referendum può avere più quesiti; il trend usa il primo quesito
- **Schede**: le schede bianche e nulle non sono incluse nel calcolo SI/NO

---

## Risorse

- [open-politica](https://github.com/dataciviclab/open-politica)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/elezioni_referendum/2022/elezioni_referendum_2022_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/open-politica/tree/main/datasets/elezioni-referendum)

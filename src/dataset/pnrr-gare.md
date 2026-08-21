---
title: PNRR Gare — Italia Domani
description: "Gare d'appalto dei progetti PNRR (fonte ReGiS): collegamento CUP→CIG, importi, procedura e submisura"
source: MEF — Italia Domani (italiadomani.gov.it)
source_url: https://italiadomani.gov.it/
period: "2016–2025"
last_modified: 2026-08-20
dataset_slug: pnrr_gare
data_driven: true
---

# PNRR Gare — Italia Domani

**Le gare d'appalto del PNRR: ${num(data.kpi.n_gare)} bandi per ${numFix(data.kpi.importo_mld, 1)} mld di importo complessivo. Di quanto è stato aggiudicato? E quali submisure assorbono la spesa?**

Gare d'appalto dei progetti PNRR pubblicate su ReGiS/Italia Domani. Ogni riga è una gara collegata a un progetto tramite CUP e CIG. I dati mostrano l'importo complessivo, l'importo aggiudicato, la procedura di scelta del contraente e la submisura PNRR. I numeri si aggiornano a build-time dal parquet pulito.

```js
import { num, numFix, pct, euroCompact, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/pnrr-gare.json").json();
```

<div class="grid grid-cols-4">
  <div class="card"><h3>Gare totali</h3><span class="big">${num(data.kpi.n_gare)}</span></div>
  <div class="card"><h3>Importo complessivo</h3><span class="big">${numFix(data.kpi.importo_mld, 1)} mld</span></div>
  <div class="card"><h3>Aggiudicato</h3><span class="big">${numFix(data.kpi.aggiudicato_mld, 1)} mld</span></div>
  <div class="card"><h3>% Aggiudicazione</h3><span class="big">${pct(data.kpi.importo_mld > 0 ? data.kpi.aggiudicato_mld / data.kpi.importo_mld * 100 : 0, 0)}</span></div>
</div>

---

## 1. Trend gare per anno

Le gare pubblicate crescono dal 2020 in poi, con un picco nel 2024-2025. L'importo totale segue lo stesso trend.

```js
const plot = await import("npm:@observablehq/plot");
```

```js
display(plot.plot({
  title: `Gare PNRR per anno — importo e aggiudicato`,
  width: 800, height: 350,
  x: {tickFormat: String, label: null},
  y: {grid: true, label: "Miliardi €"},
  color: {domain: ["Importo", "Aggiudicato"], range: ["#3182bd", "#2ca02c"], legend: true},
  marks: [
    plot.lineY(data.trend, {x: "anno", y: "importo_mld", stroke: "#3182bd", strokeWidth: 2}),
    plot.lineY(data.trend, {x: "anno", y: "aggiudicato_mld", stroke: "#2ca02c", strokeWidth: 2}),
    plot.dot(data.trend, {x: "anno", y: "importo_mld", fill: "#3182bd"}),
    plot.dot(data.trend, {x: "anno", y: "aggiudicato_mld", fill: "#2ca02c"}),
    plot.tip(data.trend, {x: "anno", y: "importo_mld", title: d => `${d.anno}: €${d.importo_mld} mld`}),
    plot.tip(data.trend, {x: "anno", y: "aggiudicato_mld", title: d => `${d.anno}: €${d.aggiudicato_mld} mld`}),
    plot.ruleY([0])
  ]
}))
```

> L'importo totale include gare non ancora aggiudicrate. Il gap tra linea blu (importo) e verde (aggiudicato) mostra le gare in corso o annullate.

---

## 2. Top submisure per importo

Le submisure PNRR che assorbono più risorse. Le infrastrutture digitali e la mobilità sostenibile dominano la classifica.

```js
const { header, format } = tableFormat({
  submisura: { label: "Submisura PNRR", fmt: "string" },
  n_gare: { label: "Gare", fmt: "num" },
  importo_mln: { label: "Importo (M€)", fmt: "num" },
  aggiudicato_mln: { label: "Aggiudicato (M€)", fmt: "num" }
});
```

```js
Inputs.table(data.per_submisura, {
  columns: ["submisura", "n_gare", "importo_mln", "aggiudicato_mln"],
  header, format, rows: 10, width: "100%",
  sort: "importo_mln", reverse: true
})
```

---

## 3. Mix delle procedure

```js
display(plot.plot({
  title: "Gare per procedura di aggiudicazione",
  width: 800, height: 250,
  x: {grid: true, label: "Numero gare"},
  y: {label: null},
  color: {scheme: "Set2"},
  marks: [
    plot.barY(data.per_procedura, {
      y: d => d.procedura.length > 40 ? d.procedura.slice(0, 40) + "…" : d.procedura,
      x: "n_gare",
      fill: "procedura",
      tip: true,
      sort: {y: "-x"}
    }),
    plot.ruleX([0])
  ]
}))
```

---

## Limiti

- **Fonte**: ReGiS/Italia Domani — dati pubblicati dalle PA aggiudicatrici
- **Copertura**: solo gare con CIG pubblicato; gare senza CIG sono escluse
- **Importi**: valori a pubblicazione; l'importo aggiudicato può essere successivo
- **Aggiornamento**: dati estratti al ${data.kpi.max_data || "2026"}

---

## Risorse

- [Italia Domani — PNRR](https://italiadomani.gov.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/pnrr_gare/2026/pnrr_gare_2026_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/pnrr-gare)

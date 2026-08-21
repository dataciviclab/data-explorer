---
title: PNRR Pagamenti — Italia Domani
description: "Pagamenti dei progetti PNRR: finanziamento, erogazioni e fonti di finanziamento"
source: MEF — Italia Domani (italiadomani.gov.it)
source_url: https://italiadomani.gov.it/
period: "2021–2025"
last_modified: 2026-08-20
dataset_slug: pnrr_pagamenti
data_driven: true
---

```js
const data = await FileAttachment("../data/pnrr-pagamenti.json").json();
const plot = await import("npm:@observablehq/plot");
import { num, numFix, pct } from "../import/format-utils.js";
```

```js
const last = data.per_submisura[0];
const gap = data.kpi.fin_mld - data.kpi.pag_mld;
```

# PNRR Pagamenti — quanto denaro parte davvero?

**${numFix(data.kpi.fin_mld, 1)} mld di finanziamento previsti, ${numFix(data.kpi.pag_mld, 1)} mld effettivamente pagati (${data.kpi.pct_erogata}%).** Il PNRR prevede enormi investimenti, ma la capacità di spesa reale è molto inferiore a quella prevista. Quanto denaro è ancora fermo?

I pagamenti PNRR sono le erogazioni effettive ai progetti. Ogni riga è un progetto con il suo finanziamento e quanto è stato effettivamente pagato. I dati mostrano il divario tra quanto previsto e quanto erogato, e chi sta effettivamente pagando.

---

## 1. Finanziamento vs Pagamento

<div class="grid grid-cols-4">
  <div class="card"><h3>Finanziamento</h3><span class="big">${numFix(data.kpi.fin_mld, 1)} mld</span></div>
  <div class="card"><h3>Pagato</h3><span class="big">${numFix(data.kpi.pag_mld, 1)} mld</span></div>
  <div class="card"><h3>% Erogata</h3><span class="big">${data.kpi.pct_erogata}%</span></div>
  <div class="card"><h3>Gap</h3><span class="big">${numFix(gap, 1)} mld</span></div>
</div>

<div class="grid grid-cols-2">
  <div>
    Il finanziamento PNRR totale e di ${numFix(data.kpi.fin_mld, 1)} mld, ma solo ${numFix(data.kpi.pag_mld, 1)} mld sono stati effettivamente pagati. Il divario di ${numFix(gap, 1)} mld rappresenta la capacità di spesa non ancora realizzata.
  </div>
  <div>
    Di quanto pagato, ${numFix(data.kpi.pag_pnrr_mld, 1)} mld proviene direttamente dai fondi PNRR. il resto e cofinanziato da Stato, UE e altre fonti.
  </div>
</div>

---

## 2. Dove va il denaro — le submisure

Non tutte le submisure riescono a spendere allo stesso ritardo. Alcune erogano quasi tutto; altre hanno enormi fondi bloccati.

```js
const subPlot = data.per_submisura.map(d => ({
  ...d,
  label: d.submisura.length > 40 ? d.submisura.slice(0, 40) + "…" : d.submisura
}));

display(plot.plot({
  title: "Finanziamento vs Pagamento per submisura (milioni €)",
  width: 800, height: 380,
  x: {grid: true, label: "Milioni €"},
  y: {label: null},
  marks: [
    plot.barX(subPlot, {y: "label", x: "fin_mln", fill: "#ddd", tip: true, title: d => `${d.submisura}
Finanziato: €${d.fin_mln} M`}),
    plot.barX(subPlot, {y: "label", x: "pag_mln", fill: "#2ca02c", tip: true, title: d => `${d.submisura}
Pagato: €${d.pag_mln} M (${d.pct}%)`}),
    plot.text(subPlot, {y: "label", x: d => d.fin_mln + 500, text: d => `${d.pct}%`, fill: "#333", fontSize: 11, textAnchor: "start"}),
    plot.ruleX([0])
  ]
}))
```

> Le barre grigie sono il finanziamento previsto, le verdi l’effettivo pagamento. Il **Sistema duale** ha ${data.per_submisura[0].pct}% di erogazione. Le submisure con erogazione bassa sono quelle con gare ancora in corso o progetti non partiti.

---

## 3. Chi paga — le fonti di finanziamento

I pagamenti non vengono tutti dalla stessa fonte. Lo Stato è il principale erogatore, ma anche UE, FPOP e regioni contribuiscono.

```js
const fontiFiltro = data.fonti.filter(d => d.mld > 0);

display(plot.plot({
  title: "Pagamenti per fonte di finanziamento (miliardi €)",
  width: 800, height: 280,
  x: {grid: true, label: "Miliardi €"},
  y: {label: null},
  color: {scheme: "Set2"},
  marks: [
    plot.barX(fontiFiltro, {
      y: "fonte", x: "mld", fill: "fonte", tip: true,
      sort: {y: "-x"}
    }),
    plot.text(fontiFiltro, {
      y: "fonte", x: "mld",
      text: d => `${d.mld} mld`,
      dx: 5, textAnchor: "start", fontSize: 11
    }),
    plot.ruleX([0])
  ]
}))
```

> Lo Stato paga ${data.fonti[0].mld} mld, la fonte più consistente. I fondi UE diretti sono ${data.fonti[1].mld} mld. Il FPOP (Prosecuzione Opere Pubbliche) contribuisce con ${data.fonti[2].mld} mld.

---

## Vedi anche

<div style="display:flex; flex-wrap:wrap; gap:0.5em">
  <a href="/dataset/pnrr-gare" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Gare d’appalto</a>
  <a href="/dataset/pnrr-progetti" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Progetti e stato di avanzamento</a>
</div>

---

## Limiti

- **Fonte**: ReGiS/Italia Domani — dati pubblicati dalle PA
- **Aggregazione**: i record possono avere CUP duplicati (un progetto per fonte di finanziamento)
- **Tempistica**: dati estratti al 2026; i pagamenti sono in continuo aggiornamento
- **Non include**: pagamenti non ancora registrati nel sistema

---

## Risorse

- [Italia Domani — PNRR](https://italiadomani.gov.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/pnrr_pagamenti/2026/pnrr_pagamenti_2026_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/pnrr-pagamenti)

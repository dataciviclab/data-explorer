---
title: PNRR Progetti — Italia Domani
description: "Progetti PNRR: stato di avanzamento, finanziamento e cronoprogramma"
source: MEF — Italia Domani (italiadomani.gov.it)
source_url: https://italiadomani.gov.it/
period: "2021–2025"
last_modified: 2026-08-20
dataset_slug: pnrr-progetti
data_driven: true
---

```js
const data = await FileAttachment("../data/pnrr-progetti.json").json();
const plot = await import("npm:@observablehq/plot");
import { num, numFix, pct } from "../import/format-utils.js";
```

```js
const inCorso = data.per_stato.find(d => d.stato === "In Corso");
const inCorsoN = inCorso ? inCorso.n : 0;
const inCorsoPct = data.kpi.n_progetti > 0 ? Math.round(inCorsoN / data.kpi.n_progetti * 100) : 0;
```

# PNRR Progetti — quanti vanno avanti, quanti si bloccano?

**${num(data.kpi.n_progetti)} progetti per ${numFix(data.kpi.fin_mld, 1)} mld di finanziamento totale.** Di questi, ${inCorsoN} sono "In Corso" (${inCorsoPct}%). Il PNRR è un piano enorme — ma quanti progetti stanno effettivamente andando avanti?

Ogni progetto PNRR ha un CUP, un amministrazione titolare, un finanziamento previsto e uno stato di avanzamento. Questi dati mostrano quanti progetti ci sono, dove sono concentrati e in che fase si trovano.

---

## 1. Stato dei progetti

<div class="grid grid-cols-3">
  <div class="card"><h3>Progetti totali</h3><span class="big">${num(data.kpi.n_progetti)}</span></div>
  <div class="card"><h3>Finanziamento</h3><span class="big">${numFix(data.kpi.fin_mld, 1)} mld</span></div>
  <div class="card"><h3>Di cui PNRR</h3><span class="big">${numFix(data.kpi.fin_pnrr_mld, 1)} mld</span></div>
</div>

```js
display(plot.plot({
  title: "Progetti per stato di avanzamento",
  width: 800, height: 300,
  x: {grid: true, label: "Numero progetti"},
  y: {label: null},
  color: {scheme: "Tableau10"},
  marks: [
    plot.barX(data.per_stato, {
      y: "stato", x: "n", fill: "stato", tip: true,
      sort: {y: "-x"}
    }),
    plot.text(data.per_stato, {
      y: "stato", x: "n",
      text: d => `${d.n.toLocaleString("it-IT")}`,
      dx: 5, textAnchor: "start", fontSize: 11
    }),
    plot.ruleX([0])
  ]
}))
```

> Lo stato "In Corso" domina con ${inCorsoN} progetti. Gli stati "Concluso" e "Non Avviato" mostrano rispettivamente i progetti terminati e quelli ancora fermi.

---

## 2. Finanziamento per missione

Il PNRR è diviso in 5 missioni. Queste sono le missioni con più risorse assegnate.

```js
display(plot.plot({
  title: "Finanziamento per missione (miliardi €)",
  width: 800, height: 300,
  x: {grid: true, label: "Miliardi €"},
  y: {label: null},
  color: {scheme: "Tableau10"},
  marks: [
    plot.barX(data.per_missione, {
      y: "missione", x: "fin_mld", fill: "missione", tip: true,
      sort: {y: "-x"}
    }),
    plot.text(data.per_missione, {
      y: "missione", x: "fin_mld",
      text: d => `${d.fin_mld} mld`,
      dx: 5, textAnchor: "start", fontSize: 11
    }),
    plot.ruleX([0])
  ]
}))
```

> Le 5 missioni del PNRR coprono: Rivoluzione verde e transizione ecologica (M2), Istruzione e Ricerca (M1), Infrastrutture per la mobilita (M3), Istruzione e Ricerca (M4), Inclusione e Coesione (M5).

---

## 3. Fase di avanzamento

Oltre allo stato generale, i progetti hanno una fase di iter specifica che indica dove si trovano nel processo.

```js
const fasiPlot = data.per_fase.slice(0, 8);

display(plot.plot({
  title: "Progetti per fase di iter",
  width: 800, height: 300,
  x: {grid: true, label: "Numero progetti"},
  y: {label: null},
  color: {scheme: "Set2"},
  marks: [
    plot.barX(fasiPlot, {
      y: "fase", x: "n", fill: "fase", tip: true,
      sort: {y: "-x"}
    }),
    plot.text(fasiPlot, {
      y: "fase", x: "n",
      text: d => `${d.n.toLocaleString("it-IT")}`,
      dx: 5, textAnchor: "start", fontSize: 11
    }),
    plot.ruleX([0])
  ]
}))
```

> Le fasi più comuni sono "Esecuzione" (progetti in realizzazione) e "Avvio" (progetti appena partiti). Le fasi "Definizione" e "Progettazione" mostrano i progetti ancora in fase preliminare.

---

## Vedi anche

<div style="display:flex; flex-wrap:wrap; gap:0.5em">
  <a href="/dataset/pnrr-gare" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Gare d’appalto</a>
  <a href="/dataset/pnrr-pagamenti" style="text-decoration:none; padding:0.4em 0.8em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">Pagamenti erogati</a>
</div>

---

## Limiti

- **Fonte**: ReGiS/Italia Domani — dati pubblicati dalle PA
- **Aggregazione**: un progetto può comparire più volte se ha più CUP
- **Tempistica**: dati estratti al 2026; lo stato di avanzamento cambia continuamente
- **Non include**: progetti non ancora inseriti nel sistema CUP

---

## Risorse

- [Italia Domani — PNRR](https://italiadomani.gov.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/pnrr_progetti/2026/pnrr_progetti_2026_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/pnrr-progetti)

---
title: PNRR Gare — Italia Domani
description: "Gare d'appalto dei progetti PNRR (fonte ReGiS): collegamento CUP→CIG, importi, procedura e submisura"
source: MEF — Italia Domani (italiadomani.gov.it)
source_url: https://italiadomani.gov.it/
period: "2018–2025"
last_modified: 2026-08-20
dataset_slug: pnrr_gare
data_driven: true
---

```js
const data = await FileAttachment("../data/pnrr-gare.json").json();
const plot = await import("npm:@observablehq/plot");
import { num, numFix, pct } from "../import/format-utils.js";
```

```js
// Calcoli derivati
const last = data.trend[data.trend.length - 1];
const peak = data.trend.reduce((a, b) => b.n_gare > a.n_gare ? b : a);
const gap = data.kpi.importo_mld - data.kpi.aggiudicato_mld;
```

# PNRR Gare — il clock corre, i soldi partono?

**${num(data.kpi.n_gare)} gare d'appalto per ${numFix(data.kpi.importo_mld, 1)} mld di importo. Ma solo il ${numFix(data.kpi.importo_mld > 0 ? data.kpi.aggiudicato_mld / data.kpi.importo_mld * 100 : 0, 0)}% è stato aggiudicato.** Il picco è stato nel ${peak.anno} (${num(peak.n_gare)} gare), poi il ritmo è crollato. Quanto denaro è ancora fermo?

Il PNRR (Piano Nazionale di Ripresa e Resilienza) finanzia progetti di infrastrutture, transizione verde e digitalizzazione. Ogni progetto ha un CUP; quando parte la gara, viene pubblicato un CIG. Questi dati mostrano quante gare vengono pubblicate, quanto valgono, e quante vengono effettivamente aggiudicate.

---

## 1. L'esplosione delle gare

<div class="grid grid-cols-4">
  <div class="card"><h3>Gare totali</h3><span class="big">${num(data.kpi.n_gare)}</span></div>
  <div class="card"><h3>Progetti (CUP)</h3><span class="big">${num(data.kpi.n_progetti)}</span></div>
  <div class="card"><h3>Importo</h3><span class="big">${numFix(data.kpi.importo_mld, 1)} mld</span></div>
  <div class="card"><h3>Gap non aggiudicato</h3><span class="big">${numFix(gap, 1)} mld</span></div>
</div>

Dal 2022 il PNRR ha prodotto una valanga di gare. Il ${peak.anno} ha registrato il picco con **${num(peak.n_gare)} bandi**, prevalentemente affidamenti diretti sotto soglia. Ma il numero di gare non equivale ai soldi spesi — molte sono piccole e molte restano sulla carta.

```js
display(plot.plot({
  title: "Gare pubblicate per anno",
  width: 800, height: 300,
  x: {tickFormat: String, label: null},
  y: {grid: true, label: "Numero gare"},
  marks: [
    plot.barY(data.trend, {x: "anno", y: "n_gare", fill: "#3182bd", tip: true}),
    plot.ruleY([0])
  ]
}))
```

---

## 2. Il gap tra gare e aggiudicazioni

Le gare vengono pubblicate, ma quante vanno a buon fine? Il grafico mostra l'importo totale (blu) e quello effettivamente aggiudicato (verde). Il divario è il denaro che non parte.

```js
// Dati per grouped bar
const groupedData = data.trend.flatMap(d => [
  {anno: String(d.anno), valore: d.importo_mld, tipo: "Importo gara"},
  {anno: String(d.anno), valore: d.aggiudicato_mld, tipo: "Aggiudicato"}
]);

display(plot.plot({
  title: "Importo vs Aggiudicato per anno (miliardi €)",
  width: 800, height: 350,
  fx: {label: null},
  x: {label: null},
  y: {grid: true, label: "Miliardi €"},
  color: {domain: ["Importo gara", "Aggiudicato"], range: ["#3182bd", "#2ca02c"], legend: true},
  marks: [
    plot.barY(groupedData, {x: "anno", y: "valore", fill: "tipo", fx: "tipo", tip: true}),
    plot.ruleY([0])
  ]
}))
```

> **Nel ${peak.anno}**: ${num(peak.n_gare)} gare per €${peak.importo_mld} mld, ma solo €${peak.aggiudicato_mld} mld aggiudicati (**${peak.pct_aggiudicazione}%**).
> **Nel ${last.anno}**: ${num(last.n_gare)} gare per €${last.importo_mld} mld, con solo €${last.aggiudicato_mld} mld aggiudicati (**${last.pct_aggiudicazione}%**).

Il tasso di aggiudicazione crolla dal 2023 in poi. Significa che molte gare vengono pubblicate ma non trovano aggiudicatario, vanno deserte, o vengono annullate.

---

## 3. Dove va il denaro — le submisure

Non tutti i progetti PNRR sono uguali. Alcune submisure assorbono risorse enormi ma aggiudicano poco; altre funzionano meglio.

```js
const subTop = data.per_submisura.slice(0, 8);
const subPlot = subTop.map(d => ({
  ...d,
  label: d.submisura.length > 40 ? d.submisura.slice(0, 40) + "…" : d.submisura,
  pct: d.importo_mln > 0 ? Math.round(d.aggiudicato_mln / d.importo_mln * 100) : 0
}));

display(plot.plot({
  title: "Importo vs Aggiudicato per submisura (milioni €)",
  width: 800, height: 340,
  x: {grid: true, label: "Milioni €"},
  y: {label: null},
  marks: [
    plot.barX(subPlot, {y: "label", x: "importo_mln", fill: "#ddd", tip: true, title: d => `${d.submisura}\nImporto: €${d.importo_mln} M`}),
    plot.barX(subPlot, {y: "label", x: "aggiudicato_mln", fill: "#2ca02c", tip: true, title: d => `${d.submisura}\nAggiudicato: €${d.aggiudicato_mln} M (${d.pct}%)`}),
    plot.text(subPlot, {y: "label", x: d => d.importo_mln + 1500, text: d => `${d.pct}%`, fill: "#333", fontSize: 11, textAnchor: "start"}),
    plot.ruleX([0])
  ]
}))
```

> Le barre grigie sono l'importo totale, le verdi l'importo aggiudicato. Il **Sistema duale** assorbe €86.6 mld ma ne aggiudica solo €22.7 mld (**26%**). Le **smart grid** funzionano meglio: €29.3 mld, €25.3 aggiudicati (**86%**). Il divario racconta la capacità di spesa di ciascuna area.

---

## 4. Affidamento diretto: semplificazione o frammentazione?

Il **73% delle gare** (205.934 su 282.655) è affidamento diretto. Solo il **3.6%** è procedura aperta. Questo significa che la maggior parte dei bandi non passa da una gara vera e propria.

```js
const topProc = data.per_procedura.slice(0, 5);
const totalProc = topProc.reduce((s, d) => s + d.n_gare, 0);
```

```js
display(plot.plot({
  title: "Top 5 procedure per numero di gare",
  width: 800, height: 280,
  x: {grid: true, label: "Numero gare"},
  y: {label: null},
  color: {scheme: "Set2"},
  marks: [
    plot.barX(topProc, {
      y: d => d.procedura.length > 45 ? d.procedura.slice(0, 45) + "…" : d.procedura,
      x: "n_gare",
      fill: "procedura",
      tip: true,
      sort: {y: "-x"}
    }),
    plot.text(topProc, {
      y: d => d.procedura.length > 45 ? d.procedura.slice(0, 45) + "…" : d.procedura,
      x: "n_gare",
      text: d => `${d.n_gare.toLocaleString("it-IT")}`,
      dx: 5,
      textAnchor: "start",
      fontSize: 11
    }),
    plot.ruleX([0])
  ]
}))
```

Le prime 5 procedure coprono il ${Math.round(totalProc / data.kpi.n_gare * 100)}% delle gare. L'affidamento diretto domina — è la conseguenza delle soglie alzate dal nuovo Codice Appalti (D.Lgs. 36/2023).

---

## Limiti

- **Fonte**: ReGiS/Italia Domani — dati pubblicati dalle PA aggiudicatrici
- **Copertura**: solo gare con CIG pubblicato; molte gare senza CIG non sono censite
- **Importi**: valori a pubblicazione; l'importo aggiudicato può essere successivo
- **Tempistica**: i dati del ${last.anno} sono parziali (gare in corso)
- **Non include**: gare sotto soglia comunitaria non pubblicate su ReGiS

---

## Risorse

- [Italia Domani — PNRR](https://italiadomani.gov.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/pnrr_gare/2026/pnrr_gare_2026_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/pnrr-gare)

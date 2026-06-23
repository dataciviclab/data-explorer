---
title: Posti letto ospedalieri
description: Serie storica dei posti letto ospedalieri italiani per stabilimento, disciplina e regime di degenza, 2020-2023
source: Ministero della Salute — Banca Dati Posti Letto
source_url: https://www.salute.gov.it/portale/lea/dettaglioContenutiLea.jsp?lingua=italiano&id=5551&area=Lea&menu=vuoto
period: "2020–2023"
last_modified: 2026-06-09
dataset_slug: posti_letto_stabilimento
---

# Posti letto ospedalieri

Evoluzione della capacità ricettiva degli ospedali italiani dal 2020 al 2023. Il dato include tutti gli stabilimenti (pubblici e privati accreditati) e tutte le discipline, con dettaglio per regime di degenza: ordinaria, day hospital e day surgery.

**Fonte**: Ministero della Salute · **Periodo**: 2020–2023

```js
import { num, euro, euroCompact, pct, numFix, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/posti-letto-stabilimento.json").json();
```

```js
// Aggregazione per anno (Italia)
const perAnno = Array.from(d3.rollup(data, v => ({
  totale: d3.sum(v, d => d.totale_posti_letto),
  ordinaria: d3.sum(v, d => d.posti_letto_degenza_ordinaria),
  dh: d3.sum(v, d => d.posti_letto_day_hospital),
  ds: d3.sum(v, d => d.posti_letto_day_surgery),
}), d => d.anno), ([anno, v]) => ({anno, ...v}))
  .sort((a,b) => a.anno - b.anno);

// Anno più recente per default
const anni = perAnno.map(d => d.anno).sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
// Dati per l'anno selezionato
const annoData = data.filter(d => d.anno === annoSel);

// Per tipo struttura
const perTipo = Array.from(d3.rollup(annoData, v => ({
  letti: d3.sum(v, d => d.totale_posti_letto),
  strutture: new Set(v.map(d => d.descrizione_disciplina)).size,
}), d => d.descrizione_tipo_struttura), ([descrizione_tipo_struttura, v]) => ({tipo: descrizione_tipo_struttura, ...v}))
  .sort((a,b) => b.letti - a.letti);

// Per regione
const perRegioneAnno = Array.from(d3.rollup(annoData, v => ({
  letti: d3.sum(v, d => d.totale_posti_letto),
}), d => d.descrizione_regione), ([descrizione_regione, v]) => ({regione: descrizione_regione, ...v}))
  .sort((a,b) => b.letti - a.letti);
```

<div class="grid grid-cols-4">
  <div class="card">
    <h3>Totale posti letto</h3>
    <span class="big">${num(perAnno.find(d => d.anno === annoSel).totale)}</span>
  </div>
  <div class="card">
    <h3>Degenza ordinaria</h3>
    <span class="big">${num(perAnno.find(d => d.anno === annoSel).ordinaria)}</span>
  </div>
  <div class="card">
    <h3>Day Hospital</h3>
    <span class="big">${num(perAnno.find(d => d.anno === annoSel).dh)}</span>
  </div>
  <div class="card">
    <h3>Day Surgery</h3>
    <span class="big">${num(perAnno.find(d => d.anno === annoSel).ds)}</span>
  </div>
</div>

---

## Trend posti letto in Italia

Dopo il calo del 2020 (primo anno di pandemia), i posti letto totali sono aumentati nel 2021 per poi diminuire gradualmente. I letti di degenza ordinaria seguono lo stesso andamento, mentre day hospital e day surgery restano più stabili.

```js
Plot.plot({
  title: "Posti letto totali Italia — 2020-2023",
  width: 800,
  height: 350,
  x: {grid: true, label: null},
  y: {grid: true, label: "Posti letto", tickFormat: "~s"},
  color: {range: ["#e6550d"]},
  marks: [
    Plot.line(perAnno, {
      x: "anno",
      y: "totale",
      stroke: "#e6550d",
      strokeWidth: 2.5,
      marker: true,
      tip: {format: {y: d => num(d)}}
    }),
    Plot.text(perAnno, {
      x: "anno",
      y: "totale",
      text: d => num(d.totale),
      dy: -12,
      fill: "var(--theme-foreground-muted)",
      fontSize: 11
    }),
    Plot.ruleY([0])
  ]
})
```

```js
// Trend per regime di degenza
const perAnnoRegime = perAnno.flatMap(d => [
  {anno: d.anno, regime: "Ordinaria", letti: d.ordinaria},
  {anno: d.anno, regime: "Day Hospital", letti: d.dh},
  {anno: d.anno, regime: "Day Surgery", letti: d.ds},
]);
```

```js
Plot.plot({
  title: "Trend per regime di degenza — 2020-2023",
  width: 800,
  height: 350,
  x: {grid: true, label: null},
  y: {grid: true, label: "Posti letto", tickFormat: "~s"},
  color: {legend: true},
  marks: [
    Plot.line(perAnnoRegime, {
      x: "anno",
      y: "letti",
      stroke: "regime",
      strokeWidth: 2,
      marker: true,
      tip: {format: {y: d => num(d)}}
    }),
    Plot.ruleY([0])
  ]
})
```

---

## Posti letto per tipo struttura

Come si distribuiscono i posti letto tra ospedali pubblici, case di cura private accreditate, IRCCS e altre tipologie nell'anno selezionato?

```js
Plot.plot({
  title: `Posti letto per tipo struttura — ${annoSel}`,
  width: 800,
  height: 350,
  marginLeft: 220,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(perTipo, {
      y: "tipo",
      x: "letti",
      fill: "tipo",
      sort: {y: "-x"},
      tip: {format: {x: d => num(d)}}
    }),
    Plot.text(perTipo, {
      y: "tipo",
      x: "letti",
      text: d => num(d.letti),
      dx: 6,
      textAnchor: "start",
      fill: "var(--theme-foreground-muted)",
      fontSize: 11
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Dettaglio regioni

```js
const { header, format } = tableFormat({
  regione: { label: "Regione", fmt: "string" },
  letti: { label: "Posti letto", fmt: "num" },
});
```

```js
Inputs.table(perRegioneAnno, {
  columns: ["regione", "letti"],
  header,
  format,
  rows: 25,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie storica copre 2020-2023. Dati precedenti (pre-pandemia) non sono inclusi in questo dataset.
- **Doppio conteggio**: lo stesso posto letto può essere conteggiato in più discipline all'interno dello stesso stabilimento. Il totale Italia per anno è una somma di tutti i record.
- **Riclassificazioni**: cambi nella classificazione delle strutture o delle discipline tra anni possono influenzare la confrontabilità della serie.
- **Privati**: i dati includono anche le case di cura private accreditate, che possono avere dinamiche diverse rispetto al pubblico.

---

## Risorse

- [Ministero della Salute — Banca Dati Posti Letto](https://www.salute.gov.it/portale/lea/dettaglioContenutiLea.jsp?lingua=italiano&id=5551&area=Lea&menu=vuoto)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/posti_letto_stabilimento/2023/posti_letto_stabilimento_2023_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/posti-letto-stabilimento)

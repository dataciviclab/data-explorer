---
title: Posti letto per disciplina ospedaliera
description: Reparti di ricovero italiani per disciplina — posti letto ordinari, day hospital, day surgery, tasso di utilizzo e degenza media, 2022
source: Ministero della Salute
source_url: https://www.salute.gov.it/portale/lea/dettaglioContenutiLea.jsp?lingua=italiano&id=5551&area=Lea&menu=vuoto
period: "2022"
last_modified: 2026-06-05
dataset_slug: reparti_ricovero
---

# Posti letto per disciplina ospedaliera

La capacità ricettiva degli ospedali italiani per disciplina: Medicina Generale, Chirurgia, Ortopedia, Ostetricia, Terapia Intensiva e tutte le altre specialità. Per ogni disciplina i posti letto disponibili, il tasso di utilizzo e la degenza media. Dati 2022 del Ministero della Salute.

**Fonte**: Ministero della Salute · **Periodo**: 2022

```js
import { num, euro, euroCompact, pct, numFix, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/reparti-ricovero.json").json();
```

```js
// Aggregazione per disciplina
const perDisciplina = Array.from(d3.rollup(data, v => ({
  letti_ordinari: d3.sum(v, d => d.posti_letto_degenza_ordinaria),
  letti_dh: d3.sum(v, d => d.posti_letto_day_hospital),
  letti_ds: d3.sum(v, d => d.posti_letto_day_surgery),
  letti_util: d3.sum(v, d => d.posti_letto_utilizzati),
  tasso_medio: d3.mean(v, d => d.tasso_utilizzo),
  degenza_media: d3.mean(v, d => d.degenza_media_ordinaria),
}), d => d.disciplina), ([disciplina, v]) => ({disciplina, ...v}))
  .sort((a,b) => b.letti_ordinari - a.letti_ordinari);

const topDiscipline = perDisciplina.slice(0, 15);

const totaleLettiOrd = d3.sum(data, d => d.posti_letto_degenza_ordinaria);
const totaleLettiDH = d3.sum(data, d => d.posti_letto_day_hospital);
const totaleLettiDS = d3.sum(data, d => d.posti_letto_day_surgery);
const totaleLettiUtil = d3.sum(data, d => d.posti_letto_utilizzati);
```

<div class="grid grid-cols-4">
  <div class="card">
    <h3>Letti degenza ordinaria</h3>
    <span class="big">${num(totaleLettiOrd)}</span>
  </div>
  <div class="card">
    <h3>Letti Day Hospital</h3>
    <span class="big">${num(totaleLettiDH)}</span>
  </div>
  <div class="card">
    <h3>Letti Day Surgery</h3>
    <span class="big">${num(totaleLettiDS)}</span>
  </div>
  <div class="card">
    <h3>Letti utilizzati</h3>
    <span class="big">${num(totaleLettiUtil)} <small style="opacity:0.6">/ ${num(totaleLettiOrd + totaleLettiDH + totaleLettiDS)}</small></span>
  </div>
</div>

---

## Posti letto ordinari per disciplina

Medicina Generale domina con oltre 31.000 letti, seguita da Chirurgia Generale, Ortopedia e Ostetricia. La distribuzione riflette il peso epidemiologico e organizzativo delle diverse specialità.

```js
Plot.plot({
  title: "Posti letto degenza ordinaria per disciplina — 2022",
  width: 800,
  height: 400,
  marginLeft: 200,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(topDiscipline, {
      y: "disciplina",
      x: "letti_ordinari",
      fill: "disciplina",
      sort: {y: "-x"},
      tip: {format: {x: d => num(d) + " (" + numFix(d / totaleLettiOrd * 100, 1) + "%)"}}
    }),
    Plot.text(topDiscipline, {
      y: "disciplina",
      x: "letti_ordinari",
      text: d => num(d.letti_ordinari),
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

## Tasso di utilizzo per disciplina

Il tasso di occupazione dei posti letto misura l'efficienza con cui vengono utilizzati i letti disponibili. Un tasso molto alto (sopra il 90%) può indicare saturazione, uno molto basso (sotto il 60%) possibile sovradimensionamento.

```js
const perDisciplinaUtil = perDisciplina
  .filter(d => d.letti_ordinari > 500)  // solo discipline con almeno 500 letti
  .sort((a,b) => b.tasso_medio - a.tasso_medio);
```

```js
Plot.plot({
  title: "Tasso di utilizzo posti letto per disciplina — 2022",
  width: 800,
  height: 400,
  marginLeft: 200,
  y: {label: null, tickSize: 0},
  x: {grid: true, label: "Tasso di occupazione (%)", domain: [50, 90]},
  color: {scheme: "RdYlGn", type: "diverging", domain: [50, 70, 90]},
  marks: [
    Plot.barX(perDisciplinaUtil, {
      y: "disciplina",
      x: "tasso_medio",
      fill: "tasso_medio",
      sort: {y: "-x"},
      tip: {format: {x: d => numFix(d) + "%"}}
    }),
    Plot.ruleX([50, 70, 85])
  ]
})
```

> **Nota**: il tasso di utilizzo è calcolato come (giornate di degenza / giornate disponibili) × 100. Valori superiori a 85% indicano saturazione. Sono incluse solo discipline con almeno 500 letti ordinari.

---

## Degenza media per disciplina

La degenza media varia molto per specialità: pochi giorni per Ostetricia e Otorinolaringoiatria, settimane per Recupero e Riabilitazione e Lungodegenti.

```js
const perDisciplinaDegenza = perDisciplina
  .filter(d => d.letti_ordinari > 500)
  .sort((a,b) => b.degenza_media - a.degenza_media);
```

```js
Plot.plot({
  title: "Degenza media ordinaria per disciplina (giorni) — 2022",
  width: 800,
  height: 400,
  marginLeft: 200,
  y: {label: null, tickSize: 0},
  x: {grid: true, label: "Degenza media (giorni)"},
  color: {scheme: "BuPu"},
  marks: [
    Plot.barX(perDisciplinaDegenza, {
      y: "disciplina",
      x: "degenza_media",
      fill: "degenza_media",
      sort: {y: "-x"},
      tip: {format: {x: d => numFix(d, 1) + " giorni"}}
    }),
    Plot.text(perDisciplinaDegenza, {
      y: "disciplina",
      x: "degenza_media",
      text: d => numFix(d.degenza_media, 1),
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

## Dettaglio per regione e disciplina

```js
const { header, format } = tableFormat({
  regione: { label: "Regione", fmt: "string" },
  disciplina: { label: "Disciplina", fmt: "string" },
  posti_letto_degenza_ordinaria: { label: "Letti ordinari", fmt: "num" },
  posti_letto_utilizzati: { label: "Letti utilizzati", fmt: "num" },
  tasso_utilizzo: { label: "Tasso utilizzo %", fmt: "pct" },
  degenza_media_ordinaria: { label: "Degenza media (gg)", fmt: "num" },
});
```

```js
Inputs.table(data, {
  columns: ["regione", "disciplina", "posti_letto_degenza_ordinaria", "posti_letto_day_hospital", "posti_letto_utilizzati", "tasso_utilizzo", "degenza_media_ordinaria"],
  header,
  format,
  rows: 20,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: i dati si riferiscono al 2022. Variazioni annuali nella disponibilità di posti letto non sono catturate in questo dataset (vedi posti-letto-stabilimento per la serie storica).
- **Tasso di utilizzo**: il valore è calcolato a livello di reparto. Il tasso aggregato per disciplina può nascondere variazioni significative tra strutture della stessa disciplina.
- **Day Surgery**: i letti di Day Surgery sono dedicati a interventi con ricovero inferiore a 12 ore. Possono essere conteggiati anche in reparti con degenza ordinaria.

---

## Risorse

- [Ministero della Salute — Open Data Reparti di ricovero](https://www.salute.gov.it/portale/lea/dettaglioContenutiLea.jsp?lingua=italiano&id=5551&area=Lea&menu=vuoto)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/reparti_ricovero/2022/reparti_ricovero_2022_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/reparti-ricovero)

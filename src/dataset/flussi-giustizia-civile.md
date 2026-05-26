---
title: Flussi della giustizia civile
description: Sopravvenuti, definiti e pendenti per distretto — Ministero della Giustizia, 2014-2025
source: Ministero della Giustizia — Direzione Generale di Statistica
source_url: https://datiestatistiche.giustizia.it
period: "2014–2025"
last_modified: 2026-05-26
dataset_slug: civile_flussi
---

# Flussi della giustizia civile

Dati del Ministero della Giustizia sui flussi civili nei tribunali distrettuali italiani. Sopravvenuti, definiti e pendenti per distretto.

**Fonte**: Ministero della Giustizia · **Periodo**: 2014–2025

```js
const data = await FileAttachment("../data/civile-flussi.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(anni, {label: "Anno", value: anni[0]}));
```

```js
const filtered = data
  .filter(d => d.anno === annoSel)
  .sort((a, b) => b.pendenti_finali - a.pendenti_finali)
  .map(d => ({
    ...d,
    rapporto_def_sop: Math.round(d.definiti_totale / d.sopravvenuti * 100) / 100
  }));
```

```js
const totSopravvenuti = filtered.reduce((s, d) => s + d.sopravvenuti, 0);
const totDefiniti = filtered.reduce((s, d) => s + d.definiti_totale, 0);
const totPendenti = filtered.reduce((s, d) => s + d.pendenti_finali, 0);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Sopravvenuti</h3>
    <span class="big">${totSopravvenuti.toLocaleString("it-IT")}</span>
  </div>
  <div class="card">
    <h3>Definiti</h3>
    <span class="big">${totDefiniti.toLocaleString("it-IT")}</span>
  </div>
  <div class="card">
    <h3>Pendenti finali</h3>
    <span class="big">${totPendenti.toLocaleString("it-IT")}</span>
  </div>
</div>

---

## Pendenti per distretto

```js
Plot.plot({
  title: `Pendenti finali per distretto — ${annoSel}`,
  width: 800,
  height: 450,
  marginLeft: 140,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Reds"},
  marks: [
    Plot.barX(filtered, {
      y: "distretto",
      x: "pendenti_finali",
      fill: "pendenti_finali",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Rapporto definiti / sopravvenuti

```js
const rapportoFiltered = [...filtered].sort((a, b) => a.rapporto_def_sop - b.rapporto_def_sop);
```

```js
Plot.plot({
  title: `Rapporto definiti / sopravvenuti per distretto — ${annoSel}`,
  width: 800,
  height: 450,
  marginLeft: 140,
  y: {label: null, tickSize: 0},
  x: {grid: true},
  color: {scheme: "RdYlGn"},
  marks: [
    Plot.barX(rapportoFiltered, {
      y: "distretto",
      x: "rapporto_def_sop",
      fill: "rapporto_def_sop",
      sort: {y: "x"},
      tip: true
    }),
    Plot.ruleX([0]),
    Plot.ruleX([1], {stroke: "var(--theme-foreground-muted)", strokeDasharray: "4,4"})
  ]
})
```

> **Nota**: un rapporto > 1 significa che il distretto ha definito più cause di quante ne siano sopravvenute (smaltimento). &lt; 1 indica accumulo.

---

## Dettaglio per distretto

```js
Inputs.table(filtered, {
  columns: ["distretto", "sopravvenuti", "definiti_totale", "pendenti_finali", "rapporto_def_sop"],
  header: {distretto: "Distretto", sopravvenuti: "Sopravvenuti", definiti_totale: "Definiti", pendenti_finali: "Pendenti", rapporto_def_sop: "Rapporto D/S"},
  format: {sopravvenuti: x => x.toLocaleString("it-IT"), definiti_totale: x => x.toLocaleString("it-IT"), pendenti_finali: x => x.toLocaleString("it-IT")},
  rows: 30,
  width: "100%"
})
```

---

---

## Limiti

- **Copertura**: la serie storica 2014-2025 proviene da un unico file snapshot. Anni precedenti al 2014 non sono disponibili.
- **Rapporto D/S**: il rapporto definiti/sopravvenuti è un indicatore di smaltimento annuale. Un rapporto > 1 indica smaltimento parziale dell'arretrato, non necessariamente efficienza complessiva del sistema giudiziario.
- **Granularità**: i dati sono aggregati per distretto di Corte d'Appello. Non è possibile scendere al dettaglio di singoli tribunali con questo dataset.

---

## Risorse

- [Ministero della Giustizia (fonte originale)](https://datiestatistiche.giustizia.it)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/civile_flussi/2025/civile_flussi_2025_clean.parquet)
- [Analisi completa](https://github.com/dataciviclab/dataciviclab/tree/main/analisi/civile-flussi)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/civile-flussi)

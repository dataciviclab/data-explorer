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
import { num, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/civile-flussi.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
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
    <span class="big">${num(totSopravvenuti)}</span>
  </div>
  <div class="card">
    <h3>Definiti</h3>
    <span class="big">${num(totDefiniti)}</span>
  </div>
  <div class="card">
    <h3>Pendenti finali</h3>
    <span class="big">${num(totPendenti)}</span>
  </div>
</div>

---

## Pendenti per distretto e anno

La heatmap mostra in un colpo solo l'evoluzione dei pendenti in tutti i distretti dal 2014 al 2025. Ogni cella è un distretto in un anno: più scura è la cella, più alto è il carico pendente. Si vede immediatamente quali distretti hanno più arretrato e come cambia nel tempo.

```js
// Dati per heatmap: exclude rows with missing distretto, aggregate if needed
const heatmapData = data
  .filter(d => d.distretto)
  .map(d => ({...d, anno_str: String(d.anno)}))
  .sort((a, b) => a.anno - b.anno);
const distretti = [...new Set(heatmapData.map(d => d.distretto))].sort();
```

```js
Plot.plot({
  title: "Pendenti per distretto e anno — giustizia civile",
  width: 800,
  height: Math.max(400, distretti.length * 22 + 40),
  marginLeft: 140,
  marginTop: 30,
  x: {label: null, type: "band"},
  y: {label: null, tickSize: 0},
  color: {scheme: "Reds", legend: true, type: "symlog"},
  marks: [
    Plot.cell(heatmapData, {
      x: "anno_str",
      y: "distretto",
      fill: "pendenti_finali",
      tip: {format: {fill: d => num(d)}}
    }),
    Plot.text(heatmapData, {
      x: "anno_str",
      y: "distretto",
      text: d => (d.pendenti_finali / 1000).toFixed(0) + "k",
      fill: d => d.pendenti_finali > 80000 ? "white" : "var(--theme-foreground-muted)",
      fontSize: 9
    })
  ]
})
```

Un rapporto > 1 significa che il distretto ha definito più cause di quante ne siano sopravvenute (smaltimento). &lt; 1 indica accumulo. I dettagli per anno selezionato sono nei blocchi seguenti.

## Rapporto definiti / sopravvenuti

```js
const rapportoFiltered = [...filtered].sort((a, b) => a.rapporto_def_sop - b.rapporto_def_sop);
```

```js
Plot.plot({
  title: `Rapporto definiti / sopravvenuti per distretto — ${String(annoSel)}`,
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
const { header, format } = tableFormat({
  distretto: { label: "Distretto", fmt: "string" },
  sopravvenuti: { label: "Sopravvenuti", fmt: "num" },
  definiti_totale: { label: "Definiti", fmt: "num" },
  pendenti_finali: { label: "Pendenti", fmt: "num" },
  rapporto_def_sop: { label: "Rapporto D/S", fmt: "string" },
});
Inputs.table(filtered, {
  columns: ["distretto", "sopravvenuti", "definiti_totale", "pendenti_finali", "rapporto_def_sop"],
  header,
  format,
  rows: 30,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie storica 2014-2025 proviene da un unico file snapshot. Anni precedenti al 2014 non sono disponibili.
- **Rapporto D/S**: il rapporto definiti/sopravvenuti è un indicatore di smaltimento annuale. Un rapporto > 1 indica smaltimento parziale dell'arretrato, non necessariamente efficienza complessiva del sistema giudiziario.
- **Granularità**: i dati sono aggregati per distretto di Corte d'Appello. Non è possibile scendere al dettaglio di singoli tribunali con questo dataset.

---

## Risorse

- [Ministero della Giustizia (fonte originale)](https://datiestatistiche.giustizia.it)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/civile_flussi/2025/civile_flussi_2025_clean.parquet)
- [Analisi completa](https://github.com/dataciviclab/dataciviclab/tree/main/analisi/civile-flussi)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/civile-flussi)

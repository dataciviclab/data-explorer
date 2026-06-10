---
title: Alunni per corso ed età
description: Alunni delle scuole statali italiane per ordine, regione e anno scolastico — MIM, 2015-2025
source: MIM — Ministero dell'Istruzione e del Merito
source_url: https://dati.istruzione.it/opendata/
period: "2015–2025"
last_modified: 2026-05-31
dataset_slug: mim_alunni_corso_eta
---

# Alunni per corso ed età

Alunni delle scuole statali italiane per ordine scolastico (primaria, secondaria I e II grado), regione e anno scolastico. I dati mostrano l'evoluzione della popolazione scolastica e la distribuzione tra territori e gradi di istruzione.

**Fonte**: [MIM](https://dati.istruzione.it/opendata/) · **Periodo**: 2015–2025

```js
import { num, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/mim-alunni-corso-eta.json").json();
```

```js
// Estrai anno di inizio dall'anno scolastico "202324" → 2023
const conAnno = data.map(d => ({...d, anno: parseInt(d.anno_scolastico.slice(0, 4))}));
const anni = [...new Set(conAnno.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno scolastico", value: anni[0]}));
```

```js
const filtered = conAnno.filter(d => d.anno === annoSel);
const totale = d3.sum(filtered, d => d.alunni);
const nRegioni = new Set(filtered.map(d => d.regione)).size;
```

```js
// Per ordine scolastico
const perOrdine = Array.from(
  d3.rollup(filtered, v => d3.sum(v, d => d.alunni), d => d.ordine_scuola),
  ([ordine_scuola, alunni]) => ({ordine_scuola, alunni})
).sort((a, b) => b.alunni - a.alunni);

// Per regione
const perRegione = Array.from(
  d3.rollup(filtered, v => d3.sum(v, d => d.alunni), d => d.regione),
  ([regione, alunni]) => ({regione, alunni})
).sort((a, b) => b.alunni - a.alunni);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Alunni totali</h3>
    <span class="big">${(totale / 1e6).toFixed(1)} <small style="opacity:0.6">mln</small></span>
  </div>
  <div class="card">
    <h3>Ordini</h3>
    <span class="big">${perOrdine.length}</span>
  </div>
  <div class="card">
    <h3>Regioni</h3>
    <span class="big">${nRegioni}</span>
  </div>
</div>

---

## Alunni per ordine scolastico

Come si distribuiscono gli alunni tra primaria, secondaria di I grado e secondaria di II grado? La secondaria di II grado è l'ordine con più iscritti.

```js
const totOrd = d3.sum(perOrdine, d => d.alunni);
const ordineConPct = perOrdine.map(d => ({...d, pct: d.alunni / totOrd * 100}));
```

```js
Plot.plot({
  title: `Alunni per ordine scolastico — anno ${String(annoSel)}/${String(annoSel+1)}`,
  width: 800,
  height: 250,
  marginLeft: 180,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(ordineConPct, {
      y: "ordine_scuola",
      x: "alunni",
      fill: "ordine_scuola",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.text(ordineConPct, {
      y: "ordine_scuola",
      x: "alunni",
      text: d => `${d.pct.toFixed(1)}%`,
      dx: 6,
      textAnchor: "start",
      fill: "var(--theme-foreground-muted)",
      fontSize: 12
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Alunni per regione

Quali regioni hanno più studenti? La classifica segue la popolazione residente, ma il dato per ordine scolastico — nella tabella sottostante — mostra differenze nella composizione del sistema scolastico locale.

```js
Plot.plot({
  title: `Alunni per regione — anno ${String(annoSel)}/${String(annoSel+1)}`,
  width: 800,
  height: 450,
  marginLeft: 120,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Blues"},
  marks: [
    Plot.barX(perRegione, {
      y: "regione",
      x: "alunni",
      fill: "alunni",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Dettaglio per regione e ordine

```js
const pivot = Array.from(
  d3.rollup(filtered, v => d3.sum(v, d => d.alunni), d => d.regione, d => d.ordine_scuola),
  ([regione, ordini]) => ({regione, ...Object.fromEntries(ordini)})
).sort((a, b) => {
  const totA = (a["SCUOLA PRIMARIA"] || 0) + (a["SCUOLA SECONDARIA I GRADO"] || 0) + (a["SCUOLA SECONDARIA II GRADO"] || 0);
  const totB = (b["SCUOLA PRIMARIA"] || 0) + (b["SCUOLA SECONDARIA I GRADO"] || 0) + (b["SCUOLA SECONDARIA II GRADO"] || 0);
  return totB - totA;
});
```

```js
const { header, format } = tableFormat({
  regione: { label: "Regione", fmt: "string" },
  "SCUOLA PRIMARIA": { label: "Primaria", fmt: "num" },
  "SCUOLA SECONDARIA I GRADO": { label: "Secondaria I", fmt: "num" },
  "SCUOLA SECONDARIA II GRADO": { label: "Secondaria II", fmt: "num" },
});
Inputs.table(pivot, {
  columns: ["regione", "SCUOLA PRIMARIA", "SCUOLA SECONDARIA I GRADO", "SCUOLA SECONDARIA II GRADO"],
  header,
  format,
  rows: 25,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie copre gli anni scolastici dal 2015/16 al 2024/25. Dati precedenti non sono disponibili in questo dataset.
- **Scuole statali**: i dati si riferiscono alle sole scuole statali. Non includono scuole paritarie, private o regionali.
- **Anno scolastico**: l'anno mostrato è l'anno di inizio del ciclo scolastico (es. 2023 = anno scolastico 2023/24).
- **Granularità**: i dati sono aggregati per regione e ordine scolastico. La disaggregazione per singola scuola è disponibile nel dataset originale.

---

## Risorse

- [MIM — Dati istruzione](https://dati.istruzione.it/opendata/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/mim_alunni_corso_eta/2025/mim_alunni_corso_eta_2025_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/mim-alunni-corso-eta)

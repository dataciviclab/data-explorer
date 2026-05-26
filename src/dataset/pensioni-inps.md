---
title: Pensioni INPS
description: Numero di pensioni INPS per gestione previdenziale, area geografica e anno, 2020-2024
source: INPS — Open Data
source_url: https://www.inps.it/open-data
period: "2020–2024"
last_modified: 2026-05-26
dataset_slug: inps_pensioni_trimestrale
---

# Pensioni INPS

Numero di pensioni INPS per gestione previdenziale, regione, classe d'età e classe di importo, con cadenza trimestrale.

**Fonte**: INPS · **Periodo**: 2020–2024

```js
const data = await FileAttachment("../data/inps-pensioni.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(anni, {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel);
```

```js
const perGestione = Array.from(d3.rollup(filtered, v => d3.sum(v, d => d.numero_pensioni), d => d.gestione), ([gestione, numero_pensioni]) => ({gestione, numero_pensioni})).sort((a,b) => b.numero_pensioni - a.numero_pensioni);
const perArea = Array.from(d3.rollup(filtered, v => d3.sum(v, d => d.numero_pensioni), d => d.area_geografica), ([area_geografica, numero_pensioni]) => ({area_geografica, numero_pensioni})).sort((a,b) => b.numero_pensioni - a.numero_pensioni);
```

```js
const totale = d3.sum(filtered, d => d.numero_pensioni);
```

<div class="grid grid-cols-2">
  <div class="card">
    <h3>Pensioni totali</h3>
    <span class="big">${(totale / 1e6).toFixed(1)} <small style="opacity:0.6">mln</small></span>
  </div>
  <div class="card">
    <h3>Gestioni</h3>
    <span class="big">${perGestione.length}</span>
  </div>
</div>

---

## Per gestione previdenziale

```js
Plot.plot({
  title: `Pensioni per gestione — ${annoSel}`,
  width: 800,
  height: 350,
  marginLeft: 200,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(perGestione, {
      y: "gestione",
      x: "numero_pensioni",
      fill: "gestione",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Per area geografica

```js
Plot.plot({
  title: `Pensioni per area geografica — ${annoSel}`,
  width: 800,
  height: 250,
  marginLeft: 120,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Blues"},
  marks: [
    Plot.barX(perArea, {
      y: "area_geografica",
      x: "numero_pensioni",
      fill: "numero_pensioni",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Dettaglio gestioni

```js
Inputs.table(perGestione, {
  columns: ["gestione", "numero_pensioni"],
  header: {gestione: "Gestione", numero_pensioni: "Pensioni"},
  format: {numero_pensioni: x => `${(x / 1e6).toFixed(2)} mln`},
  rows: 20,
  width: "100%"
})
```

---

---

## Limiti

- **Periodo**: il dato si riferisce al 2024 (ultimo anno disponibile). I dati precedenti (2020-2023) sono disponibili ma non ancora caricati in questa pagina.
- **Cadenza trimestrale**: i dati sono pubblicati con cadenza trimestrale da INPS. Il totale mostrato è la somma dei trimestri dell'anno. Il numero di pensioni è uno **stock** (pensioni in essere alla fine del trimestre), non un flusso di nuove decorrenze: la somma annuale non va dunque interpretata come "nuove pensioni erogate nell'anno".
- **Gestioni**: la disaggregazione per gestione segue la classificazione INPS. Alcune gestioni minori potrebbero essere aggregate in voci residuali.
- **Aggiornamento**: il dataset viene aggiornato con cadenza trimestrale. L'ultimo aggiornamento disponibile è il quarto trimestre 2024.

---

## Risorse

- [INPS Open Data (fonte originale)](https://www.inps.it/open-data)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/inps_pensioni_trimestrale/2024/inps_pensioni_trimestrale_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/inps-pensioni)

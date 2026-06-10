---
title: Indice prezzi abitazioni (IPAB) per area
description: Dati ISTAT sull'indice dei prezzi delle abitazioni (IPAB) per area geografica e trimestre, 2010-2025
source: ISTAT
source_url: https://www.istat.it/it/archivio/16773
period: "2010–2025"
last_modified: 2026-05-26
dataset_slug: istat_ipab_aree
---

# Indice prezzi abitazioni (IPAB) per area

L'indice dei prezzi delle abitazioni (IPAB) misura l'evoluzione dei prezzi delle abitazioni sul mercato italiano, disaggregato per macro-area e città (Milano, Roma, Torino).

**Fonte**: ISTAT · **Periodo**: 2010–2025 · Dati trimestrali

```js
import { numFix } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/istat-ipab-aree.json").json();
```

```js
const areeMacro = ["Nord-ovest", "Nord-est", "Centro (I)", "Mezzogiorno", "Italy"];
const citta = ["Milano", "Roma", "Torino"];

const macroData = data.filter(d => areeMacro.includes(d.area));
const cittaData = data.filter(d => citta.includes(d.area));

const ultimoTrimestre = [...new Set(data.map(d => d.trimestre))].sort().pop();
const ultimiValori = data.filter(d => d.trimestre === ultimoTrimestre);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Italia — ${ultimoTrimestre}</h3>
    <span class="big">${ultimiValori.find(d => d.area === "Italy")?.indice_prezzi?.toFixed(1)}</span>
  </div>
  <div class="card">
    <h3>Milano</h3>
    <span class="big">${ultimiValori.find(d => d.area === "Milano")?.indice_prezzi?.toFixed(1)}</span>
  </div>
  <div class="card">
    <h3>Mezzogiorno</h3>
    <span class="big">${ultimiValori.find(d => d.area === "Mezzogiorno")?.indice_prezzi?.toFixed(1)}</span>
  </div>
</div>

---

## Andamento prezzi per macro-area

Il divario Nord-Sud emerge chiaramente: mentre il Nord-ovest e il Nord-est superano la media nazionale, il Mezzogiorno resta stabilmente sotto. Milano viaggia ben distante da tutte.

```js
Plot.plot({
  title: "Indice IPAB per macro-area — 2010–2025",
  width: 800,
  height: 400,
  y: {grid: true, label: "indice (base 2010=100)"},
  color: {legend: true},
  marks: [
    Plot.line(macroData, {
      x: "trimestre",
      y: "indice_prezzi",
      z: "area",
      stroke: "area",
      tip: true
    }),
    Plot.ruleY([100])
  ]
})
```

---

## Prezzi nelle grandi città

Milano si distacca nettamente da Roma e Torino, con un indice che sfiora 180 — quasi l'80% in più rispetto al 2010.

```js
Plot.plot({
  title: "Indice IPAB — Milano, Roma, Torino",
  width: 800,
  height: 350,
  y: {grid: true, label: "indice (base 2010=100)"},
  color: {legend: true, scheme: "Set1"},
  marks: [
    Plot.line(cittaData, {
      x: "trimestre",
      y: "indice_prezzi",
      z: "area",
      stroke: "area",
      tip: true
    }),
    Plot.ruleY([100])
  ]
})
```

---

## Ultimo trimestre — tutte le aree

```js
Inputs.table(ultimiValori, {
  columns: ["area", "indice_prezzi"],
  header: {area: "Area", indice_prezzi: "Indice prezzi"},
  format: {indice_prezzi: x => numFix(x, 1)},
  sort: "area",
  rows: 10,
  width: "100%"
})
```

---

---

## Limiti

- **Copertura**: la serie copre il periodo 2010-2025. Dati precedenti non sono disponibili in questo dataset.
- **Indice base**: l'indice è calcolato con base 2010=100. Le variazioni percentuali sono relative al 2010, non all'anno precedente.
- **Tipologia**: i dati si riferiscono a abitazioni esistenti (EXST_DW). Non include abitazioni nuove o di nuova costruzione.
- **Aree**: la disaggregazione include macro-aree ISTAT e tre città (Milano, Roma, Torino). Non sono disponibili dati comunali o provinciali.

---

## Risorse

- [ISTAT — IPAB (fonte originale)](https://www.istat.it/it/archivio/16773)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/istat_ipab_aree/2024/istat_ipab_aree_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/istat-ipab-aree)

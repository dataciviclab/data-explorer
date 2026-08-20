---
title: Indice prezzi abitazioni (IPAB) per area
description: Dati ISTAT sull'indice dei prezzi delle abitazioni (IPAB) per area geografica e trimestre, 2010-2025
source: ISTAT
source_url: https://www.istat.it/it/archivio/16773
period: "2010–2025"
last_modified: 2026-05-26
dataset_slug: istat_ipab_aree
data_driven: true
---

# Indice prezzi abitazioni (IPAB) per area — Milano accelera, il Mezzogiorno rallenta?

```js
import { numFix, pct } from "../import/format-utils.js";
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

const indiceItaly = ultimiValori.find(d => d.area === "Italy")?.indice_prezzi;
const indiceMilano = ultimiValori.find(d => d.area === "Milano")?.indice_prezzi;
const indiceMezzo = ultimiValori.find(d => d.area === "Mezzogiorno")?.indice_prezzi;
const divarioMilanoMezzo = (indiceMilano && indiceMezzo) ? indiceMilano - indiceMezzo : null;
```

**All'${ultimoTrimestre} l'indice IPAB per l'Italia è a ${indiceItaly?.toFixed(1) ?? "—"} (base 2010=100), ma Milano sfiora i ${indiceMilano?.toFixed(1) ?? "—"} — oltre il 60% in più del Mezzogiorno (${indiceMezzo?.toFixed(1) ?? "—"}). Il divario tra le due Italie immobiliari è di ${divarioMilanoMezzo?.toFixed(0) ?? "—"} punti.**

L'indice dei prezzi delle abitazioni (IPAB) misura l'evoluzione dei prezzi delle abitazioni sul mercato italiano, disaggregato per macro-area e città. Base 2010=100: un valore a 150 significa che i prezzi sono cresciuti del 50% rispetto al 2010.

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Italia — ${ultimoTrimestre}</h3>
    <span class="big">${indiceItaly?.toFixed(1) ?? "—"}</span>
  </div>
  <div class="card">
    <h3>Milano</h3>
    <span class="big">${indiceMilano?.toFixed(1) ?? "—"}</span>
  </div>
  <div class="card">
    <h3>Mezzogiorno</h3>
    <span class="big">${indiceMezzo?.toFixed(1) ?? "—"}</span>
  </div>
</div>

---

## 1. Come si muovono i prezzi tra le macro-aree?

Il divario Nord-Sud emerge chiaramente: il Nord-ovest e il Nord-est superano la media nazionale, il Mezzogiorno resta stabilmente sotto. La convergenza non è in vista.

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

> **Nota**: la linea a 100 segna il livello del 2010. Ogni curva sopra la linea indica una crescita dei prezzi rispetto a quell'anno.

---

## 2. Cosa succede nelle grandi città?

Milano si distacca nettamente da Roma e Torino, con un indice che si avvicina a 180. Le due città mostrano traiettorie simili ma con un divario crescente rispetto alla capitale.

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

## Dettaglio — ultimo trimestre

<small>Valori dell'indice per tutte le aree nell'ultimo trimestre disponibile.</small>

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

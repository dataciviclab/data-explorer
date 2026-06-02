---
title: Densità abitativa
description: Indice di densità abitativa per titolo di godimento — ISTAT, 2004-2025
source: ISTAT — Dataflow 33_179
source_url: https://esploradati.istat.it/
period: "2004–2025"
last_modified: 2026-06-02
dataset_slug: istat_housing_crowding
---

# Densità abitativa

Indice di densità abitativa (componenti per 100 mq) per titolo di godimento. I dati mostrano come evolve l'affollamento abitativo in Italia e le differenze tra proprietà e affitto.

**Fonte**: [ISTAT](https://esploradati.istat.it/) · **Periodo**: 2004–2025

```js
const data = await FileAttachment("../data/housing-crowding.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel);
const totale = d3.mean(filtered, d => d.componenti_per_100mq);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Densità media</h3>
    <span class="big">${totale.toFixed(1)}</span>
    <small style="opacity:0.6">componenti/100mq</small>
  </div>
  <div class="card">
    <h3>Anni</h3>
    <span class="big">${anni.length}</span>
  </div>
  <div class="card">
    <h3>Min – Max</h3>
    <span class="big">${d3.min(filtered, d => d.componenti_per_100mq).toFixed(1)} – ${d3.max(filtered, d => d.componenti_per_100mq).toFixed(1)}</span>
  </div>
</div>

---

## Densità per titolo di godimento

Chi vive in case più affollate? Chi affitta ha una densità abitativa maggiore rispetto a chi possiede l'abitazione.

```js
Plot.plot({
  title: `Componenti per 100 mq per titolo di godimento — ${String(annoSel)}`,
  width: 800,
  height: 250,
  marginLeft: 120,
  y: {label: null, tickSize: 0},
  x: {grid: true},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(filtered, {
      y: "titolo_godimento",
      x: "componenti_per_100mq",
      fill: "titolo_godimento",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Evoluzione 2004-2025

Come cambia la densità abitativa nel tempo? Il divario tra proprietà e affitto si è ridotto negli ultimi vent'anni.

```js
const trend = data.sort((a, b) => a.anno - b.anno);
```

```js
Plot.plot({
  title: "Componenti per 100 mq — tendenza 2004-2025",
  width: 800,
  height: 350,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, label: "Componenti per 100 mq"},
  color: {legend: true},
  marks: [
    Plot.line(trend, {
      x: "anno",
      y: "componenti_per_100mq",
      z: "titolo_godimento",
      stroke: "titolo_godimento",
      tip: true
    }),
    Plot.dot(trend, {
      x: "anno",
      y: "componenti_per_100mq",
      z: "titolo_godimento",
      fill: "titolo_godimento",
      r: 1.5
    })
  ]
})
```

---

## Dettaglio per anno

```js
Inputs.table(trend, {
  columns: ["anno", "titolo_godimento", "componenti_per_100mq"],
  header: {anno: "Anno", titolo_godimento: "Titolo godimento", componenti_per_100mq: "Comp./100mq"},
  format: {componenti_per_100mq: x => x.toFixed(2)},
  rows: 25,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie copre il periodo 2004-2025. Dati precedenti non sono disponibili.
- **Indice**: la densità abitativa misura i componenti del nucleo familiare ogni 100 mq di abitazione. Valori più alti indicano maggiore affollamento.
- **Nazionale**: i dati sono a livello nazionale. Non è disponibile la disaggregazione regionale in questo dataset.
- **Fonte**: i dati provengono dall'indagine ISTAT sulle condizioni abitative (SDMX 33_179).

---

## Risorse

- [ISTAT — Esplora dati](https://esploradati.istat.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/istat_housing_crowding/2024/istat_housing_crowding_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/istat-housing-crowding)

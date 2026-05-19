---
title: Capacità rinnovabile per regione
description: Dati Terna sulla capacità di generazione rinnovabile installata per regione e fonte
---

# Capacità rinnovabile per regione

Dati Terna sulla capacità di generazione rinnovabile installata per regione e fonte (potenza netta).

**Fonte**: Terna · **Periodo**: 2023–2024

```js
const data = await FileAttachment("../data/terna-fonti.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(anni, {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel);
```

```js
const totNazionale = d3.sum(filtered, d => d.potenza_mw);
const fontiNazionali = Array.from(d3.rollup(filtered, v => d3.sum(v, d => d.potenza_mw), d => d.fonti), ([fonti, potenza_mw]) => ({fonti, potenza_mw})).sort((a,b) => b.potenza_mw - a.potenza_mw);
const nRegioni = new Set(filtered.map(d => d.regione)).size;
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Potenza totale</h3>
    <span class="big">${Math.round(totNazionale).toLocaleString("it-IT")} <small style="opacity:0.6">MW</small></span>
  </div>
  <div class="card">
    <h3>Fonti</h3>
    <span class="big">${fontiNazionali.length}</span>
  </div>
  <div class="card">
    <h3>Regioni</h3>
    <span class="big">${nRegioni}</span>
  </div>
</div>

---

## Potenza per fonte

```js
Plot.plot({
  title: `Capacità rinnovabile per fonte — ${annoSel}`,
  width: 800,
  height: 300,
  marginLeft: 140,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(fontiNazionali, {
      y: "fonti",
      x: "potenza_mw",
      fill: "fonti",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Ripartizione regionale

```js
const regioniTot = Array.from(d3.rollup(filtered, v => d3.sum(v, d => d.potenza_mw), d => d.regione), ([regione, potenza_mw]) => ({regione, potenza_mw})).sort((a,b) => b.potenza_mw - a.potenza_mw);
```

```js
Plot.plot({
  title: `Capacità rinnovabile per regione — ${annoSel}`,
  width: 800,
  height: 400,
  marginLeft: 120,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Greens"},
  marks: [
    Plot.barX(regioniTot, {
      y: "regione",
      x: "potenza_mw",
      fill: "potenza_mw",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Dettaglio per regione e fonte

```js
Inputs.table(filtered, {
  columns: ["regione", "fonti", "potenza_mw"],
  header: {regione: "Regione", fonti: "Fonte", potenza_mw: "Potenza (MW)"},
  format: {potenza_mw: x => `${Math.round(x).toLocaleString("it-IT")} MW`},
  rows: 30,
  width: "100%"
})
```

---

## Risorse

- [Terna](https://www.terna.it/)
- [Analisi](https://github.com/dataciviclab/dataciviclab/tree/main/analisi/terna-electricity-by-source)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/terna-capacita-rinnovabile)

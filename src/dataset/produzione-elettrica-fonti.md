---
title: Produzione elettrica per fonte
description: Produzione di energia elettrica in GWh per fonte, regione e tipo — Terna, 2023-2024
source: Terna S.p.A. — dati.terna.it
source_url: https://www.terna.it/
period: "2023–2024"
last_modified: 2026-05-26
dataset_slug: terna_electricity_by_source
---

# Produzione elettrica per fonte

Produzione netta di energia elettrica in GWh per fonte e regione. I dati mostrano come cambia il mix di generazione elettrica tra territori e fonti.

**Fonte**: [Terna](https://www.terna.it/) · **Periodo**: 2023–2024

```js
const data = await FileAttachment("../data/produzione-elettrica-fonti.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel);
```

```js
const perTipo = Array.from(
  d3.rollup(filtered, v => d3.sum(v, d => d.produzione_gwh), d => d.fonte),
  ([fonte, produzione_gwh]) => ({fonte, produzione_gwh})
).sort((a, b) => b.produzione_gwh - a.produzione_gwh);

const perRegione = Array.from(
  d3.rollup(filtered, v => d3.sum(v, d => d.produzione_gwh), d => d.regione),
  ([regione, produzione_gwh]) => ({regione, produzione_gwh})
).sort((a, b) => b.produzione_gwh - a.produzione_gwh);
```

```js
const totaleGWh = d3.sum(perTipo, d => d.produzione_gwh);
const nTipi = perTipo.length;
const nRegioni = perRegione.length;
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Produzione totale</h3>
    <span class="big">${Math.round(totaleGWh).toLocaleString("it-IT")} <small style="opacity:0.6">GWh</small></span>
  </div>
  <div class="card">
    <h3>Fonti</h3>
    <span class="big">${nTipi}</span>
  </div>
  <div class="card">
    <h3>Regioni</h3>
    <span class="big">${nRegioni}</span>
  </div>
</div>

---

## Produzione netta per fonte

Come si distribuisce la produzione netta di energia elettrica tra le diverse fonti? Il termoelettrico e l'idroelettrico dominano il mix nazionale, mentre il fotovoltaico è in crescita progressiva.

```js
const totMix = d3.sum(perTipo, d => d.produzione_gwh);
const tipoConPct = perTipo.map(d => ({...d, pct: d.produzione_gwh / totMix * 100}));
```

```js
Plot.plot({
  title: `Produzione netta per fonte — ${String(annoSel)}`,
  width: 800,
  height: 300,
  marginLeft: 160,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(tipoConPct, {
      y: "fonte",
      x: "produzione_gwh",
      fill: "fonte",
      sort: {y: "-x"},
      tip: {format: {x: d => `${(d / 1000).toFixed(0)} TWh`}}
    }),
    Plot.text(tipoConPct, {
      y: "fonte",
      x: "produzione_gwh",
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

## Produzione per regione

Quali regioni producono più energia elettrica? La classifica è dominata dalle regioni del Nord, dove si concentrano buona parte della produzione termoelettrica e idroelettrica.

```js
Plot.plot({
  title: `Produzione elettrica per regione — ${String(annoSel)}`,
  width: 800,
  height: 450,
  marginLeft: 120,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Blues"},
  marks: [
    Plot.barX(perRegione, {
      y: "regione",
      x: "produzione_gwh",
      fill: "produzione_gwh",
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
  columns: ["regione", "fonte", "produzione_gwh"],
  header: {regione: "Regione", fonte: "Fonte", produzione_gwh: "Produzione (GWh)"},
  format: {produzione_gwh: x => `${Math.round(x).toLocaleString("it-IT")} GWh`},
  rows: 30,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: il dataset copre il biennio 2023-2024. Non sono disponibili dati precedenti in questo dataset.
- **Produzione**: i dati si riferiscono alla produzione effettiva di energia elettrica (GWh), non alla capacità installata (MW). Per la capacità installata, vedi il dataset [Capacità rinnovabile](/dataset/capacita-rinnovabile).
- **Granularità**: la disaggregazione per provincia è disponibile nel dato originale ma non in questa pagina.

---

## Risorse

- [Terna (fonte originale)](https://www.terna.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/terna_electricity_by_source/2024/terna_electricity_by_source_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/terna-electricity-by-source)
<!-- - [Analisi](/analisi/terna-electricity-by-source) -->

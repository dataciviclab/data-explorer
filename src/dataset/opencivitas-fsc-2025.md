---
title: Fondo di Solidarietà Comunale 2025
description: FSC 2025 — capacità fiscale, fondo perequativo e dotazione finale per comune — OpenCivitas
source: OpenCivitas / Sogei
source_url: https://www.opencivitas.it/
period: "2025"
last_modified: 2026-05-28
dataset_slug: opencivitas_fsc_2025_rso
---

# Fondo di Solidarietà Comunale 2025

Fondo di Solidarietà Comunale (FSC) 2025 per comune: capacità fiscale, fondo perequativo, dotazione finale e risorse storiche. I dati mostrano come si distribuiscono le risorse tra i comuni italiani e quali territori contribuiscono o ricevono dalla perequazione.

**Fonte**: [OpenCivitas](https://www.opencivitas.it/) · **Periodo**: 2025

```js
import * as topojson from "npm:topojson-client";

const regTopo = await FileAttachment("../data/regioni.topojson").json();
const regioniGeo = topojson.feature(regTopo, regTopo.objects.regioni);
const confiniReg = topojson.mesh(regTopo, regTopo.objects.regioni, (a, b) => a !== b);
```

```js
const data = await FileAttachment("../data/opencivitas-fsc-2025.json").json();
```

```js
const totaleFsc = d3.sum(data, d => d.dotazione_finale_fsc);
const totalePerequativo = d3.sum(data, d => d.fondo_perequativo);
const totalePopolazione = d3.sum(data, d => d.popolazione);
const nComuni = data.length;
const nRegioni = new Set(data.map(d => d.regione)).size;
```

```js
const perRegione = Array.from(
  d3.rollup(data, v => ({
    fsc: d3.sum(v, d => d.dotazione_finale_fsc),
    perequativo: d3.sum(v, d => d.fondo_perequativo),
    capacita: d3.sum(v, d => d.capacita_fiscale),
    comuni: v.length,
    popolazione: d3.sum(v, d => d.popolazione)
  }), d => d.regione),
  ([regione, v]) => ({regione, ...v})
).sort((a, b) => b.fsc - a.fsc);
```

```js
// Contribuenti netti (fondo_perequativo negativo) vs beneficiari
const contribNetti = data.filter(d => d.fondo_perequativo < 0).length;
const percContribNetti = (contribNetti / nComuni * 100).toFixed(1);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Dotazione FSC</h3>
    <span class="big">€ ${(totaleFsc / 1e9).toFixed(1)} <small style="opacity:0.6">mld</small></span>
  </div>
  <div class="card">
    <h3>Comuni</h3>
    <span class="big">${nComuni.toLocaleString("it-IT")}</span>
  </div>
  <div class="card">
    <h3>Popolazione</h3>
    <span class="big">${(totalePopolazione / 1e6).toFixed(1)} <small style="opacity:0.6">mln</small></span>
  </div>
</div>

---

## Dotazione FSC per regione

```js
function normalizzaReg(nome) {
  return nome.toUpperCase().replace(/ \/ /g, '/').replace(/ /g, '-');
}

const fscLookup = new Map(perRegione.map(d => [normalizzaReg(d.regione), d.fsc]));
```

```js
Plot.plot({
  title: "Dotazione FSC per regione — 2025",
  projection: {type: "mercator", domain: regioniGeo},
  width: 800,
  height: 600,
  color: {scheme: "Blues", legend: true, label: "Dotazione FSC (€)", type: "quantile"},
  marks: [
    // RSO: colore per dotazione FSC
    Plot.geo(regioniGeo, {
      filter: d => fscLookup.has(normalizzaReg(d.properties.DEN_REG)),
      fill: d => fscLookup.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#888",
      strokeWidth: 0.25,
      tip: true
    }),
    // Regioni a statuto speciale: grigio
    Plot.geo(regioniGeo, {
      filter: d => !fscLookup.has(normalizzaReg(d.properties.DEN_REG)),
      fill: "#e0e0e0",
      stroke: "#888",
      strokeWidth: 0.25,
      tip: {format: {fill: () => "Dato non disponibile (RSO)"}}
    }),
    Plot.geo(confiniReg, {
      stroke: "#888",
      strokeWidth: 0.7
    })
  ]
})
```
> Il FSC copre solo le Regioni a Statuto Ordinario (RSO). Le regioni in grigio (Sicilia, Sardegna, Friuli-Venezia Giulia, Trentino-Alto Adige e Valle d'Aosta) non sono incluse nel dataset.

---

## Contribuenti netti vs beneficiari

Il fondo perequativo è negativo per i comuni che contribuiscono (capacità fiscale maggiore del fabbisogno) e positivo per chi riceve. Il ${percContribNetti}% dei comuni è contribuente netto.

```js
const perComune = data
  .map(d => ({...d, fsc_procapite: d.dotazione_finale_fsc / d.popolazione}))
  .sort((a, b) => b.fondo_perequativo - a.fondo_perequativo);
// Top 10 e bottom 10
const top10 = perComune.slice(0, 10);
const bottom10 = perComune.slice(-10).reverse();
```

```js
Plot.plot({
  title: "Fondo perequativo pro capite — top 10 comuni beneficiari e contribuenti",
  width: 800,
  height: 350,
  marginLeft: 200,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "PiYG"},
  marks: [
    Plot.barX([...top10, ...bottom10], {
      y: "comune",
      x: "fondo_perequativo",
      fill: d => d.fondo_perequativo > 0 ? "beneficiario" : "contribuente",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Dettaglio regioni

```js
Inputs.table(perRegione, {
  columns: ["regione", "comuni", "popolazione", "fsc", "perequativo", "capacita"],
  header: {regione: "Regione", comuni: "Comuni", popolazione: "Popolazione", fsc: "Dotazione FSC (€)", perequativo: "Perequativo (€)", capacita: "Capacità fiscale (€)"},
  format: {
    popolazione: x => Math.round(x).toLocaleString("it-IT"),
    fsc: x => `€ ${(x / 1e6).toFixed(0)} mln`,
    perequativo: x => `€ ${(x / 1e6).toFixed(0)} mln`,
    capacita: x => `€ ${(x / 1e6).toFixed(0)} mln`
  },
  rows: 25,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: il dataset copre il solo 2025. Non sono disponibili anni precedenti in questo dataset.
- **Comuni RSO**: i dati si riferiscono ai comuni delle Regioni a Statuto Ordinario. Non include comuni delle Regioni a Statuto Speciale.
- **Perequativo**: il fondo perequativo con segno negativo indica un comune contribuente netto (la sua capacità fiscale supera il fabbisogno standard).
- **Fonte**: i dati provengono da OpenCivitas / Sogei. La metodologia di calcolo del FSC è definita dalla legge di bilancio annuale.

---

## Risorse

- [OpenCivitas (fonte originale)](https://www.opencivitas.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/opencivitas_fsc_2025_rso/2025/opencivitas_fsc_2025_rso_2025_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/opencivitas-fsc-2025-rso)

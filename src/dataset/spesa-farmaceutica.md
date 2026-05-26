---
title: Spesa farmaceutica convenzionata
description: Dati AIFA su spesa e consumo farmaceutico convenzionato SSN per regione e classe terapeutica ATC, 2018-2024
source: AIFA — Agenzia Italiana del Farmaco
source_url: https://www.aifa.gov.it/open-data
period: "2018–2024"
last_modified: 2026-05-26
dataset_slug: aifa_spesa_consumo
---

# Spesa farmaceutica convenzionata

Spesa e consumo della farmaceutica convenzionata SSN, disaggregati per regione, mese e classe terapeutica ATC. I dati mostrano quali categorie terapeutiche assorbono più risorse e come varia la spesa tra territori.

**Fonte**: AIFA · **Periodo**: 2018–2024

```js
const data = await FileAttachment("../data/aifa-spesa.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel);
```

```js
const perRegione = Array.from(d3.rollup(filtered, v => ({
  spesa: d3.sum(v, d => d.spesa_convenzionata),
  confezioni: d3.sum(v, d => d.numero_confezioni_convenzionata)
}), d => d.regione), ([regione, v]) => ({regione, ...v})).sort((a,b) => b.spesa - a.spesa);
```

```js
const totaleSpesa = d3.sum(perRegione, d => d.spesa);
const totaleConfezioni = d3.sum(perRegione, d => d.confezioni);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Spesa totale</h3>
    <span class="big">€ ${(totaleSpesa / 1e6).toFixed(1)} <small style="opacity:0.6">mln</small></span>
  </div>
  <div class="card">
    <h3>Confezioni</h3>
    <span class="big">${(totaleConfezioni / 1e6).toFixed(1)} <small style="opacity:0.6">mln</small></span>
  </div>
  <div class="card">
    <h3>Regioni</h3>
    <span class="big">${perRegione.length}</span>
  </div>
</div>

---

## Spesa per classe terapeutica

Quali categorie di farmaci assorbono più risorse del SSN? Il sistema cardiovascolare, l'apparato gastrointestinale e il sistema nervoso guidano la spesa farmaceutica convenzionata.

```js
const perAtc1 = Array.from(
  d3.rollup(filtered, v => d3.sum(v, d => d.spesa_convenzionata), d => d.descrizione_atc1),
  ([descrizione_atc1, spesa]) => ({descrizione_atc1, spesa})
).sort((a, b) => b.spesa - a.spesa);

const totAtc = d3.sum(perAtc1, d => d.spesa);
const atcConPct = perAtc1.map(d => ({...d, pct: d.spesa / totAtc * 100}));
```

```js
Plot.plot({
  title: `Spesa per classe terapeutica ATC1 — ${annoSel}`,
  width: 800,
  height: 350,
  marginLeft: 200,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(atcConPct, {
      y: "descrizione_atc1",
      x: "spesa",
      fill: "descrizione_atc1",
      sort: {y: "-x"},
      tip: {format: {x: d => `€ ${(d / 1e6).toFixed(0)} mln`}}
    }),
    Plot.text(atcConPct, {
      y: "descrizione_atc1",
      x: "spesa",
      text: d => `${d.pct.toFixed(1)}%`,
      dx: 6,
      textAnchor: "start",
      fill: "var(--theme-foreground-muted)",
      fontSize: 11
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Spesa per regione

Come si distribuisce la spesa farmaceutica tra le regioni? Le regioni più popolose hanno una spesa maggiore in valore assoluto, ma la spesa pro capite — non ancora presente in questa pagina — darebbe un quadro più preciso.

```js
Plot.plot({
  title: `Spesa convenzionata per regione — ${annoSel}`,
  width: 800,
  height: 400,
  marginLeft: 120,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Oranges"},
  marks: [
    Plot.barX(perRegione, {
      y: "regione",
      x: "spesa",
      fill: "spesa",
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
  columns: ["regione", "spesa", "confezioni"],
  header: {regione: "Regione", spesa: "Spesa (€)", confezioni: "Confezioni"},
  format: {spesa: x => `€ ${Math.round(x).toLocaleString("it-IT")}`, confezioni: x => Math.round(x).toLocaleString("it-IT")},
  rows: 25,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie storica copre 2018-2024. Dati precedenti non sono disponibili in questo dataset.
- **Convenzionata**: i dati si riferiscono alla sola farmaceutica convenzionata SSN (farmaci rimborsati dal Servizio Sanitario Nazionale). Non include la spesa farmaceutica privata o ospedaliera.
- **Classificazione ATC**: la disaggregazione per classe terapeutica segue la classificazione Anatomico Terapeutica Chimica (ATC) livello 1. Classificazioni più granulari (ATC2, ATC3) sono disponibili nel dato originale ma non in questa pagina.

---

## Risorse

- [AIFA — Open Data (fonte originale)](https://www.aifa.gov.it/open-data)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/aifa_spesa_consumo/2024/aifa_spesa_consumo_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/aifa-spesa-consumo)

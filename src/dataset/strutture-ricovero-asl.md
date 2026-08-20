---
title: Strutture di ricovero del SSN
description: Ospedali pubblici, IRCCS e case di cura del Servizio Sanitario Nazionale — personale, posti letto, ricoveri per struttura, 2022
source: Ministero della Salute
source_url: https://www.salute.gov.it/portale/lea/dettaglioContenutiLea.jsp?lingua=italiano&id=5551&area=Lea&menu=vuoto
period: "2022"
last_modified: 2026-06-05
dataset_slug: strutture_ricovero_asl
data_driven: true
---

# Strutture di ricovero del SSN — quanti posti letto, quanto personale?

```js
import { num, euro, euroCompact, pct, numFix, tableFormat } from "../import/format-utils.js";
import { normalizzaReg, loadItalianRegions, buildMapLookup } from "../import/geo-utils.js";
```

```js
const regTopo = await FileAttachment("../data/regioni.topojson").json();
const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
```

```js
const data = await FileAttachment("../data/strutture-ricovero-asl.json").json();
```

```js
const extraFallbacks = { "VALLE D`AOSTA": "VALLE-D'AOSTA/VALLÉE-D'AOSTE" };

const totaleStrutture = new Set(data.map(d => d.denominazione_struttura)).size;
const totaleLettiPrevisti = d3.sum(data, d => d.posti_letto_previsti);
const totaleLettiUtilizzati = d3.sum(data, d => d.posti_letto_utilizzati);
const totalePersonale = d3.sum(data, d => d.totale_personale);
const totaleRicoveri = d3.sum(data, d => d.ricoveri);

const tassoUtilizzo = totaleLettiPrevisti > 0 ? totaleLettiUtilizzati / totaleLettiPrevisti * 100 : 0;
const lettiPerPersonale = totalePersonale > 0 ? totaleLettiPrevisti / totalePersonale : 0;

const perTipo = Array.from(d3.rollup(data, v => ({
  strutture: new Set(v.map(d => d.denominazione_struttura)).size,
  letti_prev: d3.sum(v, d => d.posti_letto_previsti),
  letti_util: d3.sum(v, d => d.posti_letto_utilizzati),
  personale: d3.sum(v, d => d.totale_personale),
  ricoveri: d3.sum(v, d => d.ricoveri),
}), d => d.tipo_struttura), ([tipo_struttura, v]) => ({tipo_struttura, ...v}))
  .sort((a,b) => b.letti_prev - a.letti_prev);

const perRegione = Array.from(d3.rollup(data, v => ({
  letti_util: d3.sum(v, d => d.posti_letto_utilizzati),
  ricoveri: d3.sum(v, d => d.ricoveri),
  personale: d3.sum(v, d => d.totale_personale),
}), d => d.regione), ([regione, v]) => ({regione, ...v}))
  .sort((a,b) => b.ricoveri - a.ricoveri);
```

**Nel 2022 il SSN contava ${num(totaleStrutture)} strutture di ricovero con ${num(totaleLettiPrevisti)} posti letto previsti, di cui ${pct(tassoUtilizzo, 1)} effettivamente utilizzati. Con ${num(totalePersonale)} addetti, il rapporto letti/personale è di ${numFix(lettiPerPersonale, 1)}.**

Il sistema delle strutture di ricovero pubbliche e convenzionate italiane: ospedali a gestione diretta, aziende ospedaliere, IRCCS pubblici e privati, policlinici universitari. Dati 2022 del Ministero della Salute.

<div class="grid grid-cols-4">
  <div class="card">
    <h3>Strutture</h3>
    <span class="big">${num(totaleStrutture)}</span>
  </div>
  <div class="card">
    <h3>Tasso utilizzo letti</h3>
    <span class="big">${pct(tassoUtilizzo, 1)}</span>
    <small style="opacity:0.6">${num(totaleLettiUtilizzati)} / ${num(totaleLettiPrevisti)}</small>
  </div>
  <div class="card">
    <h3>Personale</h3>
    <span class="big">${num(totalePersonale)}</span>
  </div>
  <div class="card">
    <h3>Ricoveri</h3>
    <span class="big">${num(totaleRicoveri)}</span>
  </div>
</div>

---

## 1. Come si distribuiscono i posti letto tra i tipi di struttura?

Le aziende ospedaliere e gli ospedali a gestione diretta concentrano la maggioranza dei posti letto. Gli IRCCS, pur essendo meno numerosi, detengono una quota significativa di letti specializzati.

```js
Plot.plot({
  title: "Posti letto per tipo struttura — 2022",
  width: 800,
  height: 350,
  marginLeft: 220,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(perTipo, {
      y: "tipo_struttura",
      x: "letti_prev",
      fill: "tipo_struttura",
      sort: {y: "-x"},
      tip: {format: {x: d => num(d) + " (" + numFix(d / totaleLettiPrevisti * 100, 1) + "%)"}}
    }),
    Plot.text(perTipo, {
      y: "tipo_struttura",
      x: "letti_prev",
      text: d => num(d.letti_prev),
      dx: 6,
      textAnchor: "start",
      fill: "var(--theme-foreground-muted)",
      fontSize: 11
    }),
    Plot.ruleX([0])
  ]
})
```

> **Nota**: i posti letto previsti (autorizzati) possono differire significativamente da quelli effettivamente utilizzati. Il tasso di utilizzo è un indicatore di capacity, non di efficienza clinica.

---

## 2. Dove si concentrano i ricoveri?

La mappa mostra la distribuzione geografica dei ricoveri: le regioni più popolose guidano il totale, ma il confronto pro capite (non in questo dataset) rivelerebbe differenze più sottili.

```js
const lookupRicoveri = buildMapLookup(perRegione, regioniGeo, "regione", "ricoveri", null, extraFallbacks);
```

```js
Plot.plot({
  title: "Ricoveri per regione — 2022",
  projection: {type: "mercator", domain: regioniGeo},
  width: 800,
  height: 600,
  color: {scheme: "Purples", legend: true, label: "Ricoveri", type: "quantile"},
  marks: [
    Plot.geo(regioniGeo, {
      fill: d => lookupRicoveri.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#888",
      strokeWidth: 0.25,
      tip: {format: {fill: d => num(d)}}
    }),
    Plot.geo(confiniReg, {
      stroke: "#888",
      strokeWidth: 0.7
    })
  ]
})
```

---

## Dettaglio strutture

<small>Elenco delle singole strutture con posti letto, personale e ricoveri. Il tasso di utilizzo è calcolato come posti utilizzati su previsti.</small>

```js
const { header, format } = tableFormat({
  denominazione_struttura: { label: "Struttura", fmt: "string" },
  comune: { label: "Comune", fmt: "string" },
  regione: { label: "Regione", fmt: "string" },
  tipo_struttura: { label: "Tipo", fmt: "string" },
  asl: { label: "ASL", fmt: "string" },
  posti_letto_previsti: { label: "Letti previsti", fmt: "num" },
  posti_letto_utilizzati: { label: "Letti utilizzati", fmt: "num" },
  totale_personale: { label: "Personale", fmt: "num" },
  ricoveri: { label: "Ricoveri", fmt: "num" },
});
```

```js
Inputs.table(data, {
  columns: ["denominazione_struttura", "comune", "regione", "tipo_struttura", "posti_letto_previsti", "posti_letto_utilizzati", "totale_personale", "ricoveri"],
  header,
  format,
  rows: 15,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: i dati si riferiscono al 2022 e includono le strutture di ricovero pubbliche e IRCCS. Non includono le case di cura private accreditate.
- **Personale**: il totale personale è la somma di tutte le categorie (medici, infermieri, tecnici, amministrativi). La distribuzione per categoria è disponibile nelle colonne dedicate ma non in questa pagina.
- **Ricoveri**: il dato può includere più ricoveri per lo stesso paziente in strutture diverse.

---

## Risorse

- [Ministero della Salute — Open Data Strutture di ricovero per ASL](https://www.salute.gov.it/portale/lea/dettaglioContenutiLea.jsp?lingua=italiano&id=5551&area=Lea&menu=vuoto)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/strutture_ricovero_asl/2022/strutture_ricovero_asl_2022_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/strutture-ricovero-asl)

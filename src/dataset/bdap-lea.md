---
title: Spesa sanitaria regionale LEA
description: Dati BDAP sui costi dei Livelli Essenziali di Assistenza per regione, macro-area e voce contabile
source: BDAP — Banca Dati delle Amministrazioni Pubbliche
last_modified: 2025-06-30
---

# Spesa sanitaria regionale LEA

I costi sostenuti dalle regioni italiane per garantire i Livelli Essenziali di Assistenza (LEA), disaggregati per ente, macro-area (prevenzione, assistenza distrettuale, ospedaliera e ricerca) e voce contabile.

**Fonte**: BDAP — Banca Dati delle Amministrazioni Pubbliche · **Periodo**: 2024

```js
const regioni = await FileAttachment("../data/bdap-lea-regioni.json").json();
const macro = await FileAttachment("../data/bdap-lea-macro.json").json();
```

```js
const totSpesa = d3.sum(regioni, d => d.importo_totale);
const nRegioni = regioni.length;
const mediaRegione = totSpesa / nRegioni;
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Spesa totale LEA</h3>
    <span class="big">€ ${(totSpesa / 1e9).toFixed(1)} <small style="opacity:0.6">mld</small></span>
  </div>
  <div class="card">
    <h3>Media per regione</h3>
    <span class="big">€ ${(mediaRegione / 1e9).toFixed(2)} <small style="opacity:0.6">mld</small></span>
  </div>
  <div class="card">
    <h3>Regioni</h3>
    <span class="big">${nRegioni}</span>
  </div>
</div>

---

## Spesa per regione

Quanto spende ciascuna regione per i LEA? Le regioni più popolose guidano la classifica, ma il dato pro capite — non ancora presente in questo dataset — darebbe un quadro più preciso dell'efficienza.

```js
const ordinato = regioni
  .sort((a, b) => b.importo_totale - a.importo_totale)
  .map(d => ({...d, spesa_mld: d.importo_totale / 1e9}));
```

```js
Plot.plot({
  title: "Spesa LEA per regione — 2024",
  width: 800,
  height: 450,
  marginLeft: 140,
  y: {label: null, tickSize: 0},
  x: {grid: true, label: "miliardi di €", tickFormat: "~s"},
  color: {scheme: "Blues"},
  marks: [
    Plot.barX(ordinato, {
      y: "descrizione_regione",
      x: "importo_totale",
      fill: "importo_totale",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Composizione della spesa per macro-area

Come si distribuisce la spesa tra le quattro macro-aree? In tutte le regioni l'assistenza distrettuale e ospedaliera assorbono la quasi totalità delle risorse, mentre prevenzione e ricerca pesano in misura marginale.

```js
const macroLabel = {
  "TOTALE PREVENZIONE COLLETTIVA E SANITA' PUBBLICA": "Prevenzione e sanità pubblica",
  "TOTALE ASSISTENZA DISTRETTUALE": "Assistenza distrettuale",
  "TOTALE ASSISTENZA OSPEDALIERA": "Assistenza ospedaliera",
  "TOTALE COSTI PER ATTIVITA' DI RICERCA": "Ricerca"
};

const macroShort = macro.map(d => ({
  ...d,
  macro: macroLabel[d.descrizione_voce_contabile] || d.descrizione_voce_contabile
}));
```

```js
// Top 5 regioni per spesa totale + composizione
const top5 = ordinato.slice(0, 5).map(d => d.descrizione_regione);
const macroTop5 = macroShort.filter(d => top5.includes(d.descrizione_regione));
```

```js
Plot.plot({
  title: "Composizione spesa LEA — top 5 regioni (2024)",
  width: 800,
  height: 350,
  marginLeft: 120,
  color: {legend: true, scheme: "Set2"},
  y: {label: null, tickSize: 0},
  x: {grid: true, label: "miliardi di €", tickFormat: d => (d / 1e9).toFixed(0)},
  marks: [
    Plot.barX(macroTop5, {
      y: "descrizione_regione",
      x: "importo_totale",
      fill: "macro",
      sort: {y: "-x"},
      tip: {format: {x: d => `€ ${(d / 1e6).toFixed(0)} mln`}}
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Dettaglio regioni

```js
Inputs.table(ordinato, {
  columns: ["descrizione_regione", "importo_totale"],
  header: {descrizione_regione: "Regione", importo_totale: "Spesa totale (€)"},
  format: {importo_totale: x => `€ ${Math.round(x).toLocaleString("it-IT")}`},
  rows: 25,
  width: "100%"
})
```

---

## Risorse

- [BDAP — Open Data](https://bdap-opendata.rgs.mef.gov.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/bdap_lea/2024/bdap_lea_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/bdap-lea)

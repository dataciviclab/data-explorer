---
title: Spesa sanitaria regionale LEA
description: Dati BDAP sui costi dei Livelli Essenziali di Assistenza per regione, macro-area e voce contabile, 2024
source: BDAP — Banca Dati delle Amministrazioni Pubbliche (RGS MEF)
source_url: https://bdap-opendata.rgs.mef.gov.it/
period: "2024"
last_modified: 2025-06-30
dataset_slug: bdap_lea
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

## Composizione della spesa per macro-area

Come si distribuisce la spesa sanitaria tra le quattro macro-aree? L'assistenza distrettuale e ospedaliera assorbono la quasi totalità delle risorse, mentre prevenzione e ricerca pesano in misura marginale.

```js
const nazionaleMacro = Array.from(
  d3.rollup(macro, v => d3.sum(v, d => d.importo_totale), d => d.descrizione_voce_contabile),
  ([descrizione_voce_contabile, importo_totale]) => ({descrizione_voce_contabile, importo_totale})
).sort((a, b) => b.importo_totale - a.importo_totale);
const totMacro = d3.sum(nazionaleMacro, d => d.importo_totale);
const macroConPct = nazionaleMacro.map(d => ({...d, pct: d.importo_totale / totMacro * 100}));
```

```js
Plot.plot({
  title: "Composizione della spesa LEA per macro-area — 2024",
  width: 800,
  height: 300,
  marginLeft: 200,
  y: {label: null, tickSize: 0},
  x: {grid: true, label: "miliardi di €", tickFormat: d => (d / 1e9).toFixed(1)},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(macroConPct, {
      y: "descrizione_voce_contabile",
      x: "importo_totale",
      fill: "descrizione_voce_contabile",
      sort: {y: "-x"},
      tip: {format: {x: d => `€ ${(d / 1e9).toFixed(1)} mld`}}
    }),
    Plot.text(macroConPct, {
      y: "descrizione_voce_contabile",
      x: "importo_totale",
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

> **Nota sul totale**: la spesa complessiva (~€${(totSpesa / 1e9).toFixed(0)} mld) include le **transazioni inter-ente** per mobilità sanitaria (prestazioni acquistate da altri enti SSN). Ogni prestazione è contata sia dall'ente pagante sia dall'ente erogante. Escludendo questo effetto, il costo operativo diretto è circa €${((totSpesa - d3.sum(regioni, d => d.prestazioni_sanitarie)) / 1e9).toFixed(0)} mld.

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

## Dettaglio regioni — composizione della spesa

```js
Inputs.table(ordinato, {
  columns: [
    "descrizione_regione",
    "importo_totale",
    "prestazioni_sanitarie",
    "personale_sanitario",
    "consumi_sanitari",
    "servizi_sanitari",
    "ammortamenti"
  ],
  header: {
    descrizione_regione: "Regione",
    importo_totale: "Spesa totale (€)",
    prestazioni_sanitarie: "Prestazioni",
    personale_sanitario: "Personale",
    consumi_sanitari: "Consumi",
    servizi_sanitari: "Servizi",
    ammortamenti: "Ammortam."
  },
  format: {
    importo_totale: x => `€ ${(x / 1e6).toFixed(0)} mln`,
    prestazioni_sanitarie: x => `€ ${(x / 1e6).toFixed(0)} mln`,
    personale_sanitario: x => `€ ${(x / 1e6).toFixed(0)} mln`,
    consumi_sanitari: x => `€ ${(x / 1e6).toFixed(0)} mln`,
    servizi_sanitari: x => `€ ${(x / 1e6).toFixed(0)} mln`,
    ammortamenti: x => `€ ${(x / 1e6).toFixed(0)} mln`
  },
  rows: 25,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: il dataset copre il solo 2024. Non sono disponibili dati precedenti in questo dataset.
- **Doppia contabilizzazione**: la spesa totale include le prestazioni sanitarie tra enti SSN (mobilità sanitaria), che vengono contate sia dall'ente pagante sia dall'ente erogante. Il costo operativo diretto è inferiore di circa il valore delle prestazioni.
- **Enti esclusi**: le voci aggregate (codice ente '000' e '999') sono escluse dal dataset per evitare duplicazioni contabili.
- **Pro capite**: il dato di spesa pro capite non è ancora disponibile in questo dataset.

---

## Risorse

- [BDAP — Open Data (fonte originale)](https://bdap-opendata.rgs.mef.gov.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/bdap_lea/2024/bdap_lea_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/bdap-lea)

---
title: Infrastrutture strategiche SILOS
description: Opere strategiche e prioritarie censite da SILOS — costi, disponibilità finanziaria, fabbisogno residuo, sistema infrastrutturale, livello gerarchico e stato di attuazione
source: Camera dei Deputati — SILOS
source_url: https://silos.infrastrutturestrategiche.it/
period: "2004–2024"
last_modified: 2026-07-03
dataset_slug: silos_infrastrutture
---

# Infrastrutture strategiche SILOS

Il dataset raccoglie le infrastrutture strategiche e prioritarie censite nel sistema SILOS: ferrovie, strade, sistemi urbani, porti, aeroporti, opere idriche e altri interventi. La struttura è gerarchica: livelli alti descrivono programmi, direttrici o macro-opere; livelli più bassi descrivono articolazioni operative e sotto-interventi.

**Fonte**: [SILOS — Camera dei Deputati](https://silos.infrastrutturestrategiche.it/) · **Periodo**: 2004–2024 · Snapshot 2024

```js
import { num, euroCompact, pct } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/silos-infrastrutture.json").json();
```

```js
const interventi = data.interventi;
const perLivello = data.per_livello;
const livelli = perLivello.map(d => d.livello).sort((a, b) => a - b);
const livelloSel = view(Inputs.select(
  new Map(livelli.map(l => [`Livello ${l}`, l])),
  {label: "Livello gerarchico", value: 2}
));
```

```js
const filtered = interventi.filter(d => d.livello === livelloSel);
const mlnToEuro = d => (d || 0) * 1_000_000;
const euroMln = d => euroCompact(mlnToEuro(d || 0));

const totali = {
  interventi: filtered.length,
  cup: new Set(filtered.filter(d => d.cup).map(d => d.cup)).size,
  costi_mln_euro: d3.sum(filtered, d => d.costi_mln_euro || 0),
  disponibilita_mln_euro: d3.sum(filtered, d => d.disponibilita_mln_euro || 0),
  fabbisogno_mln_euro: d3.sum(filtered, d => d.fabbisogno_mln_euro || 0),
};

const quotaCoperta = totali.costi_mln_euro ? (totali.disponibilita_mln_euro / totali.costi_mln_euro) * 100 : 0;

function aggregateBy(rows, key, valueName = key) {
  return Array.from(
    d3.rollup(
      rows,
      v => ({
        interventi: v.length,
        costi_mln_euro: d3.sum(v, d => d.costi_mln_euro || 0),
        disponibilita_mln_euro: d3.sum(v, d => d.disponibilita_mln_euro || 0),
        fabbisogno_mln_euro: d3.sum(v, d => d.fabbisogno_mln_euro || 0),
      }),
      d => d[key] || "Non indicato"
    ),
    ([label, values]) => ({[valueName]: label, ...values})
  ).sort((a, b) => b.costi_mln_euro - a.costi_mln_euro);
}

const perSistema = aggregateBy(filtered, "sistema_infrastrutturale").slice(0, 18);
const perLuogo = aggregateBy(filtered, "luogo_lavori").slice(0, 18);
const perStato = aggregateBy(filtered, "stato_attuazione").slice(0, 18);
const perUltimazione = aggregateBy(
  filtered.filter(d => d.anno_ultimazione_previsto),
  "anno_ultimazione_previsto"
).sort((a, b) => d3.ascending(a.anno_ultimazione_previsto, b.anno_ultimazione_previsto));
const topInterventi = filtered.slice().sort((a, b) => b.costi_mln_euro - a.costi_mln_euro).slice(0, 50);
```

<div class="grid grid-cols-4">
  <div class="card">
    <h3>Righe nel livello</h3>
    <span class="big">${num(totali.interventi)}</span>
    <small style="opacity:0.6">livello ${String(livelloSel)}</small>
  </div>
  <div class="card">
    <h3>Costo</h3>
    <span class="big">${euroMln(totali.costi_mln_euro)}</span>
  </div>
  <div class="card">
    <h3>Disponibilità</h3>
    <span class="big">${euroMln(totali.disponibilita_mln_euro)}</span>
    <small style="opacity:0.6">${pct(quotaCoperta)} del costo</small>
  </div>
  <div class="card">
    <h3>Fabbisogno</h3>
    <span class="big">${euroMln(totali.fabbisogno_mln_euro)}</span>
  </div>
</div>

---

## Livelli della gerarchia

La tabella mostra quanto cambia il quadro passando da un livello all'altro. Non bisogna sommare i livelli tra loro: una stessa opera può comparire come direttrice, intervento e sotto-intervento.

```js
const levelHeader = {
  livello: "Livello",
  righe: "Righe",
  righe_con_cup: "Con CUP",
  costi_mln_euro: "Costo",
  disponibilita_mln_euro: "Disponibilità",
  fabbisogno_mln_euro: "Fabbisogno",
};
const levelFormat = {
  livello: x => num(x),
  righe: x => num(x),
  righe_con_cup: x => num(x),
  costi_mln_euro: x => euroMln(x),
  disponibilita_mln_euro: x => euroMln(x),
  fabbisogno_mln_euro: x => euroMln(x),
};
```

```js
Inputs.table(perLivello, {
  columns: ["livello", "righe", "righe_con_cup", "costi_mln_euro", "disponibilita_mln_euro", "fabbisogno_mln_euro"],
  header: levelHeader,
  format: levelFormat,
  rows: 10,
  width: "100%"
})
```

---

## Sistemi infrastrutturali

Il grafico legge solo il livello selezionato. A livelli alti emergono macro-direttrici e programmi; a livelli bassi aumenta il dettaglio operativo.

```js
Plot.plot({
  title: `Costo e fabbisogno per sistema infrastrutturale — livello ${livelloSel}`,
  width: 900,
  height: Math.max(340, perSistema.length * 32 + 50),
  marginLeft: 170,
  x: {grid: true, label: null, tickFormat: d => euroCompact(mlnToEuro(d))},
  y: {label: null, tickSize: 0},
  color: {legend: true, domain: ["Costo", "Fabbisogno"], range: ["#4e79a7", "#e15759"]},
  marks: [
    Plot.barX(perSistema, {
      y: "sistema_infrastrutturale",
      x: "costi_mln_euro",
      fill: "Costo",
      sort: {y: "-x"},
      tip: {format: {x: euroMln}}
    }),
    Plot.tickX(perSistema, {
      y: "sistema_infrastrutturale",
      x: "fabbisogno_mln_euro",
      stroke: "Fabbisogno",
      strokeWidth: 3,
      tip: {format: {x: euroMln}}
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Localizzazione dichiarata

La localizzazione SILOS non è sempre una singola regione: molte opere sono multi-regionali o non ripartibili a livello regionale. La vista territoriale va letta come localizzazione dichiarata, non come ripartizione puntuale dei costi.

```js
Plot.plot({
  title: `Prime localizzazioni per costo — livello ${livelloSel}`,
  width: 900,
  height: 560,
  marginLeft: 260,
  x: {grid: true, label: null, tickFormat: d => euroCompact(mlnToEuro(d))},
  y: {label: null, tickSize: 0},
  color: {scheme: "Greens"},
  marks: [
    Plot.barX(perLuogo, {
      y: "luogo_lavori",
      x: "costi_mln_euro",
      fill: "costi_mln_euro",
      sort: {y: "-x"},
      tip: {format: {x: euroMln}}
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Stato di attuazione

Lo stato non è compilato in modo uniforme su tutti i livelli. Quando il livello selezionato contiene molte righe "Non indicato", il grafico segnala un limite informativo della fonte, non necessariamente assenza di avanzamento.

```js
Plot.plot({
  title: `Costo per stato di attuazione — livello ${livelloSel}`,
  width: 900,
  height: Math.max(300, perStato.length * 30 + 50),
  marginLeft: 240,
  x: {grid: true, label: null, tickFormat: d => euroCompact(mlnToEuro(d))},
  y: {label: null, tickSize: 0},
  color: {scheme: "Purples"},
  marks: [
    Plot.barX(perStato, {
      y: "stato_attuazione",
      x: "costi_mln_euro",
      fill: "costi_mln_euro",
      sort: {y: "-x"},
      tip: {format: {x: euroMln}}
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Ultimazione prevista

Molti interventi non riportano un anno di ultimazione previsto. Dove la data è presente, il profilo temporale cambia molto al variare del livello gerarchico.

```js
Plot.plot({
  title: `Costo per anno di ultimazione previsto — livello ${livelloSel}`,
  width: 900,
  height: 340,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, label: null, tickFormat: d => euroCompact(mlnToEuro(d))},
  marks: [
    Plot.barY(perUltimazione, {
      x: "anno_ultimazione_previsto",
      y: "costi_mln_euro",
      fill: "#f28e2b",
      tip: {format: {y: euroMln}}
    }),
    Plot.ruleY([0])
  ]
})
```

---

## Interventi nel livello selezionato

```js
const header = {
  progressivo: "Prog.",
  denominazione: "Intervento",
  sistema_infrastrutturale: "Sistema",
  luogo_lavori: "Localizzazione",
  soggetto_competente: "Soggetto",
  stato_attuazione: "Stato",
  anno_ultimazione_previsto: "Ultimazione",
  costi_mln_euro: "Costo",
  disponibilita_mln_euro: "Disponibilità",
  fabbisogno_mln_euro: "Fabbisogno",
};
const format = {
  progressivo: x => num(x),
  anno_ultimazione_previsto: x => x == null ? "—" : num(x),
  costi_mln_euro: x => euroMln(x),
  disponibilita_mln_euro: x => euroMln(x),
  fabbisogno_mln_euro: x => euroMln(x),
};
```

```js
Inputs.table(topInterventi, {
  columns: [
    "progressivo",
    "denominazione",
    "sistema_infrastrutturale",
    "luogo_lavori",
    "soggetto_competente",
    "stato_attuazione",
    "anno_ultimazione_previsto",
    "costi_mln_euro",
    "disponibilita_mln_euro",
    "fabbisogno_mln_euro"
  ],
  header,
  format,
  rows: 20,
  width: "100%"
})
```

---

## Limiti

- **Gerarchia**: i livelli SILOS non vanno sommati tra loro. La pagina li differenzia con un selettore, ma una lettura contabile rigorosa richiede di decidere prima quale livello rappresenta l'unità di analisi.
- **Snapshot**: il parquet pubblicato è uno snapshot 2024 di un censimento che documenta opere con storia pluriennale.
- **Localizzazione**: `luogo_lavori` può indicare aree vaste, combinazioni di regioni o voci non ripartibili. Non è una ripartizione territoriale contabile.
- **Stati**: lo stato di attuazione non è compilato in modo uniforme su tutti i livelli della gerarchia.
- **Importi**: costi, disponibilità e fabbisogno sono espressi dalla fonte in milioni di euro e non sono rivalutati.

---

## Risorse

- [SILOS — Infrastrutture strategiche](https://silos.infrastrutturestrategiche.it/)
- [Dump dati.camera.it](https://dati.camera.it/ocd/dump/silos/PISRapportoCSV2024.zip)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/silos_infrastrutture/2024/silos_infrastrutture_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/silos-infrastrutture)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)

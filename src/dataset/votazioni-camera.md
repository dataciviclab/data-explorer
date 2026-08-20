---
title: Votazioni Camera dei Deputati
description: Esito, conteggi e indicatori delle votazioni della Camera — 2018-2025
source: Camera dei Deputati — Dati aperti
source_url: https://dati.camera.it/
period: "2018–2025"
last_modified: 2026-05-30
dataset_slug: camera_votazioni_sparql
data_driven: true
---

# Votazioni Camera dei Deputati — quante fiducie e quante approvazioni?

```js
import { num, pct, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/votazioni-camera.json").json();

const conAnno = data.map(d => ({...d, anno: new Date(d.data).getFullYear()}));
```

```js
const anni = [...new Set(conAnno.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = conAnno.filter(d => d.anno === annoSel);

const totVoti = filtered.length;
const approvati = filtered.filter(d => d.approvato).length;
const fiducia = filtered.filter(d => d.richiesta_fiducia).length;
const pctApprovati = totVoti > 0 ? Math.round(approvati / totVoti * 1000) / 10 : 0;
```

**Nel ${String(annoSel)} la Camera ha votato ${num(totVoti)} volte, con ${pct(pctApprovati, 1)} di provvedimenti approvati e ${num(fiducia)} richieste di fiducia. La fiducia resta lo strumento-chiave del governo: quante volte lo costringe a puntare tutto su una singola votazione?**

Le votazioni della Camera (legislature XVIII e XIX) registrano esito, conteggi e l'uso della questione di fiducia come indicatore della relazione governo-parlamento.

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Votazioni ${String(annoSel)}</h3>
    <span class="big">${num(totVoti)}</span>
  </div>
  <div class="card">
    <h3>Tasso approvazione</h3>
    <span class="big">${pct(pctApprovati, 1)}</span>
    <small style="opacity:0.6">${num(approvati)} su ${num(totVoti)}</small>
  </div>
  <div class="card">
    <h3>Fiducie</h3>
    <span class="big">${num(fiducia)}</span>
    <small style="opacity:0.6">${totVoti > 0 ? pct(fiducia / totVoti * 100, 1) : "—"} delle votazioni</small>
  </div>
</div>

---

## 1. Come evolve l'attività legislativa anno per anno?

Il numero di votazioni e la percentuale di approvati mostrano il ritmo dei lavori parlamentari: anni frenetici e anni più pigri si alternano a seconda della Agenda legislativa.

```js
const perAnno = Array.from(
  d3.rollup(conAnno, v => ({
    tot: v.length,
    approvati: d3.sum(v, d => d.approvato ? 1 : 0),
    fiducia: d3.sum(v, d => d.richiesta_fiducia ? 1 : 0),
    mediaFav: d3.mean(v, d => d.favorevoli),
    mediaContr: d3.mean(v, d => d.contrari),
  }), d => d.anno),
  ([anno, v]) => ({anno, ...v, pct_ok: Math.round(v.approvati / v.tot * 1000) / 10})
).sort((a, b) => a.anno - b.anno);
```

```js
Plot.plot({
  title: "Votazioni e approvati per anno — Camera",
  width: 800,
  height: 350,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, label: "Votazioni"},
  color: {scheme: "Set2", legend: true},
  marks: [
    Plot.barY(perAnno, {
      x: "anno",
      y: "tot",
      fill: "#4e79a7",
      tip: {format: {y: d => num(d)}}
    }),
    Plot.barY(perAnno, {
      x: "anno",
      y: d => d.approvati,
      fill: "#59a14f",
      tip: true
    }),
    Plot.text(perAnno, {
      x: "anno",
      y: "tot",
      text: d => `${d.pct_ok}%`,
      dy: -6,
      fill: "var(--theme-foreground-muted)",
      fontSize: 11
    })
  ]
})
```

---

## 2. Quante volte il governo piazza la fiducia?

La fiducia comprime i tempi di approvazione ma elimina ogni possibilità di emendamento. L'andamento annuale rivela quanto spesso il governo sceglie la via del "tutto o niente".

```js
const fiduciaAnno = Array.from(
  d3.rollup(conAnno, v => ({
    tot: v.length,
    fiducia: d3.sum(v, d => d.richiesta_fiducia ? 1 : 0),
  }), d => d.anno),
  ([anno, v]) => ({anno, ...v})
).sort((a, b) => a.anno - b.anno);
```

```js
Plot.plot({
  title: "Votazioni con richiesta di fiducia per anno",
  width: 800,
  height: 300,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, label: "Voti di fiducia"},
  marks: [
    Plot.barY(fiduciaAnno, {
      x: "anno",
      y: "fiducia",
      fill: "#e15759",
      tip: true
    }),
    Plot.ruleY([0])
  ]
})
```

---

## Dettaglio votazioni

<small>Filtri per anno, esito e fiducia. La tabella mostra le singole votazioni con conteggi e indicatori.</small>

```js
const esitoFilter = view(Inputs.select(["Tutte", "Approvate", "Respinte"], {label: "Esito"}));
const fiduciaFilter = view(Inputs.checkbox(["Solo voti di fiducia"], {label: " "}));
```

```js
const filtered2 = filtered.filter(d => {
  if (esitoFilter === "Approvate" && !d.approvato) return false;
  if (esitoFilter === "Respinte" && d.approvato) return false;
  if (fiduciaFilter.length > 0 && !d.richiesta_fiducia) return false;
  return true;
});
```

```js
Inputs.table(filtered2, {
  columns: ["data", "titolo", "favorevoli", "contrari", "astenuti", "votanti", "presenti", "approvato", "richiesta_fiducia"],
  header: {data: "Data", titolo: "Oggetto", favorevoli: "Fav", contrari: "Contr", astenuti: "Ast", votanti: "Votanti", presenti: "Presenti", approvato: "Esito", richiesta_fiducia: "Fiducia"},
  format: {
    data: x => new Date(x).toLocaleDateString("it-IT"),
    approvato: x => x ? "✅ Approvato" : "❌ Respinto",
    richiesta_fiducia: x => x ? "Sì" : "No"
  },
  rows: 20,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie copre le legislature XVIII e XIX (2018-2025). Votazioni precedenti al 2018 non sono disponibili in questo dataset.
- **Titolo**: l'oggetto della votazione è il testo disponibile nell'ontologia della Camera. Alcuni titoli possono essere abbreviati o tecnici.
- **Fiducia**: la colonna `richiesta_fiducia` indica le votazioni in cui il governo ha posto la questione di fiducia. Non include mozioni di sfiducia o altri istituti.
- **Dettaglio**: il dataset non include i voti dei singoli deputati, solo i conteggi aggregati per votazione.

---

## Risorse

- [Camera dei Deputati — Dati aperti](https://dati.camera.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/camera_votazioni_sparql/2025/camera_votazioni_sparql_2025_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/camera-votazioni-sparql)

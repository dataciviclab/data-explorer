---
title: Camera dei Deputati — Legislature e composizione
description: "165 anni di rappresentanza: deputati, genere e gruppi parlamentari dalla Costituente ad oggi"
source: Camera dei Deputati — Dati aperti
source_url: https://dati.camera.it/
period: "1861–2026"
last_modified: 2026-08-22
dataset_slug: camera_deputati_legislature
data_driven: true
---

```js
const data = await FileAttachment("../data/camera-deputati.json").json();
const plot = await import("npm:@observablehq/plot");
import { num, numFix, pct } from "../import/format-utils.js";
```

```js
const genere = data.deputati_per_legislatura;
const ultima = data.kpi.ultima;
const depOggi = data.kpi.tot_deputati;
const pctDonneOggi = data.kpi.pct_donne;
const prima = genere[0];
const pctDonnePrima = prima.pct_donne;
```

# Camera dei Deputati — 165 anni di rappresentanza

**Dalla Costituente (${data.per_legislatura[0].legislatura}) alla ${ultima}: ${data.kpi.tot_legislature} legislature, ${num(depOggi)} deputati oggi, ${pct(pctDonneOggi)} di donne.** Come è cambiata la composizione della Camera in un secolo e mezzo di storia italiana?

Ogni riga è un deputato iscritto nell'Anagrafe della Camera. I dati coprono tutte le legislature dal Regno d'Italia alla XIX legislatura repubblicana.

---

## 1. La Camera oggi

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Legislature</h3>
    <span class="big">${data.kpi.tot_legislature}</span>
  </div>
  <div class="card">
    <h3>Deputati (${ultima})</h3>
    <span class="big">${num(depOggi)}</span>
  </div>
  <div class="card">
    <h3>Donne (${ultima})</h3>
    <span class="big">${pct(pctDonneOggi)}</span>
  </div>
</div>

La Camera dei Deputati ha cambiato composizione in ogni legislature. Oggi conta ${num(depOggi)} seggi, di cui ${pct(pctDonneOggi)} occupati da donne — un record storico, ma ancora lontano dalla parità.

---

## 2. Deputati per legislatura — uomini e donne

Ogni barra mostra il totale dei deputati, diviso per genere. La Camera ha oscillato tra i 230 seggi del Regno e i 630 della XVII legislatura.

```js
const ultime = genere.slice(-12);

display(plot.plot({
  title: "Deputati per legislature (uomini vs donne)",
  width: 800, height: 400,
  x: {label: null, tickFormat: d => d.length > 12 ? d.slice(0, 12) + "…" : d},
  y: {grid: true, label: "Deputati"},
  color: {domain: ["Uomini", "Donne"], range: ["#4e79a7", "#e15759"], legend: true},
  marginLeft: 60,
  marks: [
    plot.barY(ultime, {x: "legislatura", y: "uomini", fill: "#4e79a7", tip: true, title: d => `${d.legislatura}: ${d.uomini} uomini`}),
    plot.barY(ultime, {x: "legislatura", y: "donne", fill: "#e15759", tip: true, title: d => `${d.legislatura}: ${d.donne} donne`, y1: "uomini"}),
    plot.ruleY([0])
  ]
}))
```

> La Costituente aveva solo ${prima.donne} donne su ${num(prima.n)} deputati (${pct(pctDonnePrima)}). La crescita è stata lentissima fino agli anni '80, poi accelerata dalla legge quota del 1993.

---

## 3. L'evoluzione della rappresentanza femminile

La quota di donne è il termometro della rappresentanza politica italiana. Ogni balzo corrisponde spesso a un cambiamento normativo.

```js
display(plot.plot({
  title: "Quota di donne in Parlamento (%)",
  width: 800, height: 320,
  x: {label: null, tickFormat: d => d.length > 12 ? d.slice(0, 12) + "…" : d},
  y: {domain: [0, 40], grid: true, label: "% donne"},
  color: {scheme: "Set2"},
  marks: [
    plot.lineY(ultime, {x: "legislatura", y: "pct_donne", stroke: "#e15759", strokeWidth: 2}),
    plot.dot(ultime, {x: "legislatura", y: "pct_donne", fill: "#e15759", r: 4, tip: true, title: d => `${d.legislatura}: ${d.pct_donne}%`}),
    plot.ruleY([0])
  ]
}))
```

> La quota ha superato il 10% solo con la XIII legislatura (1996) e il 30% con la XVIII (2018). La crescita riflette le leggi di parità e le quote di genere.

---

## 4. Gruppi parlamentari — ultima legislatura

I gruppi che compongono la Camera nella legislatura attuale.

<div style="display:flex; flex-wrap:wrap; gap:0.5em">
${data.dep_per_gruppo.map(g => html`<span style="padding:0.3em 0.7em; border:1px solid #ccc; border-radius:6px; font-size:0.9em">${g.gruppo}</span>`)}
</div>

> I gruppi di maggioranza e opposizione si bilanciano attorno alla soglia di 100 deputati ciascuno. Il Gruppo Misto raccoglie chi non ha una collocazione precisa.

---

## Tabella — tutte le legislature

```js
display(genere.map(d => ({
  legislature: d.legislatura,
  deputati: d.n,
  uomini: d.uomini,
  donne: d.donne,
  pct_donne: d.pct_donne + "%"
})))
```

```js
Inputs.table(genere, {
  columns: ["legislatura", "n", "uomini", "donne", "pct_donne"],
  header: {legislatura: "Legislatura", n: "Deputati", uomini: "Uomini", donne: "Donne", pct_donne: "% Donne"},
  format: {pct_donne: d => d + "%"},
  rows: 20,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: dalla I legislatura del Regno (1861) alla XIX della Repubblica (2022-2026). Alcune legislature del Regno hanno nomi diversi (regno_01, regno_02...).
- **Genere**: la colonna `gender` è valorizzata solo dalla Costituente in poi. Le legislature del Regno non hanno dati di genere (mostrati come 0).
- **Gruppi**: l'elenco dei gruppi è disponibile, ma non il conteggio dei membri per gruppo. I dati riflettono lo stato a fine legislatura.
- **Non include**: il Senato della Repubblica (ha dati separati).

---

## Risorse

- [Camera dei Deputati — Dati aperti](https://dati.camera.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/camera_deputati_legislature/2026/camera_deputati_legislature_2026_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/open-politica/tree/main/datasets/camera-deputati-legislature)

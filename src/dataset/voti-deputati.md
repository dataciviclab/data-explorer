---
title: Voti dei Deputati — accountability parlamentare
description: "7,7 milioni di voti individuali: come vota ogni deputato e quanto è coerente con il proprio gruppo"
source: Camera dei Deputati — Dati aperti
source_url: https://dati.camera.it/
period: "2022–2026"
last_modified: 2026-08-22
dataset_slug: camera_voti
data_driven: true
---

```js
const data = await FileAttachment("../data/voti-deputati.json").json();
const plot = await import("npm:@observablehq/plot");
import { num, numFix, pct } from "../import/format-utils.js";
```

```js
const trend = data.trend;
const gruppo = data.per_gruppo;
const coerenti = data.top_coerenti;
const dissidenti = data.top_dissidenti;
```

# Voti dei Deputati — come si vota in Parlamento?

**${num(data.kpi.tot_votazioni)} votazioni dalla XIX legislatura, ${num(data.kpi.media_annuale)} all'anno.** Ogni voto è registrato: chi è favorevole, chi contrario, chi si astiene. Questi dati mostrano la coerenza dei deputati con il proprio gruppo — chi va sempre d'accordo con la linea di partito, e chi osa dissentire.

---

## 1. L'attività votante

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Votazioni totali</h3>
    <span class="big">${num(data.kpi.tot_votazioni)}</span>
  </div>
  <div class="card">
    <h3>Media annuale</h3>
    <span class="big">${num(data.kpi.media_annuale)}</span>
  </div>
  <div class="card">
    <h3>Anni</h3>
    <span class="big">${data.kpi.anni}</span>
  </div>
</div>

Il numero di votazioni è cresciuto dalla fondazione della legislatura (${trend[0].n_votazioni} nel ${trend[0].anno}, anno parziale) a un picco di ${num(trend.find(d => d.n_votazioni === Math.max(...trend.map(t => t.n_votazioni))).n_votazioni)} nel ${trend.find(d => d.n_votazioni === Math.max(...trend.map(t => t.n_votazioni))).anno}.

```js
display(plot.plot({
  title: "Votazioni per anno",
  width: 800, height: 280,
  x: {tickFormat: String, label: null},
  y: {grid: true, label: "Votazioni"},
  marks: [
    plot.barY(trend, {x: "anno", y: "n_votazioni", fill: "#4e79a7", tip: true, title: d => `${d.anno}: ${num(d.n_votazioni)} votazioni`}),
    plot.ruleY([0])
  ]
}))
```

---

## 2. Come votano i gruppi — linea di partito

Per ogni gruppo, la percentuale di voti favorevoli. I 5 gruppi principali mostrano la coerenza di voto nella legislatura.

```js
const topGroups = ["FDI", "PD-IDP", "M5S", "LEGA", "FI-PPE"];
const gruppoTop = gruppo.filter(d => topGroups.includes(d.gruppo) && d.anno >= 2023);
```

```js
display(plot.plot({
  title: "Voti favorevoli per gruppo (%)",
  width: 800, height: 350,
  x: {tickFormat: String, label: null},
  y: {domain: [0, 100], grid: true, label: "% favorevoli"},
  color: {domain: topGroups, range: ["#1a3c6e", "#d32f2f", "#f5c518", "#008000", "#0066cc"], legend: true},
  marks: [
    plot.lineY(gruppoTop, {x: "anno", y: "pct_fav", stroke: "gruppo", strokeWidth: 2}),
    plot.dot(gruppoTop, {x: "anno", y: "pct_fav", fill: "gruppo", r: 3, tip: true, title: d => `${d.gruppo}: ${d.pct_fav}%`}),
    plot.ruleY([50])
  ]
}))
```

> I gruppi di maggioranza (FDI, LEGA, FI-PPE) tendono a votare più compatti. L'opposizione mostra maggiore dispersione.

---

## 3. I più fedeli alla linea di gruppo

Deputati con almeno 100 voti la cui percentuale di favorevoli si avvicina di più alla media del proprio gruppo.

```js
const tabCoerenti = coerenti.filter(c => c.nome && c.cognome);
```

```js
Inputs.table(tabCoerenti, {
  columns: ["cognome", "nome", "gruppo", "n_voti", "pct_fav", "pct_gruppo"],
  header: {cognome: "Cognome", nome: "Nome", gruppo: "Gruppo", n_voti: "Voti", pct_fav: "% Fav", pct_gruppo: "% Gruppo"},
  format: {
    pct_fav: d => d + "%",
    pct_gruppo: d => d + "%"
  },
  rows: 15,
  width: "100%"
})
```

---

## 4. I più indipendenti dalla linea

Deputati che si discostano di più dalla media del proprio gruppo — votano diversamente dalla maggioranza dei colleghi.

```js
const tabDiss = dissidenti.filter(d => d.nome && d.cognome);
```

```js
Inputs.table(tabDiss, {
  columns: ["cognome", "nome", "gruppo", "n_voti", "pct_fav", "pct_gruppo"],
  header: {cognome: "Cognome", nome: "Nome", gruppo: "Gruppo", n_voti: "Voti", pct_fav: "% Fav", pct_gruppo: "% Gruppo"},
  format: {
    pct_fav: d => d + "%",
    pct_gruppo: d => d + "%"
  },
  rows: 15,
  width: "100%"
})
```

> La coerenza di gruppo non è necessariamente un merito o un difetto: dipende dal contesto. Un deputato che vota contro la linea del partito può essere un segnale di democrazia interna o di frammentazione.

---

## Limiti

- **Copertura**: XIX legislatura (2022-2026). Il 2022 è anno parziale (inizio legislatura).
- **Coerenza**: calcolata come distanza tra la % di favorevoli del deputato e quella media del gruppo. Non tiene conto di astensioni o voti mancati.
- **Gruppi**: le sigle dei gruppi possono cambiare durante la legislatura (fusioni, scissioni).
- **Non include**: il Senato della Repubblica.

---

## Risorse

- [Camera dei Deputati — Dati aperti](https://dati.camera.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/camera_voti/2026/camera_voti_2026_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/open-politica/tree/main/datasets/camera-voti)

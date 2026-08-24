---
title: Attività in Aula — Camera dei Deputati
description: "Chi parla e chi relaziona? Interventi, relazioni e partecipazione dei deputati nella XIX legislatura"
source: Camera dei Deputati — Dati aperti
source_url: https://dati.camera.it/
period: "2022–2026"
last_modified: 2026-08-22
dataset_slug: camera_interventi
data_driven: true
---

```js
const data = await FileAttachment("../data/attivita-aula.json").json();
const plot = await import("npm:@observablehq/plot");
import { num, numFix, pct } from "../import/format-utils.js";
```

```js
const trend = data.trend.filter(t => t.anno >= 2022);
const topParl = data.top_parlanti.filter(p => p.nome && p.cognome);
const topRel = data.top_relatori.filter(r => r.nome && r.cognome);
```

# Attività in Aula — chi parla e chi relaziona?

**${num(data.kpi.tot_interventi)} interventi e ${num(data.kpi.tot_relazioni)} relazioni nei due anni più recenti (2024-2025).** Ogni deputato può intervenire in aula o relazionare su un provvedimento. Questi dati mostrano chi è più attivo e come si distribuisce il lavoro legislativo.

---

## 1. L'attività della Camera

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Interventi (2024-25)</h3>
    <span class="big">${num(data.kpi.tot_interventi)}</span>
  </div>
  <div class="card">
    <h3>Relazioni (2024-25)</h3>
    <span class="big">${num(data.kpi.tot_relazioni)}</span>
  </div>
  <div class="card">
    <h3>Parlanti (2025)</h3>
    <span class="big">${data.kpi.parlanti_2025}</span>
  </div>
</div>

La Camera lavora attraverso interventi in aula e relazioni sui provvedimenti. L'attività è cresciuta dalla fondazione della legislatura (2022, anno parziale) a un picco nel 2024.

---

## 2. Trend: interventi e relazioni per anno

```js
display(plot.plot({
  title: "Interventi e relazioni per anno",
  width: 800, height: 320,
  x: {tickFormat: String, label: null},
  y: {grid: true, label: "Numero"},
  color: {domain: ["Interventi", "Relazioni"], range: ["#4e79a7", "#f28e2b"], legend: true},
  marks: [
    plot.lineY(trend, {x: "anno", y: "n_interventi", stroke: "#4e79a7", strokeWidth: 2}),
    plot.dot(trend, {x: "anno", y: "n_interventi", fill: "#4e79a7", r: 4, tip: true, title: d => `${d.anno}: ${num(d.n_interventi)} interventi`}),
    plot.lineY(trend, {x: "anno", y: "n_relat", stroke: "#f28e2b", strokeWidth: 2, strokeDasharray: "5,3"}),
    plot.dot(trend, {x: "anno", y: "n_relat", fill: "#f28e2b", r: 4, tip: true, title: d => `${d.anno}: ${num(d.n_relat)} relazioni`}),
    plot.ruleY([0])
  ]
}))
```

> Gli interventi sono circa 10 volte più numerosi delle relazioni. Entrambi seguono lo stesso andamento: crescita fino al 2024, poi leggero calo.

---

## 3. Chi parla di più in aula

I deputati con più interventi nei due anni più recenti (2024-2026).

```js
Inputs.table(topParl, {
  columns: ["cognome", "nome", "n_interventi"],
  header: {cognome: "Cognome", nome: "Nome", n_interventi: "Interventi"},
  rows: 15,
  width: "100%",
  sort: "n_interventi",
  reverse: true
})
```

---

## 4. Chi relaziona di più

I deputati che relazionano sui provvedimenti — un ruolo chiave nell'iter legislativo.

```js
Inputs.table(topRel, {
  columns: ["cognome", "nome", "n_relat"],
  header: {cognome: "Cognome", nome: "Nome", n_relat: "Relazioni"},
  rows: 15,
  width: "100%",
  sort: "n_relat",
  reverse: true
})
```

> Relazionare è un incarico di Partito: il relatore guida l'iter del provvedimento in commissione e in aula. I relatori più attivi sono spesso i capigruppo o i presidenti di commissione.

---

## Limiti

- **Copertura**: XIX legislatura (2022-2026). Il 2022 è anno parziale (inizio legislatura).
- **Interventi**: il dataset registra gli interventi in aula. Non include interventi in commissione o scritti.
- **Relatori**: il tipo è sempre "Relatore" nel clean. Il dataset non distingue tra relatore di maggioranza e di minoranza.
- **Nomini**: i nomi derivano dal join con `camera_deputati_legislature` sulla legislatura XIX. Deputati non presenti nella XIX non hanno nome.

---

## Risorse

- [Camera dei Deputati — Dati aperti](https://dati.camera.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito — interventi](https://storage.googleapis.com/dataciviclab-clean/open-politica/camera_interventi/2026/camera_interventi_2026_clean.parquet)
- [Scarica il parquet pulito — relatori](https://storage.googleapis.com/dataciviclab-clean/open-politica/camera_relatori/2026/camera_relatori_2026_clean.parquet)
- [Pipeline interventi](https://github.com/dataciviclab/open-politica/tree/main/datasets/camera-interventi)
- [Pipeline relatori](https://github.com/dataciviclab/open-politica/tree/main/datasets/camera-relatori)

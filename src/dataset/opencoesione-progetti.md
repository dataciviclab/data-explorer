---
title: OpenCoesione — Progetti delle politiche di coesione
description: Progetti finanziati da fondi UE e FSC (2000-2027) - risorse assegnate, impegnate e pagate per ciclo, territorio e tema
source: Presidenza del Consiglio dei Ministri — OpenCoesione
source_url: https://opencoesione.gov.it/
period: "2000–2027"
last_modified: 2026-06-04
dataset_slug: opencoesione_progetti
---

# OpenCoesione — Progetti delle politiche di coesione

Tutti i progetti finanziati dalle politiche di coesione italiane — fondi europei (FESR, FSE, FEASR, FEAMP) e Fondo per lo Sviluppo e la Coesione (FSC) — dal ciclo 2000-2006 al 2021-2027. I dati coprono finanziamento totale, impegni e pagamenti, con dettaglio per macroarea geografica e tema.

**Fonte**: [OpenCoesione](https://opencoesione.gov.it/) · **Periodo**: 2000–2027

```js
import { num, euro, euroCompact, pct, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/opencoesione-progetti.json").json();
```

```js
// Filtro: ciclo di programmazione (sostituisce il filtro anno standard)
const cicli = [...new Set(data.map(d => d.OC_DESCR_CICLO))].sort();
const cicloSel = view(Inputs.select(
  new Map(cicli.map(c => [c, c])),
  {label: "Ciclo di programmazione", value: cicli[cicli.length - 1]}
));
```

```js
// Dati filtrati per ciclo selezionato
const cicloData = data.filter(d => d.OC_DESCR_CICLO === cicloSel);
```

```js
// Metriche riassuntive
const totFinanziato = d3.sum(cicloData, d => d.FINANZ_TOTALE_PUBBLICO);
const totPagato = d3.sum(cicloData, d => d.TOT_PAGAMENTI);
const tassoPagamento = totFinanziato > 0 ? (totPagato / totFinanziato) * 100 : 0;
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Finanziamento totale</h3>
    <span class="big">${euroCompact(totFinanziato)}</span>
  </div>
  <div class="card">
    <h3>Pagamenti totali</h3>
    <span class="big">${euroCompact(totPagato)}</span>
  </div>
  <div class="card">
    <h3>Tasso di pagamento</h3>
    <span class="big">${pct(tassoPagamento)}</span>
  </div>
</div>

---

## Finanziamento per macroarea

La distribuzione dei fondi tra Centro-Nord e Mezzogiorno è il nodo centrale delle politiche di coesione. Il Mezzogiorno assorbe la maggior parte delle risorse, essendo l'obiettivo principale del riequilibrio territoriale.

```js
// Aggregazione per macroarea
const perMacroarea = d3.rollups(
  cicloData,
  v => ({
    finanziato: d3.sum(v, d => d.FINANZ_TOTALE_PUBBLICO),
    pagato: d3.sum(v, d => d.TOT_PAGAMENTI),
  }),
  d => d.OC_MACROAREA
).map(([key, val]) => ({macroarea: key, ...val}))
 .sort((a, b) => b.finanziato - a.finanziato);
```

```js
Plot.plot({
  title: `Finanziamento per macroarea — ${cicloSel}`,
  width: 800,
  height: 300,
  marginLeft: 140,
  y: {label: null, tickSize: 0},
     x: {grid: true, label: "euro", tickFormat: d => euroCompact(d)},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(perMacroarea, {
      y: "macroarea",
      x: "finanziato",
      fill: "macroarea",
      sort: {y: "-x"},
      tip: {format: {x: d => euroCompact(d)}}
    }),
    Plot.ruleX([0])
  ]
})
```

> **Nota**: la macroarea indica la localizzazione prevalente del progetto. "Centro-Nord" include le regioni del Centro e del Nord Italia, "Mezzogiorno" include Abruzzo, Molise, Campania, Puglia, Basilicata, Calabria, Sicilia e Sardegna.

---

## Risorse per tema

Quali ambiti ricevono più finanziamenti? Ricerca e innovazione, trasporti e ambiente sono tra i temi più finanziati, ma il mix cambia sensibilmente tra un ciclo e l'altro.

```js
// Aggregazione per tema sintetico
const perTema = d3.rollups(
  cicloData,
  v => ({
    finanziato: d3.sum(v, d => d.FINANZ_TOTALE_PUBBLICO),
  }),
  d => d.OC_TEMA_SINTETICO
).map(([key, val]) => ({tema: key, ...val}))
 .sort((a, b) => b.finanziato - a.finanziato);
```

```js
Plot.plot({
  title: `Risorse per tema — ${cicloSel}`,
  width: 800,
  height: Math.max(300, perTema.length * 30 + 40),
  marginLeft: 180,
  y: {label: null, tickSize: 0},
   x: {grid: true, label: "euro", tickFormat: d => euroCompact(d)},
  color: {scheme: "Spectral"},
  marks: [
    Plot.barX(perTema, {
      y: "tema",
      x: "finanziato",
      fill: "finanziato",
      sort: {y: "-x"},
      tip: {format: {x: d => euroCompact(d)}}
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Dettaglio per macroarea e ciclo

```js
// Dati aggregati per macroarea × ciclo (tutti i cicli)
const perMacroareaCiclo = d3.rollups(
  data,
  v => ({
    finanziato: d3.sum(v, d => d.FINANZ_TOTALE_PUBBLICO),
    pagato: d3.sum(v, d => d.TOT_PAGAMENTI),
    tasso: (d3.sum(v, d => d.FINANZ_TOTALE_PUBBLICO) > 0
      ? (d3.sum(v, d => d.TOT_PAGAMENTI) / d3.sum(v, d => d.FINANZ_TOTALE_PUBBLICO)) * 100
      : 0)
  }),
  d => d.OC_DESCR_CICLO,
  d => d.OC_MACROAREA
).flatMap(([ciclo, macroMap]) =>
  Array.from(macroMap, ([macroarea, val]) => ({
    ciclo,
    macroarea,
    finanziato: val.finanziato,
    pagato: val.pagato,
    tasso_pagamento: val.tasso,
  }))
).sort((a, b) => a.ciclo.localeCompare(b.ciclo) || a.macroarea.localeCompare(b.macroarea));
```

```js
const { header, format } = tableFormat({
  ciclo: { label: "Ciclo", fmt: "string" },
  macroarea: { label: "Macroarea", fmt: "string" },
  finanziato: { label: "Finanziato", fmt: "euroCompact" },
  pagato: { label: "Pagato", fmt: "euroCompact" },
  tasso_pagamento: { label: "Tasso pagamento", fmt: "pct" },
});
```

```js
Inputs.table(perMacroareaCiclo, {
  columns: ["ciclo", "macroarea", "finanziato", "pagato", "tasso_pagamento"],
  header,
  format,
  rows: 15,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: il ciclo 2021-2027 è ancora in corso. I dati parziali (finanziamenti programmati vs effettivamente spesi) non vanno confrontati come definitivi con i cicli chiusi.
- **Valori nominali**: le cifre non sono rivalutate per inflazione. I confronti tra cicli distanti (es. 2007-2013 vs 2021-2027) vanno letti con cautela.
- **Macroarea**: la disaggregazione territoriale è limitata alla macroarea (Centro-Nord / Mezzogiorno). Non è possibile scendere al dettaglio regionale con questo dataset.

---

## Risorse

- [OpenCoesione (fonte originale)](https://opencoesione.gov.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/opencoesione_progetti/2026/opencoesione_progetti_2026_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/opencoesione-progetti)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)

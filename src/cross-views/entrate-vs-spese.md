---
title: "Entrate vs Spese — Il Bilancio dello Stato"
description: "Confronto aggregato tra entrate e spese dello Stato: saldo e rapporto di copertura per anno, 2008–2024"
source: MEF — RGS · BDAP
source_url: https://bdap.rgs.mef.gov.it/
period: "2008–2024"
data_driven: true
cross_view: true
datasets:
  - bdap_entrate_stato
  - bdap_spese_stato
---

# Entrate vs Spese — il bilancio dello Stato in un'occhiata

**Nel ${last.anno} le entrate dello Stato superano le spese di ${euroCompact(saldoLast)} — un avanzo di bilancio. I saldi negativi sono rari: si sono verificati in ${rows.filter(d => d.saldo < 0).length} anni su ${rows.length}, ma il ${worstRapporto.anno} ha registrato un deficit senza precedenti (${euroCompact(Math.abs(worst.saldo))}), legato alle misure pandemiche. Da allora il bilancio è tornato in pareggio, anche se il surplus si è ridotto: ${euroCompact(avgPost)} nel periodo ${post2020[0].anno}–${last.anno}, contro ${euroCompact(avgPre)} nel ${pre2020[0].anno}–${pre2020[pre2020.length-1].anno}.**

Questa cross-view confronta le **entrate totali** (previsioni definitive, BDAP) con le **spese totali** per ogni anno dal ${first.anno} al ${last.anno}. Mostra il saldo di bilancio e il rapporto di copertura.

```js
import { euroCompact, pct, numFix, tableFormat } from "../import/format-utils.js";
```

```js
const rows = await FileAttachment("../data/entrate-vs-spese.json").json();
```

```js
const last = rows[rows.length - 1];
const first = rows[0];
const saldoLast = last.saldo;
const rapportoLast = last.rapporto_spese_entrate;

// Saldo minimo (anno peggiore) e rapporto massimo
const worst = rows.reduce((min, d) => d.saldo < min.saldo ? d : min, rows[0]);
const worstRapporto = rows.reduce((max, d) => d.rapporto_spese_entrate > max.rapporto_spese_entrate ? d : max, rows[0]);
// Media saldo pre-2020 e post-2020
const pre2020 = rows.filter(d => d.anno <= 2019);
const post2020 = rows.filter(d => d.anno >= 2020);
const avgPre = pre2020.length ? d3.mean(pre2020, d => d.saldo) : null;
const avgPost = post2020.length ? d3.mean(post2020, d => d.saldo) : null;
```

<div class="grid grid-cols-4">
  <div class="card"><h3>Entrate ${last.anno}</h3><span class="big">${euroCompact(last.totale_entrate)}</span></div>
  <div class="card"><h3>Spese ${last.anno}</h3><span class="big">${euroCompact(last.totale_spese)}</span></div>
  <div class="card"><h3>Saldo ${last.anno}</h3><span class="big" style="color: ${saldoLast < 0 ? '#d62728' : '#2ca02c'}">${euroCompact(saldoLast)}</span></div>
  <div class="card"><h3>Rapporto spese/entrate</h3><span class="big">${pct(rapportoLast * 100)}</span></div>
</div>

Nel ${last.anno} le entrate dello Stato valgono **${euroCompact(last.totale_entrate)}**, le spese **${euroCompact(last.totale_spese)}**. Il saldo è di **${euroCompact(saldoLast)}**. Rispetto al ${first.anno}, il rapporto spese/entrate è passato dal **${pct(first.rapporto_spese_entrate * 100)}** al **${pct(rapportoLast * 100)}**.

## 1. Entrate e Spese nel tempo — ${first.anno}–${last.anno}

Il grafico mostra l'andamento delle entrate e delle spese dello Stato. I saldi negativi si concentrano in due periodi: gli anni della crisi (${rows.filter(d => d.saldo < 0 && d.anno < 2020).map(d => d.anno).join(", ")}) e il ${worstRapporto.anno} (COVID). Negli anni successivi entrate e spese sono tornate vicine, con le entrate leggermente superiori.

```js
const plot = await import("npm:@observablehq/plot");
display(plot.plot({
  title: `Entrate e Spese dello Stato — ${first.anno}–${last.anno}`,
  width: 800, height: 360,
  x: {tickFormat: String},
  y: {grid: true, label: null, tickFormat: d => (d / 1e9).toFixed(0) + " B€"},
  marks: [
    plot.areaY(rows.filter(d => d.totale_entrate >= d.totale_spese), {x: "anno", y1: "totale_spese", y2: "totale_entrate", fill: "#2ca02c", fillOpacity: 0.25, curve: "catmull-rom"}),
    plot.areaY(rows.filter(d => d.totale_spese > d.totale_entrate), {x: "anno", y1: "totale_entrate", y2: "totale_spese", fill: "#d62728", fillOpacity: 0.25, curve: "catmull-rom"}),
    plot.line(rows, {x: "anno", y: "totale_entrate", stroke: "#2c7fb8", strokeWidth: 2.5}),
    plot.line(rows, {x: "anno", y: "totale_spese", stroke: "#d62728", strokeWidth: 2.5}),
    plot.dot(rows, {x: "anno", y: "totale_entrate", fill: "#fff", stroke: "#2c7fb8", r: 3.5, tip: true, channels: {Spese: "totale_spese"}, format: {x: String, y: euroCompact, Spese: euroCompact}}),
    plot.dot(rows, {x: "anno", y: "totale_spese", fill: "#fff", stroke: "#d62728", r: 3.5, tip: true, channels: {Entrate: "totale_entrate"}, format: {x: String, y: euroCompact, Entrate: euroCompact}})
  ]
}))
```

La **zona verde** è dove le entrate superano le spese (surplus), la **zona rossa** è dove le spese superano le entrate (deficit).

## 2. Il saldo di bilancio — ${first.anno}–${last.anno}

Il saldo è la differenza tra entrate e spese. Un saldo negativo significa che lo Stato spende più di quanto incassa, finanziando la differenza con debito.

```js
display(plot.plot({
  title: "Saldo di bilancio dello Stato",
  width: 800, height: 300,
  x: {tickFormat: String},
  y: {grid: true, label: "saldo (entrate - spese)", tickFormat: d => (d / 1e9).toFixed(0) + " B€"},
  marks: [
    plot.ruleY([0], {stroke: "#888"}),
    plot.barY(rows, {
      x: "anno", y: "saldo",
      fill: d => d.saldo >= 0 ? "#2ca02c" : "#d62728",
      tip: true
    }),
    plot.text(rows.filter(d => d.anno === last.anno), {
      x: "anno", y: "saldo",
      text: d => " " + euroCompact(d.saldo),
      dx: 8, dy: -8, fontSize: 11, textAnchor: "start"
    })
  ]
}))
```

L'anno peggiore è stato il **${worst.anno}** con un saldo di **${euroCompact(worst.saldo)}**. La media del saldo pre-2020 era di **${euroCompact(avgPre)}**, mentre post-2020 è di **${euroCompact(avgPost)}**.

## 3. Il rapporto spese/entrate — superare il 100%

Quando il rapporto supera il 100%, le spese superano le entrate. Il ${worstRapporto.anno} ha registrato il rapporto più alto della serie (${pct(worstRapporto.rapporto_spese_entrate * 100)}), ma non è stato l'unico anno sopra la parità: anche nel ${rows.filter(d => d.rapporto_spese_entrate > 1 && d.anno !== worstRapporto.anno).map(d => d.anno).join(" e nel ")} le spese hanno superato le entrate. Negli anni successivi al ${worstRapporto.anno} il rapporto è tornato sotto la parità.

```js
display(plot.plot({
  title: "Rapporto spese / entrate — quando le spese superano le entrate",
  width: 800, height: 300,
  x: {tickFormat: String},
  y: {grid: true, domain: [0.9, 1.1], label: "rapporto spese/entrate"},
  marks: [
    plot.ruleY([1], {stroke: "#d95f0e", strokeDasharray: "4 4"}),
    plot.line(rows, {x: "anno", y: "rapporto_spese_entrate", stroke: "#2c7fb8", strokeWidth: 2}),
    plot.dot(rows, {x: "anno", y: "rapporto_spese_entrate", fill: "#fff", stroke: "#2c7fb8"}),
    plot.text(rows.filter(d => d.anno === last.anno), {
      x: "anno", y: "rapporto_spese_entrate",
      text: d => " " + pct(d.rapporto_spese_entrate * 100),
      dx: 8, dy: -8, fontSize: 11
    })
  ]
}))
```

La linea tratteggiata è la parità (100%). Sopra = le spese superano le entrate.

---

## Dettaglio annuale

<small>Entrate, spese, saldo e rapporto per ogni anno. Il saldo negativo indica che lo Stato spende più di quanto incassa.</small>

```js
const { header, format } = tableFormat({
  anno: { label: "Anno", fmt: "string" },
  totale_entrate: { label: "Entrate", fmt: "euroCompact" },
  totale_spese: { label: "Spese", fmt: "euroCompact" },
  saldo: { label: "Saldo", fmt: "euroCompact" },
  rapporto_spese_entrate: { label: "Rapporto", fmt: "pct" },
});
```

```js
const table = rows.map(d => ({
  anno: String(d.anno),
  totale_entrate: d.totale_entrate,
  totale_spese: d.totale_spese,
  saldo: d.saldo,
  rapporto_spese_entrate: d.rapporto_spese_entrate * 100,
}));
```

```js
Inputs.table(table, {
  columns: ["anno", "totale_entrate", "totale_spese", "saldo", "rapporto_spese_entrate"],
  header,
  format,
  rows: rows.length,
  width: "100%",
  sort: "anno",
  reverse: true
})
```

---

## Limiti

- **Previsioni, non consuntivo**: i valori delle entrate e delle spese sono le previsioni definitive del bilancio, non gli incassi/pagamenti effettivi; la differenza con il consuntivo può essere significativa.
- **Copertura**: la serie parte dal ${first.anno} (contabilità armonizzata dello Stato); gli anni precedenti non sono comparabili.
- **Aggregazione**: questa vista mostra il totale aggregato; per il dettaglio per titolo o missione, vedi le pagine dei singoli dataset.

## Risorse

- [Cross-view definition](https://github.com/dataciviclab/data-explorer/blob/main/cross-views/defs/entrate-vs-spese.sql) — SQL riutilizzabile da MCP, dashboard, notebook
- [Entrate dello Stato](/dataset/entrate-stato) — dettaglio per titolo
- [Previsione vs Consuntivo](/cross-views/previsione-vs-consuntivo) — dettaglio per missione
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Pipeline entrate](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/bdap-entrate-stato) · [Pipeline spese](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/bdap-spese-stato)

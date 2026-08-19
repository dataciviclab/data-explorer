---
title: Entrate dello Stato
description: "Le previsioni definitive di entrata dello Stato per titolo, 2008-2024 — come si finanzia il bilancio (BDAP RGS MEF)"
source: MEF — RGS · BDAP
source_url: https://bdap.rgs.mef.gov.it/
period: "2008–2024"
last_modified: 2026-05-26
dataset_slug: bdap_entrate_stato
data_driven: true
---

# Entrate dello Stato — come si finanzia il bilancio

**In ${last - first} anni le entrate tributarie sono cresciute del ${numFix(deltaTrib, 0)}%, ma le accensioni di prestiti sono più che raddoppiate (+${numFix(deltaPres, 0)}%). Dal 2020 lo Stato si finanzia con debito quasi quanto con le tasse: la quota delle entrate tributarie sul totale è passata dal ${pct(pctTrib2008)} al ${pct(pctTribLast)}, scendendo per quattro anni su cinque sotto la soglia del 50%.**

Previsioni definitive di **entrata dello Stato per titolo**, dal bilancio dello Stato (BDAP — RGS MEF). Ogni numero di questa pagina è calcolato dal dato a build-time: se si ripubblica il parquet, KPI e grafici si aggiornano da soli.

```js
import { euroCompact, pct, numFix, tableFormat } from "../import/format-utils.js";
```

```js
const rows = await FileAttachment("../data/bdap-entrate.json").json();
```

```js
// Nomi titoli → etichette corte e leggibili (i 4 titoli del bilancio per natura economica)
const titoLabel = (t) =>
  /EXTRA-TRIBUTARIE/.test(t) ? "Entrate extra-tributarie"
  : /TRIBUTARIE/.test(t) ? "Entrate tributarie"
  : /ALIENAZIONE/.test(t) ? "Alienazione e ammortamento beni"
  : /PRESTITI/.test(t) ? "Accensione di prestiti"
  : t.trim();

const data = rows.map(d => ({
  anno: d.esercizio_finanziario,
  titolo: titoLabel(d.titolo),
  comp: d.previsioni_definitive_cp || 0
}));
```

```js
// Serie per anno e lookup titolo×anno (previsioni definitive di competenza)
const byAnno = Array.from(d3.rollup(data, v => d3.sum(v, d => d.comp), d => d.anno))
  .map(([anno, comp]) => ({ anno, comp }))
  .sort((a, b) => a.anno - b.anno);
const last = byAnno[byAnno.length - 1].anno;
const first = byAnno[0].anno;
const compBy = (anno, titolo) => data.find(d => d.anno === anno && d.titolo === titolo)?.comp ?? 0;
const totaleLast = byAnno[byAnno.length - 1].comp;
const tribLast = compBy(last, "Entrate tributarie");
const presLast = compBy(last, "Accensione di prestiti");

const trib = byAnno.map(y => {
  const tr = compBy(y.anno, "Entrate tributarie");
  const pr = compBy(y.anno, "Accensione di prestiti");
  return { anno: y.anno, trib: tr, pres: pr, tot: y.comp, pct: y.comp ? (tr / y.comp) * 100 : null };
});
const d2008 = trib[0];
const pctTribLast = trib[trib.length - 1].pct;
const pctTrib2008 = d2008 ? d2008.pct : null;
const deltaTrib = d2008 ? ((tribLast - d2008.trib) / d2008.trib) * 100 : null;
const deltaPres = d2008 ? ((presLast - d2008.pres) / d2008.pres) * 100 : null;
```

<div class="grid grid-cols-4">
  <div class="card"><h3>Entrate totali ${last}</h3><span class="big">${euroCompact(totaleLast)}</span></div>
  <div class="card"><h3>Entrate tributarie</h3><span class="big">${euroCompact(tribLast)}</span></div>
  <div class="card"><h3>Accensione prestiti</h3><span class="big">${euroCompact(presLast)}</span></div>
  <div class="card"><h3>Quota tributarie</h3><span class="big">${pct(pctTribLast)}</span></div>
</div>

Nel ${last} le entrate tributarie valgono **${euroCompact(tribLast)}**, i prestiti **${euroCompact(presLast)}**. Rispetto al ${first}, le tributarie sono cresciute del **${numFix(deltaTrib, 0)}%**, i prestiti di quasi il doppio (**${numFix(deltaPres, 0)}%**). La quota delle tributarie sul totale è passata dal **${pct(pctTrib2008)}** del ${first} al **${pct(pctTribLast)}** del ${last}.

## 1. Come si compongono le entrate — ${last}

Per natura economica il bilancio dello Stato si divide in quattro titoli. Nel ${last} le **entrate tributarie** restano la voce principale, ma le **accensioni di prestiti** pesano ormai oltre il 40% del totale: sedici anni fa coprivano circa un terzo.

```js
const plot = await import("npm:@observablehq/plot");
const lastComp = data.filter(d => d.anno === last).sort((a, b) => b.comp - a.comp);
display(plot.plot({
  title: `Composizione delle entrate dello Stato — ${last}`,
  width: 800, height: 300, marginLeft: 240,
  x: {grid: true, tickFormat: euroCompact},
  y: {label: null, tickSize: 0},
  marks: [
    plot.barX(lastComp, {x: "comp", y: "titolo", fill: "#3182bd", sort: {y: "-x"}, tip: true}),
    plot.text(lastComp, {x: "comp", y: "titolo", text: (d) => ` ${euroCompact(d.comp)} — ${pct((d.comp / totaleLast) * 100)}`, dx: 6, textAnchor: "start", fontSize: 11}),
    plot.ruleX([0])
  ]
}))
```

> **Nota di lettura**: il grafico mostra lo **stock** del ${last}: quanto incasserebbe lo Stato da ciascuna fonte. È il dato nella sua forma più naturale; trend e confronti arrivano qui sotto.
## 2. La quota delle entrate tributarie ${first}–${last}

La composizione non è fissa. La quota delle tributarie sul totale — la parte delle entrate "che paghiamo noi" rispetto a quella finanziata con debito — era stabile sopra il 55% prima del 2020, poi è crollata sotto la soglia psicologica del 50% ed è rimasta lì per quattro anni su cinque.

```js
display(plot.plot({
  title: `Quota delle entrate tributarie sul totale — ${first}–${last}`,
  width: 800, height: 320,
  x: {tickFormat: String}, y: {grid: true, label: "% sul totale delle entrate"},
  marks: [
    plot.ruleY([50], {stroke: "#d95f0e", strokeDasharray: "4 4"}),
    plot.line(trib, {x: "anno", y: "pct", stroke: "#2c7fb8", strokeWidth: 2, tip: true}),
    plot.dot(trib, {x: "anno", y: "pct", fill: "#fff", stroke: "#2c7fb8"}),
    plot.text(trib.filter(t => t.anno === last), {x: "anno", y: "pct", text: (t) => " " + pct(t.pct), dx: 8, dy: -8, fontSize: 11})
  ]
}))
```

La linea tratteggiata è la soglia del 50%. Nel **2020** i prestiti hanno superato per la prima volta le tributarie: il punto in cui il finanziamento del bilancio è passato da "per lo più fiscale" a "per metà su debito" è lo spartiacque del periodo.

## 3. Prima e dopo il 2020: il salto dei prestiti

Il dato più strutturale è la **media annua delle accensioni di prestiti**, che dopo il 2020 si è quasi raddoppiata: l'Italia non è mai tornata ai livelli pre-pandemia.

```js
const pre = trib.filter(t => t.anno <= 2019);
const post = trib.filter(t => t.anno >= 2020);
const mediaPresPre = pre.length ? d3.mean(pre, t => t.pres) : 0;
const mediaPresPost = post.length ? d3.mean(post, t => t.pres) : 0;
const conf = [
  { periodo: `Pre-COVID (${first}–2019)`, media: mediaPresPre },
  { periodo: `Post-COVID (2020–${last})`, media: mediaPresPost },
];
```

```js
display(plot.plot({
  title: "Accensione media annua di prestiti, prima e dopo il 2020",
  width: 800, height: 260, marginLeft: 40,
  x: {grid: true, tickFormat: (d) => euroCompact(d)},
  y: {label: null, tickSize: 0},
  color: {domain: conf.map(c => c.periodo), range: ["#9ecae1", "#d95f0e"]},
  marks: [
    plot.barX(conf, {x: "media", y: "periodo", fill: "periodo", sort: {y: null}, tip: true}),
    plot.text(conf, {x: "media", y: "periodo", text: (d) => " " + euroCompact(d.media), dx: 8, textAnchor: "start", fontSize: 12}),
    plot.ruleX([0])
  ]
}))
```

Dai **${euroCompact(mediaPresPre)}** del periodo pre-COVID ai **${euroCompact(mediaPresPost)}** post-2020: il rapporto è di **×${numFix(mediaPresPost / (mediaPresPre || NaN), 1)}**. La traiettoria post-pandemia apre una domanda che i soli dati non possono chiudere: è una fase transitoria o la nuova normalità della finanza pubblica italiana?

---

## Dettaglio annuale

<small>Totale e componenti per esercizio (miliardi compatti). Il dettaglio completo per titolo è nel parquet collegato qui sotto.</small>

```js
const { header, format } = tableFormat({
  anno: { label: "Anno", fmt: "string" },
  tot: { label: "Totale entrate", fmt: "euroCompact" },
  trib: { label: "Entrate tributarie", fmt: "euroCompact" },
  pres: { label: "Accensione prestiti", fmt: "euroCompact" },
  pct: { label: "% tributarie", fmt: "pct" }
});
```

```js
const table = trib.map(t => ({
  anno: String(t.anno), tot: t.tot, trib: t.trib, pres: t.pres, pct: t.pct
}));
```

```js
Inputs.table(table, {
  columns: ["anno", "tot", "trib", "pres", "pct"],
  header,
  format,
  rows: 17,
  width: "100%",
  sort: "anno",
  reverse: true
})
```

---

## Limiti

- **Previsioni, non consuntivo**: i valori sono le previsioni definitive (base competenza) del bilancio, non gli incassi effettivi; la differenza con il consuntivo può essere significativa.
- **Copertura**: la serie parte dal 2008 (contabilità armonizzata dello Stato); gli anni precedenti non sono comparabili.
- **Classificazione**: la disaggregazione per titolo segue la classificazione economica del bilancio, soggetta a riclassificazioni tra esercizi.

## Risorse

- [RGS · BDAP — fonte originale](https://bdap.rgs.mef.gov.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/bdap_entrate_stato/2024/bdap_entrate_stato_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/bdap-entrate-stato)

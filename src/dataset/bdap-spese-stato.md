---
title: Spese dello Stato
description: "Le previsioni definitive di spesa dello Stato per amministrazione e missione, 2008-2024 — chi spende e in cosa (BDAP RGS MEF)"
source: MEF — RGS · BDAP
source_url: https://www.rgs.mef.gov.it/
period: "2008–2024"
last_modified: 2026-08-19
dataset_slug: bdap_spese_stato
data_driven: true
---

# Spese dello Stato — chi spende e in cosa

**In ${last - first} anni la spesa statale è cresciuta del ${numFix(deltaPct, 0)}% (da ${numFix(d2008.spesa / 1e9, 0)} a ${numFix(totLast / 1e9, 0)} miliardi), con il salto del 2020 legato alle misure pandemiche. Ma la spesa è fortemente concentrata: ${top.amministrazione.toLowerCase()} vale da solo ${pct(topShare)} del totale, e le prime voci obbligate — debito pubblico, relazioni finanziarie e previdenza — assorbono ${pct(voceShare)} della spesa.**

Previsioni definitive di **spesa dello Stato per amministrazione e missione** (BDAP — RGS MEF). Ogni numero è calcolato dal dato a build-time: se si ripubblica il parquet, KPI e grafici si aggiornano da soli.

```js
import { num, euroCompact, pct, numFix, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/bdap-spese-stato.json").json();
```

```js
const byAnno = Array.from(d3.rollup(data, v => d3.sum(v, d => d.spesa_cp), d => d.anno))
  .map(([anno, spesa]) => ({ anno, spesa }))
  .sort((a, b) => a.anno - b.anno);
const last = byAnno[byAnno.length - 1].anno;
const first = byAnno[0].anno;
const minimo = byAnno.reduce((m, x) => x.spesa < m.spesa ? x : m, byAnno[0]);
const totLast = byAnno[byAnno.length - 1].spesa;
const d2008 = byAnno[0];
const deltaPct = d2008 ? ((totLast - d2008.spesa) / d2008.spesa) * 100 : null;

const lastRows = data.filter(d => d.anno === last);
const perAmm = Array.from(
  d3.rollup(lastRows, v => d3.sum(v, d => d.spesa_cp), d => d.amministrazione),
  ([amministrazione, spesa]) => ({ amministrazione, spesa })
).sort((a, b) => b.spesa - a.spesa);
const perMis = Array.from(
  d3.rollup(lastRows, v => d3.sum(v, d => d.spesa_cp), d => d.missione),
  ([missione, spesa]) => ({ missione, spesa })
).sort((a, b) => b.spesa - a.spesa);
const nAmm = perAmm.length;
const nMis = perMis.length;
const top = perAmm[0];
const topShare = totLast ? (top.spesa / totLast) * 100 : null;
const voceShare = totLast
  ? (perMis.filter(m => m.missione.includes("Debito pubblico") || m.missione.includes("Relazioni finanziarie") || m.missione.includes("Politiche previdenziali")).reduce((s, m) => s + m.spesa, 0) / totLast) * 100
  : null;
```

<div class="grid grid-cols-4">
  <div class="card"><h3>Spesa totale ${last}</h3><span class="big">${euroCompact(totLast)}</span></div>
  <div class="card"><h3>Δ ${first}→${last}</h3><span class="big">${deltaPct >= 0 ? "+" : ""}${numFix(deltaPct, 0)}%</span></div>
  <div class="card"><h3>Amministrazioni</h3><span class="big">${num(nAmm)}</span></div>
  <div class="card"><h3>Missioni</h3><span class="big">${num(nMis)}</span></div>
</div>

## 1. Chi spende — la spesa per amministrazione (${last})

Per natura, la spesa si articola per amministrazione. Il quadro del ${last} è dominato da un solo attore, il Ministero dell'Economia, che gestisce da solo oltre ${pct(topShare)} del totale (interessi sul debito, relazioni finanziarie e gran parte delle partite "obbligate").

```js
const plot = await import("npm:@observablehq/plot");
display(plot.plot({
  title: `Spesa per amministrazione — ${last}`,
  width: 800, height: 400, marginLeft: 150,
  x: {grid: true, tickFormat: plot.formatNumber},
  y: {label: null, tickSize: 0},
  color: {scheme: "Blues"},
  marks: [
    plot.barX(perAmm, {x: "spesa", y: "amministrazione", fill: "spesa", sort: {y: "-x"}, tip: true}),
    plot.text(perAmm, {x: "spesa", y: "amministrazione", text: (d) => ` ${euroCompact(d.spesa)} — ${pct((d.spesa / totLast) * 100)}`, dx: 6, textAnchor: "start", fontSize: 10}),
    plot.ruleX([0])
  ]
}))
```

> **Nota di lettura**: mostra lo **stock** del ${last}: quanto spende ogni ministero. È il dato nella sua forma naturale; il trend e la composizione per missione arrivano qui sotto.

## 2. Il trend ${first}–${last}: crescita e scatto del 2020

Nel complesso la spesa è cresciuta per quasi tutto il periodo, con un plateau/rimbalzi nella prima parte del decennio e lo **scatto strutturale del 2020** (misure pandemiche) da cui non si è più tornati indietro.

```js
display(plot.plot({
  title: `Spesa totale dello Stato — ${first}–${last}`,
  width: 800, height: 320,
  x: {tickFormat: String}, y: {grid: true, tickFormat: (d) => euroCompact(d)},
  marks: [
    plot.lineY(byAnno, {x: "anno", y: "spesa", stroke: "#3182bd", strokeWidth: 2, tip: {format: {y: (d) => euroCompact(d)}}}),
    plot.dot(byAnno, {x: "anno", y: "spesa", fill: "#fff", stroke: "#3182bd"}),
    plot.dot(byAnno.filter(d => d.anno === minimo.anno), {x: "anno", y: "spesa", fill: "#d95f0e", r: 4, tip: true}),
    plot.ruleY([byAnno[0].spesa], {stroke: "#999", strokeDasharray: "4 4"})
  ]
}))
```

La linea tratteggiata è il livello del ${first}; il punto arancione segna il minimo della serie (${minimo.anno}).

## 3. In cosa si spende — le missioni (${last})

Guardando per **missione** (classificazione COFOG), emergono le voci che da sole spiegano la concentrazione: gli **interessi sul debito pubblico**, le **relazioni finanziarie** con gli enti territoriali e le **politiche previdenziali** sono le prime tre voci di spesa.

```js
const perMisTop = perMis.slice(0, 12);
display(plot.plot({
  title: `Spesa per missione — ${last} (top 12)`,
  width: 800, height: 380, marginLeft: 190,
  x: {grid: true, tickFormat: plot.formatNumber},
  y: {label: null, tickSize: 0},
  color: {scheme: "Oranges"},
  marks: [
    plot.barX(perMisTop, {x: "spesa", y: "missione", fill: "spesa", sort: {y: "-x"}, tip: true}),
    plot.text(perMisTop, {x: "spesa", y: "missione", text: (d) => ` ${euroCompact(d.spesa)} — ${pct((d.spesa / totLast) * 100)}`, dx: 6, textAnchor: "start", fontSize: 10}),
    plot.ruleX([0])
  ]
}))
```
---

## Dettaglio ${last} per amministrazione e missione

<small>Righe amministrazione×missione per l'anno più recente (${last}). Cerca un amministrazione o una voce.</small>

```js
const { header, format } = tableFormat({
  amministrazione: { label: "Amministrazione", fmt: "string" },
  missione: { label: "Missione", fmt: "string" },
  spesa_cp: { label: "Spesa (competenza)", fmt: "euroCompact" },
  spesa_cs: { label: "Spesa (cassa)", fmt: "euroCompact" }
});
```

```js
const searchQuery = view(Inputs.search(lastRows, {placeholder: "cerca ministero o missione…", label: "Cerca"}));
```

```js
Inputs.table(searchQuery, {
  columns: ["amministrazione", "missione", "spesa_cp", "spesa_cs"],
  header,
  format,
  rows: 20,
  width: "100%",
  sort: "spesa_cp",
  reverse: true
})
```

---

## Limiti

- **Copertura**: la serie copre il periodo 2008-2024 (unico file BDAP multi-anno); anni precedenti non comparabili.
- **Previsioni definitive**: i valori sono previsioni di spesa definitive (base competenza), non spese effettivamente sostenute; possono differire dai consuntivi.
- **Amministrazioni**: la denominazione può cambiare nel periodo (fusioni/scissioni di ministeri); i dati riflettono la denominazione al momento della previsione.
- **Missioni**: la classificazione segue il COFOG; alcune denominazioni variano leggermente tra gli anni.

## Risorse

- [MEF · RGS · BDAP (fonte originale)](https://www.rgs.mef.gov.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/bdap_spese_stato/2024/bdap_spese_stato_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/bdap-spese-stato)
La spesa è passata da **${euroCompact(d2008.spesa)}** nel ${first} a **${euroCompact(totLast)}** nel ${last}, toccando il minimo della serie nel **${minimo.anno}** (${euroCompact(minimo.spesa)}). Il **2020** segna lo scatto pandemico: da lì il livello non è più sceso. La crescita, però, è trainata soprattutto da voci "obbligate" concentrate al centro: ${top.amministrazione.toLowerCase()} vale ${pct(topShare)} e debito+relazioni+previdenza pesano ${pct(voceShare)}.

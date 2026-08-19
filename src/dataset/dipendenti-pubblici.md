---
title: Dipendenti pubblici per comparto
description: "Il pubblico impiego dal 2010 al 2024: declino, svolta e composizione di genere per comparto (BDAP RGS MEF)"
source: MEF — RGS · BDAP
source_url: https://www.rgs.mef.gov.it/
period: "2010–2024"
last_modified: 2026-08-19
dataset_slug: dipendenti_pubblici
data_driven: true
---

# Dipendenti pubblici — declino, svolta e divari

**La PA italiana ha smesso di rimpicciolirsi. Dopo un calo ininterrotto fino al ${minimo.anno} (${numFix(minimo.tot / 1e6, 2)} milioni di dipendenti), nel ${last} si supera quota ${numFix(totLast / 1e6, 2)} milioni. Ma la ripresa non è diffusa: la crescita è trainata quasi solo da Istruzione e Sanità, mentre funzioni centrali e locali continuano a perdere personale. E la PA resta un mondo a forte prevalenza femminile (${pct(donnePctLast)}), con divari enormi tra comparti.**

Dati BDAP/RGS sul pubblico impiego per **comparto, genere e orario di lavoro**, dal 2010 al 2024. Ogni numero è calcolato dal dato a build-time: se si ripubblica il parquet, KPI e grafici si aggiornano da soli.

```js
import { num, pct, numFix, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/dipendenti-pubblici.json").json();
```

```js
// Serie per anno e per comparto (stock, non saldo netto)
const byAnno = Array.from(d3.rollup(data, v => ({
  tot: d3.sum(v, d => d.totale),
  donne: d3.sum(v, d => d.donne),
  uomini: d3.sum(v, d => d.uomini)
}), d => d.anno))
  .map(([anno, v]) => ({ anno, ...v }))
  .sort((a, b) => a.anno - b.anno);
const first = byAnno[0].anno;
const last = byAnno[byAnno.length - 1].anno;
const y = a => byAnno.find(x => x.anno === a);
const minimo = byAnno.reduce((m, x) => x.tot < m.tot ? x : m, byAnno[0]);
const totLast = y(last).tot;
const deltaAbs = totLast - byAnno[0].tot;
const deltaPct = byAnno[0].tot ? (deltaAbs / byAnno[0].tot) * 100 : null;
const donnePctLast = totLast ? (y(last).donne / totLast) * 100 : null;
const caloMin = byAnno[0].tot - minimo.tot;
```

```js
// Stock per comparto nell'anno più recente + variazione dal primo anno
const stockLast = data.filter(d => d.anno === last)
  .map(d => ({ comparto: d.comparto, totale: d.totale, donne: d.donne, pctDonne: d.totale ? (d.donne / d.totale) * 100 : null }))
  .sort((a, b) => b.totale - a.totale);
const comparti = data.filter(d => d.anno === first).map(d => d.comparto);
const varOf = c => {
  const a = data.find(d => d.anno === first && d.comparto === c)?.totale ?? 0;
  const b = data.find(d => d.anno === last && d.comparto === c)?.totale ?? 0;
  return { a, b, var: b - a, pct: a ? ((b - a) / a) * 100 : null };
};
const deltaCp = comparti.map(c => ({ comparto: c, ...varOf(c) })).sort((x, z) => z.var - x.var);
const cresciuti = deltaCp.filter(c => c.var > 0);
const inCalo = deltaCp.filter(c => c.var < 0);
const varNamed = sub => deltaCp.find(c => c.comparto.includes(sub));
const istruzione = varNamed("ISTRUZIONE");
const sanita = varNamed("SANITA");
const funzLocali = varNamed("FUNZIONI LOCALI");
const funzCentrali = varNamed("FUNZIONI CENTRALI");
```

<div class="grid grid-cols-4">
  <div class="card"><h3>Dipendenti ${last}</h3><span class="big">${num(totLast)}</span></div>
  <div class="card"><h3>Minimo della serie</h3><span class="big">${num(minimo.tot)}</span><small style="opacity:0.7">nel ${minimo.anno}</small></div>
  <div class="card"><h3>Δ ${first}→${last}</h3><span class="big">${deltaAbs >= 0 ? "+" : ""}${num(deltaAbs)}</span></div>
  <div class="card"><h3>Donne ${last}</h3><span class="big">${pct(donnePctLast)}</span></div>
</div>

Dal **${first}** al **${minimo.anno}** il pubblico impiego si è ridotto di ${num(caloMin)} unità, effetto del blocco del turnover e dei tagli. Poi la curva ha cambiato direzione e nel **${last}** si contano **${num(totLast)}** dipendenti, più del punto di partenza. Ma la crescita è concentrata in pochi comparti: **Istruzione e Ricerca (${istruzione.var > 0 ? "+" : ""}${num(istruzione.var)})** e **Sanità (${sanita.var > 0 ? "+" : ""}${num(sanita.var)})** crescono, mentre **Funzioni Locali (${num(funzLocali.var)})** e **Centrali (${num(funzCentrali.var)})** continuano a calare.
## 1. Chi lavora nella PA — lo stock ${last}

Per natura, il pubblico impiego si divide in comparti di contrattazione. Il quadro del ${last} è dominato da Istruzione e Ricerca, che da sola impiega più di un terzo del totale, davanti a Sanità e alle funzioni amministrative.

```js
const plot = await import("npm:@observablehq/plot");
display(plot.plot({
  title: `Dipendenti pubblici per comparto — ${last}`,
  width: 800, height: 360, marginLeft: 150,
  x: {grid: true, tickFormat: (d) => numFix(d / 1e6, 1) + " M"},
  y: {label: null, tickSize: 0},
  marks: [
    plot.barX(stockLast, {x: "totale", y: "comparto", fill: "#3182bd", sort: {y: "-x"}, tip: true}),
    plot.text(stockLast, {x: "totale", y: "comparto", text: (d) => ` ${num(d.totale)}`, dx: 6, textAnchor: "start", fontSize: 11}),
    plot.ruleX([0])
  ]
}))
```

> **Nota di lettura**: il grafico mostra lo **stock** del ${last}: quanti dipendenti contano i vari comparti, indipendentemente dalle assunzioni. L'istruzione domina con oltre ${num(stockLast[0].totale)} addetti.

## 2. Il trend ${first}–${last}: declino e svolta

Lo stock complessivo racconta la parabola: un calo lento ma costante fino a **${minimo.anno}** (${num(minimo.tot)} dipendenti, il minimo della serie), poi la risalita, accelerata negli ultimi anni, fino ai **${num(totLast)}** del ${last}.

```js
display(plot.plot({
  title: `Dipendenti pubblici totali — ${first}–${last}`,
  width: 800, height: 320,
  x: {tickFormat: String}, y: {grid: true, tickFormat: "~s"},
  marks: [
    plot.lineY(byAnno, {x: "anno", y: "tot", stroke: "#2c7fb8", strokeWidth: 2, tip: true}),
    plot.dot(byAnno, {x: "anno", y: "tot", fill: "#fff", stroke: "#2c7fb8"}),
    plot.dot(byAnno.filter(d => d.anno === minimo.anno), {x: "anno", y: "tot", fill: "#d95f0e", r: 4, tip: true}),
    plot.ruleY([byAnno[0].tot], {stroke: "#999", strokeDasharray: "4 4"})
  ]
}))
```

La linea tratteggiata è il livello del ${first}. Il punto arancione segna il minimo storico del ${minimo.anno}.

## 3. I divari dentro la PA: la composizione di genere

```js
const donnePctArr = stockLast.map(d => d.pctDonne ?? 0);
const donneBars = stockLast.map(d => ({ comparto: d.comparto, donne: d.pctDonne ?? 0 }));
```

La PA è un mondo a forte prevalenza femminile (il **${pct(donnePctLast)}** del totale nel ${last}), ma con differenze straordinarie tra comparti: si va dal **${pct(Math.max(...donnePctArr))}** dell'istruzione al **${pct(Math.min(...donnePctArr))}** del personale in regime di diritto pubblico.

```js
display(plot.plot({
  title: `Quota di donne per comparto — ${last}`,
  width: 800, height: 340, marginLeft: 150,
  x: {grid: true, domain: [0, 100], label: "% donne"}, y: {label: null, tickSize: 0},
  color: {scheme: "Blues"},
  marks: [
    plot.ruleX([50], {stroke: "#d95f0e", strokeDasharray: "4 4"}),
    plot.barX(donneBars, {x: "donne", y: "comparto", fill: "donne", sort: {y: "-x"}, tip: true}),
    plot.text(donneBars, {x: "donne", y: "comparto", text: (d) => " " + pct(d.donne), dx: 6, textAnchor: "start", fontSize: 11})
  ]
}))
```

La soglia tratteggiata è il 50%. L'indice è nettamente sopra quota 50 nella sanità e nell'istruzione, dove le donne superano i due terzi, e scende moltissimo nel personale in regime di diritto pubblico (forze dell'ordine e magistratura).

---

## Dettaglio per comparto e anno

<small>Serie completa ${first}–${last}, per comparto e anno.</small>

```js
const { header, format } = tableFormat({
  anno: { label: "Anno", fmt: "string" },
  comparto: { label: "Comparto", fmt: "string" },
  donne: { label: "Donne", fmt: "num" },
  uomini: { label: "Uomini", fmt: "num" },
  totale: { label: "Totale", fmt: "num" }
});
```

```js
Inputs.table(data, {
  columns: ["anno", "comparto", "donne", "uomini", "totale"],
  header, format, rows: 20, width: "100%", sort: "anno", reverse: true
})
```

---

## Limiti

- **Solo stock**: i dati di questa pagina mostrano il numero di dipendenti per comparto; non includono il saldo netto (assunti/cessati). La lettura "declino/svolta" si basa sullo stock complessivo.
- **Nessuna geografia**: il dataset non contiene la regione, l'analisi è solo nazionale.
- **Classificazione**: la definizione dei comparti può essere soggetta a riclassificazioni (es. il salto netto del "Comparto autonomo" nel 2014), che vanno considerate nei confronti di lungo periodo.

## Risorse

- [MEF · RGS · BDAP (fonte originale)](https://www.rgs.mef.gov.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/dipendenti_pubblici/2024/dipendenti_pubblici_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/dipendenti-pubblici)

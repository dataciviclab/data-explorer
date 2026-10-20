---
title: "Chi cattura la crescita? Produttività, salari e imprese"
description: "Quota lavoro, salari reali, produttività e margini per settore in Italia, 1995-2024"
source: "Eurostat · INPS · ISTAT · MEF · OECD"
period: "1995-2024"
data_driven: true
cross_view: true
datasets:
  - eurostat_nama10_gdp
  - eurostat_labour_productivity_nuts3
  - eurostat_emp_nuts3
  - inps_retribuzioni
  - istat_sbs_imprese
  - istat_asia_imprese_addetti
  - ires_redditi_regione
  - irpef_comunale
  - iva_sez_attivita
  - oecd_taxing_wages
---

# Chi cattura la crescita?

**Nel ${last.anno} la quota lavoro sul valore aggiunto è ${pct(last.quota_lavoro_pct)}; nel ${first.anno} era ${pct(first.quota_lavoro_pct)}. Tra il ${base.anno} e il ${idx2023.anno} la produttività reale per persona è cresciuta del ${numFix(idx2023.produttivita - 100, 1)}%, mentre il salario reale per dipendente è cambiato del ${numFix(idx2023.salari - 100, 1)}%: un divario di ${numFix(gap2023, 1)} punti percentuali. Nel ${idx2024.anno} il divario si è ridotto a ${numFix(gap2024, 1)} punti.**

Questa pagina mette insieme contabilità nazionale, dichiarazioni fiscali, retribuzioni INPS e statistiche d'impresa. L'obiettivo è separare tre cose che spesso vengono confuse: quanto cresce il valore aggiunto, come si divide tra lavoro e capitale, e quanto arriva davvero in busta paga. I numeri sono calcolati dal dato a build-time.

```js
import { num, euro, euroCompact, pct, numFix, tableFormat } from "../import/format-utils.js";
```

```js
const macro = await FileAttachment("../data/chi-cattura-la-crescita-macro.json").json();
const settori = await FileAttachment("../data/chi-cattura-la-crescita-settori.json").json();
const imprese = await FileAttachment("../data/chi-cattura-la-crescita-imprese.json").json();
const cuneo = await FileAttachment("../data/chi-cattura-la-crescita-cuneo.json").json();
```

```js
const macroOk = macro.filter(d => d.quota_lavoro_pct != null);
const first = macroOk[0];
const last = macroOk[macroOk.length - 1];
const base = macro.find(d => d.anno === 2014);
const idx = macro
  .filter(d => d.anno >= 2014 && d.produttivita_reale != null && d.salari_reali != null)
  .map(d => ({
    anno: d.anno,
    produttivita: d.produttivita_reale / base.produttivita_reale * 100,
    salari: d.salari_reali / base.salari_reali * 100,
    redditi: d.redditi_reali / base.redditi_reali * 100,
  }));
const idx2023 = idx.find(d => d.anno === 2023);
const idx2024 = idx.find(d => d.anno === 2024);
const gap2023 = idx2023.produttivita - idx2023.salari;
const gap2024 = idx2024.produttivita - idx2024.salari;
const maxQuota = Math.max(...macroOk.map(d => d.quota_lavoro_pct));
const minQuota = Math.min(...macroOk.map(d => d.quota_lavoro_pct));
const gapYear = idx.reduce((max, d) => (d.produttivita - d.salari) > (max.produttivita - max.salari) ? d : max, idx[0]);
const gapYearValue = gapYear.produttivita - gapYear.salari;
```

```js
const s2014 = new Map(settori.filter(d => d.anno === 2014).map(d => [d.settore_codice, d]));
const s2023 = new Map(settori.filter(d => d.anno === 2023).map(d => [d.settore_codice, d]));
const settoriGrowth = [...s2023.values()]
  .map(d => {
    const a = s2014.get(d.settore_codice);
    if (!a || !a.va_per_addetto || !a.retribuzione_media_settimana) return null;
    const vaGrowth = (d.va_per_addetto / a.va_per_addetto - 1) * 100;
    const wageGrowth = (d.retribuzione_media_settimana / a.retribuzione_media_settimana - 1) * 100;
    return {
      settore_codice: d.settore_codice,
      settore_nace: d.settore_nace,
      va_growth: vaGrowth,
      wage_growth: wageGrowth,
      gap: vaGrowth - wageGrowth,
      va_per_addetto: d.va_per_addetto,
      retribuzione_media_settimana: d.retribuzione_media_settimana,
      n_lavoratori: d.n_lavoratori,
    };
  })
  .filter(Boolean);
const topGap = [...settoriGrowth].sort((a, b) => b.gap - a.gap)[0];
const bottomGap = [...settoriGrowth].sort((a, b) => a.gap - b.gap)[0];
const labelSectors = new Set(
  [...settoriGrowth].sort((a, b) => b.gap - a.gap).slice(0, 5)
    .concat([...settoriGrowth].sort((a, b) => a.gap - b.gap).slice(0, 3))
    .map(d => d.settore_codice)
);
const minAxis = Math.min(...settoriGrowth.flatMap(d => [d.va_growth, d.wage_growth]));
const maxAxis = Math.max(...settoriGrowth.flatMap(d => [d.va_growth, d.wage_growth]));
const diag = [{ x: minAxis, y: minAxis }, { x: maxAxis, y: maxAxis }];
```

```js
const baseImp = imprese.find(d => d.anno === 2015);
const lastImp = imprese[imprese.length - 1];
const impreseIdx = imprese.map(d => ({
  anno: d.anno,
  ires: d.ires_netto / baseImp.ires_netto * 100,
  irpef: d.irpef_lavoro_dipendente / baseImp.irpef_lavoro_dipendente * 100,
  margine: d.margine_va_pct,
}));
const iresGrowth = (lastImp.ires_netto / baseImp.ires_netto - 1) * 100;
const irpefGrowth = (lastImp.irpef_lavoro_dipendente / baseImp.irpef_lavoro_dipendente - 1) * 100;
const ivaData = imprese.filter(d => d.margine_va_pct != null);
const iva2014 = ivaData[0];
const iva2023 = ivaData[ivaData.length - 1];
const ivaMin = ivaData.reduce((min, d) => d.margine_va_pct < min.margine_va_pct ? d : min, ivaData[0]);
```

```js
const cuneoFirst = cuneo[0];
const cuneoLast = cuneo[cuneo.length - 1];
const cuneoDelta = cuneoLast.cuneo_pct - cuneoFirst.cuneo_pct;
```

<div class="grid grid-cols-4">
  <div class="card"><h3>Quota lavoro ${last.anno}</h3><span class="big">${pct(last.quota_lavoro_pct)}</span></div>
  <div class="card"><h3>Gap produttività-salari ${idx2023.anno}</h3><span class="big">${numFix(gap2023, 1)} pp</span></div>
  <div class="card"><h3>Settore con gap maggiore</h3><span class="big">${topGap.settore_nace}</span></div>
  <div class="card"><h3>Cuneo fiscale ${cuneoLast.anno}</h3><span class="big">${pct(cuneoLast.cuneo_pct)}</span></div>
</div>

## 1. La torta: lavoro e capitale

La quota lavoro è rimasta in una forbice stretta tra ${pct(minQuota)} e ${pct(maxQuota)} dal ${first.anno} al ${last.anno}. Non c'è un crollo di lungo periodo: il calo è concentrato nel ${idx2023.anno} e rimbalza nel ${last.anno}. La quota “capitale” però include il **reddito misto degli autonomi**, quindi non è solo profitto: è la parte che resta alle imprese e ai lavoratori indipendenti.

```js
const plot = await import("npm:@observablehq/plot");
display(plot.plot({
  title: `Quota lavoro e quota capitale sul valore aggiunto — ${first.anno}–${last.anno}`,
  width: 800, height: 360,
  x: {label: "Anno", tickFormat: String},
  y: {grid: true, label: "% del valore aggiunto", domain: [0, 100]},
  marks: [
    plot.areaY(macroOk, {x: "anno", y1: 0, y2: "quota_lavoro_pct", fill: "#2c7fb8", fillOpacity: 0.85}),
    plot.areaY(macroOk, {x: "anno", y1: "quota_lavoro_pct", y2: 100, fill: "#d95f0e", fillOpacity: 0.75}),
    plot.line(macroOk, {x: "anno", y: "quota_lavoro_pct", stroke: "#fff", strokeWidth: 1.5}),
    plot.text([{x: 2005, y: 20, text: "Lavoro"}], {x: "x", y: "y", text: "text", fill: "#fff", fontSize: 14, fontWeight: 600}),
    plot.text([{x: 2005, y: 80, text: "Capitale e reddito misto"}], {x: "x", y: "y", text: "text", fill: "#fff", fontSize: 14, fontWeight: 600})
  ]
}))
```

> **Nota di lettura**: la quota lavoro è `D1 / B1G` (redditi da lavoro dipendente sul valore aggiunto). La quota capitale è `B2A3G / B1G` (risultato lordo di gestione e reddito misto). Non è un tasso di sfruttamento.

## 2. Produttività e salari reali

L'indice della produttività reale per persona è calcolato deflazionando il valore aggiunto per persona con il deflatore del PIL. I salari reali sono la retribuzione media per dipendente, sempre deflazionata. Nel ${gapYear.anno} il divario ha toccato il massimo: ${numFix(gapYearValue, 1)} punti percentuali; nel ${idx2024.anno} è sceso a ${numFix(gap2024, 1)}.

```js
display(plot.plot({
  title: `Produttività e salari reali — indice ${base.anno}=100`,
  width: 800, height: 380,
  x: {label: "Anno", tickFormat: String},
  y: {grid: true, label: `Indice (${base.anno}=100)`},
  marks: [
    plot.ruleY([100], {stroke: "#bbb", strokeDasharray: "4 4"}),
    plot.areaY(idx, {x: "anno", y1: "salari", y2: "produttivita", fill: "#2c7fb8", fillOpacity: 0.12}),
    plot.line(idx, {x: "anno", y: "produttivita", stroke: "#2c7fb8", strokeWidth: 2.5}),
    plot.line(idx, {x: "anno", y: "salari", stroke: "#d95f0e", strokeWidth: 2.5}),
    plot.line(idx, {x: "anno", y: "redditi", stroke: "#7f7f7f", strokeWidth: 1.5, strokeDasharray: "4 4"}),
    plot.dot(idx, {x: "anno", y: "produttivita", fill: "#2c7fb8", r: 3, tip: true}),
    plot.dot(idx, {x: "anno", y: "salari", fill: "#d95f0e", r: 3, tip: true}),
    plot.text([{x: idx2024.anno, y: idx2024.produttivita, text: "Produttività"}], {x: "x", y: "y", text: "text", dx: -8, dy: -10, textAnchor: "end", fill: "#2c7fb8", fontSize: 11}),
    plot.text([{x: idx2024.anno, y: idx2024.salari, text: "Salari"}], {x: "x", y: "y", text: "text", dx: -8, dy: 10, textAnchor: "end", fill: "#d95f0e", fontSize: 11})
  ]
}))
```

La linea grigia tratteggiata è la retribuzione complessiva (inclusi i contributi datoriali); la linea arancione è il salario. Il divario si apre nel ${gapYear.anno}, quando la produttività recupera e i salari reali restano indietro; nel ${idx2024.anno} si riduce.

## 3. Il divario è settoriale

Il settore con il divario maggiore è **${topGap.settore_nace}**: tra il ${s2014.get(topGap.settore_codice).anno} e il ${s2023.get(topGap.settore_codice).anno} il valore aggiunto per addetto è cresciuto del ${numFix(topGap.va_growth, 1)}%, la retribuzione media per settimana del ${numFix(topGap.wage_growth, 1)}%. All'estremo opposto **${bottomGap.settore_nace}**: valore aggiunto per addetto ${numFix(bottomGap.va_growth, 1)}%, retribuzioni ${numFix(bottomGap.wage_growth, 1)}%.

```js
display(plot.plot({
  title: `Valore aggiunto per addetto vs retribuzione per settimana — crescita ${s2014.get(settoriGrowth[0].settore_codice).anno}–${s2023.get(settoriGrowth[0].settore_codice).anno}`,
  width: 860, height: 540,
  marginLeft: 60, marginRight: 30,
  x: {grid: true, label: "Δ retribuzione media per settimana (%)", domain: [minAxis - 5, maxAxis + 5]},
  y: {grid: true, label: "Δ valore aggiunto per addetto (%)", domain: [minAxis - 5, maxAxis + 5]},
  color: {scheme: "RdBu", domain: [-20, 65], legend: true, label: "Gap VA - salari (pp)"},
  marks: [
    plot.ruleX([0], {stroke: "#aaa"}),
    plot.ruleY([0], {stroke: "#aaa"}),
    plot.line(diag, {x: "x", y: "y", stroke: "#aaa", strokeDasharray: "4 4"}),
    plot.dot(settoriGrowth, {x: "wage_growth", y: "va_growth", r: 5, fill: "gap", fillOpacity: 0.9, tip: true}),
    plot.text(settoriGrowth.filter(d => labelSectors.has(d.settore_codice)), {x: "wage_growth", y: "va_growth", text: "settore_nace", dx: 7, fontSize: 9, fill: "#333", textAnchor: "start"})
  ]
}))
```

<small>Il colore indica il gap (rosso = valore aggiunto cresciuto più delle retribuzioni; blu = il contrario). La tabella sotto riporta i valori per tutti i settori.</small>

```js
const { header, format } = tableFormat({
  settore_nace: { label: "Settore", fmt: "string" },
  va_growth: { label: "Δ VA/addetto", fmt: "num", decimals: 1 },
  wage_growth: { label: "Δ retribuzione/settimana", fmt: "num", decimals: 1 },
  gap: { label: "Gap (pp)", fmt: "num", decimals: 1 },
  n_lavoratori: { label: "Lavoratori 2023", fmt: "num" },
});
```

```js
Inputs.table(
  [...settoriGrowth].sort((a, b) => b.gap - a.gap),
  {
    columns: ["settore_nace", "va_growth", "wage_growth", "gap", "n_lavoratori"],
    header,
    format,
    rows: 20,
    width: "100%",
    sort: "gap",
    reverse: true,
  }
)
```

> **Nota di lettura**: sopra la linea diagonale il valore aggiunto per addetto cresce più della retribuzione; sotto, il contrario. Il valore aggiunto viene da SBS+ASIA (industria e servizi di mercato), le retribuzioni da INPS (settore privato non agricolo). Sono universi diversi: il confronto è descrittivo, non una misura di sfruttamento. La finanza non è coperta da SBS.

## 4. Le imprese e i redditi dichiarati

Tra il ${baseImp.anno} e il ${lastImp.anno} il reddito imponibile netto IRES è cresciuto del ${numFix(iresGrowth, 1)}%, il reddito da lavoro dipendente dichiarato all'IRPEF del ${numFix(irpefGrowth, 1)}%. Il margine IVA (valore aggiunto fiscale su fatturato) è passato dal ${pct(iva2014.margine_va_pct)} nel ${iva2014.anno} al ${pct(iva2023.margine_va_pct)} nel ${iva2023.anno}, con un minimo nel ${ivaMin.anno} (${pct(ivaMin.margine_va_pct)}).

```js
display(plot.plot({
  title: `Reddito imponibile delle imprese e reddito da lavoro dipendente — indice ${baseImp.anno}=100`,
  width: 800, height: 360,
  x: {label: "Anno", tickFormat: String},
  y: {grid: true, label: `Indice (${baseImp.anno}=100)`},
  marks: [
    plot.ruleY([100], {stroke: "#bbb", strokeDasharray: "4 4"}),
    plot.line(impreseIdx, {x: "anno", y: "ires", stroke: "#d95f0e", strokeWidth: 2.5}),
    plot.line(impreseIdx, {x: "anno", y: "irpef", stroke: "#2c7fb8", strokeWidth: 2.5}),
    plot.dot(impreseIdx, {x: "anno", y: "ires", fill: "#d95f0e", r: 3, tip: true}),
    plot.dot(impreseIdx, {x: "anno", y: "irpef", fill: "#2c7fb8", r: 3, tip: true}),
    plot.text([{x: lastImp.anno, y: impreseIdx[impreseIdx.length - 1].ires, text: "IRES"}], {x: "x", y: "y", text: "text", dx: -8, dy: -10, textAnchor: "end", fill: "#d95f0e", fontSize: 11}),
    plot.text([{x: lastImp.anno, y: impreseIdx[impreseIdx.length - 1].irpef, text: "IRPEF lavoro dipendente"}], {x: "x", y: "y", text: "text", dx: -8, dy: 10, textAnchor: "end", fill: "#2c7fb8", fontSize: 11})
  ]
}))
```

```js
display(plot.plot({
  title: "Margine IVA: valore aggiunto fiscale su fatturato",
  width: 800, height: 300,
  x: {label: "Anno", tickFormat: String},
  y: {grid: true, label: "% del fatturato"},
  marks: [
    plot.line(ivaData, {x: "anno", y: "margine_va_pct", stroke: "#2c7fb8", strokeWidth: 2.5}),
    plot.dot(ivaData, {x: "anno", y: "margine_va_pct", fill: "#2c7fb8", r: 3, tip: true})
  ]
}))
```

> **Nota di lettura**: l'IRES è un **reddito imponibile**, non un profitto: risente di deduzioni, perdite e cambios di base. Il margine IVA è un proxy, non un margine di bilancio. Il ${lastImp.anno} IRES è provvisorio; il ${ivaMin.anno} è l'anno del shock energetico, con fatturato gonfiato e margine compresso.

## 5. Cuneo fiscale e distribuzione

Il cuneo fiscale è passato dal ${pct(cuneoFirst.cuneo_pct)} nel ${cuneoFirst.anno} al ${pct(cuneoLast.cuneo_pct)} nel ${cuneoLast.anno}: ${numFix(Math.abs(cuneoDelta), 1)} punti in meno. Su cento euro di costo azienda, ${numFix(cuneoLast.netto_su_costo_pct, 1)} euro arrivano netti. La quota di reddito dichiarato sopra i 55mila euro è passata dal ${pct(cuneoFirst.pct_reddito_oltre55)} al ${pct(cuneoLast.pct_reddito_oltre55)}; sopra i 120mila euro dal ${pct(cuneoFirst.pct_reddito_oltre120)} al ${pct(cuneoLast.pct_reddito_oltre120)}.

```js
display(plot.plot({
  title: "Cuneo fiscale e netto su costo azienda — single, 100% salario medio",
  width: 800, height: 320,
  x: {label: "Anno", tickFormat: String},
  y: {grid: true, label: "%", domain: [0, 100]},
  marks: [
    plot.line(cuneo, {x: "anno", y: "cuneo_pct", stroke: "#d95f0e", strokeWidth: 2.5}),
    plot.line(cuneo, {x: "anno", y: "netto_su_costo_pct", stroke: "#2c7fb8", strokeWidth: 2.5}),
    plot.dot(cuneo, {x: "anno", y: "cuneo_pct", fill: "#d95f0e", r: 3, tip: true}),
    plot.dot(cuneo, {x: "anno", y: "netto_su_costo_pct", fill: "#2c7fb8", r: 3, tip: true}),
    plot.text([{x: cuneoLast.anno, y: cuneoLast.cuneo_pct, text: "Cuneo"}], {x: "x", y: "y", text: "text", dx: -8, dy: -10, textAnchor: "end", fill: "#d95f0e", fontSize: 11}),
    plot.text([{x: cuneoLast.anno, y: cuneoLast.netto_su_costo_pct, text: "Netto su costo"}], {x: "x", y: "y", text: "text", dx: -8, dy: 10, textAnchor: "end", fill: "#2c7fb8", fontSize: 11})
  ]
}))
```

```js
display(plot.plot({
  title: "Quota di reddito dichiarato sopra 55mila e 120mila euro",
  width: 800, height: 300,
  x: {label: "Anno", tickFormat: String},
  y: {grid: true, label: "% del reddito complessivo"},
  marks: [
    plot.line(cuneo, {x: "anno", y: "pct_reddito_oltre55", stroke: "#2c7fb8", strokeWidth: 2.5}),
    plot.line(cuneo, {x: "anno", y: "pct_reddito_oltre120", stroke: "#d95f0e", strokeWidth: 2.5}),
    plot.dot(cuneo, {x: "anno", y: "pct_reddito_oltre55", fill: "#2c7fb8", r: 3, tip: true}),
    plot.dot(cuneo, {x: "anno", y: "pct_reddito_oltre120", fill: "#d95f0e", r: 3, tip: true}),
    plot.text([{x: cuneoLast.anno, y: cuneoLast.pct_reddito_oltre55, text: "Sopra 55k"}], {x: "x", y: "y", text: "text", dx: -8, dy: -10, textAnchor: "end", fill: "#2c7fb8", fontSize: 11}),
    plot.text([{x: cuneoLast.anno, y: cuneoLast.pct_reddito_oltre120, text: "Sopra 120k"}], {x: "x", y: "y", text: "text", dx: -8, dy: 10, textAnchor: "end", fill: "#d95f0e", fontSize: 11})
  ]
}))
```

> **Nota di lettura**: le soglie IRPEF sono nominali e fisse: l'inflazione sposta contribuenti tra fasce. L'aumento delle quote non è quindi una misura pura di disuguaglianza. Il cuneo OECD si riferisce a un single senza figli al 100% del salario medio.

## Cosa possiamo dire e cosa no

**Possiamo dire**:
- in quali settori il valore aggiunto per addetto è cresciuto più delle retribuzioni;
- come è cambiata la quota lavoro dal ${first.anno};
- quanto del gap tra costo azienda e netto è cuneo fiscale;
- come si sono mossi i redditi dichiarati delle imprese e dei lavoratori.

**Non possiamo dire**:
- quale singola azienda non redistribuisce: servono bilanci firm-level (AIDA/Cerved/Registro Imprese XBRL), non open;
- che i profitti siano tutti extra-profitto: servono markup e potere di mercato;
- che ci sia causalità tra margini e salari.

## Limiti

- **IRES non è profitto**: è reddito imponibile netto (redditi meno perdite), sensibile a deduzioni e cambi di base. Il dato ${lastImp.anno} è provvisorio.
- **SBS copre industria e servizi di mercato**: la finanza non è inclusa, la PA nemmeno. Il confronto settoriale è descrittivo.
- **INPS è settore privato non agricolo**: `n_lavoratori` non è FTE; il salario per settimana è una media, non un salario orario.
- **Deflatore PIL, non CPI**: i salari reali sono una stima; con il CPI il potere d'acquisto sarebbe probabilmente più basso.
- **Rottura 2019 INPS**: obs 347 e 492 sono due tavole; la serie è utilizzabile con nota.
- **IVA 2024 esclusa**: il file 2025 cambia copertura; il margine si ferma al ${iva2023.anno}.
- **Nessun dato firm-level**: le dichiarazioni e i dati settoriali non permettono di attribuire il comportamento a singole imprese.

## Risorse

- [Eurostat — NAMA10, produttività e occupazione](https://ec.europa.eu/eurostat/)
- [INPS — Osservatori Statistici](https://servizi2.inps.it/servizi/osservatoristatistici/)
- [ISTAT — SBS e ASIA](https://esploradati.istat.it/)
- [MEF — Dichiarazioni fiscali](https://www1.finanze.gov.it/)
- [OECD — Taxing Wages](https://www.oecd.org/tax/taxing-wages.htm)

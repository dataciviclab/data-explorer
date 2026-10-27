---
title: "Chi cattura la crescita? Produttività, salari e imprese"
description: "Quota lavoro, salari reali, produttività e margini per settore in Italia, 1995-2024"
source: "Eurostat · ISTAT · MEF · OECD"
period: "1995-2024"
data_driven: true
cross_view: true
datasets:
  - eurostat_nama10_gdp
  - eurostat_labour_productivity_nuts3
  - eurostat_emp_nuts3
  - eurostat_gva_nuts3
  - istat_sbs_imprese
  - ires_redditi_regione
  - irpef_comunale
  - iva_sez_attivita
  - oecd_taxing_wages
---

# Chi cattura la crescita?

**Nel ${last.anno} la quota lavoro sul valore aggiunto è ${pct(last.quota_lavoro_pct)}; nel ${first.anno} era ${pct(first.quota_lavoro_pct)}. Tra il ${base.anno} e il ${idx2023.anno} la produttività reale per persona è cresciuta del ${numFix(idx2023.produttivita - 100, 1)}%, mentre il salario reale per dipendente è cambiato del ${numFix(idx2023.salari - 100, 1)}%: un divario di ${numFix(gap2023, 1)} punti percentuali. Nel ${idx2024.anno} il divario si è ridotto a ${numFix(gap2024, 1)} punti.**

Questa pagina mette insieme contabilità nazionale, statistiche d'impresa, dichiarazioni fiscali e cuneo fiscale. L'obiettivo è separare tre cose che spesso vengono confuse: quanto cresce il valore aggiunto, come si divide tra lavoro e capitale, e quanto arriva davvero in busta paga. I numeri sono calcolati dal dato a build-time.

```js
import { num, euro, euroCompact, pct, numFix, tableFormat } from "../import/format-utils.js";
```

```js
const macro = await FileAttachment("../data/chi-cattura-la-crescita-macro.json").json();
const settori = await FileAttachment("../data/chi-cattura-la-crescita-settori.json").json();
const dentro = await FileAttachment("../data/chi-cattura-la-crescita-dentro-settori.json").json();
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
const s2014 = new Map(settori.filter(d => d.anno === 2014).map(d => [d.nace_codice, d]));
const s2023 = new Map(settori.filter(d => d.anno === 2023).map(d => [d.nace_codice, d]));
const settoriGrowth = [...s2023.values()]
  .map(d => {
    const a = s2014.get(d.nace_codice);
    if (!a || !a.va_per_ora_reale || !a.costo_lavoro_per_ora_reale) return null;
    const vaGrowth = (d.va_per_ora_reale / a.va_per_ora_reale - 1) * 100;
    const costGrowth = (d.costo_lavoro_per_ora_reale / a.costo_lavoro_per_ora_reale - 1) * 100;
    return {
      settore_codice: d.nace_codice,
      settore_nace: d.nace,
      va_mila_eur: d.va_mila_eur,
      va_mld: d.va_mila_eur / 1e6,
      va_growth: vaGrowth,
      cost_growth: costGrowth,
      gap: vaGrowth - costGrowth,
      va_per_ora: d.va_per_ora_eur,
      costo_lavoro_per_ora: d.costo_lavoro_per_ora_eur,
      salario_per_ora: d.salario_per_ora_eur,
      quota_lavoro: d.quota_lavoro_pct,
      quota_lavoro_2014: a.quota_lavoro_pct,
      gos_su_va: d.gos_su_va_pct,
      investimenti_su_va: d.investimenti_su_va_pct,
    };
  })
  .filter(Boolean);
// Esclude i settori molto piccoli/volatili dal titolo (es. estrazione).
const settoriRilevanti = settoriGrowth.filter(d => d.va_mila_eur >= 20000000);
const topGap = [...settoriRilevanti].sort((a, b) => b.gap - a.gap)[0];
const bottomGap = [...settoriRilevanti].sort((a, b) => a.gap - b.gap)[0];
const labelSectors = new Set(
  [...settoriGrowth].sort((a, b) => b.gap - a.gap).slice(0, 5)
    .concat([...settoriGrowth].sort((a, b) => a.gap - b.gap).slice(0, 3))
    .map(d => d.settore_codice)
);
const minAxis = Math.min(...settoriGrowth.flatMap(d => [d.va_growth, d.cost_growth]));
const maxAxis = Math.max(...settoriGrowth.flatMap(d => [d.va_growth, d.cost_growth]));
const diag = [{ x: minAxis, y: minAxis }, { x: maxAxis, y: maxAxis }];

const sizeOrder = ["0-9", "10-19", "20-49", "50-249", "250+"];
const sizeManif = (dentro.size || [])
  .filter(d => d.nace_codice === "C")
  .sort((a, b) => sizeOrder.indexOf(a.size_class) - sizeOrder.indexOf(b.size_class));
const sizeLong = sizeManif.flatMap(d => [
  { size_class: d.size_class, tipo: "VA/ora", valore: d.va_per_ora_eur },
  { size_class: d.size_class, tipo: "Costo lavoro/ora", valore: d.costo_lavoro_per_ora_eur },
]);
const distSel = (dentro.distribuzione || []).filter(d => ["C", "F", "G", "M", "J"].includes(d.nace_codice));
const distRatio = distSel.flatMap(d => [
  { settore: d.nace, tipo: "VA/addetto", ratio: d.rapporto_q3_q1_va },
  { settore: d.nace, tipo: "Costo/dipendente", ratio: d.rapporto_q3_q1_costo },
]);
const cDist = distSel.find(d => d.nace_codice === "C");
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

## 3. Il divario è settoriale e dentro i settori

A livello aggregato il divario produttività-salari del ${idx2023.anno} era ${numFix(gap2023, 1)} punti; qui guardiamo quanto cambia per settore.

Il settore con il divario maggiore è **${topGap.settore_nace}**: tra il ${s2014.get(topGap.settore_codice).anno} e il ${s2023.get(topGap.settore_codice).anno} il valore aggiunto reale per ora è cresciuto del ${numFix(topGap.va_growth, 1)}%, il costo del lavoro reale per ora è cambiato del ${numFix(topGap.cost_growth, 1)}%. All'estremo opposto **${bottomGap.settore_nace}**: VA reale per ora ${numFix(bottomGap.va_growth, 1)}%, costo del lavoro reale ${numFix(bottomGap.cost_growth, 1)}%.

```js
display(plot.plot({
  title: `Valore aggiunto reale per ora vs costo del lavoro reale per ora — crescita ${s2014.get(settoriGrowth[0].settore_codice).anno}–${s2023.get(settoriGrowth[0].settore_codice).anno}`,
  width: 860, height: 540,
  marginLeft: 70, marginRight: 30,
  x: {grid: true, label: "Δ costo del lavoro reale per ora (%)", domain: [minAxis - 5, maxAxis + 5]},
  y: {grid: true, label: "Δ valore aggiunto reale per ora (%)", domain: [minAxis - 5, maxAxis + 5]},
  color: {scheme: "RdBu", domain: [-10, 35], legend: true, label: "Gap VA - costo lavoro (pp)"},
  marks: [
    plot.ruleX([0], {stroke: "#aaa"}),
    plot.ruleY([0], {stroke: "#aaa"}),
    plot.line(diag, {x: "x", y: "y", stroke: "#aaa", strokeDasharray: "4 4"}),
    plot.dot(settoriGrowth, {x: "cost_growth", y: "va_growth", r: 5, fill: "gap", fillOpacity: 0.9, tip: true}),
    plot.text(settoriGrowth.filter(d => labelSectors.has(d.settore_codice)), {x: "cost_growth", y: "va_growth", text: "settore_nace", dx: 7, fontSize: 11, fontWeight: 600, fill: "#111", stroke: "#fff", strokeWidth: 3, textAnchor: "start"})
  ]
}))
```

<small>Il colore indica il gap (rosso = valore aggiunto cresciuto più del costo del lavoro; blu = il contrario). La tabella sotto riporta i valori per tutti i settori; il settore citato nel titolo è scelto tra quelli rilevanti per dimensione, per evitare che settori molto piccoli o volatili dominino la lettura.</small>

```js
const { header, format } = tableFormat({
  settore_nace: { label: "Settore", fmt: "string" },
  va_mld: { label: "VA 2023 (mld €)", fmt: "num", decimals: 1 },
  va_per_ora: { label: "VA/ora 2023", fmt: "euro" },
  costo_lavoro_per_ora: { label: "Costo lavoro/ora 2023", fmt: "euro" },
  quota_lavoro: { label: "Quota lavoro 2023", fmt: "pct" },
  va_growth: { label: "Δ VA/ora reale", fmt: "num", decimals: 1 },
  cost_growth: { label: "Δ costo/ora reale", fmt: "num", decimals: 1 },
  gap: { label: "Gap (pp)", fmt: "num", decimals: 1 },
});
```

```js
Inputs.table(
  [...settoriGrowth].sort((a, b) => b.gap - a.gap),
  {
    columns: ["settore_nace", "va_mld", "va_per_ora", "costo_lavoro_per_ora", "quota_lavoro", "va_growth", "cost_growth", "gap"],
    header,
    format,
    rows: 20,
    width: "100%",
    sort: "gap",
    reverse: true,
  }
)
```

> **Nota di lettura**: sopra la diagonale il valore aggiunto reale per ora cresce più del costo del lavoro reale; sotto, il contrario. Valore aggiunto e costo del lavoro vengono dalla stessa fonte (SBS, settore privato di mercato) e sono entrambi per ora, deflazionati con il deflatore GVA dell'aggregato NACE più vicino. Il confronto reale si ferma al ${s2023.get(settoriGrowth[0].settore_codice).anno}: il mart contiene anche il 2024, ma il deflatore GVA 2024 non è disponibile per tutti i settori. La finanza e la PA non sono coperte.

### Redditività e investimenti

Il GOS/VA è un proxy di redditività lorda; gli investimenti/VA dicono quanto di quel valore viene reinvestito. Un GOS alto non implica investimenti alti: guardare le due colonne insieme. GOS non è profitto netto.

```js
const { header: headerRed, format: formatRed } = tableFormat({
  settore_nace: { label: "Settore", fmt: "string" },
  gos_su_va: { label: "GOS/VA 2023", fmt: "pct" },
  investimenti_su_va: { label: "Investimenti/VA 2023", fmt: "pct" },
});
```

```js
Inputs.table(
  [...settoriGrowth].sort((a, b) => b.gos_su_va - a.gos_su_va),
  {
    columns: ["settore_nace", "gos_su_va", "investimenti_su_va"],
    header: headerRed,
    format: formatRed,
    rows: 20,
    width: "100%",
    sort: "gos_su_va",
    reverse: true,
  }
)
```

### Dentro i settori: dimensioni e dispersione

**Grandi vs piccole (manifattura 2023).** Il VA/ora passa da ${euro(sizeManif[0]?.va_per_ora_eur)} nella classe ${sizeManif[0]?.size_class} a ${euro(sizeManif[4]?.va_per_ora_eur)} nella classe ${sizeManif[4]?.size_class}; il costo del lavoro/ora da ${euro(sizeManif[0]?.costo_lavoro_per_ora_eur)} a ${euro(sizeManif[4]?.costo_lavoro_per_ora_eur)}.

```js
display(plot.plot({
  title: "Manifattura 2023: VA/ora e costo del lavoro/ora per classe dimensionale",
  width: 800, height: 320,
  x: {label: "Classe dimensionale (addetti)", domain: sizeOrder},
  y: {grid: true, label: "€/ora"},
  color: {domain: ["VA/ora", "Costo lavoro/ora"], range: ["#2c7fb8", "#d95f0e"], legend: true},
  marks: [
    plot.line(sizeLong, {x: "size_class", y: "valore", stroke: "tipo", strokeWidth: 2.5, tip: true}),
    plot.dot(sizeLong, {x: "size_class", y: "valore", fill: "tipo", r: 4, tip: true})
  ]
}))
```

```js
const { header: headerSize, format: formatSize } = tableFormat({
  size_class: { label: "Classe", fmt: "string" },
  va_per_ora_eur: { label: "VA/ora", fmt: "euro" },
  costo_lavoro_per_ora_eur: { label: "Costo lavoro/ora", fmt: "euro" },
  quota_lavoro_pct: { label: "Quota lavoro", fmt: "pct" },
  gos_su_va_pct: { label: "GOS/VA", fmt: "pct" },
  investimenti_su_va_pct: { label: "Investimenti/VA", fmt: "pct" },
});
```

```js
Inputs.table(
  sizeManif,
  {
    columns: ["size_class", "va_per_ora_eur", "costo_lavoro_per_ora_eur", "quota_lavoro_pct", "gos_su_va_pct", "investimenti_su_va_pct"],
    header: headerSize,
    format: formatSize,
    rows: 10,
    width: "100%",
  }
)
```

**La forbice Q3/Q1.** In manifattura il VA per addetto del terzo quartile è ${numFix(cDist?.rapporto_q3_q1_va, 2)} volte quello del primo, mentre il costo per dipendente è ${numFix(cDist?.rapporto_q3_q1_costo, 2)} volte. La dispersione della produttività è più ampia di quella delle retribuzioni.

```js
display(plot.plot({
  title: "Dispersione dentro il settore: Q3/Q1 di VA per addetto e costo per dipendente — 2023",
  width: 800, height: 360,
  marginLeft: 120,
  x: {grid: true, label: "Q3/Q1 (x)", domain: [1, 3.6]},
  y: {label: null},
  color: {domain: ["VA/addetto", "Costo/dipendente"], range: ["#2c7fb8", "#d95f0e"], legend: true},
  marks: [
    plot.ruleX([1], {stroke: "#aaa", strokeDasharray: "4 4"}),
    plot.dot(distRatio, {x: "ratio", y: "settore", fill: "tipo", r: 6, tip: true}),
    plot.text(distRatio, {x: "ratio", y: "settore", text: d => ` ${numFix(d.ratio, 2)}x`, dx: 8, fontSize: 11, fontWeight: 600, fill: "#111", stroke: "#fff", strokeWidth: 3, textAnchor: "start"})
  ]
}))
```

```js
const { header: headerDist, format: formatDist } = tableFormat({
  nace: { label: "Settore", fmt: "string" },
  va_per_addetto_q1: { label: "VA/addetto Q1", fmt: "euro" },
  va_per_addetto_q3: { label: "VA/addetto Q3", fmt: "euro" },
  costo_personale_dipendente_q1: { label: "Costo/dip. Q1", fmt: "euro" },
  costo_personale_dipendente_q3: { label: "Costo/dip. Q3", fmt: "euro" },
  rapporto_q3_q1_va: { label: "Q3/Q1 VA", fmt: "num", decimals: 2 },
  rapporto_q3_q1_costo: { label: "Q3/Q1 costo", fmt: "num", decimals: 2 },
});
```

```js
Inputs.table(
  [...distSel].sort((a, b) => b.rapporto_q3_q1_va - a.rapporto_q3_q1_va),
  {
    columns: ["nace", "va_per_addetto_q1", "va_per_addetto_q3", "costo_personale_dipendente_q1", "costo_personale_dipendente_q3", "rapporto_q3_q1_va", "rapporto_q3_q1_costo"],
    header: headerDist,
    format: formatDist,
    rows: 10,
    width: "100%",
    sort: "rapporto_q3_q1_va",
    reverse: true,
  }
)
```

> **Nota di lettura**: i quartili sono calcolati sulle imprese del settore, non sono un panel: non dicono se le stesse imprese migliorano nel tempo. Le classi dimensionali sono solo nazionali; nelle classi piccole una quota lavoro sopra il 100% può capitare per VA molto basso o arrotondamenti.

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
- in quali settori il valore aggiunto reale per ora è cresciuto più del costo del lavoro reale;
- quanto è ampia la dispersione di produttività e retribuzioni dentro i settori;
- come è cambiata la quota lavoro dal ${first.anno};
- quanto del gap tra costo azienda e netto è cuneo fiscale;
- come si sono mossi i redditi dichiarati delle imprese e dei lavoratori.

**Non possiamo dire**:
- quale singola azienda non redistribuisce: servono bilanci firm-level (AIDA/Cerved/Registro Imprese XBRL), non open;
- che i profitti siano tutti extra-profitto: servono markup e potere di mercato;
- che ci sia causalità tra margini e salari.

## Limiti

- **IRES non è profitto**: è reddito imponibile netto (redditi meno perdite), sensibile a deduzioni e cambi di base. Il dato ${lastImp.anno} è provvisorio.
- **SBS copre industria, costruzioni, commercio e servizi di mercato**: finanza e PA non sono incluse. Il confronto settoriale è descrittivo.
- **Ore lavorate = dipendenti**: non includono gli autonomi; il costo del lavoro include salari e contributi sociali.
- **GOS è un risultato lordo**, non profitto netto.
- **Deflatore settoriale approssimato**: usiamo il deflatore GVA dell'aggregato NACE più vicino; per B/D/E, G/H/I, M/N, P/Q, R/S non è esatto.
- **Confronto reale 2014–2023**: il mart SBS contiene il 2024, ma il deflatore GVA 2024 non è completo per tutti i settori; il confronto reale si ferma al 2023.
- **Quartili e classi dimensionali**: solo nazionale; i quartili coprono 2013–2024 e non sono un panel di imprese. Nelle classi piccole le quote possono superare il totale.
- **Deflatore PIL, non CPI**: i salari reali macro sono una stima; con il CPI il potere d'acquisto sarebbe probabilmente più basso.
- **IVA 2024 esclusa**: il file 2025 cambia copertura; il margine si ferma al ${iva2023.anno}.
- **Nessun dato firm-level**: le dichiarazioni e i dati settoriali non permettono di attribuire il comportamento a singole imprese.

## Risorse

- [Eurostat — NAMA10, produttività, GVA e occupazione](https://ec.europa.eu/eurostat/)
- [ISTAT — Structural Business Statistics (SBS)](https://esploradati.istat.it/)
- [MEF — Dichiarazioni fiscali](https://www1.finanze.gov.it/)
- [OECD — Taxing Wages](https://www.oecd.org/tax/taxing-wages.htm)

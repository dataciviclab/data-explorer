---
title: IRPEF — quanto reddito si dichiara in ogni territorio
description: "Contribuenti, reddito imponibile e reddito medio IRPEF per regione e capoluogo, 2019-2023 (MEF)"
source: MEF — Dipartimento delle Finanze
source_url: https://www1.finanze.gov.it/
period: "2019–2023"
last_modified: 2026-05-26
dataset_slug: irpef_comunale
data_driven: true
---

# IRPEF — quanto si dichiara in ogni territorio

**Nel ${anno} in Italia **${num(contribNaz)}** contribuenti hanno dichiarato ${euroCompact(redditoNaz)} di reddito imponibile IRPEF. Il reddito medio è **${euro(medioNaz)}** all'anno, in crescita del **${numFix(pctMedio, 1)}%** rispetto al ${primo}. Ma dietro quella media c'è un divario territoriale marcato: la regione con il reddito medio più alto, **${topReg.regione}**, supera la media nazionale di quasi un quinto, e a **${capMax.comune}** si dichiara più del doppio che a **${capMin.comune}**.**

Ogni anno i contribuenti italiani dichiarano redditi all'IRPEF (imposta personale sul reddito) al MEF — Dipartimento delle Finanze. Questa pagina mostra come si distribuisce il reddito dichiarato per territorio: prima la fotografia per regione, poi l'evoluzione nel tempo e infine il dettaglio sui capoluoghi di regione. I numeri sono calcolati dal dato a build-time: se si ripubblica il parquet, KPI e grafici si aggiornano da soli.

```js
import { num, euro, euroCompact, pct, numFix, tableFormat } from "../import/format-utils.js";
import { normalizzaReg, loadItalianRegions, buildMapLookup } from "../import/geo-utils.js";
```

```js
const regTopo = await FileAttachment("../data/regioni.topojson").json();
const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
```

```js
const regioniRaw = await FileAttachment("../data/irpef-regioni.json").json();
const capoluoghi = await FileAttachment("../data/irpef-capoluoghi.json").json();
```

```js
// Anni disponibili e ultimo anno di riferimento
const anni = [...new Set(regioniRaw.map(d => d.anno_di_imposta))].sort((a, b) => a - b);
const anno = anni[anni.length - 1];
const primo = anni[0];
```

```js
// Esclude le righe di somma/errore e tiene solo l'ultimo anno
const regOk = regioniRaw.filter(d => !/MANCANTE|ERRATA/.test(d.regione.toUpperCase()));
const regLast = regOk.filter(d => d.anno_di_imposta === anno);
```

```js
// Unisce le due P.A. Trentino (come nel TopoJSON ISTAT), con media pesata per contribuenti
const adige = regLast.filter(r => /P\.A\./.test(r.regione));
const aggre = (l) => ({
  reddito: d3.sum(l, r => r.reddito_imponibile_eur),
  contribuenti: d3.sum(l, r => r.numero_contribuenti)
});
const perRegione = [
  ...regLast.filter(r => !/P\.A\./.test(r.regione)).map(r => ({ regione: r.regione, reddito_medio: r.numero_contribuenti ? r.reddito_imponibile_eur / r.numero_contribuenti : null })),
  ...(adige.length ? [(() => { const a = aggre(adige); return { regione: "TRENTINO-ALTO-ADIGE", reddito_medio: a.contribuenti ? a.reddito / a.contribuenti : null }; })()] : [])
];
const lookup = buildMapLookup(perRegione, regioniGeo, "regione", "reddito_medio");
const topReg = [...perRegione].sort((a, b) => (b.reddito_medio ?? 0) - (a.reddito_medio ?? 0))[0];
```

```js
// Metriche nazionali sull'ultimo anno
const redditoNaz = d3.sum(regLast, r => r.reddito_imponibile_eur);
const contribNaz = d3.sum(regLast, r => r.numero_contribuenti);
const medioNaz = contribNaz ? redditoNaz / contribNaz : null;
const impostaNaz = d3.sum(regLast, r => r.imposta_netta_eur);
```

```js
// Serie storica del reddito medio nazionale + crescita dal primo anno
const aggAnno = (a) => {
  const r = regOk.filter(d => d.anno_di_imposta === a);
  const c = d3.sum(r, q => q.numero_contribuenti);
  return { anno: a, contribuenti: c, reddito_tot: d3.sum(r, q => q.reddito_imponibile_eur), reddito_medio: c ? d3.sum(r, q => q.reddito_imponibile_eur) / c : null };
};
const serie = anni.map(aggAnno);
const primoAgg = aggAnno(primo);
const pctMedio = medioNaz && primoAgg.reddito_medio ? ((medioNaz / primoAgg.reddito_medio) - 1) * 100 : null;
```

```js
// Capoluoghi di regione: reddito medio per contribuente, ordinati
const capLast = capoluoghi
  .filter(d => d.anno === anno)
  .map(d => ({ ...d, reddito_medio: d.numero_contribuenti ? d.reddito_imponibile_eur / d.numero_contribuenti : null }))
  .sort((a, b) => (b.reddito_medio ?? 0) - (a.reddito_medio ?? 0));
const capMax = capLast[0];
const capMin = capLast[capLast.length - 1];
```

```js
const plot = await import("npm:@observablehq/plot");
```

<div class="grid grid-cols-4">
  <div class="card"><h3>Contribuenti ${anno}</h3><span class="big">${num(contribNaz)}</span></div>
  <div class="card"><h3>Reddito medio</h3><span class="big">${euro(medioNaz)}</span></div>
  <div class="card"><h3>Δ medio dal ${primo}</h3><span class="big">${pctMedio >= 0 ? "+" : ""}${numFix(pctMedio, 1)}%</span></div>
  <div class="card"><h3>Reddito imponibile</h3><span class="big">${euroCompact(redditoNaz)}</span></div>
</div>

## 1. Quanto si guadagna per regione

La mappa mostra il **reddito medio dichiarato per contribuente**. La geografia è netta: i colori più alti al Nord-Ovest e in parte del Centro, il Mezzogiorno in coda. La regione col valore più alto, **${topReg.regione} (${euro(topReg.reddito_medio)})**, supera la media nazionale di circa il **${numFix((topReg.reddito_medio / medioNaz - 1) * 100, 0)}%**.

```js
display(plot.plot({
  title: `Reddito medio per contribuente — ${anno}`,
  projection: {type: "mercator", domain: regioniGeo},
  width: 800, height: 600,
  color: {scheme: "OrRd", legend: true, label: "Reddito medio (€)", type: "quantile"},
  marks: [
    plot.geo(regioniGeo, {
      fill: d => lookup.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#888", strokeWidth: 0.25, tip: true,
      title: d => `${d.properties.DEN_REG}: ${euro(lookup.get(normalizzaReg(d.properties.DEN_REG))) ?? "— n.d."}`
    }),
    plot.geo(confiniReg, {stroke: "#888", strokeWidth: 0.7})
  ]
}))
```

> **Nota di lettura**: a parità di scala, la classifica per reddito complessivo è dominata dalle regioni più popolose; qui guardiamo il reddito **medio per contribuente**, che misura la capacità dichiarata indipendentemente dalla dimensione demografica.

## 2. L'evoluzione del reddito medio (${primo}–${anno})

Nel corso del periodo il reddito medio dichiarato è passato da **${euro(primoAgg.reddito_medio)}** a **${euro(medioNaz)}**, una crescita del **+${numFix(pctMedio, 1)}%**. Intanto i contribuenti sono saliti da **${num(primoAgg.contribuenti)}** a **${num(contribNaz)}**. La crescita va letta al netto dell'inflazione per capire il vero potere d'acquisto.

```js
display(plot.plot({
  title: `Reddito medio per contribuente (€) — ${primo}–${anno}`,
  width: 800, height: 380,
  x: {label: "Anno di imposta"},
  y: {grid: true, label: "Reddito medio (€)", tickFormat: euroCompact},
  marks: [
    plot.line(serie, {x: "anno", y: "reddito_medio", stroke: "#d95f0e", strokeWidth: 2.5, tip: true}),
    plot.dot(serie, {x: "anno", y: "reddito_medio", fill: "#d95f0e", tip: true})
  ]
}))
```

## 3. Il reddito medio nei capoluoghi di regione

Il divario emerge con chiarezza nei capoluoghi. In testa **${capMax.comune} con ${euro(capMax.reddito_medio)}**; in coda **${capMin.comune} con ${euro(capMin.reddito_medio)}**. Il rapporto tra i due estremi è di circa **${numFix(capMax.reddito_medio / capMin.reddito_medio, 1)} a 1**: a Milano si dichiara oltre il doppio che a Palermo.

```js
display(plot.plot({
  title: `Reddito medio per capoluogo di regione — ${anno}`,
  width: 800, height: 420, marginLeft: 100,
  x: {grid: true, label: "Reddito medio (€)", tickFormat: euroCompact},
  y: {label: null, tickSize: 0},
  marks: [
    plot.barX(capLast, {x: "reddito_medio", y: "comune", fill: "reddito_medio", sort: {y: "-x"}, tip: true}),
    plot.ruleX([0])
  ]
}))
```

La classifica riflette soprattutto la struttura economica locale: i capoluoghi del Nord con settori ad alto valore aggiunto e costo della vita maggiore guadagnano sistematicamente più dei capoluoghi del Mezzogiorno.
---

## Dettaglio capoluoghi

<small>Cerca un comune o filtra per regione. Dati ${anno}.</small>

```js
const { header, format } = tableFormat({
  comune: { label: "Comune", fmt: "string" },
  regione: { label: "Regione", fmt: "string" },
  numero_contribuenti: { label: "Contribuenti", fmt: "num" },
  reddito_imponibile_eur: { label: "Reddito imponibile", fmt: "euro" },
  imposta_netta_eur: { label: "Imposta netta", fmt: "euro" },
  reddito_medio: { label: "Reddito medio", fmt: "euro" }
});
```

```js
const searchCap = view(Inputs.search(capLast, {placeholder: "digita il nome del comune…", label: "Cerca"}));
```

```js
Inputs.table(searchCap, {
  columns: ["comune", "regione", "numero_contribuenti", "reddito_imponibile_eur", "imposta_netta_eur", "reddito_medio"],
  header,
  format,
  rows: 20,
  width: "100%",
  sort: "reddito_medio",
  reverse: true
})
```

---

## Limiti

- **Copertura**: i dati coprono il periodo 2019–2023. Al momento dell'ultimo aggiornamento i dati 2024 non sono ancora nelle intercettazioni del data loader; il periodo dipende da quanto pubblica il MEF.
- **Reddito medio**: è il rapporto tra reddito imponibile totale e numero di contribuenti. Non tiene conto della distribuzione interna (disuguaglianza) né delle differenze del costo della vita tra territori; è un reddito imponibile, non disponibile.
- **Contribuenti**: i totali per regione si ottengono sommando le dichiarazioni per comune; un contribuente con più fonti di reddito può essere conteggiato una sola volta a seconda della metodologia di deduplicazione del MEF.
- **Capoluoghi**: la lista comprende i comuni capoluogo di regione presenti nei dati; Aosta non è disponibile nel data loader.

---

## Risorse

- [MEF — Dipartimento delle Finanze (fonte originale)](https://www1.finanze.gov.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/irpef_comunale/2023/irpef_comunale_2023_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/irpef-comunale)

---
title: IRPEF comunale
description: Contribuenti, reddito imponibile e imposta netta IRPEF per comune e regione, 2019-2023
source: MEF — Dipartimento delle Finanze
source_url: https://www1.finanze.gov.it/
period: "2019–2023"
last_modified: 2026-05-26
dataset_slug: irpef_comunale
---

# IRPEF comunale

Contribuenti, reddito imponibile e imposta netta IRPEF per comune italiano. I dati permettono di confrontare la capacità fiscale tra territori e l'evoluzione del reddito dichiarato nel tempo.

**Fonte**: [MEF — Dipartimento delle Finanze](https://www1.finanze.gov.it/) · **Periodo**: 2019–2023

```js
import * as topojson from "npm:topojson-client";

const regTopo = await FileAttachment("../data/regioni.topojson").json();
const regioniGeo = topojson.feature(regTopo, regTopo.objects.regioni);
const confiniReg = topojson.mesh(regTopo, regTopo.objects.regioni, (a, b) => a !== b);
```

```js
const regioni = await FileAttachment("../data/irpef-regioni.json").json();
const capoluoghi = await FileAttachment("../data/irpef-capoluoghi.json").json();
```

```js
const anni = [...new Set(regioni.map(d => d.anno_di_imposta))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const regFiltered = regioni
  .filter(d => d.anno_di_imposta === annoSel)
  .sort((a, b) => a.regione.localeCompare(b.regione));
```

```js
const capFiltered = capoluoghi
  .filter(d => d.anno === annoSel)
  .sort((a, b) => (b.reddito_imponibile_eur / b.numero_contribuenti) - (a.reddito_imponibile_eur / a.numero_contribuenti));
```

```js
const totContribuenti = regioni
  .filter(d => d.anno_di_imposta === annoSel)
  .reduce((s, d) => s + d.numero_contribuenti, 0);
const totReddito = regioni
  .filter(d => d.anno_di_imposta === annoSel)
  .reduce((s, d) => s + d.reddito_imponibile_eur, 0);
const nRegioni = new Set(regFiltered.map(d => d.regione)).size;
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Contribuenti</h3>
    <span class="big">${totContribuenti.toLocaleString("it-IT")}</span>
  </div>
  <div class="card">
    <h3>Reddito medio</h3>
    <span class="big">€ ${Math.round(totReddito / totContribuenti).toLocaleString("it-IT")}</span>
  </div>
  <div class="card">
    <h3>Regioni</h3>
    <span class="big">${nRegioni}</span>
  </div>
</div>

---

## Composizione del reddito per regione

```js
function normalizzaReg(nome) {
  return nome.toUpperCase().replace(/ \/ /g, '/').replace(/ /g, '-');
}

const totNazionale = d3.sum(regFiltered, d => d.reddito_imponibile_eur);
const irpefLookup = new Map(regFiltered.map(d => [normalizzaReg(d.regione), d.reddito_imponibile_eur / totNazionale * 100]));
```

```js
Plot.plot({
  title: `Quota del reddito nazionale per regione — ${String(annoSel)}`,
  projection: {type: "mercator", domain: regioniGeo},
  width: 800,
  height: 600,
  color: {scheme: "YlOrRd", legend: true, label: "% reddito nazionale", type: "quantile"},
  marks: [
    Plot.geo(regioniGeo, {
      fill: d => irpefLookup.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#fff",
      strokeWidth: 0.25,
      tip: true
    }),
    Plot.geo(confiniReg, {
      stroke: "#fff",
      strokeWidth: 0.7
    })
  ]
})
```

---

## Reddito medio per contribuente — capoluoghi

Quanto guadagna in media un contribuente nei capoluoghi italiani? La classifica mostra il reddito medio dichiarato, che riflette la struttura economica locale (settori prevalenti, costo della vita, specializzazione produttiva).

```js
const capConMedia = capFiltered.map(d => ({
  ...d,
  reddito_medio: Math.round(d.reddito_imponibile_eur / d.numero_contribuenti)
}));
```

```js
Plot.plot({
  title: `Reddito medio per contribuente — capoluoghi ${annoSel}`,
  width: 800,
  height: 350,
  marginLeft: 100,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Turbo"},
  marks: [
    Plot.barX(capConMedia, {
      y: "comune",
      x: "reddito_medio",
      fill: "reddito_medio",
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Dettaglio capoluoghi

```js
Inputs.table(capConMedia, {
  columns: ["comune", "regione", "numero_contribuenti", "reddito_imponibile_eur", "imposta_netta_eur", "reddito_medio"],
  header: {
    comune: "Comune",
    regione: "Regione",
    numero_contribuenti: "Contribuenti",
    reddito_imponibile_eur: "Reddito imponibile (€)",
    imposta_netta_eur: "Imposta netta (€)",
    reddito_medio: "Reddito medio (€)"
  },
  format: {
    reddito_imponibile_eur: x => `€ ${x.toLocaleString("it-IT")}`,
    imposta_netta_eur: x => `€ ${x.toLocaleString("it-IT")}`,
    reddito_medio: x => `€ ${x.toLocaleString("it-IT")}`,
    numero_contribuenti: x => x.toLocaleString("it-IT")
  },
  rows: 20,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: i dati coprono il periodo 2019-2023. Non sono ancora disponibili i dati 2024 al momento dell'ultimo aggiornamento.
- **Contribuenti**: il numero di contribuenti per regione è ottenuto sommando le dichiarazioni per comune. Un contribuente che presenta più fonti di reddito (es. lavoro dipendente + pensione) può essere contato una sola volta nel dato aggregato per comune, ma la metodologia esatta di deduplicazione è definita dal MEF.
- **Reddito medio**: il reddito medio per contribuente è calcolato come rapporto tra reddito imponibile totale e numero di contribuenti. Non tiene conto di distribuzione interna (disuguaglianza) né di differenze del costo della vita tra territori.
- **Capoluoghi**: la lista dei capoluoghi include i comuni capoluogo di regione. I dati per Aosta non sono attualmente disponibili nel data loader.

---

## Risorse

- [MEF — Dipartimento delle Finanze (fonte originale)](https://www1.finanze.gov.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/irpef_comunale/2023/irpef_comunale_2023_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/irpef-comunale)
<!-- Analisi non ancora pubblicata. Quando sarà disponibile, aggiungere:
- [Analisi sul reddito IRPEF](/analisi/irpef-comunale)
-->

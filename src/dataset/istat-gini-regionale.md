---
title: Indice di Gini regionale
description: Disuguaglianza del reddito netto per regione — indice di Gini ISTAT, 2003-2024
source: ISTAT — Dataflow 32_221
source_url: https://esploradati.istat.it/
period: "2003–2024"
last_modified: 2026-05-27
dataset_slug: istat_gini_regionale
---

# Indice di Gini regionale

Disuguaglianza del reddito netto per regione, misurata con l'indice di Gini. I dati permettono di confrontare il livello di disuguaglianza tra territori e la sua evoluzione nel tempo.

**Fonte**: [ISTAT](https://esploradati.istat.it/) · **Periodo**: 2003–2024

```js
import * as topojson from "npm:topojson-client";

const regTopo = await FileAttachment("../data/regioni.topojson").json();
const regioniGeo = topojson.feature(regTopo, regTopo.objects.regioni);
const confiniReg = topojson.mesh(regTopo, regTopo.objects.regioni, (a, b) => a !== b);
```

```js
const data = await FileAttachment("../data/istat-gini-regionale.json").json();
```

```js
// Filtro: default con fitti imputati (più completo per benessere economico)
const conFitti = view(Inputs.toggle({label: "Includi fitti imputati", value: true}));
const presAffImp = conFitti ? 1 : 2;
const filtered = data.filter(d => d.pres_aff_imp === presAffImp);
```

```js
const anni = [...new Set(filtered.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const annoData = filtered
  .filter(d => d.anno === annoSel)
  .sort((a, b) => b.gini - a.gini);

const mediaNazionale = d3.mean(annoData, d => d.gini);

// Normalizza nomi regione per match con TopoJSON
function normalizzaReg(nome) {
  return nome
    .toUpperCase()
    .replace(/ \/ /g, '/')     // " / " → "/"
    .replace(/ /g, '-')        // spazi → trattini
    .replace(/PROVINCIA-AUTONOMA-(BOLZANO|TRENTO).*/, 'TRENTINO-ALTO ADIGE/SÜDTIROL')
    .replace(/TRENTINO-ALTO-ADIGE/, 'TRENTINO-ALTO ADIGE');
}

// Lookup per mappa
const giniLookup = new Map();
for (const d of annoData) {
  const key = normalizzaReg(d.regione);
  // Per Trentino, somma le due province
  if (key === 'TRENTINO-ALTO ADIGE/SÜDTIROL') {
    const curr = giniLookup.get(key) || 0;
    giniLookup.set(key, curr + d.gini);
  } else {
    giniLookup.set(key, d.gini);
  }
}
// Media per Trentino (due province sommate, dividi per 2)
if (giniLookup.has('TRENTINO-ALTO ADIGE/SÜDTIROL')) {
  giniLookup.set('TRENTINO-ALTO ADIGE/SÜDTIROL', giniLookup.get('TRENTINO-ALTO ADIGE/SÜDTIROL') / 2);
}
```

```js
const trendNazionale = Array.from(
  d3.rollup(filtered, v => d3.mean(v, d => d.gini), d => d.anno),
  ([anno, gini]) => ({anno, gini})
).sort((a, b) => a.anno - b.anno);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Media regionale</h3>
    <span class="big">${mediaNazionale.toFixed(3)}</span>
    <small style="opacity:0.6">${annoSel} ${conFitti ? "con" : "senza"} fitti imputati</small>
  </div>
  <div class="card">
    <h3>Regioni</h3>
    <span class="big">${annoData.length}</span>
  </div>
  <div class="card">
    <h3>Min – Max</h3>
    <span class="big">${d3.min(annoData, d => d.gini).toFixed(3)} – ${d3.max(annoData, d => d.gini).toFixed(3)}</span>
  </div>
</div>

---

## Disuguaglianza per regione

Quali regioni hanno la distribuzione del reddito più diseguale? L'indice di Gini varia da 0 (uguaglianza perfetta) a 1 (massima disuguaglianza). La mappa mostra la distribuzione geografica della disuguaglianza, con le regioni del Sud che presentano i valori più alti.

```js
Plot.plot({
  title: `Indice di Gini per regione — ${String(annoSel)}`,
  projection: {type: "mercator", domain: regioniGeo},
  width: 800,
  height: 600,
  color: {scheme: "YlOrRd", legend: true, label: "Gini", type: "quantile"},
  marks: [
    Plot.geo(regioniGeo, {
      fill: d => giniLookup.get(normalizzaReg(d.properties.DEN_REG)),
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

Il Gini medio nazionale (linea tratteggiata) aiuta a confrontare le regioni: quelle sopra la media hanno maggiore disuguaglianza.

> **Nota**: la legenda usa la scala `quantile` — ogni colore contiene lo stesso numero di regioni, indipendentemente dal valore effettivo del Gini. I valori precisi sono nella tabella sottostante.

---

## Evoluzione regionale

La media regionale dell'indice di Gini mostra una leggera riduzione della disuguaglianza tra 2003 e metà anni 2000, seguita da una risalita graduale.

```js
Plot.plot({
  title: `Andamento media regionale ${conFitti ? "con" : "senza"} fitti imputati`,
  width: 800,
  height: 350,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, label: "Gini (0-1)"},
  marks: [
    Plot.lineY(trendNazionale, {
      x: "anno",
      y: "gini",
      tip: {format: {y: d => d.toFixed(3)}}
    }),
    Plot.dot(trendNazionale, {
      x: "anno",
      y: "gini",
      fill: "steelblue",
      r: 2
    }),
    Plot.areaY(trendNazionale, {
      x: "anno",
      y: "gini",
      fill: "steelblue",
      fillOpacity: 0.05
    })
  ]
})
```

---

## Dettaglio per regione

```js
const annoConDelta = annoData.map((d, i) => ({
  ...d,
  pos: i + 1,
  diff_media: d.gini - mediaNazionale
}));
```

```js
Inputs.table(annoConDelta, {
  columns: ["pos", "regione", "gini", "diff_media"],
  header: {pos: "#", regione: "Regione", gini: "Gini", diff_media: "Δ media"},
  format: {gini: x => x.toFixed(3), diff_media: x => (x > 0 ? "+" : "") + x.toFixed(3)},
  rows: 25,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: la serie copre il periodo 2003-2024. Dati 2025 non ancora disponibili al momento dell'ultimo aggiornamento.
- **Fitti imputati**: il toggle "Includi fitti imputati" controlla se nel reddito è incluso il valore figurativo della proprietà dell'abitazione. Con i fitti imputati la disuguaglianza è sistematicamente più bassa (~0.03 punti) perché la proprietà della casa riduce la dispersione del reddito disponibile.
- **Indice di Gini**: misura la disuguaglianza della distribuzione del reddito netto. Non cattura disuguaglianza di ricchezza, consumi o opportunità.
- **Media regionale**: calcolata come media semplice delle regioni, non ponderata per popolazione.

---

## Risorse

- [ISTAT — Esplora dati](https://esploradati.istat.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/istat_gini_regionale/2023/istat_gini_regionale_2023_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/istat-gini-regionale)

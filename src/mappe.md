---
title: Mappa regioni prototipo
description: Prototipo mappa coropletica con Observable Plot
---

# Mappa regioni prototipo

Prototipo di mappa coropletica con Observable Plot. La mappa mostra i confini delle regioni italiane con colore basato sui dati.

```js
import { normalizzaReg, loadItalianRegions, buildRegLookup } from "./import/geo-utils.js";
```

```js
const regTopo = await FileAttachment("./data/regioni.topojson").json();
const { regioniGeo: regioni, confiniReg: confiniRegioni } = await loadItalianRegions(regTopo);
```

```js
// Mappa base — proiezione auto
Plot.plot({
  projection: {type: "mercator", domain: regioni},
  width: 800,
  height: 600,
  marks: [
    Plot.geo(regioni, {
      fill: "#4e79a7",
      stroke: "#fff",
      strokeWidth: 0.25
    }),
    Plot.geo(confiniRegioni, {
      stroke: "#fff",
      strokeWidth: 0.7
    })
  ]
})
```

---

## Mappa con dati — Gini regionale 2023

```js
const giniData = await FileAttachment("./data/istat-gini-regionale.json").json();
const gini2023 = giniData.filter(d => d.anno === 2023 && d.pres_aff_imp === 1);
// Usa buildRegLookupWithTrentino per aggregare P.A. Trentino
import { buildRegLookupWithTrentino } from "./import/geo-utils.js";
const giniLookup = buildRegLookupWithTrentino(
  gini2023,
  "regione",
  (items) => d3.mean(items, d => d.gini),
  "Provincia Autonoma",
);
```

```js
Plot.plot({
  projection: {type: "mercator", domain: regioni},
  width: 800,
  height: 600,
  color: {scheme: "YlOrRd", legend: true, label: "Gini (2023)", type: "quantile"},
  marks: [
    Plot.geo(regioni, {
      fill: d => giniLookup.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#fff",
      strokeWidth: 0.25,
      tip: true
    }),
    Plot.geo(confiniRegioni, {
      stroke: "#fff",
      strokeWidth: 0.7
    })
  ]
})
```

---

## Note

- **TopoJSON**: confini ISTAT regioni, copia locale in `src/data/regioni.topojson`, convertita con `topojson-client`
- **Join**: `d.properties.DEN_REG.toUpperCase()` fa match con i nomi regione nei nostri dataset (tutti in maiuscolo)
- **Proiezione**: `mercator` con dominio calcolato sulle geometrie italiane
- **Scala colore**: `type: "quantile"` distribuisce i valori in classi equinumerose (evita squilibri)

### Passi successivi

1. Verificare quali dataset hanno nomi regione che matchano `DEN_REG.toUpperCase()`
2. Eventualmente aggiungere `province.topojson` per mappe più dettagliate
3. Integrare la mappa nelle pagine dataset esistenti (es. Gini, IRPEF, rifiuti...)

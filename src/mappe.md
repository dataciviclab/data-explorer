---
title: Mappa regioni prototipo
description: Prototipo mappa coropletica con Observable Plot
---

# Mappa regioni prototipo

Prototipo di mappa coropletica con Observable Plot. La mappa mostra i confini delle regioni italiane con colore basato sui dati.

```js
const regioni = await FileAttachment("../data/regioni.topojson").json();
```

```js
// Mostra la mappa base
Plot.plot({
  projection: "mercator",
  width: 800,
  height: 800,
  marks: [
    Plot.geo(regioni, {
      fill: "#eee",
      stroke: "#fff",
      strokeWidth: 0.5
    })
  ]
})
```

---

## Mappa con dati — Gini regionale 2023

```js
const gini = await FileAttachment("../data/istat-gini-regionale.json").json();
const gini2023 = gini.filter(d => d.anno === 2023 && d.pres_aff_imp === 1);
const giniLookup = new Map(gini2023.map(d => [d.regione.toUpperCase(), d.gini]));
```

```js
Plot.plot({
  projection: "mercator",
  width: 800,
  height: 800,
  color: {scheme: "RdYlGn", legend: true, label: "Gini (2023)", type: "quantile"},
  marks: [
    Plot.geo(regioni, {
      fill: d => {
        const nome = d.properties.DEN_REG.toUpperCase();
        return giniLookup.get(nome);
      },
      stroke: "#fff",
      strokeWidth: 0.5,
      tip: true,
      channels: {
        regione: d => d.properties.DEN_REG,
        gini: d => {
          const nome = d.properties.DEN_REG.toUpperCase();
          return giniLookup.get(nome)?.toFixed(3);
        }
      }
    })
  ]
})
```

---

## Note

- **TopoJSON**: confini ISTAT regioni, 474KB, copia locale in `src/data/regioni.topojson`
- **Join**: `d.properties.DEN_REG.toUpperCase()` fa match con i nomi regione nei nostri dataset (tutti in maiuscolo)
- **Proiezione**: `mercator` (default). Si può cambiare in `"identity"` per mantenere le proporzioni reali
- **Scala colore**: `type: "quantile"` distribuisce i valori in classi equinumerose (evita squilibri)

### Passi successivi

1. Verificare quali dataset hanno nomi regione che matchano `DEN_REG.toUpperCase()`
2. Eventualmente aggiungere `province.topojson` per mappe più dettagliate
3. Integrare la mappa nelle pagine dataset esistenti (es. Gini, IRPEF, rifiuti...)

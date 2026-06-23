---
title: 5x1000 — Beneficiari e importi per ente
description: "Oltre 90.000 enti che ricevono il 5x1000: importi per regione, categoria e singolo ente (Agenzia Entrate)"
source: Agenzia delle Entrate
source_url: https://www.agenziaentrate.gov.it/portale/area-tematica-5x1000
period: "2024"
last_modified: 2026-06-23
dataset_slug: ade_cinque_per_mille
---

# 5x1000 — Beneficiari e importi per ente

Ogni anno, i contribuenti italiani possono destinare il 5x1000 della propria IRPEF a enti del terzo settore, ricerca scientifica, sanitaria, comuni, associazioni sportive e beni culturali. Nel 2024 oltre **90.000 enti** hanno ricevuto più di **€520 milioni** da 16,7 milioni di scelte. Questa pagina mostra come si distribuiscono: per territorio, per categoria e per singolo ente.

**Fonte**: [Agenzia delle Entrate](https://www.agenziaentrate.gov.it/portale/area-tematica-5x1000) · **Periodo**: 2024

```js
import { num, euro, euroCompact, pct, numFix, tableFormat } from "../import/format-utils.js";
import { normalizzaReg, loadItalianRegions, buildMapLookup } from "../import/geo-utils.js";
```

```js
const regTopo = await FileAttachment("../data/regioni.topojson").json();
const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
```

```js
const data = await FileAttachment("../data/cinque-per-mille.json").json();
const { per_regione, per_categoria, top_enti } = data;
```

```js
// Unifica P.A. Trentino: il dataset ha due righe separate
const pa = per_regione.filter(r => r.regione && r.regione.includes("ADIGE"));
const perRegioneUnificata = [
  ...per_regione.filter(r => r.regione && !r.regione.includes("ADIGE")),
  ...(pa.length > 1 ? [{
    regione: "TRENTINO-ALTO-ADIGE",
    num_enti: d3.sum(pa, r => r.num_enti),
    tot_scelte: d3.sum(pa, r => r.tot_scelte),
    importo_totale: d3.sum(pa, r => r.importo_totale),
  }] : []),
];

const lookup = buildMapLookup(perRegioneUnificata, regioniGeo, "regione", "importo_totale");
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Enti beneficiari</h3>
    <span class="big">${num(data.num_enti)}</span>
  </div>
  <div class="card">
    <h3>Importo totale</h3>
    <span class="big">${euro(data.importo_totale)}</span>
  </div>
  <div class="card">
    <h3>Scelte dei contribuenti</h3>
    <span class="big">${num(data.tot_scelte)}</span>
  </div>
</div>

---

## Quanto riceve ogni regione?

La distribuzione territoriale del 5x1000 è fortemente concentrata: Lombardia e Lazio da sole assorbono oltre la metà delle risorse.

```js
Plot.plot({
  title: `Importi 5x1000 per regione — ${data.anno}`,
  projection: {type: "mercator", domain: regioniGeo},
  width: 800,
  height: 600,
  color: {scheme: "OrRd", legend: true, label: "Importo erogabile (€)", type: "quantile"},
  marks: [
    Plot.geo(regioniGeo, {
      fill: d => lookup.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#888",
      strokeWidth: 0.25,
      title: d => `${d.properties.DEN_REG}: ${euro(lookup.get(normalizzaReg(d.properties.DEN_REG)))}`
    }),
    Plot.geo(confiniReg, {stroke: "#888", strokeWidth: 0.7}),
    Plot.tip(regioniGeo, Plot.pointer({
      channels: {
        regione: d => d.properties.DEN_REG,
        importo: d => lookup.get(normalizzaReg(d.properties.DEN_REG))
      },
      format: {regione: d => d, importo: d => euro(d)}
    }))
  ]
})
```

---

## Dove va il 5x1000?

L'81% delle risorse va agli enti del Terzo Settore (ETS e ONLUS). La ricerca sanitaria e scientifica assorbe un altro 16%. Sport, comuni e beni culturali pesano per il restante 3%.

```js
Plot.plot({
  title: `5x1000 per categoria — ${data.anno}`,
  width: 800,
  height: 350,
  marginLeft: 200,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: d => euro(d)},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(per_categoria, {
      y: "categoria",
      x: "importo_totale",
      fill: "categoria",
      sort: {y: "-x"},
      tip: {format: {x: d => euro(Number(d))}}
    }),
    Plot.text(per_categoria, {
      y: "categoria",
      x: "importo_totale",
      text: d => euro(d.importo_totale) + " — " + num(d.num_enti) + " enti",
      dx: 8,
      textAnchor: "start",
      fill: "var(--theme-foreground-muted)",
      fontSize: 11
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Dettaglio enti

Cerca un ente per nome, oppure filtra per regione.

```js
const { header, format } = tableFormat({
  denominazione: "string",
  regione: "string",
  sigla_provincia: "string",
  comune: "string",
  numero_scelte: "num",
  importo_totale: "euro"
});
```

```js
const searchQuery = view(Inputs.search(top_enti, {label: "Cerca ente", placeholder: "digita il nome…"}));
const regioniList = ["Tutte", ...new Set(top_enti.map(d => d.regione).sort())];
const regioneFilter = view(Inputs.select(regioniList, {label: "Regione"}));
```

```js
const tableData = searchQuery
  .filter(d => regioneFilter === "Tutte" || d.regione === regioneFilter);
```

```js
Inputs.table(tableData, {
  columns: ["denominazione", "regione", "sigla_provincia", "comune", "numero_scelte", "importo_totale"],
  header,
  format,
  rows: 20,
  width: "100%",
  sort: "importo_totale",
  reverse: true
})
```

---

## Limiti

- **Copertura**: il dataset copre il solo 2024. Non sono ancora disponibili i dati 2025 nel formato clean.
- **Dettaglio ente**: la denominazione degli enti può contenere refusi o caratteri anomali (es. "Bambin Ges?" invece di "Bambin Gesù") ereditati dai CSV originali dell'Agenzia delle Entrate.
- **Categorie multiple**: un ente può appartenere a più categorie contemporaneamente (es. ente ETS che fa anche ricerca scientifica). Nel grafico per categoria ogni ente è conteggiato in tutte le sue categorie.

---

## Risorse

- [Agenzia delle Entrate — 5x1000 (fonte originale)](https://www.agenziaentrate.gov.it/portale/area-tematica-5x1000)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/ade_cinque_per_mille/2024/ade_cinque_per_mille_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/ade-cinque-per-mille)

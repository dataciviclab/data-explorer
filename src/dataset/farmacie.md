---
title: Farmacie italiane
description: Anagrafica delle farmacie italiane — indirizzo, comune, provincia, coordinate e tipologia, 2026
source: Ministero della Salute
source_url: https://www.salute.gov.it/portale/lea/dettaglioContenutiLea.jsp?lingua=italiano&id=5551&area=Lea&menu=vuoto
period: "2026"
last_modified: 2026-06-20
dataset_slug: farmacie
---

# Farmacie italiane

L'anagrafica completa delle farmacie italiane pubbliche e private: oltre 58.000 farmacie, dispensari e succursali su tutto il territorio nazionale. Per ogni farmacia sono disponibili indirizzo, coordinate geografiche, tipologia e periodo di attività. Dati aggiornati al 2026.

**Fonte**: Ministero della Salute · **Periodo**: 2026

```js
import { num, euro, euroCompact, pct, numFix, tableFormat } from "../import/format-utils.js";
import { normalizzaReg, loadItalianRegions, buildMapLookup } from "../import/geo-utils.js";
```

```js
const regTopo = await FileAttachment("../data/regioni.topojson").json();
const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
```

```js
const data = await FileAttachment("../data/farmacie.json").json();
const { per_regione, per_tipologia, per_provincia } = data;
```

```js
// Fallback per nomi regione
const extraFallbacks = {
  "VALLE D`AOSTA": "VALLE-D'AOSTA/VALLÉE-D'AOSTE",
  "PROV. AUTON. BOLZANO": "TRENTINO-ALTO-ADIGE/SÜDTIROL",
  "PROV. AUTON. TRENTO": "TRENTINO-ALTO-ADIGE/SÜDTIROL",
};
```

```js
// Unifica P.A. Bolzano + Trento per la mappa
const pa = per_regione.filter(r => r.regione.includes("PROV."));
const perRegioneUnificata = [
  ...per_regione.filter(r => !r.regione.includes("PROV.")),
  {
    regione: "TRENTINO-ALTO-ADIGE",
    totale_farmacie: d3.sum(pa, r => r.totale_farmacie),
    comuni_con_farmacie: d3.sum(pa, r => r.comuni_con_farmacie),
  },
];

const lookup = buildMapLookup(perRegioneUnificata, regioniGeo, "regione", "totale_farmacie", null, extraFallbacks);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Farmacie</h3>
    <span class="big">${num(data.totale_farmacie)}</span>
  </div>
  <div class="card">
    <h3>Tipologie</h3>
    <span class="big">${per_tipologia.length}</span>
  </div>
  <div class="card">
    <h3>Regioni</h3>
    <span class="big">${per_regione.length}</span>
  </div>
</div>

---

## Farmacie per regione

La distribuzione delle farmacie sul territorio segue la popolazione: Lombardia, Campania e Lazio hanno il numero più elevato di farmacie. Il dato include farmacie ordinarie, succursali e dispensari.

```js
Plot.plot({
  title: "Farmacie per regione — 2026",
  projection: {type: "mercator", domain: regioniGeo},
  width: 800,
  height: 600,
  color: {scheme: "Greens", legend: true, label: "Farmacie", type: "quantile"},
  marks: [
    Plot.geo(regioniGeo, {
      fill: d => lookup.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#888",
      strokeWidth: 0.25,
      title: d => `${d.properties.DEN_REG}: ${num(lookup.get(normalizzaReg(d.properties.DEN_REG)))} farmacie`
    }),
    Plot.geo(confiniReg, {stroke: "#888", strokeWidth: 0.7}),
    Plot.tip(regioniGeo, Plot.pointer({
      channels: {
        regione: d => d.properties.DEN_REG,
        farmacie: d => lookup.get(normalizzaReg(d.properties.DEN_REG))
      },
      format: {
        regione: d => d,
        farmacie: d => num(d) + " farmacie"
      }
    }))
  ]
})
```

---

## Farmacie per tipologia

La stragrande maggioranza delle farmacie italiane sono di tipo ordinario. I dispensari (farmacie rurali a orario ridotto) e le succursali completano il panorama, garantendo copertura anche nelle aree meno popolate.

```js
// Normalizza tipologie: unifica case variations
const tipi = Array.from(d3.rollup(
  per_tipologia.map(d => ({
    ...d,
    tipo: d.descrizione_tipologia === "-" ? "Non specificato"
       : d.descrizione_tipologia.toLowerCase() === "dispensario stagionale" ? "Dispensario stagionale"
       : d.descrizione_tipologia.charAt(0).toUpperCase() + d.descrizione_tipologia.slice(1).toLowerCase()
  })),
  v => ({totale: d3.sum(v, d => d.totale)}),
  d => d.tipo
), ([tipo, v]) => ({tipo, totale: v.totale}))
  .sort((a,b) => b.totale - a.totale);
```

```js
Plot.plot({
  title: "Farmacie per tipologia — 2026",
  width: 800,
  height: 300,
  marginLeft: 160,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(tipi, {
      y: "tipo",
      x: "totale",
      fill: "tipo",
      sort: {y: "-x"},
      tip: {format: {x: d => num(d)}}
    }),
    Plot.text(tipi, {
      y: "tipo",
      x: "totale",
      text: d => num(d.totale),
      dx: 6,
      textAnchor: "start",
      fill: "var(--theme-foreground-muted)",
      fontSize: 11
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Province con più farmacie

```js
const { header, format } = tableFormat({
  provincia: { label: "Provincia", fmt: "string" },
  sigla_provincia: { label: "Sigla", fmt: "string" },
  regione: { label: "Regione", fmt: "string" },
  totale: { label: "Farmacie", fmt: "num" },
});
```

```js
Inputs.table(per_provincia, {
  columns: ["provincia", "sigla_provincia", "regione", "totale"],
  header,
  format,
  rows: 30,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: i dati sono aggiornati al 2026. Le farmacie con data di chiusura antecedente possono comunque comparire nel dataset (sono conservate le record storiche).
- **Coordinate**: alcune farmacie potrebbero non avere coordinate geografiche (latitudine/longitudine non disponibili per tutti i record).
- **Tipologia**: la classificazione della tipologia presenta alcune disomogeneità (es. "Dispensario" vs "Dispensario stagionale", maiuscole/minuscole). I dati sono normalizzati il più possibile in questa pagina.
- **Doppi record**: una farmacia può avere più record se ha cambiato denominazione o gestione (date di validità multiple). Il conteggio totale (`58.691`) include queste variazioni.

---

## Risorse

- [Ministero della Salute — Open Data](https://www.salute.gov.it/portale/lea/dettaglioContenutiLea.jsp?lingua=italiano&id=5551&area=Lea&menu=vuoto)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/farmacie/2026/farmacie_2026_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/farmacie)

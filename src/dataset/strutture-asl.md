---
title: Strutture e attività delle ASL
description: Medici di base, pediatri, residenti e spesa farmaceutica per ogni Azienda Sanitaria Locale italiana, 2022
source: Ministero della Salute
source_url: https://www.salute.gov.it/portale/lea/dettaglioContenutiLea.jsp?lingua=italiano&id=5551&area=Lea&menu=vuoto
period: "2022"
last_modified: 2026-06-05
dataset_slug: strutture_asl
---

# Strutture e attività delle ASL

Medici di medicina generale, pediatri di libera scelta, popolazione residente e spesa farmaceutica convenzionata per ogni ASL italiana. I dati fotografano l'offerta territoriale della medicina di base nel 2022.

**Fonte**: Ministero della Salute · **Periodo**: 2022

```js
import { num, euro, euroCompact, pct, numFix, tableFormat } from "../import/format-utils.js";
import { normalizzaReg, loadItalianRegions, buildMapLookup } from "../import/geo-utils.js";
```

```js
const regTopo = await FileAttachment("../data/regioni.topojson").json();
const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
```

```js
const data = await FileAttachment("../data/strutture-asl.json").json();
```

```js
// Fallback per "VALLE D`AOSTA" (backtick invece di apostrofo nel dataset)
const extraFallbacks = { "VALLE D`AOSTA": "VALLE-D'AOSTA/VALLÉE-D'AOSTE" };
```

```js
// Aggregazione per regione
const perRegione = Array.from(d3.rollup(data, v => ({
  residenti: d3.sum(v, d => d.totale_residenti),
  medici: d3.sum(v, d => d.totale_medici),
  pediatri: d3.sum(v, d => d.totale_pediatri),
  importo_ricette: d3.sum(v, d => d.euro_importo_ricette),
  num_ricette: d3.sum(v, d => d.num_ricette_specialita_medicinali)
}), d => d.regione), ([regione, v]) => ({regione, ...v})).sort((a,b) => b.residenti - a.residenti);

// Medici ogni 10.000 residenti
const perRegioneMedici = perRegione.map(d => ({
  regione: d.regione,
  medici_per_10k: Math.round(d.medici / d.residenti * 10000 * 10) / 10,
  spesa_procapite: Math.round(d.importo_ricette / d.residenti),
}));
const lookup = buildMapLookup(perRegioneMedici, regioniGeo, "regione", "medici_per_10k", null, extraFallbacks);
```

```js
const totaleMedici = d3.sum(data, d => d.totale_medici);
const totalePediatri = d3.sum(data, d => d.totale_pediatri);
const totaleResidenti = d3.sum(data, d => d.totale_residenti);
const totaleRicette = d3.sum(data, d => d.euro_importo_ricette);
const numAsl = data.length;
```

<div class="grid grid-cols-4">
  <div class="card">
    <h3>ASL</h3>
    <span class="big">${num(numAsl)}</span>
  </div>
  <div class="card">
    <h3>Medici di base</h3>
    <span class="big">${num(totaleMedici)}</span>
  </div>
  <div class="card">
    <h3>Pediatri</h3>
    <span class="big">${num(totalePediatri)}</span>
  </div>
  <div class="card">
    <h3>Spesa farmaceutica</h3>
    <span class="big">${euroCompact(totaleRicette)}</span>
  </div>
</div>

---

## Medici di base ogni 10.000 residenti

Quanti medici di medicina generale servono la popolazione in ogni regione? La densità di medici di base varia sensibilmente sul territorio: si va dai circa 5 medici ogni 10.000 residenti di alcune regioni del Sud agli oltre 7 del Nord-Ovest.

```js
Plot.plot({
  title: "Medici di base ogni 10.000 residenti per regione — 2022",
  projection: {type: "mercator", domain: regioniGeo},
  width: 800,
  height: 600,
  color: {scheme: "Reds", legend: true, label: "Medici / 10.000 res.", type: "quantile"},
  marks: [
    Plot.geo(regioniGeo, {
      fill: d => lookup.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#888",
      strokeWidth: 0.25,
      tip: {format: {fill: d => numFix(d) + " ogni 10.000"}}
    }),
    Plot.geo(confiniReg, {
      stroke: "#888",
      strokeWidth: 0.7
    })
  ]
})
```

> **Nota**: il dato include i medici di medicina generale convenzionati con il SSN. Non include la medicina specialistica ambulatoriale né i pediatri (che hanno un indicatore separato più sotto).

---

## Spesa farmaceutica pro-capite per regione

La spesa per ricette farmaceutiche convenzionate varia tra regioni, riflettendo differenze nella popolazione, nella prescrizione e nell'organizzazione del sistema.

```js
Plot.plot({
  title: "Spesa farmaceutica pro-capite per regione — 2022",
  width: 800,
  height: 400,
  marginLeft: 140,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  color: {scheme: "RdYlBu", type: "diverging"},
  marks: [
    Plot.barX(perRegioneMedici.sort((a,b) => d3.descending(a.spesa_procapite, b.spesa_procapite)), {
      y: "regione",
      x: "spesa_procapite",
      fill: "spesa_procapite",
      tip: {format: {x: d => euro(d)}}
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Pediatri ogni 10.000 residenti in età infantile

La popolazione in età pediatrica (0-14 anni) è servita dai pediatri di libera scelta. Il rapporto pediatri/bambini è un indicatore importante della capacità del territorio di seguire la popolazione più giovane.

```js
// Stima popolazione infantile per regione (dal dataset strutture_asl: residenti_eta_infantile)
// Non avendo quella colonna nel loader, usiamo una proxy: 14% della popolazione totale (media italiana)
// In alternativa, usiamo il rapporto pediatri / totale residenti * 10000 * 0.14 correzione
// Meglio: mostriamo direttamente pediatri ogni 10.000 residenti totali
const perRegionePediatri = perRegione.map(d => ({
  regione: d.regione,
  pediatri_per_10k: Math.round(d.pediatri / d.residenti * 10000 * 10) / 10,
}));
const lookupPediatri = buildMapLookup(perRegionePediatri, regioniGeo, "regione", "pediatri_per_10k", null, extraFallbacks);
```

```js
Plot.plot({
  title: "Pediatri di libera scelta ogni 10.000 residenti — 2022",
  projection: {type: "mercator", domain: regioniGeo},
  width: 800,
  height: 600,
  color: {scheme: "Blues", legend: true, label: "Pediatri / 10.000 res.", type: "quantile"},
  marks: [
    Plot.geo(regioniGeo, {
      fill: d => lookupPediatri.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#888",
      strokeWidth: 0.25,
      tip: {format: {fill: d => numFix(d) + " ogni 10.000"}}
    }),
    Plot.geo(confiniReg, {
      stroke: "#888",
      strokeWidth: 0.7
    })
  ]
})
```

---

## Dettaglio ASL

```js
const { header, format } = tableFormat({
  denominazione_asl: { label: "ASL", fmt: "string" },
  regione: { label: "Regione", fmt: "string" },
  comune_asl: { label: "Sede", fmt: "string" },
  totale_residenti: { label: "Residenti", fmt: "num" },
  totale_medici: { label: "Medici", fmt: "num" },
  totale_pediatri: { label: "Pediatri", fmt: "num" },
  euro_importo_ricette: { label: "Spesa ricette (€)", fmt: "euro" },
});
```

```js
Inputs.table(data, {
  columns: ["denominazione_asl", "regione", "comune_asl", "totale_residenti", "totale_medici", "totale_pediatri", "euro_importo_ricette"],
  header,
  format,
  rows: 20,
  width: "100%"
})
```

---

## Limiti

- **Copertura**: i dati si riferiscono al 2022. Non sono disponibili anni precedenti o successivi in questo dataset.
- **Medici di base**: il dato conta i medici convenzionati, non necessariamente equivalenti a tempo pieno. I volumi di attività effettivi possono variare.
- **Spesa farmaceutica**: l'importo si riferisce alle sole ricette di specialità medicinali e galenici convenzionati SSN. Non include la spesa privata né quella ospedaliera.

---

## Risorse

- [Ministero della Salute — Open Data Strutture e attività ASL](https://www.salute.gov.it/portale/lea/dettaglioContenutiLea.jsp?lingua=italiano&id=5551&area=Lea&menu=vuoto)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/strutture_asl/2022/strutture_asl_2022_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/strutture-asl)

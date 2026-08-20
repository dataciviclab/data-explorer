---
title: FTS EU Grants — Finanziamenti UE in Italia
description: Finanziamenti UE a beneficiari italiani dal Financial Transparency System, per anno, programma, territorio e beneficiario
source: Commissione europea — Financial Transparency System
source_url: https://commission.europa.eu/funding-tenders/financial-transparency-system_en
period: "2020–2024"
last_modified: 2026-07-01
dataset_slug: fts_eu_grants
data_driven: true
---

# FTS EU Grants — Finanziamenti UE in Italia

**Nel ${annoSel} i finanziamenti UE tracciati al FTS in Italia valgono ${euroCompact(annoData?.importo_totale)}, distribuiti in ${num(annoData?.numero_grant)} operazioni a ${num(annoData?.beneficiari)} beneficiari. La domanda che apre i dati: questi flussi arrivano davvero dove sono dichiarati, o la sede del beneficiario nasconde la destinazione finale dei fondi?**

Il Financial Transparency System della Commissione europea elenca i finanziamenti UE assegnati a beneficiari italiani. Il dataset copre il periodo 2020-2024 e permette di leggere importi, programmi, beneficiari e localizzazione dichiarata.

**Fonte**: [Commissione europea — Financial Transparency System](https://commission.europa.eu/funding-tenders/financial-transparency-system_en) · **Periodo**: 2020–2024

```js
import { num, euroCompact, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/fts-eu-grants.json").json();
```

```js
const anni = [...data.anni].sort((a, b) => b - a);
const annoSel = view(Inputs.select(anni, {label: "Anno", value: anni[0]}));
```

```js
const annoData = data.per_anno.find(d => d.anno === annoSel);
const programmi = data.per_programma
  .filter(d => d.anno === annoSel)
  .sort((a, b) => d3.descending(a.importo_totale, b.importo_totale));
const tipiEnte = data.per_tipo_ente
  .filter(d => d.anno === annoSel)
  .sort((a, b) => d3.descending(a.importo_totale, b.importo_totale));
const citta = data.per_citta
  .filter(d => d.anno === annoSel)
  .sort((a, b) => d3.descending(a.importo_totale, b.importo_totale));
const beneficiari = data.top_beneficiari
  .filter(d => d.anno === annoSel)
  .sort((a, b) => d3.descending(a.importo_totale, b.importo_totale));
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Importo contrattato</h3>
    <span class="big">${euroCompact(annoData?.importo_totale)}</span>
  </div>
  <div class="card">
    <h3>Grant</h3>
    <span class="big">${num(annoData?.numero_grant)}</span>
  </div>
  <div class="card">
    <h3>Beneficiari</h3>
    <span class="big">${num(annoData?.beneficiari)}</span>
  </div>
</div>

---

## Programmi finanziati

La prima lettura mostra come si distribuiscono gli importi per area di programma nell'anno selezionato.

```js
Plot.plot({
  title: `Importo contrattato per programma — ${annoSel}`,
  width: 800,
  height: Math.max(340, programmi.length * 34 + 48),
  marginLeft: 190,
  x: {grid: true, label: "euro", tickFormat: d => euroCompact(d)},
  y: {label: null, tickSize: 0},
  color: {scheme: "Tableau10"},
  marks: [
    Plot.barX(programmi, {
      y: "categoria_programma",
      x: "importo_totale",
      fill: "categoria_programma",
      sort: {y: "-x"},
      tip: {format: {x: d => euroCompact(d)}}
    }),
    Plot.ruleX([0])
  ]
})
```

> **Nota**: la categoria "Recovery and resilience" può concentrare importi molto grandi in poche righe, perché il FTS registra anche flussi collegati al Recovery and Resilience Facility.

---

## Beneficiari e territorio

La vista per tipo di ente aiuta a distinguere imprese, università, amministrazioni e organizzazioni non profit. La vista per città mostra dove sono dichiarati gli importi maggiori, ma alcune righe FTS non indicano una città.

```js
Plot.plot({
  title: `Importo per tipo di beneficiario — ${annoSel}`,
  width: 800,
  height: 320,
  marginLeft: 170,
  x: {grid: true, label: "euro", tickFormat: d => euroCompact(d)},
  y: {label: null, tickSize: 0},
  color: {scheme: "Set2"},
  marks: [
    Plot.barX(tipiEnte, {
      y: "tipo_ente",
      x: "importo_totale",
      fill: "tipo_ente",
      sort: {y: "-x"},
      tip: {format: {x: d => euroCompact(d)}}
    }),
    Plot.ruleX([0])
  ]
})
```

```js
Plot.plot({
  title: `Prime città per importo dichiarato — ${annoSel}`,
  width: 800,
  height: 380,
  marginLeft: 130,
  x: {grid: true, label: "euro", tickFormat: d => euroCompact(d)},
  y: {label: null, tickSize: 0},
  marks: [
    Plot.barX(citta.slice(0, 12), {
      y: "citta",
      x: "importo_totale",
      fill: "var(--theme-foreground-focus)",
      sort: {y: "-x"},
      tip: {format: {x: d => euroCompact(d)}}
    }),
    Plot.ruleX([0])
  ]
})
```

---

## Trend annuale

Il confronto tra anni serve a vedere la scala complessiva del dataset, non a misurare l'intero budget UE speso in Italia.

```js
Plot.plot({
  title: "Importo contrattato per anno",
  width: 800,
  height: 320,
  x: {label: "anno", tickFormat: String},
  y: {grid: true, label: "euro", tickFormat: d => euroCompact(d)},
  marks: [
    Plot.ruleY([0]),
    Plot.lineY(data.per_anno, {
      x: "anno",
      y: "importo_totale",
      stroke: "var(--theme-foreground-focus)",
      strokeWidth: 2,
      marker: true,
      tip: {format: {y: d => euroCompact(d)}}
    })
  ]
})
```

---

## Dettaglio beneficiari

```js
const { header, format } = tableFormat({
  beneficiario_nome: { label: "Beneficiario", fmt: "string" },
  beneficiario_citta: { label: "Città", fmt: "string" },
  categoria_programma: { label: "Programma", fmt: "string" },
  tipo_ente: { label: "Tipo ente", fmt: "string" },
  numero_grant: { label: "Grant", fmt: "num" },
  importo_totale: { label: "Importo", fmt: "euroCompact" },
});
```

```js
Inputs.table(beneficiari, {
  columns: ["beneficiario_nome", "beneficiario_citta", "categoria_programma", "tipo_ente", "numero_grant", "importo_totale"],
  header,
  format,
  rows: 20,
  width: "100%",
  sort: "importo_totale",
  reverse: true
})
```

---

## La domanda che resta

FTS è una fotografia dei fondi UE **diretti** in Italia (assegnati dalla Commissione), non dei fondi gestiti a livello nazionale. Le classifiche per città e programma servono a orientare la lettura, ma la sede del beneficiario non coincide sempre con la destinazione finale delle risorse. Resta aperta la domanda: quanto di questi fondi produce investimento nei territori dichiarati, e quanto è concentrato in un numero ristretto di soggetti attraverso programmi di grande scala come il Recovery and Resilience Facility?

## Limiti

- **Perimetro**: FTS copre i pagamenti e gli impegni tracciati dalla Commissione europea; non sostituisce OpenCoesione o altre fonti sui fondi strutturali gestiti a livello nazionale.
- **Territorio**: la città del beneficiario può mancare o essere indicata come `-`, quindi le classifiche territoriali non sono una mappa completa della destinazione finale dei fondi.
- **Classificazioni**: le categorie programma e tipo ente sono derivate da campi testuali e servono per orientare la lettura, non come tassonomia ufficiale.

---

## Risorse

- [Financial Transparency System](https://commission.europa.eu/funding-tenders/financial-transparency-system_en)
- [Scarica il parquet pulito 2024](https://storage.googleapis.com/dataciviclab-clean/fts_eu_grants/2024/fts_eu_grants_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/fts-eu-grants)

---
title: 5x1000 — beneficiari e importi per ente
description: "Il 5x1000: come si distribuisce il fondo per territorio, categoria e singolo ente (Agenzia delle Entrate)"
source: Agenzia delle Entrate
source_url: https://www.agenziaentrate.gov.it/portale/area-tematica-5x1000
period: "2024"
last_modified: 2026-06-23
dataset_slug: ade_cinque_per_mille
data_driven: true
---

# 5x1000 — dove vanno i soldi della tua firma

**Nel ${anno} ${num(numEnti)} enti hanno ricevuto più di ${euroCompact(importoTot)} dal 5x1000, da ${numFix(totScelte / 1e6, 1)} milioni di scelte dei contribuenti. Ma la distribuzione è fortemente concentrata: Lombardia e Lazio da sole assorbono oltre la metà delle risorse, e i primi 10 enti prendono più di un quarto del totale.**

Ogni anno i contribuenti italiani destinano il 5x1000 della propria IRPEF a enti del Terzo Settore, ricerca scientifica e sanitaria, comuni, associazioni sportive, beni culturali e aree protette. Questa pagina mostra come si distribuiscono i fondi per territorio, categoria e singolo ente. I numeri sono calcolati dal dato a build-time: se si ripubblica il parquet, KPI e grafici si aggiornano da soli.

```js
import { num, euroCompact, pct, numFix, tableFormat } from "../import/format-utils.js";
import { normalizzaReg, loadItalianRegions, buildMapLookup } from "../import/geo-utils.js";
```

```js
const regTopo = await FileAttachment("../data/regioni.topojson").json();
const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
```

```js
const raw = await FileAttachment("../data/cinque-per-mille.json").json();
const { per_regione, per_categoria, top_enti } = raw;
const anno = raw.anno;
const numEnti = raw.num_enti;
const importoTot = raw.importo_totale;
const totScelte = raw.tot_scelte;
```

```js
// Unifica le due P.A. Trentino (bolzano+trento) in un'unica regione, come nel TopoJSON ISTAT
const adige = per_regione.filter(r => /ADIGE/.test(r.regione));
const perRegione = [
  ...per_regione.filter(r => !/ADIGE/.test(r.regione)),
  ...(adige.length ? [{
    regione: "TRENTINO-ALTO-ADIGE",
    num_enti: d3.sum(adige, r => r.num_enti),
    tot_scelte: d3.sum(adige, r => r.tot_scelte),
    importo_totale: d3.sum(adige, r => r.importo_totale)
  }] : [])
];
const regSorted = [...perRegione].sort((a, b) => b.importo_totale - a.importo_totale);
const lookup = buildMapLookup(perRegione, regioniGeo, "regione", "importo_totale");
```

```js
// Metriche derivate: concentrazione, terzo settore, top enti
const qTotale = (v, tot) => tot ? ((v ?? 0) / tot) * 100 : null;
const quotaTop2 = qTotale(regSorted[0].importo_totale + (regSorted[1]?.importo_totale ?? 0), importoTot);
const topReg = regSorted[0];
const tsShare = qTotale(d3.sum(per_categoria.filter(c => c.categoria === "ETS / ONLUS" || c.categoria.startsWith("ETS +")), c => c.importo_totale), importoTot);
const top10 = top_enti.slice(0, 10);
const quotaTop10 = qTotale(d3.sum(top10, r => r.importo_totale), importoTot);
const importoMedio = numEnti ? importoTot / numEnti : null;
```

<div class="grid grid-cols-4">
  <div class="card"><h3>Enti beneficiari ${anno}</h3><span class="big">${num(numEnti)}</span></div>
  <div class="card"><h3>Importo totale</h3><span class="big">${euroCompact(importoTot)}</span></div>
  <div class="card"><h3>Scelte dei cittadini</h3><span class="big">${numFix(totScelte / 1e6, 1)} Mln</span></div>
  <div class="card"><h3>Top 10 enti</h3><span class="big">${pct(quotaTop10)}</span></div>
</div>

## 1. Quanto riceve ogni regione?

La distribuzione territoriale del 5x1000 è fortemente polarizzata. La mappa mostra l'importo erogabile per regione: il quadro è dominato dal Nord e da due "hub" nazionali, Lombardia e Lazio, che concentrano la maggior parte delle risorse.

```js
const plot = await import("npm:@observablehq/plot");
display(plot.plot({
  title: `Importi 5x1000 per regione — ${anno}`,
  projection: {type: "mercator", domain: regioniGeo},
  width: 800, height: 600,
  color: {scheme: "OrRd", legend: true, label: "Importo erogabile (€)", type: "quantile"},
  marks: [
    plot.geo(regioniGeo, {
      fill: d => lookup.get(normalizzaReg(d.properties.DEN_REG)),
      stroke: "#888", strokeWidth: 0.25,
      title: d => `${d.properties.DEN_REG}: ${euroCompact(lookup.get(normalizzaReg(d.properties.DEN_REG)))}`,
      tip: true
    }),
    plot.geo(confiniReg, {stroke: "#888", strokeWidth: 0.7})
  ]
}))
```

> **Nota di lettura**: la mappa mostra lo **stock** del ${anno}: quanto riceve ogni regione in valore assoluto. Se la classifica per importi è dominata dalle regioni più grandi, la concentrazione emerge anche a livello di singolo ente (sezione 3).

## 2. Dove va il 5x1000: le categorie

Le risorse si distribuiscono per tipo di beneficiario. Gli **enti del Terzo Settore** (ETS e ONLUS, compresi gli ETS con attività di ricerca) assorbono la quota largamente maggioritaria: intorno al **${pct(tsShare)}** del totale.

```js
display(plot.plot({
  title: `5x1000 per categoria — ${anno}`,
  width: 800, height: 380, marginLeft: 240,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: (d) => "€" + plot.formatNumber(d)},
  color: {scheme: "Set2"},
  marks: [
    plot.barX(per_categoria, {x: "importo_totale", y: "categoria", fill: "categoria", sort: {y: "-x"}, tip: true}),
    plot.text(per_categoria, {x: "importo_totale", y: "categoria", text: (c) => ` ${euroCompact(c.importo_totale)} — ${pct(qTotale(c.importo_totale, importoTot))}`, dx: 6, textAnchor: "start", fontSize: 10}),
    plot.ruleX([0])
  ]
}))
```

Il resto è polverizzato: ricerca scientifica e sanitaria, comuni, associazioni sportive dilettantistiche, beni culturali e aree protette si spartiscono la parte rimanente in tante piccole categorie.
## 3. La concentrazione tra gli enti

La top 10 degli enti beneficiari assorbe **${pct(quotaTop10)}** dell'intero fondo. In testa ci sono grandi fondazioni e istituti di ricerca di rilevanza nazionale.

```js
const topBar = top10.map((r, i) => ({ rango: i + 1, ente: r.denominazione, regione: r.regione, importo: r.importo_totale }));
```

```js
display(plot.plot({
  title: `Top 10 enti per importo erogabile — ${anno}`,
  width: 800, height: 340, marginLeft: 40,
  x: {grid: true, tickFormat: (d) => "€" + plot.formatNumber(d)},
  y: {label: null, tickSize: 0},
  marks: [
    plot.barX(topBar, {x: "importo", y: "ente", fill: "#d95f0e", sort: {y: "-x"}, tip: true}),
    plot.ruleX([0])
  ]
}))
```

Le prime ${num(top10.length)} fondazioni da sole valgono più dell'intero 5x1000 di molte regioni. È il segnale più chiaro di quanto il fondo sia, di fatto, un canale di finanziamento per un numero ristretto di soggetti nazionali.

---

## Dettaglio enti

<small>Cerca un ente per nome, oppure filtra per regione. Dati ${anno}.</small>

```js
const { header, format } = tableFormat({
  denominazione: { label: "Ente", fmt: "string" },
  regione: { label: "Regione", fmt: "string" },
  comune: { label: "Comune", fmt: "string" },
  numero_scelte: { label: "Scelte", fmt: "num" },
  importo_totale: { label: "Importo erogabile", fmt: "euroCompact" }
});
```

```js
const regList = ["Tutte", ...new Set(top_enti.map(d => d.regione).sort())];
const searchQuery = view(Inputs.search(top_enti, {placeholder: "digita il nome dell'ente…", label: "Cerca"}));
const regioneSel = view(Inputs.select(regList, {label: "Regione", value: "Tutte"}));
```

```js
const tableData = searchQuery.filter(d => regioneSel === "Tutte" || d.regione === regioneSel);
```

```js
Inputs.table(tableData, {
  columns: ["denominazione", "regione", "comune", "numero_scelte", "importo_totale"],
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

- **Copertura**: la pagina mostra i dati del solo ${anno}. Gli anni 2023 e 2025 non sono ancora presenti in questa pagina.
- **Dettaglio ente**: la denominazione può contenere refusi o caratteri anomali (es. "Bambin Ges?") ereditati dai CSV originali dell'Agenzia delle Entrate.
- **Categorie non esclusive**: un ente può avere più attributi (es. ETS che fa anche ricerca) ed è assegnato a una categoria prevalente; l'importo è quello *erogabile* calcolato dall'Agenzia, non necessariamente l'erogato.

## Risorse

- [Agenzia delle Entrate — 5x1000 (fonte originale)](https://www.agenziaentrate.gov.it/portale/area-tematica-5x1000)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/ade_cinque_per_mille/2024/ade_cinque_per_mille_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/ade-cinque-per-mille)
Nel ${anno} le entrate erogabili valgono **${euroCompact(importoTot)}** distribuite a **${num(numEnti)}** enti (in media **${euroCompact(importoMedio)}** a ente, ma la media nasconde una concentrazione estrema). La top 10 degli enti assorbe da sola **${pct(quotaTop10)}** del totale, e la regione in testa, **${topReg.regione.toLowerCase()}**, pesa da sola il **${pct(qTotale(topReg.importo_totale, importoTot))}**.

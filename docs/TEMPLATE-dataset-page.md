---
# Template pagina dataset — DataCivicLab Explorer
# Copia in src/dataset/{slug}.md e compila ogni sezione.
# I principi guida: docs/dataset-page-standard.md
# La procedura completa: CONTRIBUTING.md → "Aggiungere una pagina dataset"
#
# FRONTMATTER — tutto obbligatorio
title: Nome leggibile del dataset
description: Una frase che dice cosa contiene e perché è utile (max 150 caratteri)
source: Ente che pubblica il dato originale (es. "ISTAT", "MEF — Dipartimento delle Finanze")
source_url: URL della fonte originale
period: "YYYY–YYYY"  # intervallo di anni coperto dal dataset
last_modified: YYYY-MM-DD  # data dell'ultimo aggiornamento del parquet pulito
dataset_slug: slug_del_dataset_su_gcs  # slug DI (con underscore) per data loader
---

# Nome leggibile del dataset

**Una frase** che spiega cosa c'è dentro, a che livello di dettaglio e qual è il periodo coperto.

**Fonte**: [Nome ente](URL) · **Periodo**: {period}

<!--
  DATA LOADER
  Riferisci i JSON prodotti dal loader in src/data/
  Naming: {slug-url}.json per loader principale, {slug-url}-{vista}.json per loader specifici
-->
```js
const data = await FileAttachment("../data/{slug-url}.json").json();
```

<!--
  SE SERVE UN SECONDO LOADER (es. per regione/dettaglio)
-->
```js
// const secondData = await FileAttachment("../data/{slug-url}-second.json").json();
```

<!--
  MODULI CONDIVISI
  Usa geo-utils.js per mappe e lookup geografici,
  format-utils.js per formattazione numeri e tabelle.
  Vedi src/import/ per API completa.
-->
```js
import { normalizzaReg, loadItalianRegions, buildRegLookup } from "../import/geo-utils.js";
import { num, euro, pct, unit, tableFormat } from "../import/format-utils.js";
```

<!--
  MAPPA (solo se il dataset ha dimensione geografica)
  Carica regioni.topojson con FileAttachment (nella pagina, non nel modulo)
  e passa il dato a loadItalianRegions().
-->
```js
// const regTopo = await FileAttachment("../data/regioni.topojson").json();
// const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
```

```js
// Filtri standard
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(anni, {label: "Anno", value: anni[0]}));
```

```js
// Preparazione dati filtrati
const filtered = data.filter(d => d.anno === annoSel);
// + metriche riassuntive (usa d3.sum, d3.mean)
```

```js
// Crea lookup per mappa coropletica
// const lookup = buildRegLookup(filtered, "regione", "nome_metrica");
// Se il dataset ha P.A. Trentino da aggregare:
//   import { buildRegLookupWithTrentino } from "../import/geo-utils.js";
//   const lookup = buildRegLookupWithTrentino(filtered, "regione", aggFn);
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Metrica 1</h3>
    <span class="big">${num(valore)}</span>
  </div>
  <div class="card">
    <h3>Metrica 2</h3>
    <span class="big">${euro(valore)}</span>
  </div>
  <div class="card">
    <h3>Metrica 3</h3>
    <span class="big">{valore}</span>
  </div>
</div>

---

## Blocco principale — distribuzione base

<!--
  PRIMO BLOCCO: mostra il dataset nella sua forma più naturale.
  Deve rispondere alla domanda guida della pagina.
  Deve essere uno solo.
  Deve mostrare STOCK / DISTRIBUZIONE / COMPOSIZIONE base, non delta o trend.
-->

Breve nota di lettura (max 2 righe). Cosa mostra questo grafico? Come leggerlo?

```js
// Mappa coropletica:
// Plot.plot({
//   projection: {type: "mercator", domain: regioniGeo},
//   ...
//   marks: [
//     Plot.geo(regioniGeo, {
//       fill: d => lookup.get(normalizzaReg(d.properties.DEN_REG)),
//       ...
//     }),
//     Plot.geo(confiniReg, ...)
//   ]
// })

// Bar chart:
// Plot.plot({
//   marks: [
//     Plot.barX(filtered, { y: "categoria", x: "metrica", sort: {y: "-x"} })
//   ]
// })
```

> **Nota**: se serve, nota breve su perimetro o metrica.

---

## Blocco secondario — confronto o dettaglio

<!--
  SECONDO BLOCCO: confronto, delta, trend, o vista alternativa.
  Deve essere diverso dal primo, non una ripetizione.
-->

Breve nota su cosa mostra questo secondo blocco.

```js
// secondo grafico o tabella
```

---

## Dettaglio

<!--
  TABELLA FINALE: vista completa, ricercabile e scaricabile.
  Default consigliato per v0. Usa tableFormat() per header/format standardizzati.
-->

```js
const { header, format } = tableFormat({
  col1: { label: "Nome leggibile", fmt: "num" },
  col2: { label: "Nome leggibile", fmt: "euro" },
  col3: { label: "Nome leggibile", fmt: "pct" },
});
```

```js
Inputs.table(filtered, {
  columns: ["col1", "col2", "col3"],
  header,
  format,
  rows: 20,
  width: "100%"
})
```

---

## Limiti

<!--
  SEZIONE OBBLIGATORIA. Elenca cosa il dataset NON permette di dire.
  Tre punti massimi, linguaggio pubblico.
-->
- **Copertura**: il dataset copre {periodo}, non sono disponibili dati precedenti
- **Granularità**: i dati sono aggregati per {livello}, non è possibile scendere a dettaglio {X}
- **Nota metodologica**: {eventuale caveat sul significato delle metriche, doppi conteggi, cambi di classificazione}
- **Aggiornamento**: l'ultimo aggiornamento risale al {data}, i dati potrebbero non riflettere l'anno in corso

---

## Risorse

- [Fonte originale]({source_url})
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/{slug_gcs}/{anno}/{slug_gcs}_{anno}_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/{slug_candidate})
- [Analisi collegate](/analisi/{slug-analisi}) <!-- se esistono -->

<!--
  CHECKLIST PRE-PUBBLICAZIONE
  [ ] Slug DE e slug DI coincidono (vedi URL_SLUG_OVERRIDES in catalog.json.py)
  [ ] Clean parquet pubblico esiste su GCS
  [ ] Data loader funziona (npm run dev)
  [ ] Frontmatter completo (title, description, source, source_url, period, last_modified, dataset_slug)
  [ ] Primo blocco mostra stock/distribuzione base, non delta o trend
  [ ] Usa moduli condivisi da src/import/ (geo-utils.js, format-utils.js)
  [ ] Sezione Limiti compilata
  [ ] Link a fonte originale e parquet funzionanti
  [ ] Pagina leggibile da un utente non tecnico
-->

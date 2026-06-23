---
title: Test — Parquet nativo in Observable
description: Caricamento diretto parquet via DuckDB WASM — data loader binario 5 righe
---

# Test: Parquet nativo via DuckDB WASM

Data loader: [`strutture_asl.parquet.py`](../data/strutture_asl.parquet.py) — **5 righe** (copiare parquet da GCS).
Niente aggregazioni SQL a build-time — tutto nel browser.

```js
// Carica il parquet via DuckDB WASM (dati già parsati come array)
const data = await FileAttachment("../data/strutture_asl.parquet").parquet();
```

```js
display(`Record: ${data.length} — Colonne: ${Object.keys(data[0]).length}`);
display(Object.keys(data[0]).join(", "));
```

## Query SQL live nel browser

```js
const db = await DuckDBClient.of({
  strutture: FileAttachment("../data/strutture_asl.parquet")
});
```

```js
const perRegione = await db.query(`
  SELECT regione,
         COUNT(*) AS n_asl,
         SUM(totale_medici) AS medici,
         SUM(totale_scelte) AS scelte,
         ROUND(AVG(totale_residenti)) AS avg_residenti
  FROM strutture
  GROUP BY regione
  ORDER BY medici DESC
`);
```

```js
Plot.plot({
  title: "Medici ASL per regione",
  width: 800, height: 400, marginLeft: 160,
  y: {label: null, tickSize: 0},
  x: {grid: true, tickFormat: "~s"},
  marks: [
    Plot.barX(perRegione, {
      y: "regione", x: "medici", fill: "steelblue",
      sort: {y: "-x"},
      tip: {format: {x: d => d.toLocaleString()}}
    }),
    Plot.ruleX([0])
  ]
})
```

```js
Inputs.table(perRegione, {rows: 10, width: "100%"})
```

## Filtro interattivo con query SQL

```js
const regione = view(Inputs.select(perRegione.map(d => d.regione), {label: "Regione", value: "LOMBARDIA"}));
```

```js
const dettaglio = await db.query(`
  SELECT denominazione_asl, totale_medici, totale_scelte, totale_residenti
  FROM strutture
  WHERE regione = '${regione}'
  ORDER BY totale_medici DESC
`);
```

```js
display(Inputs.table(dettaglio, {rows: 10, width: "100%"}));
```

---

## Confronto con data loader classico

| Aspetto | Data loader JSON (oggi) | Data loader Parquet (nuovo) |
|---|---|---|
| **Righe codice** | ~30 (query + GROUP BY) | **5** (solo copia) |
| **Build time** | ~3 sec | **~0.2 sec** |
| **Dati** | Pre-aggregati | **Intero dataset** |
| **Query browser** | ❌ | **✅ SQL arbitrario** |
| **Dipendenze Python** | DuckDB, lab-connectors | **urllib (built-in)** |

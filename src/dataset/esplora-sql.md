---
title: Esplora dati con SQL
description: Query SQL live sui dataset puliti del Lab — tutto nel browser
---

# Esplora dati con SQL

Seleziona un dataset, scrivi una query SQL e vedi i risultati live.
Tutto gira nel tuo browser via DuckDB WASM — **zero carico server**.

```js
import { num } from "../import/format-utils.js";
```

```js
const catalog = await FileAttachment("../data/catalog.json").json();
const datasets = catalog.datasets.filter(d => d.location?.type === "gcs");
```

```js
const scelta = view(Inputs.select(
  datasets.map(d => ({label: `${d.name}  (${d.period})`, value: d.slug})),
  {label: "Dataset", value: "strutture_asl"}
));
```

```js
const ds = datasets.find(d => d.slug === scelta);
const parquetUrl = ds
  ? ds.location.path.replace("gs://", "https://storage.googleapis.com/")
  : null;
```

```js
// Card informativa — gestisce ds null
display(html`<div class="card">
  ${ds
    ? html`<h4>${ds.name}</h4>
           <p>${ds.description}</p>
           <p><strong>${ds.columns.length} colonne</strong> · Periodo: ${ds.period} ·
           <a href="${parquetUrl}" target="_blank" rel="noopener">📥 Scarica parquet</a></p>`
    : html`<p>Seleziona un dataset dal menu sopra.</p>`}
</div>`);
```

```js
// Connessione DuckDB — una sola volta per dataset
const db = (typeof window !== "undefined" && parquetUrl)
  ? await DuckDBClient.of({data: parquetUrl})
  : null;
```

## Schema

```js
if (db) {
  const schema = await db.query(`
    SELECT column_name, column_type
    FROM information_schema.columns
    WHERE table_name = 'data'
    ORDER BY ordinal_position
  `);
  display(Inputs.table(schema, {rows: 30, width: "100%"}));
}
```

## Query

```js
const sql = view(Inputs.textarea({
  label: "SQL query",
  value: "SELECT * FROM data LIMIT 20",
  rows: 4, width: "100%",
  placeholder: "Scrivi una query SQL… usa 'data' come nome tabella"
}));
```

```js
if (db && sql) {
  try {
    const start = performance.now();
    const results = await db.query(sql);
    const elapsed = (performance.now() - start).toFixed(0);
    display(html`<small>Query in ${elapsed}ms · ${results.length} righe</small>`);
    display(Inputs.table(results, {rows: 25, width: "100%", maxHeight: "500px"}));
  } catch (e) {
    display(html`<p style="color:var(--theme-red, #d32f2f)">❌ ${e.message}</p>`);
  }
}
```

## Esempi

```js
display(html`<details>
  <summary>Query di esempio</summary>
  <ul>
    <li><code>SELECT * FROM data LIMIT 10</code></li>
    <li><code>SELECT COUNT(*) AS totale FROM data</code></li>
    <li><code>SELECT column_name, column_type FROM information_schema.columns WHERE table_name = 'data'</code></li>
    <li><code>SELECT regione, COUNT(*) AS n FROM data GROUP BY regione ORDER BY n DESC</code></li>
  </ul>
</details>`);
```

---

> ⚠️ DuckDB WASM viene caricato la prima volta (~5 MB). Le query successive sono veloci.

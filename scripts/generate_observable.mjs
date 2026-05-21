#!/usr/bin/env node
/**
 * Genera pagine Observable Framework per tutti i dataset del catalogo.
 * Crea src/data/{slug}.json.py (data loader) e src/dataset/{slug}.md (pagina).
 *
 * I path GCS seguono il path contract canonico:
 *   lab-connectors/lab_connectors/gcs/paths.py  (paths.json)
 * Pattern clean_parquet: {bucket}/{slug}/{year}/{slug}_{year}_clean.parquet
 */
import fs from "fs";
import path from "path";
import { loaderTemplate, pageTemplate } from "./generate-templates.mjs";

const PATHS_CONTRACT_URL =
  "https://raw.githubusercontent.com/dataciviclab/lab-connectors/main/lab_connectors/gcs/paths.json";

const CATALOG_URL =
  "https://raw.githubusercontent.com/dataciviclab/dataset-incubator/main/registry/clean_catalog.json";

const GCS_CLEAN_BUCKET =
  (await fetch(PATHS_CONTRACT_URL).then(r => r.json())).buckets.clean;

const DATA_DIR = "src/data";
const PAGES_DIR = "src/dataset";

fs.mkdirSync(DATA_DIR, { recursive: true });
fs.mkdirSync(PAGES_DIR, { recursive: true });

const resp = await fetch(CATALOG_URL);
const catalog = await resp.json();
const datasets = catalog.datasets;

// ── Genera ──────────────────────────────────────────────────────────────────
let generated = 0, skipped = 0;

for (const ds of datasets) {
  const slug = ds.slug;
  const name = ds.name || slug;
  const description = ds.description || "";
  const source = ds.source || "";
  const period = ds.period || {};
  const columns = ds.columns || [];
  const stage = ds.stage || "?";
  const yearRange = period.start && period.end
    ? "list(range(" + period.start + ", " + period.end + " + 1))"
    : "list(range(2019, 2026))";

  const dims = columns.filter(c => c.role === "dimension");
  const metrics = columns.filter(c => c.role === "metric")
    .filter(c => !/\d{4}/.test(c.name)); // esclude colonne con anno (es. incremento_2020_2021)

  if (metrics.length === 0) { skipped++; continue; }

  const yearCol = dims.find(d => d.name.toLowerCase().includes("anno"));
  const groupDim = dims.find(d => !d.name.toLowerCase().includes("anno"))
    || dims[0] || { name: columns[0]?.name || "id" };
  const groupCol = groupDim.name;
  const metricNames = metrics.map(m => m.name);

  // Determina le colonne di raggruppamento
  const groupCols = [groupCol];
  if (yearCol) groupCols.unshift(yearCol.name);

  // Data loader
  const loader = loaderTemplate(slug, name, groupCols, metricNames, yearRange);
  fs.writeFileSync(path.join(DATA_DIR, slug + ".json.py"), loader);
  fs.chmodSync(path.join(DATA_DIR, slug + ".json.py"), 0o755);

  // Pagina
  const page = pageTemplate(
    slug, name, description, source, stage,
    dims, metrics,
    !!yearCol, yearCol?.name,
    GCS_CLEAN_BUCKET
  );
  fs.writeFileSync(path.join(PAGES_DIR, slug + ".md"), page);

  generated++;
}

console.log(JSON.stringify({ generated, skipped, total: datasets.length }));

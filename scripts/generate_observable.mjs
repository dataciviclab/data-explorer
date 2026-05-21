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
import process from "node:process";
import { fileURLToPath } from "node:url";
import { loaderTemplate, pageTemplate } from "./generate-templates.mjs";

const PATHS_CONTRACT_URL =
  "https://raw.githubusercontent.com/dataciviclab/lab-connectors/main/lab_connectors/gcs/paths.json";

const CATALOG_URL =
  "https://raw.githubusercontent.com/dataciviclab/dataset-incubator/main/registry/clean_catalog.json";

const DATA_DIR = "src/data";
const PAGES_DIR = "src/dataset";

/**
 * Processa un singolo dataset dal catalogo: calcola loader e pagina.
 *
 * Funzione pura (nessun I/O) — restituisce { slug, name, loader, page, skipped }
 * dove loader e page sono stringhe di contenuto da scrivere su file.
 * Se metrics.length === 0, restituisce { skipped: true }.
 */
export function processDataset(ds, gcsBucket) {
  const slug = ds.slug;
  const name = ds.name || slug;
  const description = ds.description || "";
  const source = ds.source || "";
  const period = ds.period || {};
  const columns = ds.columns || [];
  const stage = ds.stage || "?";
  const yearRange = period.start && period.end
    ? `list(range(${  period.start  }, ${  period.end  } + 1))`
    : "list(range(2019, 2026))";

  const dims = columns.filter(c => c.role === "dimension");
  const metrics = columns.filter(c => c.role === "metric")
    .filter(c => !/\d{4}/.test(c.name));

  if (metrics.length === 0) return { slug, skipped: true };

  const yearCol = dims.find(d => d.name.toLowerCase().includes("anno"));
  const groupDim = dims.find(d => !d.name.toLowerCase().includes("anno"))
    || dims[0] || { name: columns[0]?.name || "id" };
  const groupCol = groupDim.name;
  const metricNames = metrics.map(m => m.name);

  const groupCols = [groupCol];
  if (yearCol) groupCols.unshift(yearCol.name);

  const loader = loaderTemplate(slug, name, groupCols, metricNames, yearRange);
  const page = pageTemplate(
    slug, name, description, source, stage,
    dims, metrics,
    !!yearCol, yearCol?.name,
    gcsBucket
  );

  return { slug, name, loader, page, skipped: false };
}

// ── Esecuzione diretta ──────────────────────────────────────────────────────

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const GCS_CLEAN_BUCKET =
    (await fetch(PATHS_CONTRACT_URL).then(r => r.json())).buckets.clean;

  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.mkdirSync(PAGES_DIR, { recursive: true });

  const resp = await fetch(CATALOG_URL);
  const catalog = await resp.json();
  const datasets = catalog.datasets;

  let generated = 0, skipped = 0;

  for (const ds of datasets) {
    const result = processDataset(ds, GCS_CLEAN_BUCKET);
    if (result.skipped) { skipped++; continue; }

    // Data loader
    fs.writeFileSync(path.join(DATA_DIR, `${result.slug  }.json.py`), result.loader);
    fs.chmodSync(path.join(DATA_DIR, `${result.slug  }.json.py`), 0o755);

    // Pagina
    fs.writeFileSync(path.join(PAGES_DIR, `${result.slug  }.md`), result.page);

    generated++;
  }

  console.log(JSON.stringify({ generated, skipped, total: datasets.length }));
}

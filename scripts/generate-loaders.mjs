#!/usr/bin/env node
/**
 * Genera data loader Python per ogni dataset del catalogo.
 * Crea src/data/{slug}.json.py — roba meccanica, nessuna pagina.
 *
 * Le pagine (src/dataset/*.md) si creano a mano: servono cura editoriale.
 * Usa pageTemplate() da generate-templates.mjs come punto di partenza.
 */
import fs from "fs";
import path from "path";
import { loaderTemplate } from "./generate-templates.mjs";

const CATALOG_URL =
  "https://raw.githubusercontent.com/dataciviclab/dataset-incubator/main/registry/clean_catalog.json";

const DATA_DIR = "src/data";

function metricNames(columns) {
  return columns
    .filter(c => c.role === "metric")
    .filter(c => !/\d{4}/.test(c.name))
    .map(m => m.name);
}

function yearRange(period) {
  return period?.start && period?.end
    ? `list(range(${  period.start  }, ${  period.end  } + 1))`
    : "list(range(2019, 2026))";
}

function groupCols(columns) {
  const dims = columns.filter(c => c.role === "dimension");
  const yearCol = dims.find(d => d.name.toLowerCase().includes("anno"));
  const groupDim = dims.find(d => !d.name.toLowerCase().includes("anno"))
    || dims[0] || { name: columns[0]?.name || "id" };
  const cols = [groupDim.name];
  if (yearCol) cols.unshift(yearCol.name);
  return cols;
}

const resp = await fetch(CATALOG_URL);
const catalog = await resp.json();

fs.mkdirSync(DATA_DIR, { recursive: true });

let generated = 0, skipped = 0;

for (const ds of catalog.datasets) {
  const metrics = metricNames(ds.columns || []);
  if (metrics.length === 0) { skipped++; continue; }

  const loader = loaderTemplate(
    ds.slug, ds.name || ds.slug,
    groupCols(ds.columns || []),
    metrics,
    yearRange(ds.period)
  );

  const outPath = path.join(DATA_DIR, `${ds.slug  }.json.py`);
  fs.writeFileSync(outPath, loader);
  fs.chmodSync(outPath, 0o755);
  generated++;
}

console.log(JSON.stringify({ generated, skipped, total: catalog.datasets.length }));

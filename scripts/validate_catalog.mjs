#!/usr/bin/env node
/**
 * Valida che tutti i dataset pubblicati in clean_catalog.json abbiano
 * pagina (src/dataset/{slug}.md) e data loader (src/data/{slug}.json.py).
 *
 * Questo protegge il contratto pubblico: ogni dataset published nel catalogo
 * remoto deve essere accessibile nell'Explorer.
 *
 * Dataset puramente enumerativi (senza metriche numeriche) generano solo
 * warning, non errori — non sono auto-generabili da generate_observable.mjs.
 *
 * Uso: node scripts/validate_catalog.mjs
 */
import { access } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const CATALOG_URL =
  "https://raw.githubusercontent.com/dataciviclab/dataset-incubator/main/registry/clean_catalog.json";

async function fileExists(relativePath) {
  try {
    await access(path.resolve(process.cwd(), relativePath));
    return true;
  } catch {
    return false;
  }
}

/**
 * Un dataset ha metriche se almeno una colonna ha role="metric".
 */
function hasMetrics(columns) {
  return (columns || []).some((c) => c.role === "metric");
}

async function main() {
  const resp = await fetch(CATALOG_URL);
  if (!resp.ok) {
    throw new Error(
      "Failed to fetch clean_catalog.json: HTTP " + resp.status
    );
  }
  const catalog = await resp.json();
  const datasets = catalog.datasets || [];

  const errors = [];
  const warnings = [];
  let published = 0;
  let enumerative = 0;

  for (const ds of datasets) {
    if (ds.stage !== "published") continue;
    published++;

    const slug = ds.slug;
    const columns = ds.columns || [];
    const isEnumerative = !hasMetrics(columns);

    if (isEnumerative) {
      enumerative++;
    }

    const pagePath = "src/dataset/" + slug + ".md";
    const loaderPath = "src/data/" + slug + ".json.py";
    const pageExists = await fileExists(pagePath);
    const loaderExists = await fileExists(loaderPath);

    if (!pageExists || !loaderExists) {
      const msg =
        'Published dataset "' + slug + '" (' + ds.name + ")" +
        (!pageExists ? " — missing page: " + pagePath : "") +
        (!loaderExists ? " — missing loader: " + loaderPath : "");

      if (isEnumerative) {
        warnings.push(
          msg + " [enumerative dataset, no auto-generator]"
        );
      } else {
        errors.push(msg);
      }
    }
  }

  if (warnings.length > 0) {
    console.warn("\nWarnings (" + warnings.length + "):\n");
    for (const w of warnings) console.warn("  - " + w);
  }

  if (errors.length > 0) {
    console.error("\nCatalog validation failed:\n");
    for (const err of errors) console.error("  - " + err);
    console.error(
      "\n" + errors.length + " error(s), " +
      warnings.length + " warning(s) — " +
      published + " published (" + enumerative + " enumerative)."
    );
    process.exit(1);
  }

  console.log(
    "Catalog validation passed: " + published +
    " published (" + enumerative + " enumerative), " +
    warnings.length + " warnings."
  );
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : String(err));
  process.exit(1);
});

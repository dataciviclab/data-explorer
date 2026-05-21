/**
 * Test: catalogo remoto → pagine presenti.
 *
 * Verifica che ogni dataset con stage "published" nel catalogo remoto
 * abbia pagina (src/dataset/{slug}.md) e data loader (src/data/{slug}.json.py).
 *
 * Dataset puramente enumerativi (senza metriche) generano solo warning,
 * non errore — non sono auto-generabili.
 */
import assert from "node:assert/strict";
import { before, describe, it } from "node:test";
import { access } from "node:fs/promises";
import path from "node:path";

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

function hasMetrics(columns) {
  return (columns || []).some((c) => c.role === "metric");
}

describe("published datasets have corresponding pages", () => {
  let errors = [];
  let warnings = [];

  before(async () => {
    const resp = await fetch(CATALOG_URL);
    assert.ok(resp.ok, "clean_catalog.json fetch failed: HTTP " + resp.status);
    const catalog = await resp.json();
    const datasets = catalog.datasets || [];

    for (const ds of datasets) {
      if (ds.stage !== "published") continue;
      const slug = ds.slug;
      const columns = ds.columns || [];
      const isEnumerative = !hasMetrics(columns);
      const pagePath = "src/dataset/" + slug + ".md";
      const loaderPath = "src/data/" + slug + ".json.py";
      const pageExists = await fileExists(pagePath);
      const loaderExists = await fileExists(loaderPath);

      if (!pageExists || !loaderExists) {
        const msg =
          `Published dataset "${slug}" (${ds.name})` +
          (!pageExists ? ` — missing page: ${pagePath}` : "") +
          (!loaderExists ? ` — missing loader: ${loaderPath}` : "");

        if (isEnumerative) {
          warnings.push(msg + " [enumerative dataset, no auto-generator]");
        } else {
          errors.push(msg);
        }
      }
    }
  });

  it("all non-enumerative published datasets have page + loader", () => {
    if (errors.length > 0) {
      assert.fail(
        errors.length + " published dataset(s) without page/loader:\n" +
        errors.map((e) => "  - " + e).join("\n")
      );
    }
  });

  it("enumerative datasets are tracked as warnings", () => {
    if (warnings.length > 0) {
      console.warn(
        "\n" + warnings.length + " enumerative dataset(s) without auto-generator:\n" +
        warnings.map((w) => "  - " + w).join("\n")
      );
    }
  });
});

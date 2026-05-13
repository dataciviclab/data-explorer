import { readFile, access } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const VALID_STATUSES = new Set(["incubating", "published", "deprecated"]);

async function fileExists(relativePath) {
  try {
    await access(path.resolve(process.cwd(), relativePath));
    return true;
  } catch {
    return false;
  }
}

async function readJson(relativePath) {
  const absolutePath = path.resolve(process.cwd(), relativePath);
  const raw = await readFile(absolutePath, "utf8");
  return JSON.parse(raw);
}

function assert(condition, message, errors) {
  if (!condition) errors.push(message);
}

function isNonEmptyString(value) {
  return typeof value === "string" && value.trim().length > 0;
}

async function main() {
  const catalog = await readJson("catalog/datasets.json");
  const themes = await readJson("catalog/themes.json");
  const errors = [];

  assert(catalog && typeof catalog === "object", "catalog/datasets.json must be an object with datasets[]", errors);
  assert(Array.isArray(catalog.datasets), "catalog/datasets.json datasets must be an array", errors);
  assert(Array.isArray(themes), "catalog/themes.json must be an array", errors);

  if (errors.length > 0) {
    throw new Error(errors.join("\n"));
  }

  const datasets = catalog.datasets;
  const datasetSlugs = new Set();
  const datasetBySlug = new Map();
  const themeSlugs = new Set();
  const themeBySlug = new Map();

  for (const [index, theme] of themes.entries()) {
    const prefix = "themes[" + index + "]";
    assert(isNonEmptyString(theme.slug), prefix + ".slug must be a non-empty string", errors);
    assert(isNonEmptyString(theme.name), prefix + ".name must be a non-empty string", errors);
    assert(Array.isArray(theme.datasets), prefix + ".datasets must be an array", errors);
    if (!isNonEmptyString(theme.slug)) continue;
    assert(!themeSlugs.has(theme.slug), "duplicate theme slug: " + theme.slug, errors);
    themeSlugs.add(theme.slug);
    themeBySlug.set(theme.slug, theme);
  }

  for (const [index, ds] of datasets.entries()) {
    const prefix = "datasets[" + index + "]";
    assert(isNonEmptyString(ds.slug), prefix + ".slug must be a non-empty string", errors);
    assert(isNonEmptyString(ds.name), prefix + ".name must be a non-empty string", errors);
    assert(isNonEmptyString(ds.source), prefix + ".source must be a non-empty string", errors);
    if (!isNonEmptyString(ds.slug)) continue;
    assert(!datasetSlugs.has(ds.slug), "duplicate dataset slug: " + ds.slug, errors);
    datasetSlugs.add(ds.slug);
    datasetBySlug.set(ds.slug, ds);

    if (ds.stage && !VALID_STATUSES.has(ds.stage)) {
      errors.push(prefix + ".stage must be one of [" + Array.from(VALID_STATUSES).join(", ") + "] - got: " + ds.stage);
    }

    if (Array.isArray(ds.years)) {
      assert(ds.years.length > 0, prefix + ".years must not be empty", errors);
      for (const year of ds.years) {
        assert(Number.isInteger(year), prefix + ".years must contain integers only", errors);
      }
    }

    if (ds.theme && isNonEmptyString(ds.theme)) {
      assert(themeSlugs.has(ds.theme), "dataset " + ds.slug + " references unknown theme: " + ds.theme, errors);
    }
  }

  for (const [themeSlug, theme] of themeBySlug.entries()) {
    const listedDatasets = Array.isArray(theme.datasets) ? theme.datasets : [];
    const seen = new Set();
    for (const dsSlug of listedDatasets) {
      if (!isNonEmptyString(dsSlug)) continue;
      assert(!seen.has(dsSlug), "theme " + themeSlug + " lists dataset " + dsSlug + " more than once", errors);
      seen.add(dsSlug);
      assert(datasetBySlug.has(dsSlug), "theme " + themeSlug + " references unknown dataset: " + dsSlug, errors);
    }
  }

  for (const ds of datasetBySlug.values()) {
    if (ds.stage === "published") {
      const pagePath = "pages/dataset/" + ds.slug + ".md";
      if (!(await fileExists(pagePath))) {
        errors.push("dataset " + ds.slug + " has stage " + ds.stage + " but page " + pagePath + " does not exist");
      }
    }
  }

  for (const theme of themeBySlug.values()) {
    if (Array.isArray(theme.datasets) && theme.datasets.length > 0) {
      const themePage = "pages/temi/" + theme.slug + ".md";
      if (!(await fileExists(themePage))) {
        errors.push("theme " + theme.slug + " has datasets but page " + themePage + " does not exist");
      }
    }
  }

  if (errors.length > 0) {
    console.error("Catalog validation failed:\n");
    for (const error of errors) {
      console.error("- " + error);
    }
    process.exit(1);
  }

  console.log("Catalog validation passed: " + datasets.length + " datasets, " + themes.length + " themes.");
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});

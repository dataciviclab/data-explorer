import { readFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

async function readJson(relativePath) {
  const absolutePath = path.resolve(process.cwd(), relativePath);
  const raw = await readFile(absolutePath, "utf8");
  return JSON.parse(raw);
}

function assert(condition, message, errors) {
  if (!condition) {
    errors.push(message);
  }
}

function isNonEmptyString(value) {
  return typeof value === "string" && value.trim().length > 0;
}

async function main() {
  const datasets = await readJson("catalog/datasets.json");
  const themes = await readJson("catalog/themes.json");
  const errors = [];

  assert(Array.isArray(datasets), "`catalog/datasets.json` must be an array", errors);
  assert(Array.isArray(themes), "`catalog/themes.json` must be an array", errors);

  if (errors.length > 0) {
    throw new Error(errors.join("\n"));
  }

  const datasetSlugs = new Set();
  const themeSlugs = new Set();
  const datasetBySlug = new Map();
  const themeBySlug = new Map();

  for (const [index, theme] of themes.entries()) {
    const prefix = `themes[${index}]`;
    assert(isNonEmptyString(theme.slug), `${prefix}.slug must be a non-empty string`, errors);
    assert(isNonEmptyString(theme.name), `${prefix}.name must be a non-empty string`, errors);
    assert(Array.isArray(theme.datasets), `${prefix}.datasets must be an array`, errors);

    if (!isNonEmptyString(theme.slug)) {
      continue;
    }

    assert(!themeSlugs.has(theme.slug), `duplicate theme slug: ${theme.slug}`, errors);
    themeSlugs.add(theme.slug);
    themeBySlug.set(theme.slug, theme);
  }

  for (const [index, dataset] of datasets.entries()) {
    const prefix = `datasets[${index}]`;
    assert(isNonEmptyString(dataset.slug), `${prefix}.slug must be a non-empty string`, errors);
    assert(
      isNonEmptyString(dataset.technical_slug),
      `${prefix}.technical_slug must be a non-empty string`,
      errors,
    );
    assert(isNonEmptyString(dataset.name), `${prefix}.name must be a non-empty string`, errors);
    assert(isNonEmptyString(dataset.theme), `${prefix}.theme must be a non-empty string`, errors);
    assert(isNonEmptyString(dataset.status), `${prefix}.status must be a non-empty string`, errors);
    assert(Array.isArray(dataset.years), `${prefix}.years must be an array`, errors);
    assert(isNonEmptyString(dataset.source), `${prefix}.source must be a non-empty string`, errors);

    if (!isNonEmptyString(dataset.slug)) {
      continue;
    }

    assert(!datasetSlugs.has(dataset.slug), `duplicate dataset slug: ${dataset.slug}`, errors);
    datasetSlugs.add(dataset.slug);
    datasetBySlug.set(dataset.slug, dataset);

    if (Array.isArray(dataset.years)) {
      assert(dataset.years.length > 0, `${prefix}.years must not be empty`, errors);
      for (const year of dataset.years) {
        assert(Number.isInteger(year), `${prefix}.years must contain integers only`, errors);
      }
    }

    if (isNonEmptyString(dataset.theme)) {
      assert(themeSlugs.has(dataset.theme), `dataset ${dataset.slug} references unknown theme: ${dataset.theme}`, errors);
    }
  }

  for (const [themeSlug, theme] of themeBySlug.entries()) {
    const listedDatasets = Array.isArray(theme.datasets) ? theme.datasets : [];
    const seen = new Set();

    for (const datasetSlug of listedDatasets) {
      assert(isNonEmptyString(datasetSlug), `theme ${themeSlug} contains an invalid dataset slug entry`, errors);
      if (!isNonEmptyString(datasetSlug)) {
        continue;
      }
      assert(!seen.has(datasetSlug), `theme ${themeSlug} lists dataset ${datasetSlug} more than once`, errors);
      seen.add(datasetSlug);
      assert(datasetBySlug.has(datasetSlug), `theme ${themeSlug} references unknown dataset: ${datasetSlug}`, errors);
      if (datasetBySlug.has(datasetSlug)) {
        assert(
          datasetBySlug.get(datasetSlug).theme === themeSlug,
          `theme ${themeSlug} includes dataset ${datasetSlug}, but dataset points to theme ${datasetBySlug.get(datasetSlug).theme}`,
          errors,
        );
      }
    }
  }

  for (const [datasetSlug, dataset] of datasetBySlug.entries()) {
    const theme = themeBySlug.get(dataset.theme);
    if (!theme || !Array.isArray(theme.datasets)) {
      continue;
    }

    assert(
      theme.datasets.includes(datasetSlug),
      `dataset ${datasetSlug} points to theme ${dataset.theme}, but is missing from that theme's dataset list`,
      errors,
    );
  }

  if (errors.length > 0) {
    console.error("Catalog validation failed:\n");
    for (const error of errors) {
      console.error(`- ${error}`);
    }
    process.exit(1);
  }

  console.log(`Catalog validation passed: ${datasets.length} datasets, ${themes.length} themes.`);
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});

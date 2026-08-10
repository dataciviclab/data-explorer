import { writeFile, readFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const DI_REGISTRY_URL =
  'https://raw.githubusercontent.com/dataciviclab/dataset-incubator/main/registry/registry.json';
const ROOT = process.cwd();

export async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Fetch failed for ${url}: HTTP ${res.status}`);
  return res.json();
}

export function isNonEmptyString(v) {
  return typeof v === 'string' && v.trim().length > 0;
}

/**
 * Carica la config editoriale dei temi (catalog/themes.json) e restituisce
 * una mappa category → tema. Single source condivisa con i data loader.
 */
export async function loadThemeCategories() {
  const themesPath = path.join(ROOT, 'catalog/themes.json');
  const raw = JSON.parse(await readFile(themesPath, 'utf8'));
  const temi = Array.isArray(raw) ? raw : raw.temi || [];
  const map = new Map();
  for (const t of temi) {
    for (const c of t.categories || []) {
      map.set(c, t.slug);
    }
  }
  return map;
}

export function generateCatalogEntry(diEntry, themeSlug) {
  const years = diEntry.period
    ? Array.from({ length: diEntry.period.end - diEntry.period.start + 1 }, (_, i) => diEntry.period.start + i)
    : [];
  const columns = (diEntry.columns || []).map(c => ({
    name: c.name,
    type: c.type,
    role: c.role,
    description: c.description || '',
  }));
  return {
    slug: diEntry.slug,
    name: diEntry.name,
    description: diEntry.description || '',
    theme: themeSlug || null,
    stage: diEntry.stage || 'incubating',
    years: years,
    category: diEntry.category || null,
    source: diEntry.source || '',
    source_id: diEntry.source_id || null,
    di_slug: diEntry.slug,
    columns: columns,
  };
}

async function main() {
  console.log('Fetching DI registry...');
  const registry = await fetchJson(DI_REGISTRY_URL);
  const diDatasets = new Map(registry.datasets.map(d => [d.slug, d]));
  console.log(`DI registry: ${diDatasets.size} datasets`);

  // Mappa category → tema dalla config editoriale (dinamico)
  const themeByCategory = await loadThemeCategories();
  console.log(`Themes config: ${themeByCategory.size} category mappate`);

  const generated = [];
  for (const diEntry of diDatasets.values()) {
    const themeSlug = diEntry.category ? themeByCategory.get(diEntry.category) || null : null;
    generated.push(generateCatalogEntry(diEntry, themeSlug));
  }

  // Scrivi datasets.json generato
  const output = {
    schema_version: 1,
    source: DI_REGISTRY_URL,
    generated_at: new Date().toISOString().split('T')[0],
    datasets: generated,
  };

  const outputPath = path.join(ROOT, 'catalog/datasets.json');
  await writeFile(outputPath, JSON.stringify(output, null, 2), 'utf8');
  console.log(`Generated catalog: ${generated.length} datasets`);
}

// Esegue main solo quando chiamato direttamente (non via import nei test)
const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  main().catch(err => {
    console.error(err instanceof Error ? err.message : String(err));
    process.exit(1);
  });
}

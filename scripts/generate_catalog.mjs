import { writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const DI_CATALOG_URL =
  'https://raw.githubusercontent.com/dataciviclab/dataset-incubator/main/registry/clean_catalog.json';
const ROOT = process.cwd();

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error('Fetch failed for ' + url + ': HTTP ' + res.status);
  return res.json();
}

function isNonEmptyString(v) {
  return typeof v === 'string' && v.trim().length > 0;
}

function generateCatalogEntry(diEntry, themeSlug) {
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
    source: diEntry.source || '',
    source_id: diEntry.source_id || null,
    di_slug: diEntry.slug,
    columns: columns,
  };
}

async function main() {
  console.log('Fetching DI catalog...');
  const diCatalog = await fetchJson(DI_CATALOG_URL);
  const diDatasets = new Map(diCatalog.datasets.map(d => [d.slug, d]));
  console.log('DI catalog: ' + diDatasets.size + ' datasets');

  // Carica themes.json (editoriale)
  const themesPath = path.join(ROOT, 'catalog/themes.json');
  const themesRaw = JSON.parse(await import('node:fs').then(fs => fs.readFileSync(themesPath, 'utf8')));
  const themes = Array.isArray(themesRaw) ? themesRaw : [];
  console.log('Themes: ' + themes.length + ' themes');

  // Costruisci set di dataset featured + mappa tema per slug
  const featuredSlugs = new Set();
  const themeForSlug = new Map();

  for (const theme of themes) {
    if (Array.isArray(theme.datasets)) {
      for (const ds of theme.datasets) {
        featuredSlugs.add(ds);
        themeForSlug.set(ds, theme.slug);
      }
    }
  }

  // Genera catalogo
  const generated = [];
  const seen = new Set();

  // Prima i dataset featured
  for (const slug of featuredSlugs) {
    const diEntry = diDatasets.get(slug);
    if (diEntry) {
      generated.push(generateCatalogEntry(diEntry, themeForSlug.get(slug)));
      seen.add(slug);
    } else {
      console.warn('WARN: theme references unknown DI slug: ' + slug);
    }
  }

  // Poi tutti gli altri dataset DI (non featured)
  for (const [slug, diEntry] of diDatasets) {
    if (!seen.has(slug)) {
      generated.push(generateCatalogEntry(diEntry, null));
    }
  }

  // Scrivi datasets.json generato
  const output = {
    schema_version: 1,
    source: DI_CATALOG_URL,
    generated_at: new Date().toISOString().split('T')[0],
    datasets: generated,
  };

  const outputPath = path.join(ROOT, 'catalog/datasets.json');
  await writeFile(outputPath, JSON.stringify(output, null, 2), 'utf8');
  console.log('Generated catalog: ' + generated.length + ' datasets');
}

main().catch(err => {
  console.error(err instanceof Error ? err.message : String(err));
  process.exit(1);
});

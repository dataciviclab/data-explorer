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

const CATALOG_URL =
  "https://raw.githubusercontent.com/dataciviclab/dataset-incubator/main/registry/clean_catalog.json";

// Bucket name dal path contract (lab-connectors/gcs/paths.json)
const GCS_CLEAN_BUCKET = "dataciviclab-clean";
const DATA_DIR = "src/data";
const PAGES_DIR = "src/dataset";

fs.mkdirSync(DATA_DIR, { recursive: true });
fs.mkdirSync(PAGES_DIR, { recursive: true });

const resp = await fetch(CATALOG_URL);
const catalog = await resp.json();
const datasets = catalog.datasets;

// Template loader Python
function loaderTemplate(slug, name, groupCols, metricNames, yearRange) {
  return [
    '#!/usr/bin/env python3',
    '"""Data loader: ' + name + ' — aggregazione."""',
    'import sys; sys.path.insert(0, "src/data")',
    'from _util import load_dataset',
    '',
    'load_dataset(',
    '    slug="' + slug + '",',
    '    years=' + yearRange + ',',
    '    group_cols=["' + groupCols.join('", "') + '"],',
    '    metric_cols=["' + metricNames.join('", "') + '"],',
    ')',
    '',
  ].join("\n");
}

// Template pagina markdown
function pageTemplate(slug, name, description, source, stage, dims, metrics, hasYear, yearCol) {
  const lines = [
    '---',
    'title: ' + name,
    'description: ' + (description || "").slice(0, 200),
    '---',
    '',
    '# ' + name,
    '',
  ];
  if (description) lines.push(description, "");
  if (source) lines.push("**Fonte**: " + source + "  ");
  lines.push("**Stato**: " + (stage === "published" ? "✅ Pubblicato" : "🔬 Incubazione") + "  ");
  lines.push("", "---", "");

  // Load data
  lines.push("```js");
  lines.push('const data = await FileAttachment("../data/' + slug + '.json").json();');
  lines.push("```");
  lines.push("");

  // Summary stats
  lines.push("```js");
  lines.push("const totalRows = data.length;");
  lines.push("const firstKeys = Object.keys(data[0] || {});");
  const firstDim = dims.length > 0 ? dims[0].name : "?";
  lines.push('const entityCount = new Set(data.map(d => d.' + firstDim + ')).size;');
  lines.push("```");
  lines.push("");

  lines.push('<div class="grid grid-cols-3">');
  lines.push('  <div class="card"><h3>Record</h3><span class="big">${totalRows.toLocaleString()}</span></div>');
  lines.push('  <div class="card"><h3>' + firstDim.replace(/_/g, " ") + '</h3><span class="big">${entityCount.toLocaleString()}</span></div>');
  if (metrics.length > 0) {
    const firstMetric = metrics[0].name;
    lines.push('  <div class="card"><h3>' + firstMetric.replace(/_/g, " ") + '</h3><span class="big">${d3.format(".2s")(d3.sum(data, d => d.' + firstMetric + '))}</span></div>');
  }
  lines.push('</div>');
  lines.push("");

  // Year filter
  if (hasYear && yearCol) {
    lines.push("```js");
    lines.push('const anni = [...new Set(data.map(d => d.' + yearCol + '))].sort((a,b) => b - a);');
    lines.push('const anno = view(Inputs.select(anni, {label: "Anno", value: anni[0]}));');
    lines.push('const filtered = data.filter(d => d.' + yearCol + ' === anno);');
    lines.push("```");
    lines.push("");
  } else {
    lines.push("```js");
    lines.push("const filtered = data;");
    lines.push("```");
    lines.push("");
  }

  // Table
  lines.push("---", "");
  lines.push("```js");
  lines.push("Inputs.table(filtered, {rows: 15, width: \"100%\"})");
  lines.push("```");
  lines.push("");

  // Resources
  lines.push("---", "");
  lines.push("## Risorse", "");
  lines.push("- [Scarica il parquet](https://storage.googleapis.com/" + GCS_CLEAN_BUCKET + "/" + slug + "/)");
  lines.push("- [Vai alla pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/" + slug.replace(/_/g, "-") + ")");

  return lines.join("\n") + "\n";
}

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
    !!yearCol, yearCol?.name
  );
  fs.writeFileSync(path.join(PAGES_DIR, slug + ".md"), page);

  generated++;
}

console.log(JSON.stringify({ generated, skipped, total: datasets.length }));

#!/usr/bin/env node
/**
 * Template functions per la generazione di loader Python e pagine Markdown
 * per Observable Framework. Funzioni pure — nessun I/O, nessun fetch.
 *
 * Usate da generate_observable.mjs e testate in tests/generate-templates.test.mjs.
 */

/**
 * Genera il contenuto di un data loader Python (src/data/{slug}.json.py).
 */
export function loaderTemplate(slug, name, groupCols, metricNames, yearRange) {
  return [
    '#!/usr/bin/env python3',
    `"""Data loader: ${  name  } — aggregazione."""`,
    'import sys; sys.path.insert(0, "src/data")',
    'from _util import load_dataset',
    '',
    'load_dataset(',
    `    slug="${  slug  }",`,
    `    years=${  yearRange  },`,
    `    group_cols=["${  groupCols.join('", "')  }"],`,
    `    metric_cols=["${  metricNames.join('", "')  }"],`,
    ')',
    '',
  ].join("\n");
}

/**
 * Genera il contenuto di una pagina dataset Markdown (src/dataset/{slug}.md).
 *
 * @param {string} slug - Slug del dataset
 * @param {string} name - Nome visualizzato
 * @param {string} description - Descrizione
 * @param {string} source - Fonte del dato
 * @param {string} stage - Stato (published, incubating)
 * @param {Array<{name: string, type: string, role: string}>} dims - Colonne dimensione
 * @param {Array<{name: string, type: string, role: string}>} metrics - Colonne metrica
 * @param {boolean} hasYear - Se il dataset ha colonna anno
 * @param {string|null} yearCol - Nome colonna anno
 * @param {string} gcsBucket - GCS bucket per link parquet
 */
export function pageTemplate(slug, name, description, source, stage, dims, metrics, hasYear, yearCol, gcsBucket) {
  const bucket = gcsBucket || "dataciviclab-clean";
  const lines = [
    '---',
    `title: ${  JSON.stringify(name)}`,
    `description: ${  JSON.stringify((description || "").slice(0, 200))}`,
    '---',
    '',
    `# ${  name}`,
    '',
  ];
  if (description) lines.push(description, "");
  if (source) lines.push(`**Fonte**: ${  source  }  `);
  lines.push(`**Stato**: ${  stage === "published" ? "✅ Pubblicato" : "🔬 Incubazione"  }  `);
  lines.push("", "---", "");

  // Load data
  lines.push("```js");
  lines.push(`const data = await FileAttachment("../data/${  slug  }.json").json();`);
  lines.push("```");
  lines.push("");

  // Summary stats
  lines.push("```js");
  lines.push("const totalRows = data.length;");
  lines.push("const firstKeys = Object.keys(data[0] || {});");
  const firstDim = dims.length > 0 ? dims[0].name : "?";
  lines.push(`const entityCount = new Set(data.map(d => d.${  firstDim  })).size;`);
  lines.push("```");
  lines.push("");

  lines.push('<div class="grid grid-cols-3">');
  lines.push('  <div class="card"><h3>Record</h3><span class="big">${totalRows.toLocaleString()}</span></div>');
  lines.push(`  <div class="card"><h3>${  firstDim.replace(/_/g, " ")  }</h3><span class="big">\${entityCount.toLocaleString()}</span></div>`);
  if (metrics.length > 0) {
    const firstMetric = metrics[0].name;
    lines.push(`  <div class="card"><h3>${  firstMetric.replace(/_/g, " ")  }</h3><span class="big">\${d3.format(".2s")(d3.sum(data, d => d.${  firstMetric  }))}</span></div>`);
  }
  lines.push('</div>');
  lines.push("");

  // Year filter
  if (hasYear && yearCol) {
    lines.push("```js");
    lines.push(`const anni = [...new Set(data.map(d => d.${  yearCol  }))].sort((a,b) => b - a);`);
    lines.push('const anno = view(Inputs.select(anni, {label: "Anno", value: anni[0]}));');
    lines.push(`const filtered = data.filter(d => d.${  yearCol  } === anno);`);
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
  lines.push('Inputs.table(filtered, {rows: 15, width: "100%"})');
  lines.push("```");
  lines.push("");

  // Resources
  lines.push("---", "");
  lines.push("## Risorse", "");
  lines.push(`- [Scarica il parquet](https://storage.googleapis.com/${  bucket  }/${  slug  }/)`);
  lines.push(`- [Vai alla pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/${  slug.replace(/_/g, "-")  })`);

  return `${lines.join("\n")  }\n`;
}

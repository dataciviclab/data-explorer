/**
 * lint-standards.mjs — Verifica standard di codifica nelle pagine dataset.
 *
 * Controlli:
 *   1. Nessun `toLocaleString("it-IT")` nelle pagine
 *   2. `tableFormat` e `Inputs.table` in celle separate
 *   3. Mappe: `buildMapLookup` invece di `buildRegLookup` diretto
 *   4. Data loader: nessun `duckdb.connect()` diretto
 *
 * Uso: node scripts/lint-standards.mjs
 * Integrato in: npm run lint
 */
import { readFileSync, existsSync, readdirSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const errors = [];
const warnings = [];

// ── 1. toLocaleString nelle pagine dataset ──────────────────────────────────

function checkNoToLocaleString(content, slug) {
  const matches = content.match(/\.toLocaleString\(/g);
  if (matches) {
    errors.push(
      `${slug}: ${matches.length} occorrenze di toLocaleString() — usa num(), euro(), ecc. da format-utils.js`
    );
  }
}

// ── 2. tableFormat e Inputs.table in celle separate ─────────────────────────

function checkTableFormatCell(content, slug) {
  // Trova `const { header, format } = tableFormat(`
  const tfMatch = content.match(/const \{ header, format \} = tableFormat\(/);
  if (!tfMatch) return;

  // Trova la cella che contiene questa dichiarazione
  const lines = content.split("\n");
  let tfLine = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('const { header, format } = tableFormat(')) {
      tfLine = i;
      break;
    }
  }
  if (tfLine === -1) return;

  // Trova il delimitatore ``` dopo tfLine
  let cellEnd = -1;
  for (let i = tfLine + 1; i < lines.length; i++) {
    if (lines[i].startsWith("```")) {
      cellEnd = i;
      break;
    }
  }
  if (cellEnd === -1) return;

  // Controlla se Inputs.table è nella stessa cella
  for (let i = tfLine; i < cellEnd; i++) {
    if (lines[i].includes("Inputs.table(")) {
      errors.push(
        `${slug}: tableFormat e Inputs.table nella stessa cella (riga ${tfLine + 1}) — vanno separate`
      );
      return;
    }
  }
}

// ── 3. buildRegLookup in pagine con mappa ──────────────────────────────────

function checkBuildMapLookup(content, slug) {
  if (!content.includes("regioniGeo")) return; // no map, skip

  const hasRegLookup = /\bbuildRegLookup\(/.test(content);
  const hasMapLookup = /\bbuildMapLookup\(/.test(content);
  const hasTrentino = /\bbuildRegLookupWithTrentino\(/.test(content);

  if (hasRegLookup && !hasMapLookup && !hasTrentino) {
    errors.push(
      `${slug}: usa buildRegLookup con mappa — sostituisci con buildMapLookup`
    );
  }
}

// ── 4. duckdb.connect() nei loader ──────────────────────────────────────────

function checkDuckdbConnect(loaderPath, slug) {
  if (!existsSync(loaderPath)) return;
  const content = readFileSync(loaderPath, "utf-8");
  if (content.includes("duckdb.connect()")) {
    errors.push(
      `${slug}: usa duckdb.connect() invece di safe_connect()`
    );
  }
  // Controlla anche GCS_BASE usato direttamente (dovrebbe usare https_url)
  if (content.includes("GCS_BASE")) {
    warnings.push(
      `${slug}: usa GCS_BASE invece di https_url() — preferisci lab_connectors.gcs.paths`
    );
  }
}

// ── Main ────────────────────────────────────────────────────────────────────

const datasetDir = resolve(ROOT, "src/dataset");
const dataDir = resolve(ROOT, "src/data");

let count = 0;
for (const slug of readdirSync(datasetDir)) {
  if (!slug.endsWith(".md")) continue;
  const name = slug.replace(".md", "");
  const pagePath = resolve(datasetDir, slug);
  const content = readFileSync(pagePath, "utf-8");

  checkNoToLocaleString(content, name);
  checkTableFormatCell(content, name);
  checkBuildMapLookup(content, name);

  // Loader corrispondente
  const loaderPath = resolve(dataDir, `${name}.json.py`);
  checkDuckdbConnect(loaderPath, name);

  count++;
}

// Report
if (warnings.length > 0) {
  console.log("\n⚠️  Warning:");
  for (const w of warnings) console.log(`  • ${w}`);
}

if (errors.length > 0) {
  console.log(`\n❌ ${errors.length} errore(i) in ${count} pagine:`);
  for (const e of errors) console.log(`  • ${e}`);
  process.exit(1);
} else {
  console.log(`✅ Standard check: ${count} pagine, 0 errori`);
}

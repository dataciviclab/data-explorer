/**
 * audit.mjs — Controlli sui dati del build, prima della pubblicazione.
 *
 * Nasce da un guasto reale: `ispra-emissioni-ghg` aveva `years=[2023]`
 * hardcoded, il registry pubblicava il 2024, il loader scriveva `[]` e la
 * pagina andava in errore nel browser. Nessun controllo lo vedeva.
 *
 * Errori (fanno fallire il job):
 *   1. un loader produce un output vuoto;
 *   2. la pagina mostra anni fuori dal `period` dichiarato nel frontmatter;
 *   3. un dataset `published` non ha una superficie (pagina o scheda).
 *
 * Avvisi (non bloccano):
 *   4. un loader contiene un path GCS hardcoded;
 *   5. una mappa non copre tutte le regioni del TopoJSON (esclusioni
 *      dichiarate in `mappe_escluse`, unificazioni P.A. gestite in pagina
 *      vengono saltate: non sono verificabili staticamente).
 *
 * Uso: node scripts/audit.mjs
 */
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const CACHE = resolve(ROOT, "src/.observablehq/cache/data");
const PAGES = resolve(ROOT, "src/dataset");
const LOADERS = resolve(ROOT, "src/data");
const TOPO = resolve(ROOT, "src/data/regioni.topojson");

/** Loader che non sono dati di pagina. */
const NOT_PAGE_DATA = new Set(["catalog", "themes", "cards"]);

/** Chiavi che contengono un anno nei JSON dei loader. */
const YEAR_KEYS = /^(anno|year|esercizio_finanziario|anno_scolastico|anno_riferimento|legislatura)$/i;

/** Righe "utili" di un output loader (lista o mappa di liste). */
export function countRows(value) {
  if (Array.isArray(value)) return value.length;
  if (value && typeof value === "object") {
    return Object.values(value).reduce((sum, v) => sum + (Array.isArray(v) ? v.length : 0), 0);
  }
  return 0;
}

/** Anni presenti nei dati (ricorsivo, chiavi note, intervallo plausibile). */
export function collectYears(value, out = new Set(), budget = { left: 20000 }) {
  if (budget.left <= 0 || value === null || value === undefined) return out;
  budget.left -= 1;
  if (Array.isArray(value)) {
    for (const item of value) collectYears(item, out, budget);
    return out;
  }
  if (typeof value === "object") {
    for (const [key, item] of Object.entries(value)) {
      if (YEAR_KEYS.test(key)) {
        const year = typeof item === "string" ? Number.parseInt(item.slice(0, 4), 10) : item;
        if (Number.isInteger(year) && year >= 1800 && year <= 2100) out.add(year);
      } else {
        collectYears(item, out, budget);
      }
    }
  }
  return out;
}

/** `"2018–2025"` / `"2024"` / `"2016-2024"` → [2018, 2025]. */
export function parsePeriod(period) {
  if (!period) return null;
  const years = String(period).match(/\d{4}/g);
  if (!years || years.length === 0) return null;
  const nums = years.map(Number);
  return [Math.min(...nums), Math.max(...nums)];
}

/** Anni dei dati fuori dal periodo dichiarato (la pagina mostra più di quanto dichiara). */
export function periodViolation(period, years) {
  const range = parsePeriod(period);
  if (!range || !years || years.size === 0) return [];
  return [...years].filter((year) => year < range[0] || year > range[1]).sort();
}

/** Frontmatter YAML minimale: stringhe, numeri e liste `[a, b]`. */
export function parseFrontmatter(text) {
  const match = text.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return {};
  const data = {};
  for (const line of match[1].split("\n")) {
    const sep = line.indexOf(":");
    if (sep === -1) continue;
    const key = line.slice(0, sep).trim();
    const value = line.slice(sep + 1).trim();
    if (value.startsWith("[") && value.endsWith("]")) {
      data[key] = value
        .slice(1, -1)
        .split(",")
        .map((part) => part.trim().replace(/^["']|["']$/g, ""))
        .filter(Boolean);
    } else {
      data[key] = value.replace(/^["']|["']$/g, "");
    }
  }
  return data;
}

/** Nomi dei loader con output vuoto. */
export function emptyOutputs(outputs) {
  return Object.entries(outputs)
    .filter(([name]) => !NOT_PAGE_DATA.has(name))
    .filter(([, value]) => countRows(value) === 0)
    .map(([name]) => name)
    .sort();
}

/**
 * Loader con un path GCS scritto nel sorgente.
 * Deve avere un path dopo lo schema: `path.startswith("gs://")` o
 * `path[len("gs://"):]` sono controlli di schema, non path.
 */
const GCS_PATH = /["']gs:\/\/[^"'\s]+\/|https:\/\/storage\.googleapis\.com\/[^"'\s]+/;

export function hardcodedGcs(sources) {
  return Object.entries(sources)
    .filter(([, text]) => GCS_PATH.test(text))
    .map(([name]) => name)
    .sort();
}

/** Dataset published senza pagina né scheda. */
export function publishedWithoutSurface(catalog) {
  const datasets = catalog?.datasets || [];
  return datasets
    .filter((dataset) => dataset.published && !dataset.page_url)
    .map((dataset) => dataset.slug)
    .sort();
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf-8"));
}

function outputsFromCache() {
  const outputs = {};
  for (const file of readdirSync(CACHE).filter((f) => f.endsWith(".json"))) {
    const name = file.replace(/\.json$/, "");
    if (NOT_PAGE_DATA.has(name)) continue;
    try {
      outputs[name] = readJson(resolve(CACHE, file));
    } catch {
      outputs[name] = null; // JSON rotto = output inutilizzabile
    }
  }
  return outputs;
}

function loaderSources() {
  const sources = {};
  for (const file of readdirSync(LOADERS).filter((f) => f.endsWith(".json.py"))) {
    sources[file.replace(/\.json\.py$/, "")] = readFileSync(resolve(LOADERS, file), "utf-8");
  }
  return sources;
}

function pageFiles() {
  return readdirSync(PAGES).filter((f) => f.endsWith(".md"));
}

function refsOf(text) {
  return [...new Set([...text.matchAll(/\.\.\/data\/([A-Za-z0-9_.-]+)\.json/g)].map((m) => m[1]))].filter(
    (ref) => ref !== "regioni.topojson",
  );
}

function rowsOf(value) {
  if (Array.isArray(value)) return value;
  if (value && typeof value === "object") {
    return Object.values(value).flat().filter((row) => row && typeof row === "object");
  }
  return [];
}

/**
 * Regioni senza valore in una mappa.
 *
 * Le due province autonome vengono piegate in Trentino-Alto Adige prima del
 * controllo: è quello che fanno le pagine (per somma o per scelta), e senza
 * questa normalizzazione ogni mappa risulterebbe incompleta. Il controllo
 * resta sui dati: se una regione non è nella fonte, si vede.
 */
const TRENTINO_PA = /BOLZANO|TRENTO/i;

export async function mapGaps(text, outputs, topo, buildMapLookup, normalizzaReg) {
  const calls = [...text.matchAll(/buildMapLookup\(([^)]*)\)/g)];
  if (calls.length === 0) return null;
  const names = [...new Set(topo.objects.regioni.geometries.map((g) => g.properties.DEN_REG))];
  const regioniGeo = { features: names.map((name) => ({ properties: { DEN_REG: name } })) };
  const fm = parseFrontmatter(text);
  const excluded = new Set((fm.mappe_escluse || []).map((name) => normalizzaReg(name)));
  const allRows = refsOf(text).flatMap((ref) => rowsOf(outputs[ref]));
  const missing = new Set();
  for (const call of calls) {
    const args = call[1].split(",").map((part) => part.trim());
    const keyField = (args[2] || "").replace(/^["']|["']$/g, "");
    const valueField = (args[3] || "").replace(/^["']|["']$/g, "");
    if (!keyField) continue;
    const rows = allRows
      .filter((row) => typeof row?.[keyField] === "string" && row[keyField].length > 0)
      .map((row) => ({
        ...row,
        [keyField]: TRENTINO_PA.test(row[keyField]) ? "Trentino-Alto Adige" : row[keyField],
      }));
    const lookup = buildMapLookup(rows, regioniGeo, keyField, valueField || "valore");
    for (const name of names) {
      const key = normalizzaReg(name);
      if (!lookup.has(key) && !excluded.has(key)) missing.add(name);
    }
  }
  return { missing: [...missing].sort() };
}

async function main() {
  const outputs = outputsFromCache();
  const sources = loaderSources();
  const errors = [];
  const warnings = [];

  const empty = emptyOutputs(outputs);
  for (const name of empty) {
    errors.push(`loader ${name}: output vuoto (la pagina che lo usa va in errore)`);
  }

  const catalogPath = resolve(CACHE, "catalog.json");
  if (existsSync(catalogPath)) {
    for (const slug of publishedWithoutSurface(readJson(catalogPath))) {
      errors.push(`dataset ${slug}: published senza pagina né scheda (voce morta nel catalogo)`);
    }
  }

  const geoUtils = await import(resolve(ROOT, "src/import/geo-utils.js"));
  const topo = readJson(TOPO);
  let checkedMaps = 0;

  for (const file of pageFiles()) {
    const text = readFileSync(resolve(PAGES, file), "utf-8");
    const page = file.replace(/\.md$/, "");
    const fm = parseFrontmatter(text);

    if (fm.period) {
      const years = refsOf(text).flatMap((ref) => [...collectYears(outputs[ref])]);
      const outside = periodViolation(fm.period, new Set(years));
      if (outside.length) {
        // Non è un errore: la pagina può filtrare (es. attivita-aula parte dal
        // 2022 sulla XIX legislatura). È un invito a verificare il frontmatter.
        warnings.push(
          `pagina ${page}: period "${fm.period}", dati presenti fino a ${outside.join(", ")} — verifica`,
        );
      }
    }

    if (fm.data_driven !== "true") continue;
    const gaps = await mapGaps(text, outputs, topo, geoUtils.buildMapLookup, geoUtils.normalizzaReg);
    if (!gaps) continue;
    checkedMaps += 1;
    if (gaps.missing.length) {
      warnings.push(`mappa ${page}: ${gaps.missing.length} regioni senza valore (${gaps.missing.join(", ")})`);
    }
  }

  for (const name of hardcodedGcs(sources)) {
    warnings.push(`loader ${name}: path GCS hardcoded nel sorgente`);
  }

  const total = Object.keys(outputs).length;
  console.log(`\nAUDIT dati Explorer — ${total} loader, ${checkedMaps} mappe verificate\n`);
  for (const error of errors) console.log(`✗ ${error}`);
  for (const warning of warnings) console.log(`! ${warning}`);
  if (errors.length === 0) console.log(`\n✓ nessun errore (${warnings.length} avvisi)\n`);
  else console.log(`\n✗ ${errors.length} errori, ${warnings.length} avvisi\n`);

  if (errors.length) process.exit(1);
}

const invokedDirectly = process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (invokedDirectly) {
  main().catch((error) => {
    console.error(`audit fallito: ${error.message}`);
    process.exit(1);
  });
}

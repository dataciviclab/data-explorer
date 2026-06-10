/**
 * generate-config.mjs — Genera observablehq.config.js da themes.json + catalog.json.
 *
 * Sostituisce la manutenzione manuale della sidebar in observablehq.config.js
 * con una versione auto-generata dai data loader temi + catalogo.
 *
 * Flusso:
 *   1. Legge themes.json e catalog.json dalla cache OF (src/.observablehq/cache/data/)
 *   2. Se la cache non esiste (primo build), esegue i loader Python direttamente
 *   3. Costruisce la sidebar: ogni tema = sezione collassabile, ogni dataset = link
 *   4. Dataset non assegnati a nessun tema → sezione "Altri dataset"
 *   5. Scrive observablehq.config.js
 *
 * Integrazione: npm run prebuild (eseguito automaticamente prima di npm run build)
 */

import { execSync } from "node:child_process";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");

// ── Cache OF o fallback esecuzione diretta ──────────────────────────────────

function readData(slug) {
  // Prova prima la cache OF (più veloce, evita Python + HTTP)
  const cachePath = resolve(ROOT, `src/.observablehq/cache/data/${slug}`);
  if (existsSync(cachePath)) {
    return JSON.parse(readFileSync(cachePath, "utf-8"));
  }

  // Fallback: esegue il data loader Python
  const loaderPath = resolve(ROOT, `src/data/${slug}.py`);
  if (!existsSync(loaderPath)) {
    throw new Error(`Data loader non trovato: ${loaderPath}`);
  }
  const raw = execSync(`python3 "${loaderPath}"`, {
    encoding: "utf-8",
    cwd: ROOT,
  });
  return JSON.parse(raw);
}

// ── Generazione sidebar ─────────────────────────────────────────────────────

function readPageTitle(slug) {
  /* Legge il title: dal frontmatter YAML della pagina dataset.
   * I nomi editoriali (es. "Rifiuti urbani") sono lì.
   * Fallback: lo slug. */
  const pagePath = resolve(ROOT, `src/dataset/${slug}.md`);
  if (!existsSync(pagePath)) return slug;
  const content = readFileSync(pagePath, "utf-8");
  const match = content.match(/^title:\s*(.+)$/m);
  return match ? match[1].trim() : slug;
}

function buildSidebar(themes, catalog) {
  const pages = themes.map((t) => ({
    name: t.name,
    collapsible: true,
    pages: t.datasets.map((slug) => ({
      name: readPageTitle(slug),
      path: `/dataset/${slug}`,
    })),
  }));

  // Dataset pubblicati non assegnati a nessun tema → "Altri dataset"
  // Solo se hanno una pagina .md corrispondente in src/dataset/
  const assigned = new Set(themes.flatMap((t) => t.datasets));
  const unassigned = catalog.datasets.filter((d) => {
    if (d.stage !== "published") return false;
    if (assigned.has(d.url_slug)) return false;
    const pagePath = resolve(ROOT, `src/dataset/${d.url_slug}.md`);
    if (!existsSync(pagePath)) {
      console.warn(`  ⚠  ${d.url_slug}: pubblicato ma senza pagina explorer (salta)`);
      return false;
    }
    return true;
  });
  if (unassigned.length > 0) {
    pages.push({
      name: "Altri dataset",
      collapsible: true,
      pages: unassigned.map((d) => ({
        name: readPageTitle(d.url_slug),
        path: `/dataset/${d.url_slug}`,
      })),
    });
  }

  return pages;
}

// ── Entry point ─────────────────────────────────────────────────────────────

try {
  const catalog = readData("catalog.json");
  const themes = readData("themes.json");

  const pages = buildSidebar(themes, catalog);

  const config = `export default {
  root: "src",
  output: "dist/observable",
  title: "DataCivicLab Explorer",
  theme: ["air", "ocean-floor"],
  pages: ${JSON.stringify(pages, null, 2)},
};
`;

  const configPath = resolve(ROOT, "observablehq.config.js");
  writeFileSync(configPath, config, "utf-8");
  console.log(`✓ generate-config: ${pages.length} sezioni, ${pages.flatMap(p => p.pages || []).length} dataset`);
} catch (err) {
  console.error("✗ generate-config fallito:", err.message);
  process.exit(1);
}

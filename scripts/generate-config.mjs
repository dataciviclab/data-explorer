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

import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, existsSync, readdirSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");

// ── Cache OF o fallback esecuzione diretta ──────────────────────────────────

function readData(slug) {
  // Prova prima la cache OF (più veloce, evita Python + HTTP)
  const cachePath = resolve(ROOT, `src/.observablehq/cache/data/${slug}`);
  if (existsSync(cachePath)) {
    return JSON.parse(readFileSync(cachePath, "utf-8"));
  }

  // Fallback: esegue il data loader Python. Buffer ampio: il catalogo supera
  // 1 MB e il default di execSync (1 MB) lo tronca con ENOBUFS.
  const loaderPath = resolve(ROOT, `src/data/${slug}.py`);
  if (!existsSync(loaderPath)) {
    throw new Error(`Data loader non trovato: ${loaderPath}`);
  }
  const [python, ...args] = (process.env.PYTHON3 || "python3").split(/\s+/);
  const raw = execFileSync(python, [...args, loaderPath], {
    encoding: "utf-8",
    cwd: ROOT,
    maxBuffer: 64 * 1024 * 1024,
  });
  return JSON.parse(raw);
}

// ── Generazione sidebar ─────────────────────────────────────────────────────

function readPageTitle(slug) {
  /* Legge il title: dal frontmatter YAML della pagina dataset.
   * I nomi editoriali (es. "Rifiuti urbani") sono lì.
   * Rimuove virgolette YAML (es. '"Titolo"' → 'Titolo').
   * Fallback: lo slug. */
  const pagePath = resolve(ROOT, `src/dataset/${slug}.md`);
  if (!existsSync(pagePath)) return slug;
  const content = readFileSync(pagePath, "utf-8");
  const match = content.match(/^title:\s*(.+)$/m);
  return match ? match[1].trim().replace(/^["']|["']$/g, "") : slug;
}

/**
 * Costruisce le sezioni tema della sidebar.
 *
 * Una sezione è cliccabile quando esiste la pagina del tema: il framework
 * rende il `<summary>` come link se la sezione ha `path`. Così il tema è sia
 * destinazione sia contenitore dei suoi dataset, senza voci "Panoramica".
 *
 * Un dataset senza pagina ma con una scheda (`/schede/<slug>`) resta in
 * sidebar: prima veniva scartato e l'unico modo per raggiungerlo era la home.
 *
 * hasPage: callable slug → bool, iniettabile nei test (default: fs).
 * options.hasCard: slug → bool (scheda generata)
 * options.readName: slug → titolo pubblico (pagina o scheda)
 * options.hasThemePage: slug → bool (pagina /temi/<slug>)
 */
export function resolveThemePages(themes, hasPage, options = {}) {
  const {
    hasCard = () => false,
    readName = readPageTitle,
    hasThemePage = () => false,
  } = options;

  return themes
    .map((t) => {
      const themePages = [];
      for (const slug of t.datasets || []) {
        if (hasPage(slug)) {
          themePages.push({ name: readName(slug), path: `/dataset/${slug}` });
        } else if (hasCard(slug)) {
          themePages.push({ name: readName(slug), path: `/schede/${slug}` });
        } else {
          console.warn(`  ⚠  tema ${t.name}: ${slug} senza pagina né scheda (salta)`);
        }
      }
      if (themePages.length === 0) return null;
      return {
        name: t.name,
        collapsible: true,
        ...(hasThemePage(t.slug) ? { path: `/temi/${t.slug}` } : null),
        pages: themePages,
      };
    })
    .filter(Boolean);
}

function readCrossViewTitle(slug) {
  /* Legge il title dal frontmatter YAML di una pagina cross-view. */
  const pagePath = resolve(ROOT, `src/cross-views/${slug}.md`);
  if (!existsSync(pagePath)) return slug;
  const content = readFileSync(pagePath, "utf-8");
  const match = content.match(/^title:\s*(.+)$/m);
  if (!match) return slug;
  // Rimuovi virgolette YAML
  return match[1].trim().replace(/^["']|["']$/g, "");
}

function resolveCrossViewPagesSync() {
  /* Scansiona src/cross-views/*.md e restituisce le pagine per la sidebar. */
  const crossViewsDir = resolve(ROOT, "src/cross-views");
  if (!existsSync(crossViewsDir)) return [];

  const files = readdirSync(crossViewsDir).filter(f => f.endsWith(".md"));
  if (files.length === 0) return [];

  return files.map(f => {
    const slug = f.replace(/\.md$/, "");
    return {
      name: readCrossViewTitle(slug),
      path: `/cross-views/${slug}`,
    };
  });
}

function buildSidebar(themes, catalog) {
  const byUrl = new Map(catalog.datasets.map((d) => [d.url_slug, d]));
  const pages = resolveThemePages(
    themes,
    (slug) => existsSync(resolve(ROOT, `src/dataset/${slug}.md`)),
    {
      hasCard: (slug) => Boolean(byUrl.get(slug)?.has_card),
      readName: (slug) =>
        byUrl.get(slug)?.has_card ? byUrl.get(slug).name : readPageTitle(slug),
      hasThemePage: (slug) =>
        existsSync(resolve(ROOT, `src/temi/${slug}.md`)) ||
        existsSync(resolve(ROOT, "src/temi/[slug].md")),
    }
  );

  // Schede dataset generate (indice + route dinamica /schede/[slug]).
  // Una sola voce: la lista cresce senza allungare la sidebar.
  if (existsSync(resolve(ROOT, "src/schede/index.md"))) {
    pages.push({ name: "Schede dataset", path: "/schede/" });
  }

  // Dataset con pagina explorer non assegnati a nessun tema → "Altri dataset".
  // Invariante: ogni pagina .md in src/dataset/ deve comparire nella sidebar,
  // anche se non è nel catalogo ACB (es. slug divergente). Altrimenti la pagina
  // esiste nel build ma è raggiungibile solo per URL.
  const assigned = new Set(themes.flatMap((t) => t.datasets));
  const unassigned = catalog.datasets.filter((d) => {
    if (assigned.has(d.url_slug)) return false;
    const pagePath = resolve(ROOT, `src/dataset/${d.url_slug}.md`);
    return existsSync(pagePath) || Boolean(d.has_card);
  });
  const unassignedPages = unassigned.map((d) => ({
    name: d.has_card ? d.name : readPageTitle(d.url_slug),
    path: d.page_url,
  }));
  const included = new Set([
    ...pages.flatMap((section) => (section.pages || []).map((page) => page.path)),
    ...unassignedPages.map((page) => page.path),
  ]);
  const orphans = readdirSync(resolve(ROOT, "src/dataset"))
    .filter((file) => file.endsWith(".md"))
    .map((file) => file.replace(/\.md$/, ""))
    .map((slug) => ({ name: readPageTitle(slug), path: `/dataset/${slug}` }))
    .filter((page) => !included.has(page.path));
  if (unassignedPages.length + orphans.length > 0) {
    pages.push({
      name: "Altri dataset",
      collapsible: true,
      pages: [...unassignedPages, ...orphans],
    });
  }

  // Cross-views: pagine che incrociano dati da più dataset
  const crossViewPages = resolveCrossViewPagesSync();
  if (crossViewPages.length > 0) {
    pages.push({
      name: "Visioni incrociate",
      collapsible: true,
      pages: crossViewPages,
    });
  }

  return pages;
}

// ── Entry point ─────────────────────────────────────────────────────────────

// Guardia: il modulo è importato dai test. Senza di essa ogni `npm test`
// riscriverebbe observablehq.config.js (file generato e tracciato in git).
function isMainModule() {
  return Boolean(process.argv[1]) && import.meta.url === pathToFileURL(process.argv[1]).href;
}

if (isMainModule()) {
  try {
    const catalog = readData("catalog.json");
    const themes = readData("themes.json");

    const pages = buildSidebar(themes, catalog);

    const config = `export default {
  root: "src",
  output: "dist/observable",
  title: "DataCivicLab Explorer",
  theme: ["air", "ocean-floor"],
  interpreters: {
    ".py": ${JSON.stringify((process.env.PYTHON3 || "python3").split(/\s+/))}
  },
  // Temi e schede: route dinamiche. I path dei temi vengono da themes.json
  // (generato qui), quelli delle schede dal file statico di build_cards.py.
  dynamicPaths: async function* () {
    for (const slug of ${JSON.stringify(themes.map((t) => t.slug))}) {
      yield \`/temi/\${slug}\`;
    }
    try {
      const { readFileSync } = await import("node:fs");
      const cards = JSON.parse(readFileSync(new URL("./src/data/cards.json", import.meta.url), "utf-8"));
      for (const slug of Object.keys(cards)) yield \`/schede/\${slug}\`;
    } catch {
      // Nessuna scheda generata: il sito resta valido, solo senza /schede/*
    }
  },
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
}

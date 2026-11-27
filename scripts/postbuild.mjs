#!/usr/bin/env node
/**
 * postbuild.mjs — l'unico punto che conosce il dominio e le URL.
 *
 * Observable Framework non ha sitemap, non ha redirect, non scrive `lang` su
 * `<html>` e non differenzia i meta per lingua. Sono tutte cose che si possono
 * fare **dopo** il build, su file già statici, in un passaggio solo:
 *
 *   1. `lang` su `<html>` (it di default, `en/` per l'albero inglese);
 *   2. `<link rel="canonical">` se la pagina non ne ha già uno;
 *   3. `<link rel="alternate" hreflang>` fra le due lingue;
 *   4. `sitemap.xml` + `robots.txt`;
 *   5. stub di redirect per le URL che cambiano forma.
 *
 * Nessuna dipendenza, nessun accesso alla rete, idempotente: gira su `dist/`.
 *
 * Uso:
 *   node scripts/postbuild.mjs --dist dist/observable --site https://dataciviclab.org
 */

import { readFileSync, writeFileSync, statSync } from "node:fs";
import { readdir } from "node:fs/promises";
import { join, relative, sep } from "node:path";

const argv = process.argv.slice(2);
const arg = (name, fallback) => {
  const i = argv.indexOf(`--${name}`);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : fallback;
};

const DIST = arg("dist", "dist/observable");
const SITE = arg("site", "https://explorer.dataciviclab.org").replace(/\/$/, "");
const REDIRECTS = arg("redirects", "catalog/redirects.json");
const DEFAULT_LANG = arg("lang", "it");

/** Percorsi pubblici delle pagine, in forma `/x/` o `/x`. */
async function* pages(dir, root = dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name.startsWith("_") || entry.name === "node_modules") continue;
      yield* pages(full, root);
    } else if (entry.name.endsWith(".html")) {
      yield { file: full, path: urlPath(relative(root, full)) };
    }
  }
}

/** `progetti/x/index.html` → `/progetti/x/`; `a/b.html` → `/a/b`. */
function urlPath(rel) {
  const p = rel.split(sep).join("/");
  if (p === "index.html") return "/";
  if (p.endsWith("/index.html")) return "/" + p.slice(0, -"index.html".length);
  return "/" + p.replace(/\.html$/, "");
}

function langFor(path) {
  return path === "/en" || path.startsWith("/en/") ? "en" : DEFAULT_LANG;
}

/** Controparte linguistica, se esiste: `/en/x` ⇄ `/x`. */
function counterpart(path, known) {
  if (path === "/en" || path.startsWith("/en/")) return path.replace(/^\/en/, "") || "/";
  const en = "/en" + (path === "/" ? "/" : path);
  return known.has(en) ? en : null;
}

function setLang(html, lang) {
  return html.replace(/<html(\s[^>]*)?>/i, (m, attrs = "") => {
    const cleaned = attrs.replace(/\slang="[^"]*"/i, "");
    return `<html${cleaned} lang="${lang}">`;
  });
}

function ensureCanonical(html, url) {
  if (/rel="canonical"/i.test(html)) return html;
  return html.replace("</head>", `<link rel="canonical" href="${url}">\n</head>`);
}

function ensureAlternate(html, altUrl, altLang, selfUrl, selfLang) {
  if (!altUrl || /rel="alternate"/i.test(html)) return html;
  return html.replace(
    "</head>",
    `<link rel="alternate" hreflang="${altLang}" href="${SITE}${altUrl}">\n` +
      `<link rel="alternate" hreflang="${selfLang}" href="${SITE}${selfUrl}">\n</head>`
  );
}

/** Stub di redirect: non è un 301, ma conserva link, titolo e canonical. */
function redirectStub(from, to) {
  const target = `${SITE}${to}`;
  return `<!DOCTYPE html>
<html lang="${DEFAULT_LANG}">
<head>
<meta charset="utf-8">
<title>Pagina spostata</title>
<link rel="canonical" href="${target}">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url=${to}">
</head>
<body>
<p>Questa pagina si è spostata: <a href="${to}">${target}</a></p>
<script>location.replace(${JSON.stringify(to)});</script>
</body>
</html>`;
}

// ── main ───────────────────────────────────────────────────────────────────
const all = [];
for await (const page of pages(DIST)) all.push(page);
const known = new Set(all.map((p) => p.path));

let touched = 0;
for (const { file, path } of all) {
  const url = `${SITE}${path}`;
  const lang = langFor(path);
  const alt = counterpart(path, known);
  let html = readFileSync(file, "utf8");
  const before = html;
  html = setLang(html, lang);
  html = ensureCanonical(html, url);
  html = ensureAlternate(html, alt, lang === "en" ? "it" : "en", path, lang);
  if (html !== before) {
    writeFileSync(file, html);
    ++touched;
  }
}

const urls = all
  .map(({ path }) => `  <url><loc>${SITE}${path}</loc></url>`)
  .join("\n");
writeFileSync(
  join(DIST, "sitemap.xml"),
  `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`
);
writeFileSync(join(DIST, "robots.txt"), `User-agent: *\nAllow: /\n\nSitemap: ${SITE}/sitemap.xml\n`);

let redirects = 0;
try {
  const spec = JSON.parse(readFileSync(REDIRECTS, "utf8"));
  const { mkdirSync } = await import("node:fs");
  const { existsSync } = await import("node:fs");
  // Una pagina può essere `x.html` oppure `x/index.html`: entrambe occupano `/x`.
  const taken = (p) => {
    const clean = p.replace(/^\//, "").replace(/\/$/, "");
    return existsSync(join(DIST, `${clean}.html`)) || existsSync(join(DIST, clean, "index.html"));
  };
  for (const [from, to] of Object.entries(spec)) {
    if (taken(from)) {
      console.warn(`redirect ignorato, la pagina esiste: ${from}`);
      continue;
    }
    const dir = join(DIST, from.replace(/^\//, "").replace(/\/$/, ""));
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, "index.html"), redirectStub(from, to));
    ++redirects;
  }
} catch (error) {
  if (error.code !== "ENOENT") throw error;
  console.warn(`nessun file di redirect (${REDIRECTS})`);
}

console.log(
  `postbuild: ${all.length} pagine, ${touched} con lang/canonical, ` +
    `${redirects} stub, sitemap con ${all.length} URL`
);

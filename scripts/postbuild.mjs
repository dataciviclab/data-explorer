#!/usr/bin/env node
/**
 * postbuild.mjs — l'unico punto che conosce il dominio e le URL.
 *
 * Observable Framework non ha sitemap, non ha redirect, non scrive `lang` su
 * `<html>`, non differenzia i meta per lingua e dichiara `maximum-scale=1` nel
 * viewport (impedisce lo zoom). Sono tutte cose che si possono fare **dopo** il
 * build, su file già statici, in un passaggio solo:
 *
 *   1. `lang` su `<html>` (it di default, `en/` per l'albero inglese);
 *   2. viewport senza `maximum-scale=1` (WCAG 1.4.4: lo zoom non si blocca);
 *   3. `<link rel="canonical">` se la pagina non ne ha già uno;
 *   4. `<link rel="alternate" hreflang>` reciproci + `x-default`, **solo** fra
 *      pagine che esistono davvero in entrambe le lingue e non sono escluse;
 *   5. `noindex` sulle pagine escluse (`--exclude`) e sugli stub. Nota: le
 *      pagine `draft: true` non arrivano qui, OF non le costruisce;
 *   6. `sitemap.xml` (senza escluse, con `lastmod` e alternati) + `robots.txt`;
 *   7. stub di redirect per le URL che cambiano forma.
 *
 * Nessuna dipendenza, nessun accesso alla rete, idempotente: gira su `dist/`.
 *
 * Uso:
 *   node scripts/postbuild.mjs --dist dist/observable --site https://dataciviclab.org \
 *     [--lastmod 2026-11-27] [--redirects catalog/redirects.json]
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { readdir } from "node:fs/promises";
import { join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

// ── pagine ─────────────────────────────────────────────────────────────────

async function* walk(dir, root = dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name.startsWith("_") || entry.name === "node_modules") continue;
      yield* walk(full, root);
    } else if (entry.name.endsWith(".html")) {
      yield { file: full, path: urlPath(relative(root, full)) };
    }
  }
}

/** `progetti/x/index.html` → `/progetti/x/`; `a/b.html` → `/a/b`. */
export function urlPath(rel) {
  const p = rel.split(sep).join("/");
  if (p === "index.html") return "/";
  if (p.endsWith("/index.html")) return "/" + p.slice(0, -"index.html".length);
  return "/" + p.replace(/\.html$/, "");
}

export function isDraft(html) {
  return /<main[^>]*class="[^"]*observablehq--draft/.test(html);
}

/** Uno stub di redirect non è una pagina: non va in sitemap né in hreflang. */
export function isRedirect(html) {
  return /http-equiv="refresh"/i.test(html);
}

/**
 * Pagine da tenere nel sito ma fuori dall'indice (prototipi, esperimenti).
 * Nota: `draft: true` non serve qui — OF **non costruisce** le bozze
 * (`build.js:82`), quindi non arrivano nemmeno in `dist`.
 */
export function makeExcluder(spec = "") {
  const needles = String(spec)
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  return (path) => needles.some((needle) => path.includes(needle));
}

// ── lingue ─────────────────────────────────────────────────────────────────

export function langFor(path, defaultLang = "it") {
  return path === "/en" || path.startsWith("/en/") ? "en" : defaultLang;
}

/**
 * Le due versioni della stessa pagina, o `other: null` se la controparte non
 * esiste. Il controllo è **bidirezionale**: prima mancava nel verso EN→IT, così
 * una pagina inglese senza originale riceveva `hreflang` verso un 404.
 */
export function localesFor(path, known, defaultLang = "it") {
  if (langFor(path, defaultLang) === "en") {
    const it = path === "/en" ? "/" : path.slice(3);
    const other = known.has(it) ? { lang: defaultLang, path: it } : null;
    return { lang: "en", other, xDefault: other ? it : null };
  }
  const en = "/en" + (path === "/" ? "/" : path);
  const other = known.has(en) ? { lang: "en", path: en } : null;
  return { lang: defaultLang, other, xDefault: other ? path : null };
}

// ── trasformazioni dell'HTML ───────────────────────────────────────────────

export function setLang(html, lang) {
  return html.replace(/<html(\s[^>]*)?>/i, (m, attrs = "") => {
    const cleaned = attrs.replace(/\slang="[^"]*"/i, "");
    return `<html${cleaned} lang="${lang}">`;
  });
}

export function fixViewport(html) {
  return html.replace(/(<meta name="viewport" content=")([^"]*)(")/i, (m, open, content, close) => {
    const cleaned = content
      .split(",")
      .map((part) => part.trim())
      .filter((part) => part && !/^maximum-scale\s*=\s*1$/i.test(part))
      .join(", ");
    return open + cleaned + close;
  });
}

export function ensureCanonical(html, url) {
  if (/rel="canonical"/i.test(html)) return html;
  return html.replace("</head>", `<link rel="canonical" href="${url}">\n</head>`);
}

export function ensureNoindex(html) {
  if (/name="robots"/i.test(html)) return html;
  return html.replace("</head>", `<meta name="robots" content="noindex">\n</head>`);
}

export function ensureAlternates(html, { site, self, other, xDefault }) {
  if (!other || /rel="alternate"/i.test(html)) return html;
  const links = [
    `<link rel="alternate" hreflang="${self.lang}" href="${site}${self.path}">`,
    `<link rel="alternate" hreflang="${other.lang}" href="${site}${other.path}">`,
    xDefault ? `<link rel="alternate" hreflang="x-default" href="${site}${xDefault}">` : null,
  ].filter(Boolean);
  return html.replace("</head>", links.join("\n") + "\n</head>");
}

// ── sitemap ────────────────────────────────────────────────────────────────

export function sitemapEntry({ path, alternates }, { site, lastmod }) {
  const lines = ["  <url>", `    <loc>${site}${path}</loc>`];
  if (lastmod) lines.push(`    <lastmod>${lastmod}</lastmod>`);
  for (const alt of alternates) {
    lines.push(`    <xhtml:link rel="alternate" hreflang="${alt.lang}" href="${site}${alt.path}"/>`);
  }
  lines.push("  </url>");
  return lines.join("\n");
}

// ── redirect ───────────────────────────────────────────────────────────────

export function redirectStub(to, { site, lang = "it" }) {
  const target = `${site}${to}`;
  return `<!DOCTYPE html>
<html lang="${lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
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

export async function main(argv = process.argv.slice(2)) {
  const arg = (name, fallback) => {
    const i = argv.indexOf(`--${name}`);
    return i >= 0 && argv[i + 1] ? argv[i + 1] : fallback;
  };
  const DIST = arg("dist", "dist/observable");
  const site = arg("site", "https://explorer.dataciviclab.org").replace(/\/$/, "");
  const redirectsPath = arg("redirects", "catalog/redirects.json");
  const defaultLang = arg("lang", "it");
  const lastmod = arg("lastmod", "");
  const isExcluded = makeExcluder(arg("exclude", ""));

  const found = [];
  for await (const page of walk(DIST)) {
    page.html = readFileSync(page.file, "utf8");
    page.draft = isDraft(page.html);
    page.redirect = isRedirect(page.html);
    page.excluded = isExcluded(page.path);
    found.push(page);
  }

  // La controparte linguistica conta solo se è pubblica: una bozza, uno stub o
  // una pagina esclusa non sono un URL da linkare.
  const known = new Set(
    found.filter((p) => !p.draft && !p.redirect && !p.excluded).map((p) => p.path)
  );

  let touched = 0;
  const publicPages = [];
  for (const page of found) {
    const locales = localesFor(page.path, known, defaultLang);
    let html = page.html;

    html = setLang(html, langFor(page.path, defaultLang));
    html = fixViewport(html);
    html = ensureCanonical(html, `${site}${page.path}`);

    if (page.draft || page.redirect || page.excluded) {
      html = ensureNoindex(html);
    } else {
      html = ensureAlternates(html, {
        site,
        self: { lang: locales.lang, path: page.path },
        other: locales.other,
        xDefault: locales.xDefault,
      });
      publicPages.push({
        path: page.path,
        alternates: locales.other
          ? [
              { lang: locales.lang, path: page.path },
              { lang: locales.other.lang, path: locales.other.path },
            ]
          : [],
      });
    }

    if (html !== page.html) {
      writeFileSync(page.file, html);
      ++touched;
    }
  }

  publicPages.sort((a, b) => (a.path < b.path ? -1 : a.path > b.path ? 1 : 0));
  writeFileSync(
    join(DIST, "sitemap.xml"),
    `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${publicPages.map((page) => sitemapEntry(page, { site, lastmod })).join("\n")}
</urlset>
`
  );
  writeFileSync(join(DIST, "robots.txt"), `User-agent: *\nAllow: /\n\nSitemap: ${site}/sitemap.xml\n`);

  let redirects = 0;
  if (existsSync(redirectsPath)) {
    const spec = JSON.parse(readFileSync(redirectsPath, "utf8"));
    // Una pagina può essere `x.html` oppure `x/index.html`: occupano lo stesso URL.
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
      writeFileSync(join(dir, "index.html"), redirectStub(to, { site, lang: defaultLang }));
      ++redirects;
    }
  } else {
    console.warn(`nessun file di redirect (${redirectsPath})`);
  }

  const excluded = found.filter((p) => p.excluded).length;
  console.log(
    `postbuild: ${found.length} pagine (${excluded} fuori indice), ${touched} modificate, ` +
      `${redirects} stub, sitemap con ${publicPages.length} URL`
  );
}

const isMain = process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) await main();

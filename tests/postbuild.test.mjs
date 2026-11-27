/**
 * Test per scripts/postbuild.mjs — le cose che OF non fa e che il passaggio
 * post-build deve garantire: lang, viewport accessibile, hreflang solo fra
 * pagine esistenti, bozze fuori dalla sitemap, idempotenza.
 */
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

import {
  ensureAlternates,
  fixViewport,
  isDraft,
  langFor,
  localesFor,
  makeExcluder,
  setLang,
  urlPath,
} from "../scripts/postbuild.mjs";

const SCRIPT = resolve(dirname(fileURLToPath(import.meta.url)), "..", "scripts", "postbuild.mjs");
const SITE = "https://esempio.org";

const HEAD = `<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">`;
const page = ({ draft = false, body = "x" } = {}) =>
  `<!DOCTYPE html>
<html>
<head><meta charset="utf-8">${HEAD}</head>
<body><main id="observablehq-main" class="observablehq${draft ? " observablehq--draft" : ""}">${body}</main></body>
</html>`;

function write(dist, rel, html) {
  const file = join(dist, rel);
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, html);
  return file;
}

// ── unità ──────────────────────────────────────────────────────────────────

test("urlPath: cartella, file piatto, root", () => {
  assert.equal(urlPath("index.html"), "/");
  assert.equal(urlPath("progetti/x/index.html"), "/progetti/x/");
  assert.equal(urlPath("a/b.html"), "/a/b");
});

test("langFor: albero en", () => {
  assert.equal(langFor("/"), "it");
  assert.equal(langFor("/en"), "en");
  assert.equal(langFor("/en/x"), "en");
  assert.equal(langFor("/schema/en/x"), "it");
});

test("localesFor: trova la controparte in entrambi i versi", () => {
  const known = new Set(["/", "/en/", "/x", "/en/x"]);
  assert.deepEqual(localesFor("/x", known).other, { lang: "en", path: "/en/x" });
  assert.deepEqual(localesFor("/en/x", known).other, { lang: "it", path: "/x" });
  assert.equal(localesFor("/x", known).xDefault, "/x");
});

test("localesFor: nessuna controparte → null (il bug di hreflang verso il 404)", () => {
  const known = new Set(["/", "/en/", "/solo-en", "/en/solo-en"]);
  assert.equal(localesFor("/en/solo-en", new Set(["/", "/en/"])).other, null);
  assert.equal(localesFor("/solo-it", known).other, null);
  assert.equal(localesFor("/en/solo-en", known).other?.path, "/solo-en");
});

test("localesFor: /en e / sono la stessa pagina", () => {
  const known = new Set(["/", "/en/"]);
  assert.deepEqual(localesFor("/en", known).other, { lang: "it", path: "/" });
  assert.deepEqual(localesFor("/", known).other, { lang: "en", path: "/en/" });
});

test("setLang: sostituisce, non duplica", () => {
  assert.equal(setLang("<html>", "en"), '<html lang="en">');
  assert.equal(setLang('<html lang="it" class="x">', "en"), '<html class="x" lang="en">');
});

test("fixViewport: toglie maximum-scale, tiene il resto", () => {
  const out = fixViewport(page());
  assert.match(out, /content="width=device-width, initial-scale=1"/);
  assert.doesNotMatch(out, /maximum-scale/);
});

test("ensureAlternates: reciproci + x-default, e non duplica", () => {
  const once = ensureAlternates("<head></head>", {
    site: SITE,
    self: { lang: "it", path: "/x" },
    other: { lang: "en", path: "/en/x" },
    xDefault: "/x",
  });
  assert.match(once, /hreflang="it" href="https:\/\/esempio.org\/x"/);
  assert.match(once, /hreflang="en" href="https:\/\/esempio.org\/en\/x"/);
  assert.match(once, /hreflang="x-default"/);
  assert.equal(ensureAlternates(once, { site: SITE, self: {}, other: {}, xDefault: null }), once);
});

test("isDraft: legge il marcatore di OF (le bozze non arrivano in dist)", () => {
  assert.equal(isDraft(page()), false);
  assert.equal(isDraft(page({ draft: true })), true);
});

test("makeExcluder: prefissi, più valori, nessun match", () => {
  const ex = makeExcluder(" prova-,/en/old ");
  assert.equal(ex("/prova-custom"), true);
  assert.equal(ex("/en/prova-i18n"), true);
  assert.equal(ex("/en/old/x"), true);
  assert.equal(ex("/dataset/x"), false);
  assert.equal(makeExcluder("")(  "/prova-x"), false);
});

// ── integrazione ───────────────────────────────────────────────────────────

test("end-to-end: lang, canonical, bozze fuori, sitemap, idempotenza", () => {
  const dist = mkdtempSync(join(tmpdir(), "postbuild-"));
  const redirects = join(dist, "..", "redirects.json");
  writeFileSync(redirects, JSON.stringify({ "/vecchia": "/x" }));

  write(dist, "index.html", page({ body: "home" }));
  write(dist, "en/index.html", page({ body: "home en" }));
  write(dist, "x/index.html", page({ body: "x" }));
  write(dist, "en/x/index.html", page({ body: "x en" }));
  write(dist, "en/orfana/index.html", page({ body: "solo inglese" }));
  write(dist, "prova-custom.html", page({ body: "prototipo" }));

  const run = () =>
    execFileSync(
      "node",
      [
        SCRIPT,
        "--dist", dist,
        "--site", SITE,
        "--redirects", redirects,
        "--lastmod", "2026-11-27",
        "--exclude", "prova-",
      ],
      { encoding: "utf8" }
    );

  const out = run();
  assert.match(out, /6 pagine \(1 fuori indice\)/);
  assert.match(out, /sitemap con 5 URL/);
  assert.match(out, /1 stub/);

  const it = readFileSync(join(dist, "x/index.html"), "utf8");
  assert.match(it, /<html lang="it">/);
  assert.match(it, /rel="canonical" href="https:\/\/esempio.org\/x\/"/);
  assert.match(it, /hreflang="en"/);
  assert.doesNotMatch(it, /maximum-scale/);

  // EN senza controparte IT: nessun hreflang verso un URL che non esiste.
  const orfana = readFileSync(join(dist, "en/orfana/index.html"), "utf8");
  assert.match(orfana, /<html lang="en">/);
  assert.doesNotMatch(orfana, /rel="alternate"/);

  // Pagina esclusa (prototipo): resta nel sito, fuori dalla sitemap, noindex.
  const bozza = readFileSync(join(dist, "prova-custom.html"), "utf8");
  assert.match(bozza, /name="robots" content="noindex"/);
  const sitemap = readFileSync(join(dist, "sitemap.xml"), "utf8");
  assert.doesNotMatch(sitemap, /prova-custom/);
  assert.match(sitemap, /<lastmod>2026-11-27<\/lastmod>/);
  assert.match(sitemap, /xmlns:xhtml/);
  assert.match(sitemap, /xhtml:link rel="alternate" hreflang="en"/);

  // Redirect: stub creato, con canonical verso la destinazione.
  const stub = readFileSync(join(dist, "vecchia/index.html"), "utf8");
  assert.match(stub, /http-equiv="refresh" content="0; url=\/x"/);
  assert.match(stub, /rel="canonical" href="https:\/\/esempio.org\/x"/);

  // Idempotenza: la seconda passata non cambia una virgola.
  const before = readFileSync(join(dist, "x/index.html"), "utf8");
  const sitemapBefore = readFileSync(join(dist, "sitemap.xml"), "utf8");
  run();
  assert.equal(readFileSync(join(dist, "x/index.html"), "utf8"), before);
  assert.equal(readFileSync(join(dist, "sitemap.xml"), "utf8"), sitemapBefore);
});

test("end-to-end: non crea uno stub sopra una pagina esistente", () => {
  const dist = mkdtempSync(join(tmpdir(), "postbuild-"));
  const redirects = join(dist, "..", "redirects-coll.json");
  writeFileSync(redirects, JSON.stringify({ "/x": "/altrove" }));
  write(dist, "x.html", page());

  const out = execFileSync("node", [SCRIPT, "--dist", dist, "--site", SITE, "--redirects", redirects], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });
  assert.match(out, /0 stub/);
  assert.equal(existsSync(join(dist, "x", "index.html")), false);
});

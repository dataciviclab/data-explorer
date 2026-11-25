/**
 * Test per scripts/audit.mjs — i controlli che devono fermare un guasto come
 * `ispra-emissioni-ghg` (loader vuoto) prima della pubblicazione.
 */
import assert from "node:assert/strict";
import test from "node:test";

import {
  collectYears,
  countRows,
  emptyOutputs,
  hardcodedGcs,
  mapGaps,
  parseFrontmatter,
  parsePeriod,
  pageDatasetIssue,
  periodViolation,
  publishedWithoutSurface,
} from "../scripts/audit.mjs";
import { buildMapLookup, normalizzaReg } from "../src/import/geo-utils.js";

const TOPO = {
  objects: {
    regioni: {
      geometries: [{ properties: { DEN_REG: "Lombardia" } }, { properties: { DEN_REG: "Lazio" } }],
    },
  },
};

function page(body, extraFm = "") {
  return `---\ntitle: Demo\nperiod: "2020–2024"\ndata_driven: true\n${extraFm}---\n\n${body}`;
}

test("countRows conta liste e mappe di liste", () => {
  assert.equal(countRows([{ a: 1 }, { a: 2 }]), 2);
  assert.equal(countRows({ trend: [1], top: [1, 2, 3] }), 4);
  assert.equal(countRows([]), 0);
  assert.equal(countRows(null), 0);
  assert.equal(countRows({ trend: [] }), 0);
});

test("collectYears legge solo le chiavi-anno", () => {
  const years = collectYears([
    { anno: 2024, valore: 1990 },
    { anno_scolastico: "2022/2023" },
    { esercizio_finanziario: 2019 },
  ]);
  assert.deepEqual([...years].sort(), [2019, 2022, 2024]);
});

test("parsePeriod accetta en dash, trattino e anno singolo", () => {
  assert.deepEqual(parsePeriod("2018–2025"), [2018, 2025]);
  assert.deepEqual(parsePeriod("2016-2024"), [2016, 2024]);
  assert.deepEqual(parsePeriod("2024"), [2024, 2024]);
  assert.equal(parsePeriod(""), null);
});

test("periodViolation trova solo gli anni fuori dal periodo", () => {
  assert.deepEqual(periodViolation("2018–2025", new Set([2018, 2024, 2025])), []);
  assert.deepEqual(periodViolation("2018–2025", new Set([2018, 2026])), [2026]);
  assert.deepEqual(periodViolation("2018–2025", new Set([2010])), [2010]);
});

test("parseFrontmatter gestisce stringhe e liste", () => {
  const fm = parseFrontmatter(
    '---\nperiod: "2017–2025"\nmappe_escluse: [Sicilia, Sardegna]\n---\n',
  );
  assert.equal(fm.period, "2017–2025");
  assert.deepEqual(fm.mappe_escluse, ["Sicilia", "Sardegna"]);
});

test("emptyOutputs ignora i metadati e segnala i loader vuoti", () => {
  const empty = emptyOutputs({
    catalog: { datasets: [] },
    themes: [],
    cards: {},
    "senza-dati": [],
    "con-dati": [{ anno: 2024 }],
  });
  assert.deepEqual(empty, ["senza-dati"]);
});

test("hardcodedGcs riconosce i path scritti nel loader", () => {
  assert.deepEqual(
    hardcodedGcs({
      a: "x = 'gs://bucket/path.parquet'",
      b: "url = 'https://storage.googleapis.com/bucket/x'",
      c: "from _views import mart_rows",
    }),
    ["a", "b"],
  );
});

test("hardcodedGcs non segnala i controlli di schema", () => {
  assert.deepEqual(
    hardcodedGcs({
      a: 'if (path.startsWith("gs://")) {}',
      b: 'key = path[len("gs://"):]',
    }),
    [],
  );
});

test("pageDatasetIssue: slug mancante, sconosciuto, url divergente", () => {
  const by = new Map([["terna_elettricita_per_fonte", { url_slug: "terna-elettricita-per-fonte" }]]);
  assert.deepEqual(pageDatasetIssue(undefined, "x", by), { slug: "missing", url: null });
  assert.deepEqual(pageDatasetIssue("non_esiste", "x", by), { slug: "non_esiste", url: null });
  assert.deepEqual(pageDatasetIssue("terna_elettricita_per_fonte", "produzione-elettrica-fonti", by), {
    slug: null,
    url: "terna-elettricita-per-fonte",
  });
  assert.deepEqual(pageDatasetIssue("terna_elettricita_per_fonte", "terna-elettricita-per-fonte", by), {
    slug: null,
    url: null,
  });
});

test("publishedWithoutSurface trova le voci morte nel catalogo", () => {
  const slugs = publishedWithoutSurface({
    datasets: [
      { slug: "a", published: true, page_url: "/dataset/a" },
      { slug: "b", published: true, page_url: null },
      { slug: "c", published: false, page_url: null },
    ],
  });
  assert.deepEqual(slugs, ["b"]);
});

const CHIAMATA = 'buildMapLookup(perRegione, regioniGeo, "regione", "v")';
const REF = 'FileAttachment("../data/demo.json")';

test("mapGaps: mappa completa non produce avvisi", async () => {
  const outputs = { demo: [{ regione: "LOMBARDIA", v: 1 }, { regione: "LAZIO", v: 2 }] };
  assert.deepEqual(
    await mapGaps(page(`${REF}\n${CHIAMATA}`), outputs, TOPO, buildMapLookup, normalizzaReg),
    { missing: [] },
  );
});

test("mapGaps: regione mancante segnalata", async () => {
  const outputs = { demo: [{ regione: "LOMBARDIA", v: 1 }] };
  assert.deepEqual(
    await mapGaps(page(`${REF}\n${CHIAMATA}`), outputs, TOPO, buildMapLookup, normalizzaReg),
    { missing: ["Lazio"] },
  );
});

test("mapGaps: esclusione dichiarata nel frontmatter", async () => {
  const outputs = { demo: [{ regione: "LOMBARDIA", v: 1 }] };
  const text = page(`${REF}\n${CHIAMATA}`, "mappe_escluse: [Lazio]\n");
  assert.deepEqual(await mapGaps(text, outputs, TOPO, buildMapLookup, normalizzaReg), {
    missing: [],
  });
});

test("mapGaps: le due province autonome vengono piegate nel Trentino", async () => {
  const outputs = {
    demo: [
      { regione: "LOMBARDIA", v: 1 },
      { regione: "P.A. BOLZANO", v: 2 },
      { regione: "P.A. TRENTO", v: 3 },
    ],
  };
  const text = page(`${REF}\n${CHIAMATA}`);
  assert.deepEqual(await mapGaps(text, outputs, TOPO, buildMapLookup, normalizzaReg), {
    missing: ["Lazio"],
  });
});

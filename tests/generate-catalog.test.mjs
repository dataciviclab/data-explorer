/**
 * Test unitari per generate_catalog.mjs.
 *
 * Contratto: generateCatalogEntry() produce il formato corretto per datasets.json.
 *   isNonEmptyString() è un helper di validazione.
 *   fetchJson() recupera JSON da URL remoto.
 *
 * Prova del fuoco: se cancello questi test, un refactor di generateCatalogEntry
 * può produrre datasets.json con formato rotto senza preavviso.
 */
import assert from "node:assert/strict";
import { describe, it, mock } from "node:test";
import {
  generateCatalogEntry,
  isNonEmptyString,
  fetchJson,
} from "../scripts/generate_catalog.mjs";

describe("isNonEmptyString()", () => {
  it("restituisce true per stringa valida", () => {
    assert.equal(isNonEmptyString("test"), true);
    assert.equal(isNonEmptyString("abc"), true);
    assert.equal(isNonEmptyString(" a "), true);
  });

  it("restituisce false per stringa vuota", () => {
    assert.equal(isNonEmptyString(""), false);
    assert.equal(isNonEmptyString("   "), false);
  });

  it("restituisce false per non-stringhe", () => {
    assert.equal(isNonEmptyString(null), false);
    assert.equal(isNonEmptyString(undefined), false);
    assert.equal(isNonEmptyString(0), false);
    assert.equal(isNonEmptyString(123), false);
    assert.equal(isNonEmptyString([]), false);
    assert.equal(isNonEmptyString({}), false);
  });
});

describe("generateCatalogEntry()", () => {
  const baseEntry = {
    slug: "test-slug",
    name: "Test Dataset",
    description: "Una descrizione",
    stage: "published",
    period: { start: 2020, end: 2024 },
    source: "Fonte Test",
    source_id: "test-source",
    columns: [
      { name: "anno", type: "INTEGER", role: "dimension" },
      { name: "valore", type: "DOUBLE", role: "metric" },
    ],
  };

  it("produce entry completa con theme", () => {
    const result = generateCatalogEntry(baseEntry, "economia");

    assert.equal(result.slug, "test-slug");
    assert.equal(result.name, "Test Dataset");
    assert.equal(result.description, "Una descrizione");
    assert.equal(result.theme, "economia");
    assert.equal(result.stage, "published");
    assert.deepEqual(result.years, [2020, 2021, 2022, 2023, 2024]);
    assert.equal(result.source, "Fonte Test");
    assert.equal(result.source_id, "test-source");
    assert.equal(result.di_slug, "test-slug");
    assert.equal(result.columns.length, 2);
    assert.equal(result.columns[0].name, "anno");
    assert.equal(result.columns[1].role, "metric");
  });

  it("usa theme = null quando non fornito", () => {
    const result = generateCatalogEntry(baseEntry, null);
    assert.equal(result.theme, null);
  });

  it("usa description vuota se mancante", () => {
    const entry = { ...baseEntry, description: undefined };
    const result = generateCatalogEntry(entry, null);
    assert.equal(result.description, "");
  });

  it("produce years vuoto se period mancante", () => {
    const entry = { ...baseEntry, period: undefined };
    const result = generateCatalogEntry(entry, null);
    assert.deepEqual(result.years, []);
  });

  it("produce years vuoto se period parziale", () => {
    const entry = { ...baseEntry, period: { start: 2020 } };
    const result = generateCatalogEntry(entry, null);
    assert.deepEqual(result.years, []);
  });

  it("usa stage 'incubating' se mancante", () => {
    const entry = { ...baseEntry, stage: undefined };
    const result = generateCatalogEntry(entry, null);
    assert.equal(result.stage, "incubating");
  });

  it("usa source_id null se mancante", () => {
    const entry = { ...baseEntry, source_id: undefined };
    const result = generateCatalogEntry(entry, null);
    assert.equal(result.source_id, null);
  });

  it("gestisce columns vuoto", () => {
    const entry = { ...baseEntry, columns: [] };
    const result = generateCatalogEntry(entry, null);
    assert.deepEqual(result.columns, []);
  });

  it("columns include description vuota se mancante", () => {
    const entry = {
      ...baseEntry,
      columns: [{ name: "x", type: "VARCHAR", role: "dimension" }],
    };
    const result = generateCatalogEntry(entry, null);
    assert.equal(result.columns[0].description, "");
  });
});

describe("fetchJson()", () => {
  it("restituisce JSON parsato su HTTP 200", async () => {
    const url = "https://example.com/test.json";
    mock.method(globalThis, "fetch", () =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ key: "value" }),
      })
    );

    const result = await fetchJson(url);
    assert.deepEqual(result, { key: "value" });
    assert.equal(globalThis.fetch.mock.calls.length, 1);
    assert.equal(globalThis.fetch.mock.calls[0].arguments[0], url);

    globalThis.fetch.mock.restore();
  });

  it("lancia errore su HTTP non-200", async () => {
    mock.method(globalThis, "fetch", () =>
      Promise.resolve({
        ok: false,
        status: 404,
      })
    );

    await assert.rejects(
      () => fetchJson("https://example.com/missing"),
      /Fetch failed.*HTTP 404/
    );

    globalThis.fetch.mock.restore();
  });

  it("lancia errore su HTTP 500", async () => {
    mock.method(globalThis, "fetch", () =>
      Promise.resolve({
        ok: false,
        status: 500,
      })
    );

    await assert.rejects(
      () => fetchJson("https://example.com/error"),
      /HTTP 500/
    );

    globalThis.fetch.mock.restore();
  });
});

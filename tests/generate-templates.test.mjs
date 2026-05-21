/**
 * Test unitari per le template functions di generazione pagine.
 *
 * Verifica che loaderTemplate() e pageTemplate() producano output corretto
 * per diversi scenari di input.
 */
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { loaderTemplate, pageTemplate } from "../scripts/generate-templates.mjs";

describe("loaderTemplate()", () => {
  it("genera un data loader Python corretto per diverse configurazioni", () => {
    // slug con groupCols e metriche multiple
    const r1 = loaderTemplate(
      "test-slug", "Test Dataset",
      ["anno", "regione"], ["valore"],
      "list(range(2020, 2025))"
    );
    assert.match(r1, /slug="test-slug"/);
    assert.match(r1, /from _util import load_dataset/);
    assert.match(r1, /load_dataset\(/);
    assert.match(r1, /group_cols=\["anno", "regione"\]/);
    assert.match(r1, /metric_cols=\["valore"\]/);
    assert.match(r1, /list\(range\(2020, 2025\)\)/);

    // metriche multiple
    const r2 = loaderTemplate(
      "multi", "Multi",
      ["categoria"], ["spesa", "quantita", "ricavi"],
      "list(range(2019, 2024))"
    );
    assert.match(r2, /"spesa"/);
    assert.match(r2, /"quantita"/);
    assert.match(r2, /"ricavi"/);

    // groupCols singolo
    const r3 = loaderTemplate(
      "simple", "Simple",
      ["id"], ["valore"],
      "list(range(2020, 2022))"
    );
    assert.match(r3, /group_cols=\["id"\]/);
  });
});

describe("pageTemplate()", () => {
  const defaultDims = [
    { name: "regione", type: "VARCHAR", role: "dimension" },
  ];
  const defaultMetrics = [
    { name: "valore", type: "DOUBLE", role: "metric" },
  ];
  const gcsBucket = "test-bucket";

  it("genera frontmatter con title e description", () => {
    const result = pageTemplate(
      "test-slug",
      "Test Dataset",
      "Una descrizione di test",
      "Fonte Test",
      "published",
      defaultDims,
      defaultMetrics,
      false,
      null,
      gcsBucket
    );

    assert.match(result, /title: "Test Dataset"/);
    assert.match(result, /description: "Una descrizione di test"/);
    assert.match(result, /\*\*Fonte\*\*: Fonte Test/);
    assert.match(result, /✅ Pubblicato/);
  });

  it("genera page per dataset in incubazione", () => {
    const result = pageTemplate(
      "incubating-slug",
      "Incubating Dataset",
      "In fase di incubazione",
      "Fonte Incub",
      "incubating",
      defaultDims,
      defaultMetrics,
      false,
      null,
      gcsBucket
    );

    assert.match(result, /🔬 Incubazione/);
    assert.doesNotMatch(result, /✅ Pubblicato/);
  });

  it("include filtro anno quando hasYear è true", () => {
    const result = pageTemplate(
      "yearly",
      "Yearly Dataset",
      "Con anno",
      "Fonte",
      "published",
      [{ name: "anno", type: "INTEGER", role: "dimension" }],
      defaultMetrics,
      true,
      "anno",
      gcsBucket
    );

    assert.match(result, /const anni =/);
    assert.match(result, /const anno = view\(Inputs.select/);
    assert.match(result, /const filtered = data.filter/);
  });

  it("non include filtro anno quando hasYear è false", () => {
    const result = pageTemplate(
      "noyear",
      "No Year",
      "",
      "",
      "published",
      defaultDims,
      defaultMetrics,
      false,
      null,
      gcsBucket
    );

    assert.match(result, /const filtered = data;/);
    assert.doesNotMatch(result, /view\(Inputs.select/);
  });

  it("include link al parquet su GCS", () => {
    const result = pageTemplate(
      "gcs-test",
      "GCS Test",
      "",
      "",
      "published",
      defaultDims,
      defaultMetrics,
      false,
      null,
      "my-custom-bucket"
    );

    assert.match(result, /storage\.googleapis\.com\/my-custom-bucket\/gcs-test\//);
  });

  it("include link alla pipeline dataset-incubator", () => {
    const result = pageTemplate(
      "dataset-slug",
      "Dataset",
      "",
      "",
      "published",
      defaultDims,
      defaultMetrics,
      false,
      null,
      gcsBucket
    );

    assert.match(
      result,
      /github\.com\/dataciviclab\/dataset-incubator\/tree\/main\/candidates\/dataset-slug/
    );
  });

  it("usa slugs con underscore nel link pipeline (convertiti in trattini)", () => {
    const result = pageTemplate(
      "dataset_slug_con_underscore",
      "Underscore Slug",
      "",
      "",
      "published",
      defaultDims,
      defaultMetrics,
      false,
      null,
      gcsBucket
    );

    assert.match(
      result,
      /candidates\/dataset-slug-con-underscore/
    );
  });

  it("gestisce description vuota", () => {
    const result = pageTemplate(
      "no-desc",
      "No Desc",
      "",
      "Source",
      "published",
      defaultDims,
      defaultMetrics,
      false,
      null,
      gcsBucket
    );

    // description vuota → non deve apparire una riga description: vuota
    assert.match(result, /title: "No Desc"/);
    // Nessun errore, la pagina deve essere valida
    assert.ok(result.includes("# No Desc"));
  });

  it("gestisce dims e metrics vuoti", () => {
    const result = pageTemplate(
      "empty",
      "Empty Dims",
      "",
      "",
      "published",
      [],
      [],
      false,
      null,
      gcsBucket
    );

    // Deve comunque generare qualcosa senza crash
    assert.match(result, /title: "Empty Dims"/);
    assert.match(result, /const filtered = data;/);
    // Solo 2 card (record e ?), senza metrica
    assert.ok(result.includes('card'));
  });

  it("usa il nome first dim per entityCount", () => {
    const dims = [
      { name: "comune", type: "VARCHAR", role: "dimension" },
      { name: "provincia", type: "VARCHAR", role: "dimension" },
    ];
    const result = pageTemplate(
      "entity-test",
      "Entity Test",
      "",
      "",
      "published",
      dims,
      defaultMetrics,
      false,
      null,
      gcsBucket
    );

    // La prima dim è "comune" → entityCount usa d.comune
    assert.match(result, /d\.comune/);
  });
});

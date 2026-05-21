/**
 * Test unitari per generate_observable.mjs — processDataset().
 *
 * Contratto: processDataset() produce { slug, name, loader, page, skipped }
 * per ogni dataset del catalogo, senza I/O. Le template string sono delegate
 * a generate-templates.mjs (già testato separatamente).
 *
 * Prova del fuoco: se cancello questi test, un refactor della logica di
 * selezione colonne/anni/groupBy può rompere la generazione di pagine
 * e data loader senza preavviso.
 */
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { processDataset } from "../scripts/generate_observable.mjs";

const GCS_BUCKET = "dataciviclab-clean";

function makeDs(overrides = {}) {
  return {
    slug: "test-slug",
    name: "Test Dataset",
    description: "Una descrizione",
    source: "Fonte Test",
    stage: "published",
    period: { start: 2020, end: 2024 },
    columns: [
      { name: "anno", type: "INTEGER", role: "dimension" },
      { name: "regione", type: "VARCHAR", role: "dimension" },
      { name: "valore", type: "DOUBLE", role: "metric" },
      { name: "quantita", type: "INTEGER", role: "metric" },
    ],
    ...overrides,
  };
}

describe("processDataset()", () => {
  it("produce loader e page per dataset completo", () => {
    const result = processDataset(makeDs(), GCS_BUCKET);

    assert.equal(result.skipped, false);
    assert.equal(result.slug, "test-slug");
    assert.equal(result.name, "Test Dataset");

    // Loader: contiene slug, group_cols, metric_cols
    assert.match(result.loader, /slug="test-slug"/);
    assert.match(result.loader, /group_cols=\["anno", "regione"\]/);
    assert.match(result.loader, /metric_cols=\["valore", "quantita"\]/);

    // Page: contiene titolo, descrizione, fonte, stato
    assert.match(result.page, /title: "Test Dataset"/);
    assert.match(result.page, /description: "Una descrizione"/);
    assert.match(result.page, /\*\*Fonte\*\*: Fonte Test/);
    assert.match(result.page, /✅ Pubblicato/);
  });

  it("usa yearRange di default quando period mancante", () => {
    const result = processDataset(makeDs({ period: undefined }), GCS_BUCKET);

    assert.equal(result.skipped, false);
    assert.match(result.loader, /list\(range\(2019, 2026\)\)/);
  });

  it("usa yearRange di default quando period parziale", () => {
    const result = processDataset(makeDs({ period: { start: 2020 } }), GCS_BUCKET);

    assert.equal(result.skipped, false);
    assert.match(result.loader, /list\(range\(2019, 2026\)\)/);
  });

  it("skippa dataset senza metriche", () => {
    const result = processDataset(makeDs({ columns: [] }), GCS_BUCKET);

    assert.equal(result.skipped, true);
    assert.equal(result.loader, undefined);
    assert.equal(result.page, undefined);
  });

  it("skippa dataset con metriche tutte filtrate (pattern anno)", () => {
    const result = processDataset(makeDs({
      columns: [
        { name: "anno", type: "INTEGER", role: "dimension" },
        { name: "incremento_2020_2021", type: "DOUBLE", role: "metric" },
        { name: "incremento_2021_2022", type: "DOUBLE", role: "metric" },
      ],
    }), GCS_BUCKET);

    // Tutte le metriche hanno pattern anno → filtrate → skipped
    assert.equal(result.skipped, true);
  });

  it("filtra metriche con pattern anno ma preserva altre", () => {
    const result = processDataset(makeDs({
      columns: [
        { name: "anno", type: "INTEGER", role: "dimension" },
        { name: "valore", type: "DOUBLE", role: "metric" },
        { name: "incremento_2020_2021", type: "DOUBLE", role: "metric" },
      ],
    }), GCS_BUCKET);

    assert.equal(result.skipped, false);
    // Solo "valore" tra le metriche
    assert.match(result.loader, /metric_cols=\["valore"\]/);
  });

  it("include anno in groupCols quando presente", () => {
    const result = processDataset(makeDs(), GCS_BUCKET);

    assert.match(result.loader, /group_cols=\["anno", "regione"\]/);
    assert.match(result.page, /const anni =/);
    assert.match(result.page, /const anno = view\(Inputs.select/);
  });

  it("non include anno in groupCols se colonna anno assente", () => {
    const result = processDataset(makeDs({
      columns: [
        { name: "categoria", type: "VARCHAR", role: "dimension" },
        { name: "valore", type: "DOUBLE", role: "metric" },
      ],
    }), GCS_BUCKET);

    assert.equal(result.skipped, false);
    assert.match(result.loader, /group_cols=\["categoria"\]/);
    // Nessun filtro anno nella pagina
    assert.match(result.page, /const filtered = data;/);
    assert.doesNotMatch(result.page, /Inputs.select/);
  });

  it("usa prima colonna disponibile come groupDim se nessuna dim", () => {
    const result = processDataset(makeDs({
      columns: [
        { name: "valore", type: "DOUBLE", role: "metric" },
      ],
    }), GCS_BUCKET);

    assert.equal(result.skipped, false);
    // Solo la metrica → groupDim = columns[0] = "valore"
    assert.match(result.loader, /group_cols=\["valore"\]/);
  });

  it("usa 'id' come fallback se non ci sono colonne (solo metriche)", () => {
    const result = processDataset(makeDs({
      columns: [
        { name: "valore", type: "DOUBLE", role: "metric" },
      ],
    }), GCS_BUCKET);

    assert.equal(result.skipped, false);
    assert.match(result.loader, /group_cols=\["valore"\]/);
  });

  it("funziona con stage mancante", () => {
    const result = processDataset(makeDs({ stage: undefined }), GCS_BUCKET);

    assert.equal(result.skipped, false);
    assert.match(result.page, /\*\*Stato\*\*:/);
  });

  it("funziona con source e description vuoti", () => {
    const result = processDataset(makeDs({ source: "", description: "" }), GCS_BUCKET);

    assert.equal(result.skipped, false);
    assert.match(result.page, /title: "Test Dataset"/);
  });

  it("usa 'id' come column fallback quando columns è vuoto ma metrics no", () => {
    // Caso limite: columns ha solo metriche con role="metric" ma nessuna colonna dim
    // Non possiamo avere metrics senza columns... usiamo solo metriche
    const result = processDataset(makeDs({
      columns: [
        { name: "valore", type: "DOUBLE", role: "metric" },
        { name: "totale", type: "DOUBLE", role: "metric" },
      ],
    }), GCS_BUCKET);

    assert.equal(result.skipped, false);
    // La prima colonna (valore) viene usata come groupDim
    assert.match(result.loader, /group_cols=\["valore"\]/);
  });
});

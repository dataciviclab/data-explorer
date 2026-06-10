/**
 * Test per moduli condivisi (geo-utils.js, format-utils.js).
 *
 * Prova del fuoco: i moduli condivisi sono importati da tutte le pagine.
 * Se un refactor rompe normalizzaReg o i formattatori, ogni pagina ne risente.
 *
 * Nota: le funzioni che dipendono da OF runtime (FileAttachment, import("npm:"))
 * non sono testabili in isolation in questo ambiente. Vengono testate
 * indirettamente via build CI (observable build).
 */
import assert from "node:assert/strict";
import { describe, it } from "node:test";

// ── format-utils.js ──────────────────────────────────────────────────────────

describe("num()", () => {
  it("formatta numero in locale italiano", async () => {
    const { num } = await import("../src/import/format-utils.js");
    assert.equal(num(1234567), "1.234.567");
    assert.equal(num(0), "0");
    assert.equal(num(100), "100");
  });

  it("gestisce null/undefined/NaN", async () => {
    const { num } = await import("../src/import/format-utils.js");
    assert.equal(num(null), "\u2014");
    assert.equal(num(undefined), "\u2014");
    assert.equal(num(NaN), "\u2014");
    assert.equal(num(Infinity), "\u2014");
  });
});

describe("euro()", () => {
  it("formatta valore in euro", async () => {
    const { euro } = await import("../src/import/format-utils.js");
    assert.equal(euro(1234567), "\u20AC 1.234.567");
    assert.equal(euro(0), "\u20AC 0");
  });
});

describe("pct()", () => {
  it("formatta percentuale con 1 decimale default", async () => {
    const { pct } = await import("../src/import/format-utils.js");
    assert.equal(pct(75.8), "75,8%");
    assert.equal(pct(100), "100,0%");
  });

  it("formatta percentuale con decimali custom", async () => {
    const { pct } = await import("../src/import/format-utils.js");
    assert.equal(pct(75.84, 2), "75,84%");
    assert.equal(pct(75, 0), "75%");
  });
});

describe("unit()", () => {
  it("formatta numero con unita'", async () => {
    const { unit } = await import("../src/import/format-utils.js");
    assert.equal(unit(1234567, "t"), "1.234.567 t");
    assert.equal(unit(500, "MW"), "500 MW");
  });
});

describe("tableFormat()", () => {
  it("genera header e format da spec tipizzata", async () => {
    const { tableFormat } = await import("../src/import/format-utils.js");
    const { header, format } = tableFormat({
      regione: { label: "Regione", fmt: "string" },
      valore: "num",
      prezzo: "euro",
    });
    assert.equal(header.regione, "Regione");
    assert.equal(header.valore, "valore"); // label default = nome colonna
    assert.equal(typeof format.regione, "function");
    assert.equal(typeof format.valore, "function");
    assert.equal(typeof format.prezzo, "function");
    assert.equal(format.regione(123), "123"); // string formatter
    assert.equal(format.valore(1234567), "1.234.567"); // num formatter
    assert.equal(format.prezzo(1234567), "\u20AC 1.234.567"); // euro formatter
  });
});

describe("numFix()", () => {
  it("formatta con decimali fissi", async () => {
    const { numFix } = await import("../src/import/format-utils.js");
    const result = numFix(1234.567, 2);
    // Il separatore delle migliaia dipende dal runtime (Node vs browser).
    // In Node a volte non viene aggiunto con fractionDigits.
    // Testiamo che il formato italiano sia corretto: virgola decimale.
    assert.ok(result.includes(","), "deve usare virgola decimale");
    assert.ok(result.endsWith("57"), "deve arrotondare a 2 decimali");
    // Se Node aggiunge il separatore, ok; altrimenti ok lo stesso
  });
});

// ── geo-utils.js (pure functions only) ──────────────────────────────────────

describe("normalizzaReg()", () => {
  it("converte in uppercase e sostituisce spazi con trattini", async () => {
    const { normalizzaReg } = await import("../src/import/geo-utils.js");
    assert.equal(normalizzaReg("Lombardia"), "LOMBARDIA");
    assert.equal(normalizzaReg("Emilia-Romagna"), "EMILIA-ROMAGNA");
    assert.equal(normalizzaReg("Trentino Alto Adige"), "TRENTINO-ALTO-ADIGE");
  });

  it("normalizza slash con spazi", async () => {
    const { normalizzaReg } = await import("../src/import/geo-utils.js");
    assert.equal(
      normalizzaReg("Valle d'Aosta / Vallée d'Aoste"),
      "VALLE-D'AOSTA/VALLÉE-D'AOSTE",
    );
  });

  it("non altera gia' normalizzato", async () => {
    const { normalizzaReg } = await import("../src/import/geo-utils.js");
    assert.equal(normalizzaReg("LOMBARDIA"), "LOMBARDIA");
  });

  it("gestisce stringa vuota", async () => {
    const { normalizzaReg } = await import("../src/import/geo-utils.js");
    assert.equal(normalizzaReg(""), "");
  });
});

describe("REG_FALLBACKS", () => {
  it("contiene fallback Valle d'Aosta e Trentino", async () => {
    const { REG_FALLBACKS } = await import("../src/import/geo-utils.js");
    assert.ok("VALLE-DAOSTA" in REG_FALLBACKS);
    assert.ok("TRENTINO-ALTO-ADIGE" in REG_FALLBACKS);
  });

  it("fallback Valle d'Aosta punta a nome TopoJSON", async () => {
    const { REG_FALLBACKS } = await import("../src/import/geo-utils.js");
    assert.equal(
      REG_FALLBACKS["VALLE-DAOSTA"],
      "VALLE-D'AOSTA/VALLÉE-D'AOSTE",
    );
  });
});

describe("buildRegLookup()", () => {
  it("costruisce lookup regione->valore con normalizzazione", async () => {
    const { buildRegLookup } = await import("../src/import/geo-utils.js");
    const data = [
      { regione: "Lombardia", valore: 100 },
      { regione: "Lazio", valore: 50 },
    ];
    const lookup = buildRegLookup(data, "regione", "valore");
    assert.equal(lookup.get("LOMBARDIA"), 100);
    assert.equal(lookup.get("LAZIO"), 50);
  });

  it("applica fallback per regioni non standard", async () => {
    const { buildRegLookup } = await import("../src/import/geo-utils.js");
    // Simula dati ISPRA che usano VALLE-DAOSTA
    const data = [{ regione: "Valle d'Aosta", valore: 30 }];
    const lookup = buildRegLookup(data, "regione", "valore");
    // Fallback: VALLE-DAOSTA → VALLE-D'AOSTA/VALLÉE-D'AOSTE
    assert.ok(lookup.has("VALLE-D'AOSTA/VALLÉE-D'AOSTE"));
    assert.equal(
      lookup.get("VALLE-D'AOSTA/VALLÉE-D'AOSTE"),
      30,
    );
  });

  it("accetta transformValue function", async () => {
    const { buildRegLookup } = await import("../src/import/geo-utils.js");
    const data = [{ regione: "Lombardia", val: 200, tot: 1000 }];
    const lookup = buildRegLookup(
      data,
      "regione",
      null,
      (d) => (d.val / d.tot) * 100,
    );
    assert.equal(lookup.get("LOMBARDIA"), 20); // 200/1000 * 100
  });

  it("accetta extraFallbacks", async () => {
    const { buildRegLookup } = await import("../src/import/geo-utils.js");
    const data = [{ regione: "P.A. Trento", valore: 50 }];
    const lookup = buildRegLookup(
      data,
      "regione",
      "valore",
      null,
      { "P.A. TRENTO": "TRENTINO-ALTO-ADIGE/SÜDTIROL" },
    );
    assert.ok(lookup.has("TRENTINO-ALTO-ADIGE/SÜDTIROL"));
    assert.equal(lookup.get("TRENTINO-ALTO-ADIGE/SÜDTIROL"), 50);
  });
});

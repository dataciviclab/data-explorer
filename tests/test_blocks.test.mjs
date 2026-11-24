/**
 * Test per src/import/blocks.js — parti pure (aggregazione dati mappa).
 *
 * Il renderer usa DOM/Plot e non è testabile qui; `aggregateMapRows` sì, ed è
 * il punto dove si perdono le due P.A. (Bolzano/Trento) se non si aggregano.
 */
import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { aggregateMapRows } from "../src/import/blocks.js";

describe("aggregateMapRows()", () => {
  it("fonde le due P.A. Trentino in una regione", () => {
    const rows = aggregateMapRows([
      { region: "TRENTINO ALTO ADIGE (BOLZANO)", value: 5 },
      { region: "TRENTINO ALTO ADIGE (TRENTO)", value: 3 },
      { region: "LOMBARDIA", value: 10 },
    ]);
    assert.deepEqual(
      rows.sort((a, b) => a.region.localeCompare(b.region)),
      [
        { region: "LOMBARDIA", value: 10 },
        { region: "Trentino-Alto Adige", value: 8 },
      ]
    );
  });

  it("fonde Bolzano/Bozen e Trento (PIL)", () => {
    const rows = aggregateMapRows([
      { region: "Provincia Autonoma Bolzano/Bozen", value: 30.1 },
      { region: "Provincia Autonoma Trento", value: 29.2 },
    ]);
    assert.equal(rows.length, 1);
    assert.equal(rows[0].region, "Trentino-Alto Adige");
    assert.ok(Math.abs(rows[0].value - 59.3) < 1e-9);
  });

  it("somma duplicati con nome normalizzato uguale", () => {
    const rows = aggregateMapRows([
      { region: "Emilia Romagna", value: 1 },
      { region: "Emilia-Romagna", value: 2 },
    ]);
    assert.deepEqual(rows, [{ region: "Emilia-Romagna", value: 3 }]);
  });

  it("scarta righe senza regione o valore e gestisce input vuoto", () => {
    assert.deepEqual(aggregateMapRows([]), []);
    assert.deepEqual(
      aggregateMapRows([{ region: null, value: 1 }, { region: "Lazio", value: null }]),
      []
    );
  });
});

describe("map lookup dopo l'aggregazione", () => {
  it("il Trentino aggregato risolve la feature TopoJSON", async () => {
    const { readFileSync } = await import("node:fs");
    const { buildMapLookup, normalizzaReg } = await import("../src/import/geo-utils.js");

    const topo = JSON.parse(readFileSync("src/data/regioni.topojson", "utf-8"));
    // buildMapLookup usa solo i nomi delle feature: niente topojson-client.
    const regioniGeo = {
      features: topo.objects.regioni.geometries.map((geometry) => ({
        properties: geometry.properties,
      })),
    };
    const rows = aggregateMapRows([
      { region: "Provincia Autonoma Bolzano/Bozen", value: 30.1 },
      { region: "Provincia Autonoma Trento", value: 29.2 },
    ]);
    const lookup = buildMapLookup(rows, regioniGeo, "region", "value");
    assert.ok(
      Math.abs(lookup.get(normalizzaReg("Trentino-Alto Adige/Südtirol")) - 59.3) < 1e-9
    );
  });
});

/**
 * Test per scripts/generate-config.mjs — resolveThemePages (sidebar dinamica).
 */
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { resolveThemePages } from "../scripts/generate-config.mjs";

describe("resolveThemePages()", () => {
  const themes = [
    {
      slug: "sanita",
      name: "Sanità",
      datasets: ["farmacie", "personale-ssn"],
    },
    { slug: "vuoto", name: "Tema vuoto", datasets: ["solo-senza-pagina"] },
  ];

  it("include solo i dataset con pagina e ometti i temi vuoti", () => {
    const pages = resolveThemePages(themes, (slug) => slug === "farmacie");
    assert.equal(pages.length, 1);
    assert.equal(pages[0].name, "Sanità");
    assert.deepEqual(pages[0].pages.map((p) => p.path), ["/dataset/farmacie"]);
  });

  it("non crea sezioni per temi senza dataset con pagina", () => {
    const pages = resolveThemePages(themes, () => false);
    assert.deepEqual(pages, []);
  });
});

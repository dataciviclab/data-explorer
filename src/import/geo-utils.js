/**
 * geo-utils.js — Utility condivise per mappe coropletiche TopoJSON.
 *
 * Centralizza il boilerplate di normalizzazione nomi regione,
 * caricamento TopoJSON e costruzione lookup per Plot.geo.
 *
 * Uso in una pagina OF:
 *   import { normalizzaReg, loadItalianRegions, buildRegLookup } from "../import/geo-utils.js";
 *
 * Contratto regioni ISTAT:
 *   Il TopoJSON in src/data/regioni.topojson segue la nomenclatura ISTAT
 *   (DEN_REG). I dataset possono avere nomi regione leggermente diversi
 *   (maiuscole/minuscole, trattini, slash, P.A. Trentino separato).
 */

/**
 * Normalizza un nome regione per match con TopoJSON ISTAT.
 * Istituzioni diverse (ISPRA, MEF, ISTAT) usano varianti:
 *   "Valle d'Aosta" → "VALLE-D'AOSTA/VALLÉE-D'AOSTE"
 *   "P.A. Bolzano" → "TRENTINO-ALTO-ADIGE/SÜDTIROL"
 *   "Emilia-Romagna" → "EMILIA-ROMAGNA" (identico, solo uppercase)
 */
export function normalizzaReg(nome) {
  return nome
    .toUpperCase()
    .replace(/ \/ /g, "/")
    .replace(/ /g, "-");
}

/**
 * Mappa di fallback per regioni con nomi non standard nei dataset.
 * I dataset spesso usano "VALLE-DAOSTA" senza apostrofo, o
 * "TRENTINO-ALTO-ADIGE" senza lo slash "/SÜDTIROL".
 * Questa mappa allinea i nomi dataset al TopoJSON ISTAT.
 */
export const REG_FALLBACKS = {
  "VALLE-DAOSTA": "VALLE-D'AOSTA/VALLÉE-D'AOSTE",
  "VALLE-D'AOSTA": "VALLE-D'AOSTA/VALLÉE-D'AOSTE",
  "TRENTINO-ALTO-ADIGE": "TRENTINO-ALTO-ADIGE/SÜDTIROL",
};

/**
 * Prepara feature GeoJSON + confini da regioni.topojson.
 * NON usa FileAttachment internamente (non disponibile in moduli JS).
 * Il dato TopoJSON va caricato nella pagina con FileAttachment e passato qui.
 *
 * @param {Object} regTopo — Parsed TopoJSON da FileAttachment("...regioni.topojson").json()
 * @returns {{ regioniGeo: GeoJSON.FeatureCollection, confiniReg: GeoJSON.LineString }}
 *
 * @example
 * // Nella pagina .md:
 * import { loadItalianRegions } from "../import/geo-utils.js";
 * const regTopo = await FileAttachment("../data/regioni.topojson").json();
 * const { regioniGeo, confiniReg } = await loadItalianRegions(regTopo);
 */
export async function loadItalianRegions(regTopo) {
  const { feature, mesh } = await import("npm:topojson-client");
  return {
    regioniGeo: feature(regTopo, regTopo.objects.regioni),
    confiniReg: mesh(regTopo, regTopo.objects.regioni, (a, b) => a !== b),
  };
}

/**
 * Costruisce una lookup table regione→valore, normalizzando i nomi
 * e applicando fallback per regioni con nomi non standard.
 *
 * @param {Array} data — Array di oggetti con campo regione e campo valore
 * @param {string} keyField — Nome del campo "regione" (default: "regione")
 * @param {string} valueField — Nome del campo valore (default: usato se omitValue è false)
 * @param {Function} [transformValue] — Trasformazione opzionale del valore
 *        Es: d => d.reddito_imponibile_eur / totNazionale * 100
 * @param {Object} [extraFallbacks] — Fallback aggiuntivi oltre a REG_FALLBACKS
 * @returns {Map<string, any>} lookup table
 *
 * @example
 * // Semplice: regione → metrica
 * const lookup = buildRegLookup(dataFiltrati, "regione", "quota_rd");
 *
 * // Con trasformazione: regione → % del totale nazionale
 * const tot = d3.sum(data, d => d.reddito);
 * const lookup = buildRegLookup(data, "regione", null, d => d.reddito / tot * 100);
 *
 * // Con fallback extra
 * const lookup = buildRegLookup(data, "regione", "valore", null, {"P.A. TRENTO": "TRENTINO-ALTO-ADIGE/SÜDTIROL"});
 */
export function buildRegLookup(
  data,
  keyField = "regione",
  valueField,
  transformValue,
  extraFallbacks = {},
) {
  const allFallbacks = { ...REG_FALLBACKS, ...extraFallbacks };
  const lookup = new Map();
  const hasTransform = typeof transformValue === "function";

  // Primo pass: build della lookup dai dati
  for (const d of data) {
    const key = normalizzaReg(d[keyField]);
    const val = hasTransform ? transformValue(d) : d[valueField];
    lookup.set(key, val);
  }

  // Secondo pass: applica fallback per nomi non standard
  for (const [short, full] of Object.entries(allFallbacks)) {
    const shortKey = normalizzaReg(short);
    const fullKey = normalizzaReg(full);
    if (lookup.has(shortKey) && !lookup.has(fullKey)) {
      lookup.set(fullKey, lookup.get(shortKey));
    }
    // Se il dato ha il nome lungo ma shortKey non esiste, copia comunque
    if (lookup.has(fullKey) && !lookup.has(shortKey)) {
      lookup.set(shortKey, lookup.get(fullKey));
    }
  }

  return lookup;
}

/**
 * Helper per costruire un lookup quando le P.A. Trentino sono separate
 * e vanno unificate. Pattern usato in irpef-comunale.md.
 *
 * @param {Array} data
 * @param {string} keyField — campo regione
 * @param {Function} aggregateFn — funzione che somma/aggrega i valori per Trentino
 *        Es: items => items.reduce((s, d) => s + d.reddito_imponibile_eur, 0)
 * @param {string} [trentinoKey] — Nome del Trentino unificato (default: "P.A.")
 * @returns {Map<string, any>}
 */
export function buildRegLookupWithTrentino(
  data,
  keyField = "regione",
  aggregateFn,
  trentinoKey = "P.A.",
) {
  const lookup = buildRegLookup(
    data.filter((d) => normalizzaReg(d[keyField]) !== normalizzaReg(trentinoKey)),
    keyField,
    null,
    aggregateFn ? (d) => aggregateFn([d]) : null,
  );

  // Trova e aggrega le P.A. Trentino
  const trentinoItems = data.filter(
    (d) =>
      normalizzaReg(d[keyField]).includes(normalizzaReg(trentinoKey)) ||
      normalizzaReg(d[keyField]).includes("BOLZANO") ||
      normalizzaReg(d[keyField]).includes("TRENTO"),
  );

  if (trentinoItems.length > 0 && aggregateFn) {
    const trentinoVal = aggregateFn(trentinoItems);
    const trentKey = normalizzaReg("Trentino-Alto Adige");
    lookup.set(trentKey, trentinoVal);
    lookup.set(normalizzaReg("TRENTINO-ALTO-ADIGE/SÜDTIROL"), trentinoVal);
  }

  return lookup;
}

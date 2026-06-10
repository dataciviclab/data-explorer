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
  // BDAP usa abbreviazioni (F.-V. GIULIA, P. A. BOLZANO/TRENTO)
  "F.-V. GIULIA": "FRIULI-VENEZIA-GIULIA",
  "P. A. BOLZANO": "TRENTINO-ALTO-ADIGE/SÜDTIROL",
  "P. A. TRENTO": "TRENTINO-ALTO-ADIGE/SÜDTIROL",
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
 * Tokenizza un nome regione per fuzzy matching: toglie punti, slash,
 * apostrofi e parole comuni, restituisce un set di token significativi.
 *
 * @param {string} nome — Nome regione (es. "F.-V. GIULIA")
 * @returns {string[]} Token significativi (es. ["F", "V", "GIULIA"])
 */
function tokenizeReg(nome) {
  return nome
    .toUpperCase()
    .replace(/[.\/']/g, " ")
    .replace(/-/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .split(" ")
    .filter((t) => t.length >= 3 && !STOP_WORDS.has(t));
}

/** Parole troppo generiche per il matching. */
const STOP_WORDS = new Set([
  "ALTO", "ALTA", "ALTI", "BASSO", "BASSA",
  "DELL", "DELLA", "DELLE", "DEGLI", "DEL", "DEI",
  "SÜDTIROL", "VALLÉE",
  "PROVINCIA", "AUTONOMA", "PROV",
]);

/**
 * Costruisce una lookup table regione→valore, normalizzando i nomi,
 * applicando fallback per nomi non standard e fuzzy matching opzionale.
 *
 * @param {Array} data — Array di oggetti con campo regione e campo valore
 * @param {string} keyField — Nome del campo "regione" (default: "regione")
 * @param {string} valueField — Nome del campo valore
 * @param {Function} [transformValue] — Trasformazione opzionale del valore
 * @param {Object} [extraFallbacks] — Fallback aggiuntivi oltre a REG_FALLBACKS
 * @param {string[]} [topoKeys] — Se fornito, attiva il terzo passaggio fuzzy:
 *        cerca per token comune tra chiavi dataset e nomi TopoJSON non matchati.
 * @returns {Map<string, any>} lookup table
 *
 * @example
 * // Con fuzzy matching:
 * const topoNomi = regioniGeo.features.map(d => d.properties.DEN_REG);
 * const lookup = buildRegLookup(data, "regione", "valore", null, {}, topoNomi);
 */
export function buildRegLookup(
  data,
  keyField = "regione",
  valueField,
  transformValue,
  extraFallbacks = {},
  topoKeys = null,
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
    if (lookup.has(fullKey) && !lookup.has(shortKey)) {
      lookup.set(shortKey, lookup.get(fullKey));
    }
  }

  // Terzo pass (opzionale): fuzzy matching per topoKeys ancora senza valore
  if (topoKeys && topoKeys.length > 0) {
    // Costruisce un indice tokens→chiavi dataset
    const tokenIndex = new Map(); // token → [dataKey, ...]
    for (const dataKey of lookup.keys()) {
      for (const token of tokenizeReg(dataKey)) {
        if (!tokenIndex.has(token)) tokenIndex.set(token, []);
        tokenIndex.get(token).push(dataKey);
      }
    }

    for (const topoName of topoKeys) {
      const topoKey = normalizzaReg(topoName);
      if (lookup.has(topoKey)) continue; // già matchato

      // Cerca token comuni tra topoName e le chiavi dataset
      const topoTokens = tokenizeReg(topoName);
      const candidates = new Set();
      for (const token of topoTokens) {
        const matches = tokenIndex.get(token) || [];
        for (const dk of matches) candidates.add(dk);
      }

      if (candidates.size === 1) {
        // Match univoco: assegna il valore
        const [dataKey] = candidates;
        lookup.set(topoKey, lookup.get(dataKey));
      }
      // Se 0 o più di 1 candidati, non si può determinare — skip
    }
  }

  return lookup;
}

/**
 * buildMapLookup — wrapper standard per mappe coropletiche.
 * Equivalente a buildRegLookup con topoKeys automatico da regioniGeo.
 * Elimina il boilerplate: normalizzaReg, features.map, topoKeys manuale.
 *
 * @param {Array} data — dati con campo regione
 * @param {Object} regioniGeo — GeoJSON FeatureCollection (da loadItalianRegions)
 * @param {string} [keyField="regione"] — campo regione nei dati
 * @param {string} [valueField] — campo valore
 * @param {Function} [transformValue] — trasformazione opzionale del valore
 * @param {Object} [extraFallbacks] — fallback aggiuntivi oltre a REG_FALLBACKS
 * @returns {Map<string, any>}
 *
 * @example
 * const { regioniGeo } = await loadItalianRegions(regTopo);
 * const lookup = buildMapLookup(data, regioniGeo, "regione", "valore");
 * // poi: Plot.geo(regioniGeo, { fill: d => lookup.get(normalizzaReg(d.properties.DEN_REG)) })
 */
export function buildMapLookup(
  data,
  regioniGeo,
  keyField = "regione",
  valueField,
  transformValue,
  extraFallbacks = {},
) {
  const topoKeys = regioniGeo.features.map((d) => d.properties.DEN_REG);
  return buildRegLookup(data, keyField, valueField, transformValue, extraFallbacks, topoKeys);
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

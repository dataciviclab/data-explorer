/**
 * format-utils.js — Formattazione numeri e valute in locale italiano.
 *
 * Centralizza i pattern toLocaleString("it-IT") sparsi in tutte le pagine.
 * Pensate per template literal JS in Observable.
 *
 * Uso:
 *   import { num, euro, pct, unit, tableFormat } from "../import/format-utils.js";
 */

/** Formatta un numero intero con separatore migliaia italiano. */
export function num(x) {
  if (x == null || (typeof x === "number" && !isFinite(x))) return "\u2014";
  return Math.round(x).toLocaleString("it-IT");
}

/** Formatta un numero con decimali fissi. */
export function numFix(x, dec = 1) {
  if (x == null || (typeof x === "number" && !isFinite(x))) return "\u2014";
  return x.toLocaleString("it-IT", {
    minimumFractionDigits: dec,
    maximumFractionDigits: dec,
  });
}

/** Formatta un valore in euro. */
export function euro(x) {
  if (x == null || (typeof x === "number" && !isFinite(x))) return "\u2014";
  return "\u20AC " + num(x);
}

/** Formatta una percentuale (valore gia' in %, es. 75.8). */
export function pct(x, dec = 1) {
  if (x == null || (typeof x === "number" && !isFinite(x))) return "\u2014";
  return numFix(x, dec) + "%";
}

/** Formatta un numero con unita' di misura. */
export function unit(x, unita) {
  if (x == null || (typeof x === "number" && !isFinite(x))) return "\u2014";
  return num(x) + " " + unita;
}

/**
 * Factory per formattazione Inputs.table.
 * Progetta header leggibili e format function da una spec dichiarativa.
 *
 * @param {Object} spec — { nomeColonna: { label, fmt } | nomeColonna: "tipo" }
 *   tipi supportati: "num", "euro", "pct", "euroCompact", "string"
 * @returns {{ header: Object, format: Object }}
 *
 * @example
 * const { header, format } = tableFormat({
 *   regione: { label: "Regione", fmt: "string" },
 *   totale_ru_tonnellate: "num",
 *   quota_rd: "pct"
 * });
 * Inputs.table(data, { columns: [...], header, format });
 */
export function tableFormat(spec) {
  const header = {};
  const format = {};
  for (const [col, cfg] of Object.entries(spec)) {
    const label = typeof cfg === "string" ? col : (cfg.label || col);
    const fmt = typeof cfg === "string" ? cfg : (cfg.fmt || "num");
    header[col] = label;
    format[col] = FORMATTERS[fmt] || FORMATTERS.num;
  }
  return { header, format };
}

// Mappa tipi -> formatter
const FORMATTERS = {
  num: (x) => (x != null ? num(x) : "\u2014"),
  euro: (x) => (x != null ? euro(x) : "\u2014"),
  pct: (x) => (x != null ? pct(x) : "\u2014"),
  euroCompact: (x) => (x != null ? euroCompact(x) : "\u2014"),
  string: (x) => (x != null ? String(x) : "\u2014"),
};

// Necessario per euroCompact
function euroCompact(x) {
  if (x >= 1e9) return "\u20AC " + numFix(x / 1e9, 1) + " Mld";
  if (x >= 1e6) return "\u20AC " + numFix(x / 1e6, 1) + " Mln";
  return "\u20AC " + num(x);
}

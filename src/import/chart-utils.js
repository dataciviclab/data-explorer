/**
 * chart-utils.js — Helper per Observable Plot.
 *
 * Centralizza i pattern più usati. Previene:
 *   - stroke/fill con nomi di campo → colori diretti
 *   - barY vs barX confusion → hBar è sempre orizzontale
 *   - pct() senza ×100 → labelFormat gestisce la conversione
 *   - Boxyplate ripetuto (width, grid, marginLeft)
 *
 * Uso:
 *   import { hBar, lineChart, initChartUtils } from "../import/chart-utils.js";
 *   const plot = await import("npm:@observablehq/plot");
 *   initChartUtils(plot);
 *   display(hBar(data, { y: "nome", x: "valore" }));
 */
import { euroCompact, pct, num } from "./format-utils.js";

const W = 800;
const FONT = 11;

export const tickB = (d) => `${(d / 1e9).toFixed(0)} B€`;
export const tickM = (d) => `${(d / 1e6).toFixed(0)} M€`;

function labelFmt(fmt) {
  if (typeof fmt === "function") return fmt;
  if (fmt === "pct") return (v) => pct(v);
  if (fmt === "num") return (v) => num(v);
  return (v) => euroCompact(v);
}

let _plot;
export function initChartUtils(plotModule) { _plot = plotModule; }
function P() {
  if (!_plot) throw new Error("Chiama initChartUtils(plot) prima di usare chart-utils");
  return _plot;
}

// ── hBar — barre orizzontali ───────────────────────────────────────────────

/**
 * Barre orizzontali con etichette. Previene barY vs barX confusion.
 *
 * @param {Array} data
 * @param {Object} opts — { y, x, color?, label?, height?, marginLeft?, tip?, title? }
 * @example display(hBar(top10, { y: "amm", x: "spesa" }))
 */
export function hBar(data, opts = {}) {
  const { y, x, color = "#3182bd", label = "euroCompact", height, marginLeft, tip = true, title } = opts;
  const p = P();
  const fmt = labelFmt(label);
  const h = height ?? Math.max(200, data.length * 32 + 60);
  const ml = marginLeft ?? Math.min(350, Math.max(120,
    Math.max(...data.map((d) => String(d[y]).length)) * 7 + 30
  ));
  return p.plot({
    title, width: W, height: h, marginLeft: ml,
    x: { grid: true, tickFormat: tickB, label: null },
    y: { label: null, tickSize: 0 },
    marks: [
      p.barX(data, { x, y, fill: color, sort: { y: "-x" }, tip }),
      p.text(data, { x, y, text: (d) => ` ${fmt(d[x])}`, dx: 6, textAnchor: "start", fontSize: FONT, fill: "currentColor" }),
      p.ruleX([0]),
    ],
  });
}

// ── hBarGrouped — barre raggruppate ────────────────────────────────────────

/**
 * Barre orizzontali raggruppate (2 serie). Previene stroke named bugs.
 *
 * @param {Array} data — long format: { [y]: string, [group]: string, [x]: number }
 * @param {Object} opts — { y, x, group, domains, colors, label?, title? }
 * @example
 * const d = top10.flatMap(r => [{m: r.m, t: "Prev", v: r.p}, {m: r.m, t: "Pag", v: r.pag}]);
 * display(hBarGrouped(d, { y: "m", x: "v", group: "t", domains: ["Prev","Pag"], colors: ["#9ecae1","#2c7fb8"] }))
 */
export function hBarGrouped(data, opts = {}) {
  const { y, x, group, domains, colors, label = "euroCompact", height, marginLeft, title } = opts;
  const p = P();
  const fmt = labelFmt(label);
  const uniques = [...new Set(data.map((d) => d[y]))];
  const h = height ?? Math.max(200, uniques.length * 36 + 60);
  const ml = marginLeft ?? Math.min(350, Math.max(120,
    Math.max(...uniques.map((v) => String(v).length)) * 7 + 30
  ));
  return p.plot({
    title, width: W, height: h, marginLeft: ml,
    x: { grid: true, tickFormat: tickB, label: null },
    y: { label: null, tickSize: 0, domain: uniques },
    color: { domain: domains, range: colors },
    marks: [
      p.barX(data, { x, y, fill: group }),
      p.text(data, { x, y, text: (d) => ` ${fmt(d[x])}`, dx: 4, textAnchor: "start", fontSize: 10, fill: "currentColor" }),
      p.ruleX([0]),
    ],
  });
}

// ── lineChart — serie temporali ─────────────────────────────────────────────

/**
 * Linee temporali con punti. Supporta multi-serie.
 *
 * @param {Array} data
 * @param {Object} opts — { x, y, color?, colors?, labels?, height?, yFormat?, tip?, title? }
 * @example
 * display(lineChart(rows, { x: "anno", y: ["entrate","spese"], colors: ["#2c7fb8","#d62728"], labels: ["Entrate","Spese"] }))
 */
export function lineChart(data, opts = {}) {
  const { x, y, color = "#3182bd", colors, labels, height = 300, yFormat, tip = true, title } = opts;
  const p = P();
  const ys = Array.isArray(y) ? y : [y];
  const cls = colors || ys.map(() => color);
  const marks = [];
  for (let i = 0; i < ys.length; i++) {
    marks.push(p.lineY(data, { x, y: ys[i], stroke: cls[i], strokeWidth: 2 }));
    marks.push(p.dot(data, { x, y: ys[i], fill: "#fff", stroke: cls[i], r: 3, tip }));
  }
  const yConf = { grid: true };
  if (yFormat) yConf.tickFormat = yFormat;
  if (ys.length === 1) yConf.label = null;
  return p.plot({
    title, width: W, height,
    x: { tickFormat: String },
    y: yConf,
    color: labels ? { domain: labels, range: cls } : undefined,
    marks,
  });
}

// ── kpiCards — griglia KPI ─────────────────────────────────────────────────

/**
 * Genera HTML per KPI cards.
 *
 * @param {Array<{label, value, fmt?, color?}>} cards
 * @param {number} [cols=4]
 * @returns {string} HTML
 * @example display(kpiCards([{ label: "Totale", value: 1234, fmt: "euroCompact" }]))
 */
export function kpiCards(cards, cols = 4) {
  const fmt = labelFmt;
  const html = cards.map((c) => {
    const f = fmt(c.fmt || "euroCompact");
    const style = c.color ? ` style="color:${c.color}"` : "";
    return `<div class="card"><h3>${c.label}</h3><span class="big"${style}>${f(c.value)}</span></div>`;
  }).join("\n");
  return `<div class="grid grid-cols-${cols}">\n${html}\n</div>`;
}

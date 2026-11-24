/**
 * blocks.js — componenti condivisi per le schede dataset.
 *
 * Le pagine dinamiche di OF non iniettano `Inputs` né import `npm:`: qui non
 * si importa nulla. `html`, `plot`, `width` e `fmt` arrivano dalla pagina.
 *
 * Ogni blocco è dato puro nel card JSON:
 *   {type: "kpi",     items: [{label, value, format}]}
 *   {type: "series",  title, note, x_label, y_label, y_format, data: [{x,y}]}
 *   {type: "ranking", title, note, year, dimension_label, measure_label,
 *                     measure_format, data: [{label, value}]}
 */

const PALETTE = { line: "#2c7fb8", bar: "#4e79a7", accent: "#d95f0e" };

function sectionTitle(html, title) {
  return title ? html`<h2>${title}</h2>` : "";
}

function note(html, text) {
  return text ? html`<p style="opacity:0.75">${text}</p>` : "";
}

function emptyBlock(html, label) {
  return html`<p><em>${label}: nessun dato disponibile.</em></p>`;
}

function renderKpi(block, { html, fmt }) {
  if (!block.items.length) return emptyBlock(html, "KPI");
  return html`<div class="grid grid-cols-3">
    ${block.items.map(
      (item) => html`<div class="card">
        <h3>${item.label}</h3>
        <span class="big">${fmt(item.value, item.format)}</span>
      </div>`
    )}
  </div>`;
}

function renderSeries(block, { html, plot, width, fmt }) {
  const head = html`${sectionTitle(html, block.title)}${note(html, block.note)}`;
  if (block.data.length < 2) {
    return html`${head}${emptyBlock(html, block.title || "Serie")}`;
  }
  const first = block.data[0].x;
  const last = block.data[block.data.length - 1].x;
  const chart = plot.plot({
    width,
    height: 300,
    marginLeft: 76,
    x: { tickFormat: String, label: block.x_label },
    y: {
      grid: true,
      label: block.y_label,
      tickFormat: (value) => fmt(value, block.y_format),
    },
    marks: [
      plot.lineY(block.data, {
        x: "x",
        y: "y",
        stroke: PALETTE.line,
        strokeWidth: 2,
        tip: true,
      }),
      plot.dot(block.data, { x: "x", y: "y", fill: PALETTE.line, tip: true }),
      plot.ruleY([0]),
    ],
  });
  return html`${head}<p style="opacity:0.7; font-size:0.9rem">${block.y_label}, ${first}–${last}</p>${chart}`;
}

function renderRanking(block, { html, fmt }) {
  const head = html`${sectionTitle(html, block.title)}${note(html, block.note)}`;
  if (!block.data.length) {
    return html`${head}${emptyBlock(html, block.title || "Classifica")}`;
  }
  const subtitle = block.year ? `Anno ${block.year} · ` : "";
  return html`${head}<p style="opacity:0.7; font-size:0.9rem">${subtitle}${block.measure_label}</p>
    <table>
      <thead><tr><th>#</th><th>${block.dimension_label}</th><th>${block.measure_label}</th></tr></thead>
      <tbody>${block.data.map(
        (row, index) => html`<tr>
          <td>${index + 1}</td>
          <td>${row.label}</td>
          <td>${fmt(row.value, block.measure_format)}</td>
        </tr>`
      )}</tbody>
    </table>`;
}

const RENDERERS = {
  kpi: renderKpi,
  series: renderSeries,
  ranking: renderRanking,
};

export function renderBlock(block, ctx) {
  const render = RENDERERS[block.type];
  if (!render) return ctx.html`<p><em>Blocco non supportato: ${block.type}</em></p>`;
  return render(block, ctx);
}

export function renderBlocks(blocks, ctx) {
  return (blocks || []).map((block) => renderBlock(block, ctx));
}

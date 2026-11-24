---
title: "Scheda dataset"
toc: false
---

```js
import { num, euroCompact, pct, numFix } from "../import/format-utils.js";
```

```js
// Un solo file statico per tutte le schede: il build non interroga GCS.
const cards = await FileAttachment("../data/cards.json").json();
const slug = observable.params.slug;
const card = cards[slug];
if (!card) throw new Error(`Scheda non trovata: ${slug}`);

const stageLabel = card.published ? "Pubblicato" : "In incubazione";
const fmt = (value, format) => {
  if (value == null) return "—";
  if (format === "euroCompact") return euroCompact(value);
  if (format === "pct") return pct(value);
  if (format === "deltaPct") return `${value >= 0 ? "+" : ""}${numFix(value, 1)}%`;
  return num(value);
};
const lastPoint = card.series.length ? card.series[card.series.length - 1] : null;
```

# ${card.name}

```js
display(html`<p style="margin-top:-0.4rem; opacity:0.8">
  ${stageLabel}${card.category ? ` · ${card.category}` : ""}${card.registry_source ? ` · ${card.registry_source}` : ""}${card.source_id ? ` · fonte ${card.source_id}` : ""}
</p>`);
```

```js
if (card.description) display(html`<p style="font-size:1.05rem; line-height:1.6">${card.description}</p>`);
```

```js
if (card.intro) display(html`<p style="line-height:1.6">${card.intro}</p>`);
```

```js
if (card.warnings.length) display(html`<div class="note" style="border-left:3px solid #d95f0e; padding:0.6rem 0.9rem; background:var(--theme-background-alt); border-radius:0 8px 8px 0;">
  <strong>Scheda in preparazione.</strong> ${card.warnings.join(" ")}
</div>`);
```

```js
if (card.kpis.length) display(html`<div class="grid grid-cols-3">
  ${card.kpis.map((kpi) => html`<div class="card"><h3>${kpi.label}</h3><span class="big">${fmt(kpi.value, kpi.format)}</span></div>`)}
</div>`);
```

## Serie storica

```js
display(html`<p>${card.series.length > 1
  ? `${card.y.label}, dal ${card.series[0].x} al ${lastPoint.x}. Fonte: mart ${card.mart.ref}.`
  : "Serie non disponibile per questo dataset."}</p>`);
```

```js
const plot = await import("npm:@observablehq/plot");
```

```js
display(
  card.series.length > 1
    ? plot.plot({
        width,
        height: 300,
        marginLeft: 76,
        x: { tickFormat: String, label: card.x.label },
        y: { grid: true, label: card.y.label, tickFormat: (v) => fmt(v, card.y.format) },
        marks: [
          plot.lineY(card.series, { x: "x", y: "y", stroke: "#2c7fb8", strokeWidth: 2, tip: true }),
          plot.dot(card.series, { x: "x", y: "y", fill: "#2c7fb8", tip: true }),
          plot.ruleY([0]),
        ],
      })
    : html`<em>Nessuna serie da mostrare.</em>`
);
```

---

## Colonne del dataset clean

```js
display(html`<p style="opacity:0.75; font-size:0.92rem">Le descrizioni sono quelle dichiarate nel registry: se mancano, la scheda non le inventa.</p>`);
```

```js
// Tabella statica (niente Inputs): le pagine dinamiche OF non iniettano
// le dipendenze npm/Inputs. Il dizionario completo resta nel card JSON.
display(html`<table>
  <thead><tr><th>Colonna</th><th>Tipo</th><th>Ruolo</th><th>Tipo semantico</th><th>Descrizione</th></tr></thead>
  <tbody>${card.dictionary.slice(0, 20).map((c) => html`<tr>
    <td><code>${c.name}</code></td>
    <td>${c.type ?? ""}</td>
    <td>${c.role ?? ""}</td>
    <td>${c.semantic_type ?? ""}</td>
    <td>${c.description || "—"}</td>
  </tr>`)}</tbody>
</table>
<p style="opacity:0.75; font-size:0.9rem">${card.dictionary.length} colonne in totale (prime 20 mostrate).</p>`);
```

---

## Provenienza e dati

```js
display(html`<div class="grid grid-cols-3">
  <div class="card"><h3>Righe clean</h3><span class="big">${card.rows_clean ? num(card.rows_clean) : "—"}</span></div>
  <div class="card"><h3>Periodo dichiarato</h3><span class="big" style="font-size:1.1rem">${card.period.start ?? "?"}–${card.period.end ?? "?"}</span></div>
  <div class="card"><h3>Ultima esecuzione</h3><span class="big" style="font-size:1.1rem">${card.run?.finished_at ? card.run.finished_at.slice(0, 10) : "—"}</span></div>
</div>`);
```

```js
display(html`<ul>
  <li><strong>Mart della scheda</strong>: <code>${card.mart.ref}</code></li>
  <li><strong>Fonte</strong>: ${card.source_url ? html`<a href="${card.source_url}">${card.source || card.source_id}</a>` : (card.source || card.source_id || "—")}</li>
  <li><strong>Licenza</strong>: ${card.license || "non dichiarata"}</li>
  <li><strong>Pipeline</strong>: ${card.links.pipeline ? html`<a href="${card.links.pipeline}">${card.registry_source}</a>` : "—"}</li>
  <li><strong>Parquet clean</strong>: ${card.links.parquet ? html`<a href="${card.links.parquet}">dato pubblico</a>` : "—"}</li>
  <li><strong>Query SQL</strong>: <a href="${card.links.query}">interroga i dati</a></li>
</ul>`);
```

```js
if (card.notes.length) display(html`<h2>Limiti</h2><ul>${card.notes.map((note) => html`<li>${note}</li>`)}</ul>`);
```

```js
if (card.run) display(html`<p style="opacity:0.75; font-size:0.9rem">Run ${card.run.run_id} · stato ${card.run.status} · qualità ${card.run.quality?.mart ?? "—"}</p>`);
```

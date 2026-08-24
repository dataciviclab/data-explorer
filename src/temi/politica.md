---
title: Politica
description: Elezioni, Parlamento, Governo e amministratori locali — i dati della politica italiana
---

# Politica

Elezioni politiche, comunali, europee, regionali e referendum. Composizione del Parlamento, votazioni della Camera, membri del Governo e amministratori locali. I dataset di questo tema coprono la politica italiana dal voto ai rappresentanti.

```js
const catalog = await FileAttachment("../data/catalog.json").json();
const themes = await FileAttachment("../data/themes.json").json();
const theme = themes.find(t => t.slug === "politica");
const datasets = theme.datasets.map(slug => catalog.datasets.find(d => d.url_slug === slug)).filter(Boolean);
```

```js
const periodStart = Math.min(...datasets.map(d => parseInt(d.years.split('–')[0])));
const periodEnd = Math.max(...datasets.map(d => parseInt(d.years.split('–')[1])));
const totDatasets = datasets.length;
const sources = [...new Set(datasets.map(d => d.source))];
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Dataset</h3>
    <span class="big">${totDatasets}</span>
  </div>
  <div class="card">
    <h3>Periodo</h3>
    <span class="big">${String(periodStart)}–${String(periodEnd)}</span>
  </div>
  <div class="card">
    <h3>Fonti</h3>
    <span class="big">${sources.length}</span>
  </div>
</div>

---

## Dataset del tema

```js
display(html`<div class="grid grid-cols-2">
  ${datasets.map(d => html`<div class="card">
    <h3><a href="/dataset/${d.url_slug}">${d.name}</a></h3>
    <p style="opacity:0.7; font-size:0.9em">${d.description}</p>
    <p style="font-size:0.85em">${d.years} · ${d.stage === "published" ? "✅ Pubblicato" : "🔬 Incubazione"}</p>
  </div>`)}
</div>`)
```

---

## Esplora per tema

- [Finanza pubblica](/temi/finanza-pubblica)
- [Territorio e ambiente](/temi/territorio-ambiente)
- [Sanità](/temi/sanita)
- [Welfare e lavoro](/temi/welfare-lavoro)
- [Giustizia](/temi/giustizia)
- [Terzo settore](/temi/terzo-settore)

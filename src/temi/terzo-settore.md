---
title: Terzo settore
description: 5x1000, enti non profit, flussi finanziari al terzo settore
---

# Terzo settore

Enti beneficiari del 5x1000: importi erogabili, numero di scelte e distribuzione per regione e categoria.

```js
const catalog = await FileAttachment("../data/catalog.json").json();
const themes = await FileAttachment("../data/themes.json").json();
const theme = themes.find(t => t.slug === "terzo-settore");
const datasets = theme.datasets.map(slug => catalog.datasets.find(d => d.url_slug === slug)).filter(Boolean);
```

```js
const totDatasets = datasets.length;
const sources = [...new Set(datasets.map(d => d.source))];
```

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Dataset</h3>
    <span class="big">${totDatasets}</span>
  </div>
  <div class="card">
    <h3>Fonti</h3>
    <span class="big">${sources.length}</span>
  </div>
  <div class="card">
    <h3>Stato</h3>
    <span class="big">In crescita</span>
  </div>
</div>

---

## Dataset del tema

```js
display(html`<div class="card">
    <h3><a href="/dataset/${datasets[0].url_slug}">${datasets[0].name}</a></h3>
    <p style="opacity:0.7; font-size:0.9em">${datasets[0].description}</p>
    <p style="font-size:0.85em">${datasets[0].years} · ${datasets[0].stage === "published" ? "✅ Pubblicato" : "🔬 Incubazione"}</p>
</div>`)
```

---

## Esplora per tema

- [Territorio e ambiente](/temi/territorio-ambiente)
- [Finanza pubblica](/temi/finanza-pubblica)
- [Sanità](/temi/sanita)
- [Welfare e lavoro](/temi/welfare-lavoro)
- [Giustizia](/temi/giustizia)

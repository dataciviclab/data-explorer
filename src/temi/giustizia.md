---
title: Giustizia
description: Flussi civili, tempi e carichi dei tribunali
---

# Giustizia

Flussi della giustizia civile: sopravvenuti, definiti e pendenti per distretto. Il dataset di questo tema copre l'andamento del contenzioso civile nei tribunali italiani.

```js
const catalog = await FileAttachment("../data/catalog.json").json();
const themes = await FileAttachment("../data/themes.json").json();
const theme = themes.find(t => t.slug === "giustizia");
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
    <span class="big">${periodStart}–${periodEnd}</span>
  </div>
  <div class="card">
    <h3>Fonti</h3>
    <span class="big">${sources.length}</span>
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

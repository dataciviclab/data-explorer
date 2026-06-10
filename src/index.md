---
title: DataCivicLab Explorer
description: Catalogo pubblico dei dataset civici del Lab
---

# DataCivicLab Explorer

Catalogo pubblico dei dataset civici. I dati sono puliti, documentati e disponibili in formato parquet.

```js
const catalog = await FileAttachment("data/catalog.json").json();
const themes = await FileAttachment("data/themes.json").json();
```

<div class="grid grid-cols-3">
  <div class="card"><h3>Totale</h3><span class="big">${catalog.total}</span></div>
  <div class="card"><h3>Pubblicati</h3><span class="big">${catalog.published}</span></div>
  <div class="card"><h3>Temi</h3><span class="big">${themes.length}</span></div>
</div>

## Temi

```js
display(html`<div class="grid grid-cols-2">
  ${themes.map(t => html`<div class="card">
    <h3><a href="/temi/${t.slug}">${t.name}</a></h3>
    <p style="opacity:0.7; font-size:0.9em">${t.description}</p>
    <p style="font-size:0.85em">${t.datasets.length} dataset</p>
  </div>`)}
</div>`)
```

---

## Tutti i dataset

```js
const searchQuery = view(Inputs.search(catalog.datasets, {label: "Cerca per nome, descrizione o fonte…"}));
```

```js
const stageFilter = view(Inputs.select(
  ["Tutti", "published", "incubating"],
  {label: "Filtra per stato", value: "Tutti"}
));
```

```js
const filtered = searchQuery.filter(d => stageFilter === "Tutti" || d.stage === stageFilter);
```

```js
Inputs.table(filtered, {
  columns: ["slug", "name", "stage", "years", "source"],
  header: {slug: "ID", name: "Nome", stage: "Stato", years: "Anni", source: "Fonte"},
  format: {stage: d => d === "published" ? "✅ Pubblicato" : "🔬 Incubazione"},
  sort: "slug",
  rows: 30,
  width: "100%",
})
```

<div style="margin-top: 2em; opacity: 0.6; font-size: 0.85em;">
Catalogo aggiornato: ${catalog.updated_at}
</div>

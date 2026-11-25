---
title: Tema
---

```js
// Una sola pagina per tutti i temi. Il contenuto editoriale (nome, descrizione,
// intro) viene da catalog/themes.json; numeri e dataset dal catalogo.
// Aggiungere un tema = una voce in themes.json, nessun file da scrivere.
const catalog = await FileAttachment("../data/catalog.json").json();
const themes = await FileAttachment("../data/themes.json").json();
const slug = observable.params.slug;
const theme = themes.find((t) => t.slug === slug);
if (!theme) throw new Error(`Tema non trovato: ${slug}`);

// Il frontmatter è statico: il titolo del tab si imposta qui (SEO/tab).
document.title = theme.name;
```

```js
const datasets = theme.datasets
  .map((s) => catalog.datasets.find((d) => d.url_slug === s))
  .filter((d) => d && d.page_url);

// Il periodo è quello del catalogo ({start,end}), non una stringa da spaccare:
// un dataset senza periodo non produce NaN.
const periodi = datasets.map((d) => d.period).filter((p) => p && p.start && p.end);
// `source` (nome leggibile) non è più pubblicato da ACB per la maggior parte
// dei dataset: si ricade su `source_id`, che è sempre presente.
const sources = [...new Set(datasets.map((d) => d.source || d.source_id).filter(Boolean))];
```

# ${theme.name}

${theme.intro}

<div class="grid grid-cols-3">
  <div class="card">
    <h3>Dataset</h3>
    <span class="big">${datasets.length}</span>
  </div>
  <div class="card">
    <h3>Periodo</h3>
    <span class="big">${periodi.length
      ? `${Math.min(...periodi.map((p) => Number(p.start)))}–${Math.max(...periodi.map((p) => Number(p.end)))}`
      : "—"}</span>
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
  ${datasets.map((d) => html`<div class="card">
    <h3><a href="${d.page_url}">${d.name}</a></h3>
    ${d.description
      ? html`<p style="opacity:0.7; font-size:0.9em">${d.description}</p>`
      : null}
    <p style="font-size:0.85em">${d.years} · ${d.published ? "✅ Pubblicato" : "🔬 Incubazione"}</p>
  </div>`)}
</div>`)
```

---

## Esplora per tema

```js
display(html`<ul>
  ${themes
    .filter((t) => t.slug !== theme.slug)
    .map((t) => html`<li><a href="/temi/${t.slug}">${t.name}</a></li>`)}
</ul>`)
```

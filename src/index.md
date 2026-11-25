---
title: DataCivicLab Explorer
description: "I dati pubblici italiani, puliti e pronti all'uso — dal IRPEF ai bandi ANAC, dalla spesa sanitaria ai progetti PNRR"
---

<style>

.hero {
  background: linear-gradient(135deg, var(--theme-background-alt) 0%, var(--theme-background) 100%);
  border: 1px solid var(--theme-background-alt);
  border-radius: 12px;
  padding: 2.5rem 2rem 2rem;
  margin-bottom: 1rem;
}

.hero h1 {
  margin-top: 0 !important;
  font-size: 1.85rem !important;
  line-height: 1.3;
}

.hero p {
  max-width: 640px;
  opacity: 0.8;
  line-height: 1.6;
  font-size: 1.05rem;
}

.hero-cta {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.55rem 1.4rem;
  color: #1b1e23;
  background: transparent;
  border: 2px solid var(--theme-foreground-focus);
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.92rem;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.hero-cta:hover {
  opacity: 0.85;
}

.spotlight-card {
  border-left: 3px solid var(--theme-foreground-focus);
  padding: 1rem 1.2rem;
  background: var(--theme-background-alt);
  border-radius: 0 8px 8px 0;
  transition: box-shadow 0.15s ease;
}

.spotlight-card:hover {
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.spotlight-card h4 {
  margin: 0 0 0.3rem;
  font-size: 1rem;
}

.spotlight-card .spotlight-hook {
  font-size: 0.92rem;
  opacity: 0.75;
  margin: 0 0 0.4rem;
  line-height: 1.45;
}

.spotlight-card .spotlight-badge {
  display: inline-block;
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  background: var(--theme-foreground-focus);
  color: var(--theme-background);
  opacity: 0.85;
  font-weight: 500;
}

.theme-card-icon {
  font-size: 1.5rem;
  margin-right: 0.4rem;
  vertical-align: middle;
}

.method-note {
  font-size: 0.88rem;
  opacity: 0.7;
  line-height: 1.6;
  max-width: 640px;
}

.catalog-count {
  font-size: 0.85rem;
  opacity: 0.7;
  margin: 0.2rem 0 1rem;
}

.catalog-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
}

.catalog-item {
  border: 1px solid var(--theme-background-alt);
  border-radius: 10px;
  padding: 1rem 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.catalog-item h3 {
  margin: 0;
  font-size: 1rem;
  line-height: 1.35;
}

.catalog-item h3 a {
  text-decoration: none;
}

.catalog-item h3 a:hover {
  text-decoration: underline;
}

.catalog-desc {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.45;
  opacity: 0.78;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.catalog-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.2rem 0.8rem;
  font-size: 0.8rem;
  opacity: 0.7;
  margin: 0;
}

.catalog-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin: 0.15rem 0 0;
}

.catalog-badge {
  font-size: 0.72rem;
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  border: 1px solid var(--theme-background-alt);
  white-space: nowrap;
}

.catalog-badge.ok {
  border-color: var(--theme-foreground-focus);
  color: var(--theme-foreground-focus);
}

.catalog-badge.muted {
  opacity: 0.7;
}

@media (max-width: 640px) {
  .catalog-list {
    grid-template-columns: 1fr;
  }
}

</style>

<div class="hero">
  <h1>I dati pubblici italiani, pronti all'uso</h1>
  <p>
    DataCivicLab raccoglie, pulisce e rende esplorabili i dati della pubblica
    amministrazione — da IRPEF a bandi ANAC, dalla spesa sanitaria ai progetti PNRR.
    Ogni dataset è un <strong>parquet pulito</strong>, interrogabile con DuckDB,
    pronto per analisi e visualizzazioni.
  </p>
  <button class="hero-cta" onclick="document.querySelector('[id*=tutti-i-dataset]')?.scrollIntoView({behavior:'smooth'})" style="display:inline-block;margin-top:1rem;padding:0.55rem 1.4rem;color:var(--theme-foreground);background:transparent;border:2px solid var(--theme-foreground-focus);border-radius:8px;font-weight:600;font-size:0.92rem;cursor:pointer">Esplora il catalogo →</button>
  <a class="hero-cta" href="/schede/" style="margin-left:0.5rem">Schede dataset →</a>
</div>

```js
const catalog = await FileAttachment("data/catalog.json").json();
const themes = await FileAttachment("data/themes.json").json();
```

```js
// Metriche calcolate dal catalogo
const publishedCount = catalog.published;
const totalRows = catalog.total_clean_rows;
const totalRowsLabel = totalRows >= 1e6 ? `${(totalRows / 1e6).toFixed(1)}M` : totalRows >= 1e3 ? `${(totalRows / 1e3).toFixed(0)}K` : totalRows;
const themeCount = themes.length;
const allYears = catalog.datasets.flatMap(d => d.period ? [d.period.start, d.period.end].filter(Boolean) : []);
const yearMin = Math.min(...allYears);
const yearMax = Math.max(...allYears);
```

<div class="grid grid-cols-4">
  <div class="card"><h3>Dataset pubblicati</h3><span class="big">${publishedCount}</span></div>
  <div class="card"><h3>Righe pulite</h3><span class="big">${totalRowsLabel}</span></div>
  <div class="card"><h3>Temi</h3><span class="big">${themeCount}</span></div>
  <div class="card"><h3>Copertura</h3><span class="big">${yearMin}–${yearMax}</span></div>
</div>

---

## Inizia da qui

```js
const spotlights = [
  {
    slug: "irpef-comunale",
    title: "IRPEF — quanto reddito si dichiara in ogni territorio",
    hook: "A Milano si dichiara il doppio che a Palermo. Come si distribuisce il reddito italiano?",
    theme: "Finanza pubblica",
  },
  {
    slug: "anac-bandi-gara",
    title: "Bandi di gara pubblici ANAC",
    hook: "10 anni di appalti: da 167 a 635 miliardi. Il Codice Appalti 2023 ha semplificato o frammentato?",
    theme: "Finanza pubblica",
  },
  {
    slug: "pnrr-progetti",
    title: "PNRR Progetti — Italia Domani",
    hook: "280mila progetti e 150 miliardi del Piano. Dove stanno finendo i soldi del PNRR?",
    theme: "Finanza pubblica",
  },
  {
    slug: "cinque-per-mille",
    title: "5x1000 — beneficiari e importi per ente",
    hook: "€601 milioni record nel 2025. A chi vanno i soldi del 5x1000?",
    theme: "Terzo settore",
  },
];
```

```js
display(html`<div class="grid grid-cols-2">
  ${spotlights.map(s => html`<a href="/dataset/${s.slug}" class="spotlight-card" style="text-decoration:none; color:inherit;">
    <h4>${s.title}</h4>
    <p class="spotlight-hook">${s.hook}</p>
    <span class="spotlight-badge">${s.theme}</span>
  </a>`)}
</div>`)
```

---

## Temi

```js
display(html`<div class="grid grid-cols-2">
  ${themes.map(t => html`<div class="card">
    <h3><a href="/temi/${t.slug}"><span class="theme-card-icon">${t.icon || ""}</span>${t.name}</a></h3>
    <p style="opacity:0.7; font-size:0.9em">${t.description}</p>
    <p style="font-size:0.85em; opacity:0.6">${t.datasets.length} dataset</p>
  </div>`)}
</div>`)
```

---

## Tutti i dataset

```js
const searchQuery = view(Inputs.search(catalog.datasets, {label: "Cerca", placeholder: "nome, descrizione, fonte…"}));
```

```js
const themeNames = ["Tutti i temi", ...themes.map((t) => t.name)];
const themeFilter = view(Inputs.select(themeNames, {label: "Tema", value: "Tutti i temi"}));
```

```js
const stageFilter = view(Inputs.select(
  ["Tutti", "Pubblicati", "In incubazione"],
  {label: "Stato", value: "Tutti"}
));
```

```js
const limit = view(Inputs.select([24, 48, 96], {label: "Mostra", value: 24}));
```

```js
const themeSlug = themeFilter === "Tutti i temi" ? null : themes.find((t) => t.name === themeFilter)?.slug;
const filtered = searchQuery
  .filter((d) => !themeSlug || d.theme === themeSlug)
  .filter((d) => stageFilter === "Tutti" || d.published === (stageFilter === "Pubblicati"))
  .sort((a, b) => a.name.localeCompare(b.name, "it"));
const shown = filtered.slice(0, limit);
```

```js
display(html`<p class="catalog-count">
  ${filtered.length} dataset${filtered.length > shown.length ? ` · mostrati ${shown.length}` : ""}
</p>
${shown.length
  ? html`<div class="catalog-list">
      ${shown.map((d) => html`<article class="catalog-item">
        <h3>${d.page_url ? html`<a href="${d.page_url}">${d.name}</a>` : d.name}</h3>
        <p class="catalog-desc">${d.description || "Descrizione non disponibile."}</p>
        <p class="catalog-meta">
          ${d.theme_name ? html`<span>${d.theme_name}</span>` : ""}
          ${d.years && d.years !== "?" ? html`<span>${d.years}</span>` : ""}
          ${d.source ? html`<span>${d.source}</span>` : ""}
        </p>
        <p class="catalog-badges">
          <span class="catalog-badge ${d.published ? "ok" : "muted"}">${d.published ? "Pubblicato" : "In incubazione"}</span>
          ${d.has_card ? html`<span class="catalog-badge muted">Scheda</span>` : ""}
          ${d.has_page ? html`<span class="catalog-badge muted">Pagina</span>` : ""}
        </p>
      </article>`)}
    </div>`
  : html`<p><em>Nessun dataset con questi filtri.</em></p>`}`);
```

<div style="margin-top: 2em; opacity: 0.5; font-size: 0.85em;">
Catalogo aggiornato: ${catalog.updated_at}
</div>

---

<div class="method-note">

## Come funzionano i dati

Ogni dataset parte da una **fonte governativa pubblica** (MEF, ANAC, ISTAT, Terna, Ministero della Salute, …). I **data loader Python** leggono i parquet da Google Cloud Storage via DuckDB, calcolano le metriche a build-time e producono JSON aggregato per le visualizzazioni.

Le pipeline sono open source: [dataset-incubator](https://github.com/dataciviclab/dataset-incubator) · [CONTRIBUTING.md](https://github.com/dataciviclab/data-explorer/blob/main/CONTRIBUTING.md)

</div>

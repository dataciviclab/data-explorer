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
const searchQuery = view(Inputs.search(catalog.datasets, {label: "Cerca per nome, descrizione o fonte…"}));
```

```js
const stageFilter = view(Inputs.select(
  ["Tutti", "published", "incubating"],
  {label: "Filtra per stato", value: "Tutti"}
));
```

```js
const repoList = ["Tutte", ...new Set(catalog.datasets.map(d => d.registry_source).filter(Boolean))].sort();
const repoFilter = view(Inputs.select(
  repoList,
  {label: "Filtra per repository", value: "Tutte"}
));
```

```js
const filtered = searchQuery
  .filter(d => stageFilter === "Tutti" || d.stage === stageFilter)
  .filter(d => repoFilter === "Tutte" || d.registry_source === repoFilter);
```

```js
Inputs.table(filtered, {
  columns: ["slug", "name", "description", "stage", "years", "source"],
  header: {slug: "ID", name: "Nome", description: "Descrizione", stage: "Stato", years: "Anni", source: "Fonte"},
  format: {
    stage: d => d === "published" ? "✅ Pubblicato" : "🔬 Incubazione",
    description: d => d && d.length > 80 ? d.slice(0, 80) + "…" : d,
  },
  sort: "slug",
  rows: 30,
  width: "100%",
})
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

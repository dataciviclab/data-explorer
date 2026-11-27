---
title: "Language demo"
toc: false
footer: false
---

<style>
  #observablehq-center, #observablehq-main { margin: 0 auto; padding: 0; max-width: 760px; }
  body { max-width: none; }
  .lang-switch { font-size: 13px; }
</style>

<p><a href="/en/">← Home</a> · <a href="/en/prova-i18n">English</a> · <a href="/prova-i18n" hreflang="it" lang="it">Italiano</a></p>

# Public data, in English

This page and its Italian version are **two files**, not one page with a runtime
translator. The text lives in the file; the numbers come from the same data.

- The path changes: `/prova-i18n` and `/en/prova-i18n`.
- Both are static: no JavaScript picks the language.
- The link between them is `<a hreflang="it">`, the only thing a search engine
  uses to know they are the same page.

| What | IT | EN |
|---|---|---|
| file | `src/prova-i18n.md` | `src/en/prova-i18n.md` |
| URL | `/prova-i18n` | `/en/prova-i18n` |
| `<html lang>` | from post-processing | from post-processing |
| data | **shared**: one loader, one `FileAttachment` | same |

```js
// Proof that data is not duplicated: same file, but the path is resolved
// relative to the page — from `src/en/` it needs `../data/`.
const catalog = await FileAttachment("../data/catalog.json").json();
display(html`<p><strong>${catalog.datasets.length}</strong> datasets in the catalog (read from <code>data/catalog.json</code>).</p>`);
```

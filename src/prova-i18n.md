---
title: "Prova bilinguismo"
toc: false
footer: false
---

<style>
  #observablehq-center, #observablehq-main { margin: 0 auto; padding: 0; max-width: 760px; }
  body { max-width: none; }
  .lang-switch { font-size: 13px; }
</style>

<p><a href="/">← Home</a> · <a href="/en/prova-i18n" hreflang="en" lang="en">English</a> · <a href="/prova-i18n">Italiano</a></p>

# Dati pubblici, in italiano

Questa pagina e la sua versione inglese sono **due file**, non una pagina con un
traduttore a runtime. Il testo sta nel file, i numeri arrivano dallo stesso dato.

- Il path cambia: `/prova-i18n` e `/en/prova-i18n`.
- Il contenuto è statico in entrambe: nessun JavaScript per scegliere la lingua.
- Il collegamento fra le due è `<a hreflang="en">`, l'unica cosa che un motore di
  ricerca usa per capire che sono la stessa pagina.

| Cosa | IT | EN |
|---|---|---|
| file | `src/prova-i18n.md` | `src/en/prova-i18n.md` |
| URL | `/prova-i18n` | `/en/prova-i18n` |
| `lang` di `<html>` | da post-processing | da post-processing |
| dati | **gli stessi**: un loader, un `FileAttachment` | idem |

```js
// Prova che i dati non si duplicano: lo stesso FileAttachment, dalla cartella en.
const catalog = await FileAttachment("data/catalog.json").json();
display(html`<p><strong>${catalog.datasets.length}</strong> dataset nel catalogo (letto da <code>data/catalog.json</code>).</p>`);
```

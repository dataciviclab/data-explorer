---
title: "Schede dataset (pilota)"
toc: false
---

```js
const cards = await FileAttachment("../data/cards.json").json();
const list = Object.values(cards).sort((a, b) => a.name.localeCompare(b.name, "it"));
```

# Schede dataset — pilota

Schede **generate** da catalogo + mart: nessun data loader, nessuna query a GCS durante il build. Il modello è descritto in `docs/dataset-card.md`.

```js
display(
  list.length
    ? html`<ul>${list.map(
        (card) => html`<li>
          <a href="/schede/${card.url_slug}">${card.name}</a>
          ${card.published ? "" : " · in incubazione"}
          ${card.series.length ? ` · ${card.series[0].x}–${card.series[card.series.length - 1].x}` : ""}
        </li>`
      )}</ul>`
    : html`<p>Nessuna scheda generata. Esegui <code>npm run cards</code> e ricarica.</p>`
);
```

---

Le pagine curate esistenti restano su `/dataset/*`: questo pilota **non le sostituisce**.

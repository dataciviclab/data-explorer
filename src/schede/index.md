---
title: "Schede dataset (pilota)"
toc: false
---

```js
const cards = await FileAttachment("../data/cards.json").json();
const list = Object.values(cards).sort((a, b) => a.name.localeCompare(b.name, "it"));

// Il periodo si legge dal primo blocco con un asse temporale (series/composition).
const span = (card) => {
  const block = (card.blocks || []).find((b) => b.type === "series" || b.type === "composition");
  const data = block?.data || [];
  return data.length ? ` · ${data[0].x}–${data[data.length - 1].x}` : "";
};
```

# Schede dataset — pilota

Schede **generate** da catalogo + mart: nessun data loader, nessuna query a GCS durante il build. Il modello è descritto in `docs/dataset-card.md`.

```js
display(
  list.length
    ? html`<ul>${list.map(
        (card) => html`<li>
          <a href="/schede/${card.url_slug}">${card.name}</a>
          ${card.published ? "" : " · in incubazione"}${span(card)}
        </li>`
      )}</ul>`
    : html`<p>Nessuna scheda generata. Esegui <code>npm run cards</code> e ricarica.</p>`
);
```

---

Le pagine curate esistenti restano su `/dataset/*`: questo pilota **non le sostituisce**.

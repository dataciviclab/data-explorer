---
title: "Prova tema e URL"
toc: false
footer: false
head: '<script>try{const s=localStorage.getItem("de-theme");const t=s||(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light");document.documentElement.dataset.theme=t}catch(e){}</script>'
---

<style>
  /* Token nostri, due valori. Il tema non è un file CSS diverso: è un attributo
     sull'elemento <html>, scritto prima del paint dallo script in `head:`. */
  :root {
    --dl-bg: #fbfaf7; --dl-surface: #ffffff; --dl-ink: #14181d;
    --dl-muted: #5b6470; --dl-line: #e3e0d8; --dl-accent: #1d4ed8;
  }
  :root[data-theme="dark"] {
    --dl-bg: #0f1319; --dl-surface: #161c24; --dl-ink: #e8edf3;
    --dl-muted: #93a1b1; --dl-line: #232c37; --dl-accent: #6ea0ff;
  }
  #observablehq-center, #observablehq-main { margin: 0; padding: 0; max-width: none; }
  body { max-width: none; background: var(--dl-bg); color: var(--dl-ink); }
  a[href] { color: inherit; }
  h1, h2, h3 { color: inherit; }

  .box { max-width: 880px; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }
  .bar { display: flex; align-items: center; gap: 1rem; padding: 0.8rem 1.5rem; background: var(--dl-surface); border-bottom: 1px solid var(--dl-line); }
  .bar strong { font-size: 14px; }
  .toggle { margin-left: auto; border: 1px solid var(--dl-line); background: transparent; color: var(--dl-ink); border-radius: 6px; padding: 0.35rem 0.7rem; font: inherit; font-size: 13px; cursor: pointer; }
  .card { background: var(--dl-surface); border: 1px solid var(--dl-line); border-radius: 10px; padding: 1.1rem; margin: 1rem 0; }
  .card h3 { margin: 0 0 0.4rem; font-size: 1rem; }
  .card p { margin: 0; color: var(--dl-muted); font-size: 13.5px; }
  .muted { color: var(--dl-muted); font-size: 13.5px; }
</style>

<div class="bar">
  <strong>Prova tema</strong>
  <button class="toggle" id="theme-toggle">Cambia tema</button>
</div>

<div class="box">

# Due temi, un solo CSS

I token sono definiti due volte (`:root` e `:root[data-theme="dark"]`). Lo switch
è un attributo su `<html>` più `localStorage` — nessun ricaricamento, nessun
secondo stylesheet.

<div class="card">
  <h3>Perché funziona anche sui grafici</h3>
  <p>Se i colori dei grafici sono token e non hex, il tema li cambia insieme al
  resto. Sotto: barre riempite con <code>var(--dl-accent)</code>.</p>
</div>

```js
import * as Plot from "npm:@observablehq/plot";

const fonti = [
  { fonte: "Gas naturale", twh: 121.5 },
  { fonte: "Idroelettrico", twh: 40.2 },
  { fonte: "Fotovoltaico", twh: 36.1 },
  { fonte: "Carbone", twh: 12.4 },
];

display(
  Plot.plot({
    height: 220,
    marginLeft: 110,
    style: { background: "transparent", color: "var(--dl-ink)", fontSize: "12px" },
    x: { grid: true, label: "TWh", domain: [0, 145] },
    y: { label: null },
    marks: [
      Plot.barX(fonti, { y: "fonte", x: "twh", fill: "var(--dl-accent)", rx: 3 }),
      Plot.text(fonti, { y: "fonte", x: "twh", text: (d) => d.twh.toFixed(1), dx: 6, textAnchor: "start" }),
    ],
  })
);
```

```js
// Lo switch: un listener, nessuna dipendenza.
const btn = document.getElementById("theme-toggle");
if (btn) {
  const sync = () => {
    btn.textContent = document.documentElement.dataset.theme === "dark" ? "Tema chiaro" : "Tema scuro";
  };
  sync();
  btn.addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("de-theme", next); } catch {}
    sync();
    // I grafici sono già renderizzati: i colori passano da CSS var, quindi
    // cambiano da soli. Nessun re-render necessario.
  });
}
```

<p class="muted">Il tema iniziale è deciso in `head:`, prima del paint: nessun lampo bianco al caricamento.</p>

</div>

---
title: "Prova shell"
toc: false
footer: false
header: '<div class="lab-bar"><span class="lab-mark">◆</span><strong>DataCivicLab</strong><nav><a href="/">Temi</a><a href="/progetti/">Progetti</a><a href="/schede/">Schede</a><a href="/docs/">Docs</a><a href="/chi-siamo">Chi siamo</a></nav></div>'
---

<style>
  /* Shell alternativa per UNA pagina: sidebar fuori, barra di brand, hero a tutta larghezza */
  #observablehq-sidebar { display: none; }
  #observablehq-sidebar-toggle, #observablehq-sidebar-backdrop { display: none; }
  body { max-width: none; }
  :root { --observablehq-inset-left: 0rem; --observablehq-max-width: 100vw; }
  #observablehq-center { margin: 0; }
  /* L'inset laterale non viene dalla sidebar ma dallo stato del toggle:
     va azzerato per ogni stato, altrimenti restano 288px vuoti a sinistra. */
  #observablehq-center,
  #observablehq-sidebar-toggle:checked ~ #observablehq-center,
  #observablehq-sidebar-toggle:indeterminate ~ #observablehq-center {
    --observablehq-inset-left: 0rem;
    --observablehq-inset-right: 0rem;
    padding-left: 0;
    padding-right: 0;
  }
  #observablehq-main { max-width: none; margin: 0; padding: 0; }
  /* Con l'header in flow l'offset del framework non serve più */
  #observablehq-header ~ #observablehq-main { margin-top: 0; }
  #observablehq-header { position: static; margin: 0; padding: 0; background: #0e1117; border: 0; height: auto; }
  #observablehq-footer { display: none; }
  .lab-bar { display: flex; align-items: center; gap: 1rem; padding: 0.8rem 2rem; color: #e2e8f0; font-family: var(--sans-serif); }
  .lab-bar strong { font-size: 15px; font-weight: 600; }
  .lab-bar .lab-mark { color: #60a5fa; }
  .lab-bar nav { display: flex; gap: 1.2rem; margin-left: auto; font-size: 14px; }
  .lab-bar nav a { color: #94a3b8; text-decoration: none; }
  .lab-bar nav a:hover { color: #ffffff; }
  .hero { background: #0e1117; color: #e2e8f0; padding: 5rem 2rem 4rem; }
  .hero h1 { font-size: 3rem; line-height: 1.05; margin: 0 0 1rem; color: #ffffff; max-width: 820px; }
  .hero p { font-size: 1.15rem; color: #94a3b8; max-width: 640px; margin: 0 0 2rem; }
  .hero .cta { display: inline-block; background: #2563eb; color: #fff; padding: 0.7rem 1.1rem; border-radius: 6px; text-decoration: none; font-family: var(--sans-serif); font-weight: 600; }
  .strip { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; padding: 2rem; max-width: 1200px; margin: 0 auto; }
  .strip div { border: 1px solid var(--theme-foreground-faintest); border-radius: 10px; padding: 1rem; }
  .strip span { display: block; font-size: 1.6rem; font-weight: 600; }
  .shell-wrap { max-width: 1120px; margin: 0 auto; padding: 3rem 2rem; }
  .shell-wrap h2 { font-size: 1.6rem; margin-top: 0; }
  .shell-wrap .cols { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 2rem; align-items: start; }
  .note-box { background: var(--theme-background-alt); border-left: 3px solid #2563eb; padding: 1rem 1.2rem; border-radius: 0 8px 8px 0; font-size: 0.95rem; }
</style>

<div class="hero">
  <h1>I dati pubblici italiani, senza intermediari</h1>
  <p>Una shell diversa sulla stessa pagina: barra di brand, hero a tutta larghezza, niente sidebar. Nessuna modifica al framework.</p>
  <a class="cta" href="/progetti/">Esplora i progetti</a>
</div>

<div class="strip">
  <div><span>561</span>dataset nel catalogo</div>
  <div><span>46</span>dataset pubblicati</div>
  <div><span>43</span>progetti</div>
  <div><span>7</span>temi</div>
</div>

<div class="shell-wrap">
  <h2>Cosa resta del framework sotto una shell diversa</h2>
  <div class="cols">
    <div>

Questa è una pagina Markdown normale: titoli, liste, tabelle, blocchi `js` e
caricamenti `FileAttachment` funzionano identici, perché cambia solo il CSS che
avvolge `#observablehq-center`.

| Cosa | Come |
|---|---|
| Sidebar | nascosta con una regola CSS |
| Header | frontmatter `header:` — HTML nostro |
| Larghezza | `--observablehq-max-width` a `100vw` |
| Contenuti | un `.shell-wrap` centrato a 1120px |

    </div>
    <div class="note-box">
      <strong>Il costo</strong><br>
      Questa pagina perde la nav laterale e il toc. È una scelta editoriale
      legittima per una home o una landing, non per 111 pagine.
    </div>
  </div>
</div>

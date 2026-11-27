---
title: "Prova top nav"
toc: false
footer: false
---

<style>
  /* ═══ Livello 3: la sidebar di OF diventa una barra orizzontale ═══
     Nessun markup nuovo: si riusa l'albero <ol>/<details> che OF genera dai
     `pages` del config, e la ricerca incorporata resta al suo posto. */

  /* 1. Il corpo esce dal contenitore centrato a 1440px */
  body { max-width: none; }
  :root { --observablehq-max-width: 100vw; }

  /* 2. La sidebar smette di essere un cassetto: la stato del cassetto è
        guidato da #observablehq-sidebar-toggle (checkbox + JS), quindi ogni
        variante di quello stato va riallineata alla stessa regola. */
  #observablehq-sidebar,
  #observablehq-sidebar:focus-within,
  #observablehq-sidebar-toggle:checked ~ #observablehq-sidebar,
  #observablehq-sidebar-toggle:indeterminate ~ #observablehq-sidebar {
    position: sticky;
    top: 0;
    left: auto;
    bottom: auto;
    width: 100%;
    height: auto;
    visibility: visible;
    box-shadow: none;
    overflow: visible;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.25rem 1.1rem;
    padding: 0.55rem 1.5rem;
    background: #0e1117;
    color: #94a3b8;
    font: 500 14px var(--sans-serif);
    z-index: 6;
    --observablehq-sidebar-padding-left: 0rem;
  }
  #observablehq-sidebar-toggle,
  #observablehq-sidebar-backdrop,
  #observablehq-sidebar-close { display: none; }

  /* 3. Le sezioni diventano voci di menu, non blocchi impilati */
  #observablehq-sidebar > ol,
  #observablehq-sidebar > details,
  #observablehq-sidebar > section {
    margin: 0;
    padding: 0;
    border: 0;
    position: relative;
  }
  #observablehq-sidebar > ol:first-child {
    position: static;
    font-size: 14px;
    padding: 0;
  }
  #observablehq-sidebar > ol:first-child::before { display: none; }
  #observablehq-sidebar > ol:first-child > li > a {
    height: auto;
    color: #ffffff;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
  }
  /* Il marchio entra nello slot "home", l'unico che OF riserva al brand */
  #observablehq-sidebar > ol:first-child > li > a::before {
    content: "◆";
    color: #60a5fa;
    font-size: 15px;
  }

  /* 4. I sottomenu si aprono come tendine ancorate alla voce */
  #observablehq-sidebar details > ol,
  #observablehq-sidebar section > ol {
    position: absolute;
    top: calc(100% + 0.55rem);
    left: -0.75rem;
    min-width: 260px;
    max-height: 70vh;
    overflow-y: auto;
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 0.5rem;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
    z-index: 10;
  }
  #observablehq-sidebar section > ol { display: none; }
  #observablehq-sidebar section:hover > ol,
  #observablehq-sidebar section:focus-within > ol { display: block; }
  #observablehq-sidebar summary { color: #cbd5e1; cursor: pointer; font-weight: 600; }
  #observablehq-sidebar details summary::after { display: none; }
  #observablehq-sidebar li a { color: #94a3b8; display: block; padding: 0.3rem 0.5rem; border-radius: 5px; }
  #observablehq-sidebar li a:hover { background: #1f2937; color: #ffffff; }
  #observablehq-sidebar li.observablehq-link-active > a { color: #ffffff; background: #1d4ed8; }

  /* 5. La ricerca resta quella di OF, spostata a destra della barra */
  #observablehq-search { order: 99; margin-left: auto; }
  #observablehq-search input {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 6px;
    color: #e2e8f0;
    padding: 0.3rem 0.6rem;
    width: 200px;
  }
  #observablehq-search-results:not(:empty) {
    position: absolute;
    right: 1.5rem;
    top: calc(100% + 0.4rem);
    width: 420px;
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 0.5rem;
  }

  /* 6. Il contenuto si riprende lo spazio che il cassetto riservava */
  #observablehq-center { margin: 0; }
  #observablehq-main { padding: 2rem 1.5rem 4rem; }
  @media (min-width: calc(640px + 6rem + 272px)) {
    #observablehq-sidebar-toggle:checked ~ #observablehq-center,
    #observablehq-sidebar-toggle:indeterminate ~ #observablehq-center {
      --observablehq-inset-left: 0rem;
      --observablehq-inset-right: 0rem;
      padding-left: 0;
      padding-right: 0;
    }
  }

  /* 7. Niente `header:` in questa pagina: il brand sta nello slot "home",
        l'unico che OF riserva al titolo. Una barra, non due. */
  .wrap { max-width: 1080px; margin: 0 auto; }
</style>

<div class="wrap">

# La stessa pagina, con la nav in alto

La sidebar di Observable non è un componente separato: è un `<nav>` generato dai
`pages` del config, con dentro `<ol>`, `<details>` e `<summary>`. Qui non è stata
sostituita — è stata **riletta come barra orizzontale**: le voci restano quelle
generate, la ricerca resta quella del framework, i sottomenu diventano tendine.

- **Nessun markup nuovo**: il DOM è quello di OF.
- **Nessun JS nuovo**: lo stato del cassetto è una checkbox, ignorata da queste regole.
- **La ricerca funziona**: l'indice è ancora quello costruito al build.

> Il limite è che questo è CSS di pagina, non configurazione. Vale per una pagina
> o per tutte, ma va mantenuto a mano quando il framework cambia le sue regole.

</div>

---
title: "Prova layout custom"
toc: false
footer: false
---

<style>
  /* ══════════════════════════════════════════════════════════════════
     RESET — le uniche 3 regole che parlano di OF. Da mettere una volta
     in src/style.css, non per pagina. Con sidebar:false non c'è altro
     da neutralizzare: niente cassetto, niente inset, niente toc.
     ══════════════════════════════════════════════════════════════════ */
  #observablehq-center,
  #observablehq-main { margin: 0; padding: 0; max-width: none; }
  body { max-width: none; }
  /* Solo finché la sidebar globale è accesa: con `sidebar: false` queste righe
     non servono e si cancellano. */
  #observablehq-sidebar,
  #observablehq-sidebar-toggle,
  #observablehq-sidebar-backdrop { display: none; }
  #observablehq-sidebar-toggle:checked ~ #observablehq-center,
  #observablehq-sidebar-toggle:indeterminate ~ #observablehq-center {
    --observablehq-inset-left: 0rem; padding-left: 0;
  }

  /* Base tipografica: global.css usa selettori con attributo (a[href]) che
     battono una classe. Quattro righe riportano gli elementi a "neutro";
     da qui in poi vincono i nostri selettori, senza !important. */
  a[href] { color: inherit; }
  h1, h2, h3, h4 { color: inherit; }

  /* ══════════════════════════════════════════════════════════════════
     DESIGN — tutto nostro. Nessun selettore #observablehq-*.
     ══════════════════════════════════════════════════════════════════ */
  :root {
    --dl-bg: #fbfaf7;
    --dl-ink: #14181d;
    --dl-muted: #5b6470;
    --dl-line: #e3e0d8;
    --dl-accent: #1d4ed8;
    --dl-dark: #10141a;
    --dl-max: 1180px;
    --dl-pad: 1.5rem;
  }
  body { background: var(--dl-bg); color: var(--dl-ink); font-family: var(--sans-serif); }

  /* header */
  .dl-header {
    position: sticky; top: 0; z-index: 20;
    background: var(--dl-dark); color: #cfd6df;
  }
  .dl-header__inner {
    max-width: var(--dl-max); margin: 0 auto; padding: 0.85rem var(--dl-pad);
    display: flex; align-items: center; gap: 2rem;
  }
  .dl-brand { display: inline-flex; align-items: center; gap: 0.5rem; color: #fff; font-weight: 700; font-size: 15px; text-decoration: none; }
  .dl-brand svg { width: 20px; height: 20px; }
  .dl-menu { display: flex; gap: 1.4rem; margin: 0; padding: 0; list-style: none; font-size: 14px; }
  .dl-menu a { color: #a9b4c2; text-decoration: none; }
  .dl-menu a:hover, .dl-menu a[aria-current] { color: #fff; }

  /* hero */
  .dl-hero { background: var(--dl-dark); color: #fff; padding: 4.5rem 0 3.5rem; }
  .dl-hero__inner { max-width: var(--dl-max); margin: 0 auto; padding: 0 var(--dl-pad); display: grid; grid-template-columns: 1.35fr 0.65fr; gap: 3rem; align-items: end; }
  .dl-hero h1 { font-size: clamp(2.2rem, 4vw, 3.3rem); line-height: 1.04; margin: 0 0 1.1rem; letter-spacing: -0.02em; color: #fff; }
  .dl-hero p { color: #a9b4c2; font-size: 1.06rem; max-width: 34em; margin: 0 0 1.8rem; }
  .dl-actions { display: flex; gap: 0.7rem; flex-wrap: wrap; }
  .dl-btn { display: inline-block; padding: 0.6rem 1.05rem; border-radius: 6px; font-size: 14px; font-weight: 600; text-decoration: none; }
  .dl-btn--primary { background: #2f6bff; color: #fff; }
  .dl-btn--ghost { border: 1px solid #33404f; color: #dfe6ef; }

  /* kpi */
  .dl-kpis { max-width: var(--dl-max); margin: -1.8rem auto 0; padding: 0 var(--dl-pad); position: relative; display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
  .dl-kpi { background: #fff; border: 1px solid var(--dl-line); border-radius: 10px; padding: 1rem 1.1rem; }
  .dl-kpi b { display: block; font-size: 1.5rem; letter-spacing: -0.02em; }
  .dl-kpi span { font-size: 12.5px; color: var(--dl-muted); }

  /* sezioni */
  .dl-section { max-width: var(--dl-max); margin: 0 auto; padding: 3.2rem var(--dl-pad) 0; }
  .dl-section__head { display: flex; align-items: baseline; gap: 1rem; margin-bottom: 1.3rem; }
  .dl-section__head h2 { font-size: 1.35rem; margin: 0; }
  .dl-section__head a { margin-left: auto; font-size: 13px; color: var(--dl-accent); text-decoration: none; }

  /* card */
  .dl-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
  .dl-card { display: flex; flex-direction: column; gap: 0.55rem; background: #fff; border: 1px solid var(--dl-line); border-radius: 12px; padding: 1.15rem; text-decoration: none; color: inherit; }
  .dl-card:hover { border-color: #c9c3b6; }
  .dl-card__tag { font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--dl-accent); font-weight: 600; }
  .dl-card h3 { font-size: 1.02rem; margin: 0; line-height: 1.25; }
  .dl-card p { margin: 0; font-size: 13.5px; color: var(--dl-muted); }
  .dl-card__meta { margin-top: auto; font-size: 12px; color: #8b929c; display: flex; gap: 0.8rem; }

  /* passi */
  .dl-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
  .dl-step { border-top: 2px solid var(--dl-ink); padding-top: 0.8rem; }
  .dl-step b { display: block; font-size: 13px; color: var(--dl-accent); margin-bottom: 0.3rem; }
  .dl-step p { margin: 0; font-size: 13.5px; color: var(--dl-muted); }

  /* tabella dati (renderizzata da JS dentro il nostro layout) */
  .dl-table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
  .dl-table th { text-align: left; font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--dl-muted); border-bottom: 1px solid var(--dl-line); padding: 0.4rem 0.5rem; }
  .dl-table td { padding: 0.45rem 0.5rem; border-bottom: 1px solid #efede7; }
  .dl-table td:last-child, .dl-table th:last-child { text-align: right; font-variant-numeric: tabular-nums; }

  /* footer */
  .dl-footer { background: var(--dl-dark); color: #8f9aa8; margin-top: 3.5rem; }
  .dl-footer__inner { max-width: var(--dl-max); margin: 0 auto; padding: 2.4rem var(--dl-pad); display: grid; grid-template-columns: 1.4fr repeat(3, 1fr); gap: 2rem; font-size: 13px; }
  .dl-footer h4 { color: #fff; font-size: 12px; text-transform: uppercase; letter-spacing: 0.07em; margin: 0 0 0.7rem; }
  .dl-footer ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.4rem; }
  .dl-footer a { color: #8f9aa8; text-decoration: none; }
  .dl-footer a:hover { color: #fff; }
  .dl-footer__bottom { border-top: 1px solid #1d232c; font-size: 12px; padding: 0.9rem var(--dl-pad); max-width: var(--dl-max); margin: 0 auto; display: flex; gap: 1rem; }

  @media (max-width: 900px) {
    .dl-hero__inner { grid-template-columns: 1fr; gap: 1.5rem; }
    .dl-kpis { grid-template-columns: repeat(2, 1fr); margin-top: 1rem; }
    .dl-cards, .dl-steps { grid-template-columns: 1fr; }
    .dl-footer__inner { grid-template-columns: 1fr 1fr; }
    .dl-menu { display: none; }
  }
</style>

<header class="dl-header">
  <div class="dl-header__inner">
    <a class="dl-brand" href="./">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l7 10-7 10L5 12z" fill="#2f6bff"/></svg>
      DataCivicLab
    </a>
    <nav>
      <ul class="dl-menu">
        <li><a href="./" aria-current="page">Home</a></li>
        <li><a href="./temi/finanza-pubblica">Temi</a></li>
        <li><a href="./progetti/">Progetti</a></li>
        <li><a href="./schede/">Schede</a></li>
        <li><a href="./dataset/bdap-spese-stato">Dati</a></li>
      </ul>
    </nav>
  </div>
</header>

<section class="dl-hero">
  <div class="dl-hero__inner">
    <div>
      <h1>I dati pubblici italiani, uno per uno</h1>
      <p>561 dataset ricostruiti dalle fonti originali, 46 con una lettura guidata, 43 progetti. Nessuna intermediazione, ogni numero è ricostruibile.</p>
      <div class="dl-actions">
        <a class="dl-btn dl-btn--primary" href="./progetti/">Esplora i progetti</a>
        <a class="dl-btn dl-btn--ghost" href="./schede/">Leggi le schede</a>
      </div>
    </div>
    <div class="dl-hero__col">
      <div class="dl-kpi" style="background:#161c24;border-color:#232c37">
        <b style="color:#fff">14</b><span style="color:#8f9aa8">fonti monitorate ogni notte</span>
      </div>
    </div>
  </div>
</section>

<div class="dl-kpis">
  <div class="dl-kpi"><b>561</b><span>dataset nel catalogo</span></div>
  <div class="dl-kpi"><b>46</b><span>con lettura guidata</span></div>
  <div class="dl-kpi"><b>43</b><span>progetti</span></div>
  <div class="dl-kpi"><b>7</b><span>temi</span></div>
</div>

<section class="dl-section">
  <div class="dl-section__head">
    <h2>In evidenza</h2>
    <a href="./progetti/">tutti i progetti →</a>
  </div>
  <div class="dl-cards">
    <a class="dl-card" href="./progetti/bilancio-pubblico">
      <span class="dl-card__tag">Finanza pubblica</span>
      <h3>I conti dello Stato</h3>
      <p>Spesa corrente, investimenti, entrate tributarie e saldi di bilancio dal 2003.</p>
      <div class="dl-card__meta"><span>18 dataset</span><span>2003–2027</span></div>
    </a>
    <a class="dl-card" href="./dataset/rna-aiuti-stato">
      <span class="dl-card__tag">Aiuti di Stato</span>
      <h3>Chi riceve gli aiuti pubblici</h3>
      <p>Il Registro Nazionale Aiuti letto per settore, territorio e dimensione d'impresa.</p>
      <div class="dl-card__meta"><span>1994–2025</span><span>mart</span></div>
    </a>
    <a class="dl-card" href="./dataset/terna-elettricita-per-fonte">
      <span class="dl-card__tag">Energia</span>
      <h3>Produzione elettrica per fonte</h3>
      <p>Quanta elettricità, da quale fonte, in ogni anno: il mix energetico italiano.</p>
      <div class="dl-card__meta"><span>263 TWh</span><span>2024</span></div>
    </a>
  </div>
</section>

<section class="dl-section">
  <div class="dl-section__head">
    <h2>Come funziona</h2>
  </div>
  <div class="dl-steps">
    <div class="dl-step"><b>01 · Fonte</b><p>Ogni dataset nasce da un portale pubblico verificato dal Source Observatory.</p></div>
    <div class="dl-step"><b>02 · Pipeline</b><p>Raw → clean → mart, con contratti di colonna e test. Nessun numero a mano.</p></div>
    <div class="dl-step"><b>03 · Lettura</b><p>Schede, analisi e progetti si generano dai dati, non da un foglio Excel.</p></div>
  </div>
</section>

<section class="dl-section">
  <div class="dl-section__head">
    <h2>I temi, misurati adesso</h2>
    <a href="./temi/finanza-pubblica">apri un tema →</a>
  </div>
  <div id="dl-themes"></div>
</section>

<footer class="dl-footer">
  <div class="dl-footer__inner">
    <div>
      <h4>DataCivicLab</h4>
      <p style="margin:0">Dati pubblici italiani, ricostruiti e documentati. Codice e dati aperti.</p>
    </div>
    <div>
      <h4>Esplora</h4>
      <ul><li><a href="./progetti/">Progetti</a></li><li><a href="./schede/">Schede</a></li><li><a href="./temi/finanza-pubblica">Temi</a></li></ul>
    </div>
    <div>
      <h4>Lab</h4>
      <ul><li><a href="https://dataciviclab.org/chi-siamo/">Chi siamo</a></li><li><a href="https://dataciviclab.org/docs/">Documentazione</a></li></ul>
    </div>
    <div>
      <h4>Dati</h4>
      <ul><li><a href="https://github.com/dataciviclab">GitHub</a></li><li><a href="https://dataciviclab.org/ecosistema/">Ecosistema</a></li></ul>
    </div>
  </div>
  <div class="dl-footer__bottom">
    <span>© 2026 DataCivicLab</span><span>CC BY-SA 4.0</span>
  </div>
</footer>

```js
// Un blocco dati vero dentro un layout nostro: il catalogo è un FileAttachment,
// il rendering è una tabella nostra. Nessun componente di OF è coinvolto.
//
// `mount` è l'unico ponte necessario: l'output di un blocco finisce in ordine di
// documento, quindi per metterlo DENTRO un <div> che abbiamo scritto serve
// agganciarlo. Tre righe, nessun hook del framework.
const mount = (selector, node) => document.querySelector(selector)?.replaceChildren(node);

const catalog = await FileAttachment("data/catalog.json").json();
const themes = await FileAttachment("data/themes.json").json();
const bySlug = new Map(catalog.datasets.map((d) => [d.url_slug, d]));

const rows = themes.map((t) => {
  const ds = t.datasets.map((s) => bySlug.get(s)).filter(Boolean);
  const published = ds.filter((d) => d.published).length;
  return {
    theme: t.name,
    datasets: ds.length,
    published,
    share: ds.length ? published / ds.length : 0,
  };
});

const table = html`<table class="dl-table">
  <thead><tr><th>Tema</th><th>Dataset</th><th>Con lettura</th><th>Copertura</th></tr></thead>
  <tbody>${rows.map((r) => html`<tr>
    <td><strong>${r.theme}</strong></td>
    <td>${r.datasets}</td>
    <td>${r.published}</td>
    <td>${(r.share * 100).toFixed(0)}%</td>
  </tr>`)}</tbody>
</table>`;

mount("#dl-themes", table);
```

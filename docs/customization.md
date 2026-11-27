# Personalizzare Observable Framework oltre la struttura nativa

Stato: **novembre 2026**, verificato sul build locale (112 pagine, ~30 s con cache
calda). Prototipi: `src/prova-*.md` — da cancellare prima del merge.

Per bilinguismo, tema, SEO, redirect e separazione build/dati vedi
`docs/platform.md`.

## Risposta breve

Tre modi, in ordine di costo crescente: **ristilizzare** (CSS), **sostituire la
shell di pagina** (CSS + HTML nostro), **spegnere la chrome** e costruire header,
nav e footer nostri (§5). Il terzo è l'unico che regge il redesign senza
accumulare override da mantenere.

## 1. Configurazione (stabile)

| Chiave | Note |
|---|---|
| `pages` | albero della sidebar **e generatore di pagine** (§4.4) |
| `dynamicPaths` | route `[slug]` |
| `header` / `footer` | HTML nostro, anche per pagina |
| `head` | `<head>` globale (`scripts` è deprecato) |
| `style` | sostituisce il CSS del tema: va importato `observablehq:default.css` |
| `globalStylesheets` | CSS aggiuntivo, si somma al tema |
| `sidebar` | `true`/`false`, **solo globale** |
| `search` | **spenta di default** (`null`) |
| `pager` / `toc` | anche nel frontmatter di pagina |
| `preserveIndex` / `preserveExtension` | forma dei file, non dei URL |

Frontmatter: `title`, `head`, `header`, `footer`, `toc`, `style`, `theme`.
Il markdown è reso con `html: true` (`markdown.js:134`): HTML e `<style>` in linea.

## 2. Il DOM che non cambia

```html
body
├── input#observablehq-sidebar-toggle     ← il cassetto È questa checkbox
├── nav#observablehq-sidebar              ← da `pages` (+ #observablehq-search)
└── div#observablehq-center
    ├── header#observablehq-header
    ├── aside#observablehq-toc
    ├── main#observablehq-main            ← il nostro contenuto
    └── footer#observablehq-footer
```

Variabili: `--observablehq-max-width`, `--observablehq-header-height`,
`--observablehq-inset-left/right`, `--observablehq-sidebar-padding-left`, più i
token `--theme-*`.

## 3. I tre livelli, in pratica

**A. Ristilizzare** — solo `style` + variabili. È quello che facciamo già.

**B. Shell di pagina** (`src/prova-shell.md`) — header nostro, hero full-bleed,
sidebar fuori. Il markdown, i blocchi `js` e `FileAttachment` non cambiano.

![Shell di pagina](_local/generated/screenshots/de-shell-pagina.png)

**C. Rileggere la sidebar** (`src/prova-topnav.md`) — la nav laterale diventa una
barra: voci e ricerca restano quelle generate. Si pagano i breakpoint del
framework e il mobile.

![Sidebar riletta come barra](_local/generated/screenshots/de-shell-topnav.png)

**D. Chrome nostra** — §5. È il livello che regge il redesign.

## 4. Limiti misurati

1. **L'inset non è la larghezza della sidebar.** Con `display:none` restano
   288 px a sinistra: lo spazio viene da `--observablehq-inset-left`, che i media
   query impostano in base allo stato della checkbox (`:checked`/`:indeterminate`,
   gestito da JS).
2. **Il markup della sidebar non si cambia**: `<ol>`, `<details>`, `<summary>`.
3. **Breakpoint del cassetto cablati**: `calc(640px + 6rem + 272px)` = 1008 px.
4. **`pages` genera pagine.** `config.paths()` (`config.js:118-137`) unisce file,
   `pages` e `dynamicPaths`: una voce di nav verso `[slug]` crea la pagina anche
   senza dati → build verde, errore nel browser. Misurato: la cache del catalogo
   (ferma al 26/11) teneva 4 schede di un altro branch, `buildSidebar` le metteva
   in «Altri dataset» → 4 pagine `/schede/*` rotte con exit 0. Cache invalidata:
   5 file invece di 9. **L'audit non lo vede**: legge la stessa cache.
5. **Niente redirect**, e i URL non hanno lo slash finale (`/x` → `x.html`).
6. **La ricerca è spenta di default**: `search: true` la accende (ora attiva).

## 5. Chrome nostra: `sidebar: false`

Verificato con `sidebar/pager/toc/search/footer: false`: spariscono `<nav>`,
toggle, backdrop, toc, pager e **l'inset di 288 px** (§4.1). Resta una scatola
sola, `div#observablehq-center > main#observablehq-main`.

Il CSS che parla di OF, contato, sono **6 regole** — una volta sola, senza
`!important`:

```css
#observablehq-center, #observablehq-main { margin: 0; padding: 0; max-width: none; }
body { max-width: none; }
a[href] { color: inherit; }          /* global.css usa a[href], non a */
h1, h2, h3, h4 { color: inherit; }   /* global.css stila i titoli */
```

`src/prova-custom.md` è il prototipo completo: header, nav, hero, KPI, griglia di
card, passi, tabella dati, footer. Un solo ponte: `mount(selector, node)`
(3 righe), perché l'output di un blocco va in ordine di documento e non dentro un
`<div>` scritto a mano.

![Layout interamente custom](_local/generated/screenshots/de-custom.png)

### Il prezzo: statico contro renderizzato

Parole nel `<main>` prima e dopo il JS, misurate:

| Pagina | Statico | Dopo JS | Quota |
|---|---|---|---|
| `prova-custom` (HTML + 1 cella) | 169 | 185 | **91%** |
| `dataset/bdap-spese-stato` (markdown + celle) | 352 | 831 | 42% |
| `progetti/bilancio-pubblico` (tutto componente) | 24 | 145 | **17%** |

Regola: struttura, titoli, numeri e tabelle **generati al build dentro il file**
(come `build_projects.py` fa già per titolo e meta); grafici e interazione in
celle. Mai tutto in un componente — è la pagina progetto di oggi, al 17%.

### Cosa dobbiamo possedere

| Pezzo | Come | Costo |
|---|---|---|
| nav | HTML generato al build dallo stesso array `pages` | 0 runtime |
| footer | idem, in `footer:` | 0 runtime |
| mobile | `<details>` nostro o ~20 righe di JS | basso |
| ricerca | indice snello (~50 KB) + pagina `/cerca` | 1 pomeriggio |
| toc | opzionale, solo dove serve | basso |

Il guadagno: **nessun selettore del framework nel nostro CSS**. Se OF cambia
`layout.css`, il redesign non si muove.

## 6. Passi, se la direzione è questa

1. `src/style.css` con il reset da 6 regole e i token del redesign.
2. `generate-config.mjs`: `sidebar: false`, `header`/`footer` generati da `pages`
   (stessa fonte delle route, markup nostro).
3. Ricerca nostra: indice snello + `/cerca`.
4. Audit: voce di nav senza pagina → errore; invalidare `catalog.json` quando
   cambia `catalog/cards/` (§4.4).
5. Cancellare `src/prova-*.md` prima del merge.

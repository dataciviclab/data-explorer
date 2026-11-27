# Spike: shell custom su Observable Framework

Branch di **verifica**, non di produzione. Contiene prototipi e misure, non una
proposta da mergiare così com'è.

## Cosa c'è

| File | Cosa dimostra |
|---|---|
| `docs/customization.md` | quanto si personalizza OF; i tre livelli; i limiti |
| `docs/platform.md` | bilinguismo, tema, SEO, redirect, build/dati |
| `src/prova-custom.md` | layout interamente nostro (header, nav, hero, card, sezioni, footer) |
| `src/prova-tema.md` | cambio tema con `data-theme` + grafici che seguono i token |
| `src/prova-i18n.md` + `src/en/prova-i18n.md` | due lingue, un solo loader |
| `src/prova-dir/index.md` | URL `/x/` con lo slash, senza redirect |
| `src/prova-shell.md` | shell di pagina (hero full-bleed, sidebar fuori) |
| `src/prova-topnav.md` | sidebar riletta come barra (compromesso, sconsigliato) |
| `scripts/postbuild.mjs` | `lang`, canonical, hreflang, viewport, sitemap, stub di redirect |
| `docs/architecture.md` | separazione job dati / job sito, con il contratto del bundle |

## Riprodurre

```bash
npm run build                                  # ~30 s con cache calda
node scripts/postbuild.mjs --dist dist/observable --site https://esempio.org \
  --exclude prova- --lastmod 2026-11-27
npx serve dist/observable                      # oppure: npx observable preview
```

Da aprire: `/prova-custom`, `/prova-tema` (clic sul pulsante tema, poi reload),
`/prova-i18n` e `/en/prova-i18n`, `/prova-dir/`.

Verifiche automatiche già in repo:

```bash
npm test        # 63 JS + 122 Python
npm run audit   # dati/pagine/mappe
```

## Le misure chiave

- `sidebar: false` → spariscono cassetto, toggle, inset di 288 px: restano **6
  regole CSS** che parlano di OF, tutte in `docs/customization.md` §5.
- Contenuto statico nel `<main>`: **91%** nel layout custom, 42% in una pagina
  dataset, **17%** in una pagina progetto tutta renderizzata da JS.
- `observable build` con cache presente: **0 ms per loader** (`[using stale]`).
- Sitemap: 113 URL; `lang`/canonical su 113/113 pagine.

## Cosa non è stato deciso qui

- se spegnere `sidebar` in produzione e generare nav/footer da `pages`;
- se attivare `postbuild.mjs` in CI e con quale dominio;
- quante lingue, e chi revisiona le traduzioni;
- il layout: questo branch non contiene il redesign.

## Da cancellare prima di un merge

`src/prova-*.md`, `src/prova-dir/`, `src/en/prova-i18n.md`,
`src/import/lang-switch.js`, `catalog/redirects.json` (se resta vuoto).

# Verifica pagine (Playwright)

Loop di verifica **reale**: carica la pagina in un browser headless, cattura
errori console e riporta cosa è effettivamente renderizzato.

Il rendering di Observable Framework è client-side: `npm run build` non basta
per sapere se una pagina funziona. Questi script verificano il runtime.

## Setup

`playwright` è in `devDependencies`. Il binario Chromium è nel cache locale
Playwright (`~/.cache/ms-playwright/`); se manca: `npx playwright install`.

## Uso

1. Avvia la preview:

   ```bash
   npx observable preview --port 8788
   ```

2. Verifica una pagina:

   ```bash
   node scripts/verifica/verify-page.mjs [/dataset/slug]
   # default: /dataset/anzianita
   ```

   Configurabile via env:

   ```bash
   BASE_URL=http://localhost:8788 node scripts/verifica/verify-page.mjs
   CHROME_PATH=/path/to/chrome node scripts/verifica/verify-page.mjs
   ```

## Cosa verifica

- sezioni renderizzate (`[data-section]`: kpi, trend, barrank, choropleth, table)
- conteggio SVG / tabelle / dropdown
- errori console e richieste HTTP >= 400
- primo testo visibile della pagina

Un output pulito ha `NESSUN ERRORE CONSOLE` e le sezioni attese presenti.

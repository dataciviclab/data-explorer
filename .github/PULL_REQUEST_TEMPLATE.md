## Sintesi

Descrivi in poche righe cosa cambia e perché.

## Contesto collegato

Closes #

## Cosa cambia

- [ ] Nuovo dataset — pagina explorer
- [ ] Bug fix frontend (data loader / layout / performance)
- [ ] Aggiornamento config / catalogo
- [ ] Modifica struttura dati upstream
- [ ] Documentazione
- [ ] Dipendenze o CI

## Checklist nuovo dataset

Se la PR aggiunge un nuovo dataset in explorer:

- [ ] **Data loader**: `src/data/<slug-url>.json.py` — usa `safe_connect()` (non `duckdb.connect()`)
- [ ] **Pagina**: `src/dataset/<slug-url>.md` — usa moduli condivisi (`format-utils.js`, `geo-utils.js`)
- [ ] **Tema**: aggiornato `src/data/themes.json.py` (sidebar auto-generata, non toccare `observablehq.config.js`)
- [ ] **Frontmatter**: `title`, `description`, `source`, `source_url`, `period`, `last_modified`, `dataset_slug`
- [ ] **Sezione Limiti** obbligatoria (copertura, note metodologiche)
- [ ] **Verifica**: `npm run lint` e `npm test` passano

## Standard check

Prima della review, verificare:

- [ ] **Niente `toLocaleString`** — usare `num()`, `euro()`, `pct()` da `format-utils.js`
- [ ] **`tableFormat` e `Inputs.table` in celle separate** (bug noto OF)
- [ ] **Mappe**: usare `buildMapLookup()` (non `buildRegLookup` diretto)
- [ ] **Niente `duckdb.connect()`** — usare `safe_connect()`
- [ ] **Sidebar**: auto-generata da `themes.json.py` — non modificare `observablehq.config.js`

## Verifica

```bash
npm run lint
npm test
npm run build
```

- [ ] `npm run lint` — nessun errore
- [ ] `npm test` — test passano
- [ ] `npm run build` — build completato, 0 errori

## Checklist PR

- [ ] Perimetro stretto: una PR = un dataset o un fix mirato
- [ ] Issue collegata o motivazione dell'assenza

## Note per chi revisiona

Rischi, limiti, punti da controllare con attenzione.

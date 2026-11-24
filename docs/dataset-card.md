# Scheda dataset — modello e flusso

Stato: **pilota** (3 schede, route `/schede/[slug]`). Non sostituisce ancora
`/dataset/*`.

## Perché esiste

Una scheda dataset deve costare ~0 in codice e non deve far interrogare GCS al
build. Il modello è: **metadati dal catalogo ACB + fatti da un mart**, prodotti
una volta fuori dal build e serviti come file statico.

```
pipeline → registry + mart
               │
     scripts/build-cards.py        (job separato, 1 query per scheda)
               │
     src/data/cards.json           (artefatto, gitignored)
               │
     build OF → /schede/<url_slug> (route dinamica, nessuna query)
```

## Come si aggiunge una scheda

1. Aggiungi lo slug a `SPECS` in `scripts/build-cards.py` con: `mart`, asse
   temporale (`x`), misura (`y`), etichette e formato. `y2` è opzionale.
2. `npm run cards` (scrive `src/data/cards.json`).
3. `npm run build`.

La route `src/schede/[slug].md` è generica: non si tocca per ogni dataset.
I path di build vengono da `cards.json` tramite `dynamicPaths` in
`generate-config.mjs` — nessuna lista di path hardcoded.

## Contratto `cards.json`

Per ogni URL slug:

| Campo | Fonte |
|---|---|
| `name`, `description`, `category`, `stage`, `period`, `source_id`, `rows_clean`, `dictionary` | catalogo ACB |
| `series` (`[{x,y,y2?}]`), `kpis` | mart della pipeline (ultimo anno completo) |
| `run` (`run_id`, `status`, `finished_at`, `quality`) | `signals` del registry del repo |
| `links` (`pipeline`, `parquet`, `query`) | registry + path contract |
| `warnings` | calcolati: descrizione/fonte/parquet mancanti |

## Cosa manca (qualità, non tecnica)

- **Nome e fonte leggibili**: `name` è derivato dallo slug ("Anac Bandi Gara"),
  `source` è vuoto per la maggior parte dei dataset; esiste solo `source_id`.
- **Licenza**: assente in tutti i registry.
- **Descrizioni colonne**: ~10% compilate.
- **Periodo**: il registry può essere più stretto dei file pubblicati
  (es. ANAC: `period` 2016–2025, mart 2007–2026). La scheda mostra entrambi:
  è un segnale, non un bug della pagina.

## Limiti tecnici noti

- Le pagine **dinamiche** di OF non iniettano `Inputs`/import `npm:`: la
  tabella del dizionario è HTML statico. Se serve una tabella interattiva,
  va risolto a monte (OF) o spostata in una pagina statica.
- La serie è a punti annuali; niente filtri o drill-down (quelli restano
  Streamlit / Query SQL).

# Piattaforma: bilinguismo, tema, SEO, redirect, build

Stato: **novembre 2026**, verificato sul build locale (113 pagine). Complemento di
`docs/customization.md`: qui ci sono le cinque cose che servono per unificare il
sito del Lab dentro explorer, non solo per ridisegnarlo.

| Aspetto | Si può | Come | Costo ricorrente |
|---|---|---|---|
| Bilinguismo | sì, senza middleware | due alberi `src/` e `src/en/`, dati condivisi | ogni testo due volte; audit sulla coppia |
| Cambio tema | sì, meglio di OF | `data-theme` su `<html>` + token | zero |
| SEO | sì | statico al 91% + un postbuild | ~60 righe, nessuna dipendenza |
| Redirect | solo stub | `meta refresh` + canonical + noindex | 1 file JSON; niente 301 |
| Build ≠ dati | **già così** | cache loader (`useStale`) + invalidazione | estendere la regola a `catalog/` |

## 1. Bilinguismo

OF non ha i18n: nessuna stringa traducibile, nessun `lang` su `<html>`
(`render.js:21`), nessun routing per lingua. Restano tre strade, e una sola regge:

- **runtime** (JS che sceglie la lingua): il testo non è nell'HTML;
- **`t()` in ogni cella**: ogni parola diventa codice, e le pagine generate
  perdono lo statico;
- **due alberi, un dato**: `src/` e `src/en/`, stessi loader, stessi
  `FileAttachment`.

Verificato: `src/en/prova-i18n.md` legge il catalogo con **un solo loader** e una
sola copia in `dist` (`_file/data/catalog.json`, contata una volta nel log).

Inciampo misurato: `FileAttachment` risolve **relativo alla pagina**, non alla
radice. Da `src/en/` serve `../data/catalog.json`; con `data/catalog.json` il
build si ferma su `Not found: /en/data/catalog.json`.

Il costo è il testo due volte. Per le pagine generate non è un costo: lo yml ha
`name_it`/`name_en` e il generatore scrive i due file. Per le pagine narrative
(chi siamo, docs) sono due file, e serve una regola d'audit: **ogni `src/x.md`
deve avere `src/en/x.md`**, altrimenti la traduzione invecchia in silenzio.

## 2. Cambio tema

OF offre due temi via `prefers-color-scheme` (`theme: ["air", "ocean-floor"]`) e
nessun interruttore. Con la chrome nostra il tema è un attributo:

```css
:root { --dl-bg: #fbfaf7; --dl-ink: #14181d; --dl-line: #e3e0d8; }
:root[data-theme="dark"] { --dl-bg: #0f1319; --dl-ink: #e8edf3; --dl-line: #232c37; }
```

Script di init **una volta**, in `head:` dal config (non per pagina) +
`localStorage`. Misurato su `src/prova-tema.md`:

- click → `data-theme=dark`, scritto in `localStorage`, **sopravvive al reload**;
- lo script finisce dentro `<head>` (offset 3328, `</head>` a 5249): gira prima
  del paint, nessun lampo bianco;
- **i grafici seguono**: barre con `fill: "var(--dl-accent)"` cambiano colore
  senza re-render.

![Tema chiaro](_local/generated/screenshots/de-tema-chiaro.png)

![Tema scuro](_local/generated/screenshots/de-tema-scuro.png)

Regola che ne deriva: nei grafici **mai hex**, sempre token — la stessa regola
della palette (lab-ops #114), quindi non è un costo aggiuntivo.

Limite: i componenti interni di OF (sidebar, tabelle, `Inputs`) usano
`--theme-*`, non i nostri token, quindi in dark restano chiari (si vede nello
screenshot). Con `sidebar: false` il problema sparisce per la nav; per il resto
bastano 5 righe che mappano `--theme-*` sui nostri token.

## 3. SEO

Già a posto: `<title>` e `head:` per pagina (progetti e schede li hanno) e HTML
statico al 91% con la regola «numeri al build» (`customization.md` §5).

Mancava il contorno, e si risolve in un passaggio (`scripts/postbuild.mjs`, zero
dipendenze, idempotente):

- `lang` su `<html>` per albero (`it` / `en`) — OF lo omette;
- `<link rel="canonical">` dove manca;
- `<link rel="alternate" hreflang>` fra le due lingue, solo se la controparte
  esiste davvero;
- `sitemap.xml` + `robots.txt`;
- stub di redirect (§4).

Misurato: 113 pagine, 113 con `lang` e canonical, sitemap con 113 URL,
`hreflang` reciproci solo dove la pagina esiste in entrambe le lingue.

Perché un postbuild e non un plugin: è l'unico punto che conosce il dominio e le
URL, non dipende dal framework, si testa su file statici e si può cancellare
senza toccare le pagine.

## 4. Redirect

OF non ne ha. Tre opzioni, in ordine di qualità:

1. **Non cambiare le URL** (la migliore): `src/progetti/x/index.md` esce come
   `progetti/x/index.html`, cioè `/progetti/x/` — la stessa forma del hub.
   Verificato: con `preserveIndex` attivo o no, il file è lo stesso. I 44 URL si
   conservano **scegliendo il layout**, non con i redirect.
2. **Stub** per ciò che cambia davvero: `meta refresh` + `canonical` + `noindex`.
   Non è un 301, ma conserva link, titolo e passaggio di autorità. Verificato in
   browser: `/vecchia-sezione/` finisce su `/prova-i18n`.
3. **301 veri** solo cambiando host (Cloudflare/Netlify `_redirects`). GitHub
   Pages non li supporta: sotto lo stesso host, 301 non esistono.

Il postbuild **rifiuta** di creare uno stub che coprirebbe una pagina esistente
(`x.html` oppure `x/index.html`). Non è teoria: il primo tentativo ha creato
`progetti/bilancio-pubblico/index.html` sopra la pagina reale, e l'ho corretto
dopo averlo visto.

## 5. Build separato dai dati

**È già così**, va solo reso esplicito e difeso. Meccanismo (`loader.js:330-336`):
la cache è valida se `mtime(cache) >= mtime(loader)`; `observable build` chiama i
loader con `useStale: true` (`build.js:75,175`), quindi **se l'artefatto esiste
non esegue niente**.

Misurato: `touch src/data/themes.json.py` → build 30 s, `[using stale]`, 0 ms per
loader. I dati si aggiornano solo con cache assente (clone pulito) o invalidata.

Da qui i due job:

| Job | Cosa fa | Tempo |
|---|---|---|
| dati | cache vuota → 58 loader → pubblica `src/.observablehq/cache/data/*` | ~12 min |
| sito | scarica gli artefatti (mtime nuovi) → build senza rete né Python | ~30 s |

È già implementato in `deploy.yml` (restore cache, `invalidate_cache.py`, refresh
esplicito di `catalog`/`themes`). Due buchi misurati:

- **cache locale**: cambiare `catalog/cards/*` non invalida `catalog.json` (la
  lista `SHARED` non include `catalog/`). Stamattina ha prodotto 4 pagine rotte
  in nav, con build verde.
- **audit cieco**: legge la stessa cache, quindi non vede l'incoerenza.

Da aggiungere: `catalog/**` fra le dipendenze di `catalog.json`, e la regola
«voce di nav senza superficie → errore» (già in `roadmap.md`).

## Cosa resta da decidere (non tecnico)

- **Una lingua o due**: il bilinguismo raddoppia testi e revisioni. Se l'inglese
  non è una promessa pubblica, due alberi sono solo debito.
- **Dominio**: `dataciviclab.org` su DE permette 301 veri solo cambiando host.
- **Chi valida le traduzioni**: oggi non c'è nessuno.

# Architettura unificata: due build, un contratto

Stato: **novembre 2026**. Definisce come separare davvero la build dei dati da
quella del sito, e cosa manca per farlo. Complemento di `docs/platform.md`
(bilinguismo, tema, SEO, redirect) e `docs/customization.md` (shell custom).

## 1. Il problema di oggi

`deploy.yml` ha **un solo job**. Fa checkout, ripristina la cache, invalida,
genera le schede, esegue i loader dentro `observable build`, carica `pages`.

E `observable build` decide per **mtime** (`loader.js:330-336`): se l'output è
più recente del loader, lo usa e non esegue nulla. Quindi la domanda «questi
dati li ha prodotti questa build?» non ha risposta: è un effetto collaterale
dell'orologio.

Due sintomi, entrambi riprodotti:

- con cache, un loader rotto viene mascherato: `[using stale]`, build verde,
  dati vecchi in pagina;
- senza cache, il deploy fa il lavoro pesante: misurato **4,9 min** e **150 MB**
  per i 58 loader.

## 2. Il contratto

**Job dati** produce un bundle:

```
bundle/
  manifest.json          # schema, built_at, loaders{slug: sha256}, artifacts{name: sha256}, sources
  data/*.json            # 58 output dei loader (35 MB)
  cards.json             # schede, perché dipendono dai mart
```

**Job sito** consuma il bundle e nient'altro:

1. scarica il bundle (artifact GitHub + copia durevole, §8);
2. **verifica il contratto**: per ogni `src/data/<slug>.json.py` del commit,
   `sha256(sorgente) == manifest.loaders[slug]`. Se manca un loader o l'hash non
   torna, il bundle è di un altro codice → **rosso**, non «uso quello che c'è»;
3. copia gli artefatti in `src/.observablehq/cache/` e li `touch`a (la cache OF
   si attiva per mtime: questo è il punto in cui il contratto incontra il
   framework, e va scritto e testato, non scoperto);
4. `observable build`;
5. **guardia**: per ogni artefatto, il file in `dist/_file/data/<nome>.<hash>.json`
   deve avere il prefisso di hash del manifest. Se un loader è girato, l'hash
   cambia e la guardia se ne accorge — senza leggere i log;
6. `postbuild.mjs` → deploy.

| | Oggi | Target |
|---|---|---|
| chi decide se eseguire i loader | mtime della cache | hash nel manifest |
| loader rotto | mascherato (`[using stale]`) | job dati rosso, il sito non pubblica quel codice |
| bundle assente | il sito lo genera (5 min) | **il sito fallisce** |
| invalidazione | dentro il deploy | solo nel job dati |
| durata deploy | 30 s con cache / 12 min senza | ~40-60 s, sempre |
| PR check | rischia 15 min | build del sito dal bundle di main |

Il pezzo che rende la separazione reale è il **confronto degli hash**: senza,
si può deployare codice che si aspetta colonne nuove con un bundle vecchio.

Limite dichiarato: la guardia dimostra che l'output **viene dal bundle**, non
che la rete non sia stata toccata. Per impedire davvero l'accesso a GCS serve
un container con egress bloccato; oggi non c'è, e non lo faccio passare per tale.

## 3. Trigger

| Evento | Job dati | Job sito |
|---|---|---|
| push su `src/data/**` (loader) | sì, poi il sito | dopo `workflow_run` |
| push editoriale (pagine, catalog, css) | no | sì, bundle corrente |
| cron notturno | sì | no |
| PR | preview dati opzionale, per dataset toccati | sì, bundle di main |

La regola: **il codice che legge i dati non si deploya senza il bundle che li
contiene**. Un push che tocca un loader e non il dataset aspettato resta
indietro di un giro, ed è giusto così.

## 4. Freschezza

`manifest.built_at` diventa:

- `--lastmod` per la sitemap;
- `dist/data-version.json` (run id, timestamp, commit del job dati);
- un **tetto**: se il bundle è più vecchio di 26 h, il deploy fallisce. Oggi il
  controllo esiste già su `catalog.json`; qui diventa esplicito e unico.

Serve anche in pagina: «dati aggiornati al …» è informazione editoriale, non
solo un check di CI.

## 5. Cosa resta accoppiato, per scelta

- **`cards.json`** dipende dai mart → job dati. Non è un dettaglio da spostare.
- **I loader sono codice**: cambiarli richiede un giro dati. Non c'è modo di
  evitarlo, e non va mascherato.
- **La cache OF è per worktree**: condividerla è esattamente il bundle.

## 6. Migrazione in quattro passi

1. `scripts/verify_bundle.py` + schema del manifest + job dati che **produce**
   il bundle (nessuna separazione ancora: si aggiunge una pipeline, non si
   toglie niente).
2. `deploy.yml` consuma il bundle, guardia attiva. **Qui avviene la
   separazione**: da questo momento un deploy senza bundle è rosso.
3. `invalidate_cache.py` esce dal deploy e resta solo nel job dati.
4. `prefetch.py` (#308, non mergiata) va nel job dati: è lì che il tempo dei
   loader si paga, non nel sito.

Ogni passo è reversibile: il 2 si annulla ripristinando l'invalidazione nel
deploy, e la cache torna a fare quello che fa oggi.

## 7. Rischi

- **Due pipeline, due orologi**: se il job dati non parte (cron fallito, coda),
  il sito publica dati vecchi. Mitigazione: tetto 26 h + `data-version.json`
  visibile.
- **Bundle più grande del codice**: 35 MB per run. GitHub artifact scade, quindi
  serve una copia durevole (GCS o branch `data`).
- **Mtime come leva nascosta**: dopo il checkout, un file del bundle è più
  vecchio dei loader e il build ri-eseguirebbe il loader. Il `touch` non è
  cosmetico.

## 8. Decisioni aperte

1. **Dove vive il bundle**: prefisso GCS (meglio se cresce) o branch `data`
   (versionato, gratis, 35 MB per run). Il solo artifact GitHub non basta:
   scade.
2. **Dominio**: i 301 veri esistono solo cambiando host. Con il layout a
   cartella 43 URL su 48 si conservano comunque.
3. **Traduzioni**: `source_sha` nel frontmatter EN + glossario, altrimenti la
   revisione umana non ha un segnale di traduzione vecchia.
4. **Ricerca**: pagina `/cerca` o overlay (mezza giornata / una).

# Standard Pagina Dataset

Questo documento definisce i **principi** di una buona pagina dataset nel `Data Explorer`.
Per il **template operativo** da copiare, vedi [`TEMPLATE-dataset-page.md`](TEMPLATE-dataset-page.md).

## Obiettivo

Una pagina dataset deve sembrare una pagina civica leggibile con dati vivi, non un esperimento tecnico isolato.

## Struttura minima

Ogni pagina dataset dovrebbe avere questi blocchi, nello stesso ordine:

1. frontmatter con `title`, `description`, `source`, `source_url`, `period`, `last_modified`, `dataset_slug`, **`data_driven: true`**
2. data loader + import moduli condivisi + filtro anno
3. computazione variabili (KPI, aggregazioni)
4. **intro narrativa** con template literal (usa variabili computate, mai numeri hardcoded)
5. KPI cards
6. blocco **base**: distribuzione o stock nell'anno più recente
7. blocco **derivato**: trend/confronti
8. eventuale blocco terziario
9. tabella finale ricercabile + `Limiti` + `Risorse`

## Principio dataset-first

Nel `Data Explorer` la gerarchia editoriale deve partire dal dataset, non da una tesi.

Regole:

- il primo blocco deve mostrare la distribuzione base del dataset nell'anno più recente
- solo dopo possono arrivare delta, confronti, trend o metriche derivate
- le letture più interpretative vivono come pagine di analisi dedicate
- il dataset deve essere mostrato prima di essere interpretato

## Blocco principale

Il blocco principale deve essere quello che risponde meglio alla domanda guida senza saltare la struttura base del dataset.

Regole:

- deve essere uno solo
- meglio un grafico o una tabella forte, non due blocchi equivalenti
- deve essere leggibile senza conoscere già il dataset
- deve mostrare prima stock, distribuzione o composizione base nell'anno più recente
- non deve partire subito da ranking, delta o proxy

## Blocco secondario

Il blocco secondario serve a dare un secondo livello di lettura, non a duplicare il primo.

Regole:

- meglio una tabella scaricabile oppure un confronto mirato
- deve restare semplice
- nel v0 non servono più di `2-3` query curate per pagina
- qui possono entrare confronto, delta, trend o altre letture derivate

## Tabella finale

La tabella finale non è obbligatoria in senso assoluto, ma nel v0 è il default consigliato.

Serve a:

- far vedere il dettaglio dietro il blocco principale
- permettere ricerca e download
- tenere la pagina ancorata al dataset, non solo alla lettura guidata

## Copy minimo

Ogni pagina dovrebbe contenere:

- cosa c'è dentro
- perché conta
- come leggere il blocco principale
- fonte esplicita e data di ultimo aggiornamento nel frontmatter

Il copy deve restare corto. La metodologia lunga non è il focus del v0.

## Filtri

Nel v0 il filtro standard è il filtro anno.

Regole:

- usare un solo filtro quando basta
- preferire filtri stabili e prevedibili
- evitare componenti più complesse se il guadagno di lettura è basso

## Note editoriali

Le note dentro pagina sono ammesse solo se aiutano davvero la lettura del blocco mostrato.

Regole:

- `section-note`: ok per spiegare una metrica, un filtro o il perimetro del blocco
- `method-note`: usare con cautela, solo se evita una lettura sbagliata del dato
- se la nota diventa il cuore della pagina, quel contenuto appartiene a una pagina di analisi dedicata

## Cosa evitare

- pagine che sembrano dashboard generiche
- query troppo tecniche o poco spiegabili
- troppe tabelle una dopo l'altra
- più domande guida nella stessa pagina
- conclusioni più forti dei dati disponibili

## Regola pratica del v0

Meglio una pagina con una sola lettura forte e pulita che una pagina con molte query deboli.

## Narrativa data-driven

I numeri nelle pagine **non sono hardcoded**: ogni KPI o cifra nel testo cita una variabile calcolata dal data loader a build-time, così la pagina si aggiorna da sola quando si ripubblica il parquet.

- **`data_driven: true`** nel frontmatter: attiva il lint che vieta cifre hardcoded nella prosa
- **KPI card**: 3-4 metriche chiave dal parquet (totale anno più recente, quota, variazione)
- **Frasi con numeri**: `es. Nel ${last} le entrate valgono ${euroCompact(totaleLast)}` — mai il numero scritto a mano
- **Blocco base** = la forma naturale del dataset (mappa, composizione, stock) **prima** di trend e letture derivate

### Colori nei grafici Plot

Observable Plot interpreta le stringhe come field names, non colori. Usare sempre colori literal:

```js
// ✅ Corretto
Plot.barX(data, { x: "valore", y: "categoria", fill: "#4e79a7" })

// ❌ Sbagliato — "Costo" viene interpretato come field name
Plot.barX(data, { x: "valore", y: "categoria", fill: "Costo" })
```

### Moduli condivisi

- `format-utils.js` — `num`, `euro`, `euroCompact`, `pct`, `numFix`, `tableFormat`
  - `tableFormat()` supporta `decimals: N` per campi con virgola
- `geo-utils.js` — `loadItalianRegions` + `buildMapLookup` (mai `buildRegLookup`)
- `tableFormat` e `Inputs.table` in **celle separate** (bug noto OF)

### Riferimenti canonici

`entrate-stato.md`, `cinque-per-mille.md`, `dipendenti-pubblici.md`.

## Confine editoriale

| Posizione | Contenuto |
|-----------|-----------|
| Blocco 1 | stock o distribuzione base nell'anno più recente |
| Blocco 2 | confronto, delta, trend o lettura derivata |
| Tabella finale | vista completa scaricabile |

Le letture interpretative più forti vivono in pagine di analisi dedicate, non compresse nel blocco dataset.

## Checklist rapida di review

Prima di considerare una pagina pronta, chiedersi:

- il primo blocco mostra davvero il dataset nella sua forma più naturale?
- la domanda guida orienta la lettura senza promettere più di quanto la pagina mostri?
- le metriche derivate arrivano solo dopo la vista base?
- i colori nei grafici sono literal (non field names)?
- i campi con decimali usano `decimals: N` in `tableFormat`?
- `section-note` e `method-note` sono davvero minime?
- la pagina resta leggibile con poco testo?
- il dettaglio finale riporta l'utente al dataset?

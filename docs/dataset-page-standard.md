# Standard Pagina Dataset

Questo documento definisce la forma minima di una buona pagina dataset nel `Data Explorer`.

## Obiettivo

Una pagina dataset deve sembrare una pagina civica leggibile con dati vivi, non un esperimento isolato di Evidence.

## Struttura minima

Ogni pagina dataset dovrebbe avere questi blocchi, nello stesso ordine:

1. `title`, `description`, `source` e `last_modified` nel frontmatter
2. una frase iniziale che spiega cosa contiene il dataset
3. una frase che esplicita la domanda guida della pagina
4. un filtro minimo, quasi sempre l'anno
5. un blocco principale
6. un blocco secondario
7. opzionalmente una nota breve di lettura
8. una tabella finale o un dettaglio scaricabile
9. un link al clean parquet pubblico

## Principio dataset-first

Nel `Data Explorer` la gerarchia editoriale deve partire dal dataset, non da una tesi.

Regole:

- il primo blocco deve mostrare la distribuzione base del dataset nell'anno più recente
- solo dopo possono arrivare delta, confronti, trend o metriche derivate
- le letture più interpretative restano nel repo `dataciviclab/analisi`
- il dataset deve essere mostrato prima di essere interpretato

## Blocco principale

Il blocco principale deve essere quello che risponde meglio alla domanda guida senza saltare la struttura base del dataset.

Regole:

- deve essere uno solo
- meglio un grafico o una tabella forte, non due blocchi equivalenti
- deve essere leggibile senza conoscere già il dataset
- deve mostrare prima stock, distribuzione o composizione base nell'anno più recente
- non deve partire subito da ranking, delta o proxy se il dataset non è ancora stato mostrato nella sua forma naturale

## Blocco secondario

Il blocco secondario serve a dare un secondo livello di lettura, non a duplicare il primo.

Regole:

- meglio una `DataTable` scaricabile oppure un confronto mirato
- deve restare semplice
- nel v0 non servono più di `2-3` query curate per pagina
- qui possono entrare confronto, delta, trend o altre letture derivate

## Tabella finale

La tabella finale non è obbligatoria in senso assoluto, ma nel v0 è il default consigliato.

Serve a:

- far vedere il dettaglio dietro il blocco principale
- permettere ricerca e download
- tenere la pagina ancorata al dataset, non solo alla lettura guidata

## Query curate

Ogni query dovrebbe:

- rispondere a una domanda pubblica chiara
- usare campi comprensibili o già spiegati
- evitare interpretazioni troppo fragili
- produrre output leggibili con poco testo di supporto

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
- `method-note`: usare con cautela, solo se evita una lettura palesemente sbagliata del dato
- se la nota diventa il cuore della pagina, quel contenuto probabilmente appartiene a `dataciviclab/analisi`

## Cosa evitare

- pagine che sembrano dashboard generiche
- query troppo tecniche o poco spiegabili
- troppe tabelle una dopo l'altra
- più domande guida nella stessa pagina
- conclusioni più forti dei dati disponibili

## Regola pratica del v0

Meglio una pagina con una sola lettura forte e pulita che una pagina con molte query deboli.

## Confine editoriale

| Posizione | Contenuto |
|-----------|-----------|
| Blocco 1 | stock o distribuzione base nell'anno più recente |
| Blocco 2 | confronto, delta, trend o lettura derivata |
| Tabella finale | vista completa scaricabile |

Le letture interpretative più forti appartengono a `dataciviclab/analisi`, non alle pagine del Data Explorer.

## Checklist rapida di review

Prima di considerare una pagina pronta, chiedersi:

- il primo blocco mostra davvero il dataset nella sua forma più naturale?
- la domanda guida orienta la lettura senza promettere più di quanto la pagina mostri?
- le metriche derivate arrivano solo dopo la vista base?
- la pagina resta leggibile con poco testo?
- il dettaglio finale riporta l'utente al dataset?

# Standard Pagina Dataset

Questo documento definisce la forma minima di una buona pagina dataset nel `Data Explorer`.

## Obiettivo

Una pagina dataset deve sembrare una pagina civica leggibile con dati vivi, non un esperimento isolato di Evidence.

## Struttura minima

Ogni pagina dataset dovrebbe avere questi blocchi, nello stesso ordine:

1. `title` e `description` nel frontmatter
2. una frase iniziale che spiega cosa contiene il dataset
3. una frase che esplicita la domanda guida della pagina
4. un filtro minimo, quasi sempre l'anno
5. un blocco principale
6. un blocco secondario
7. una nota interpretativa breve
8. un link al clean parquet pubblico

## Blocco principale

Il blocco principale deve essere quello che risponde meglio alla domanda guida.

Regole:

- deve essere uno solo
- meglio un grafico o una tabella forte, non due blocchi equivalenti
- deve essere leggibile senza conoscere già il dataset

## Blocco secondario

Il blocco secondario serve a dare un secondo livello di lettura, non a duplicare il primo.

Regole:

- meglio una `DataTable` scaricabile oppure un confronto mirato
- deve restare semplice
- nel v0 non servono più di `2-3` query curate per pagina

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

Il copy deve restare corto. La metodologia lunga non è il focus del v0.

## Cosa evitare

- pagine che sembrano dashboard generiche
- query troppo tecniche o poco spiegabili
- troppe tabelle una dopo l'altra
- più domande guida nella stessa pagina
- conclusioni più forti dei dati disponibili

## Regola pratica del v0

Meglio una pagina con una sola lettura forte e pulita che una pagina con molte query deboli.

# Checklist Explorer-Ready

Questa checklist serve a decidere se un dataset può entrare nel `Data Explorer` e con quale livello di esposizione.

## Classi di readiness

### A. Explorer-ready

Il dataset è pronto per una pagina pubblica completa nel sito.

Requisiti minimi:

- schema abbastanza stabile tra le versioni pubblicate
- clean parquet pubblico disponibile con URL stabile
- slug tecnico e slug pubblico già definiti
- tema pubblico assegnato nel catalogo
- almeno `2` query curate davvero leggibili
- almeno `1` visual o tabella che risponde a una domanda civica chiara
- copy minimo di contesto:
  - cosa contiene il dataset
  - perché conta
  - come leggere i risultati mostrati

### B. Public-download-ready

Il dataset può essere pubblicato come dato aperto, ma non è ancora pronto per una pagina forte nell'explorer.

Condizioni tipiche:

- clean pubblico disponibile
- schema ancora poco stabile o poco leggibile
- query civiche non ancora abbastanza difendibili
- copy pubblico ancora debole o assente

Uso nel sito:

- può comparire in catalogo o in backlog interno
- non deve ancora essere promosso come pagina dataset del v0

### C. Non pronto

Il dataset non è ancora adatto all'esposizione nel Data Explorer.

Casi tipici:

- clean pubblico assente
- schema troppo instabile
- naming o coverage ancora ambigui
- mancano le condizioni minime per una lettura pubblica affidabile

## Checklist operativa

Prima di aggiungere un dataset al sito, verificare:

- il clean parquet pubblico esiste davvero ed è interrogabile
- il dataset ha un tema pubblico chiaro
- `catalog/datasets.json` e `catalog/themes.json` possono rappresentarlo senza eccezioni ad hoc
- le colonne usate dalle query sono stabili e comprensibili
- la pagina può essere letta anche da un utente non tecnico
- il link al dato grezzo è disponibile
- le query non fanno promesse più forti dei dati disponibili

## Query curate

Una query è abbastanza buona per il Data Explorer se:

- risponde a una domanda pubblica chiara
- usa campi comprensibili o ben etichettati
- non dipende da interpretazioni troppo fragili
- produce un output leggibile come tabella o grafico

## Copy minimo richiesto

Ogni pagina dataset dovrebbe avere almeno:

- una frase iniziale che spiega cosa contiene il dataset
- una frase che esplicita la domanda guida della pagina
- una breve nota interpretativa sul blocco più importante
- `source` e `last_modified` nel frontmatter
- un link al clean parquet pubblico

## Principio guida

Nel Data Explorer entrano prima i dataset che si leggono bene, non quelli semplicemente disponibili.

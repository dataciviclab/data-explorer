---
title: Come funziona
description: Cosa trovi in questo sito, come arrivano i dati e cosa non troverai.
---

DataCivicLab Explorer è il frontend pubblico dei dataset civici del Lab.
Ogni pagina parte da una domanda concreta su un fenomeno pubblico italiano
e porta al dato più vicino che siamo riusciti a trovare, pulire e leggere.

## Cosa trovi qui

Le pagine del sito non sono dashboard automatizzate.
Sono letture curate: una domanda guida, filtri semplici quando servono, grafici leggibili e una tabella scaricabile.
Il dato grezzo è sempre raggiungibile dal footer di ogni pagina.

## Da dove arrivano i dati

Ogni dataset segue lo stesso percorso:

1. Fonte pubblica italiana (ISPRA, Ministero della Giustizia, Terna, ...)
2. Pipeline di pulizia con il toolkit del Lab (DuckDB)
3. File parquet pubblicati su Google Cloud Storage, accessibili senza login
4. Pagina in questo sito, costruita a build time con Evidence.dev

I file parquet clean sono pubblici e scaricabili direttamente dal link in fondo a ogni pagina dataset.

## Cosa non troverai

- Dati in tempo reale: i dataset sono snapshot annuali o pluriannuali
- Copertura completa: ogni dataset ha un perimetro dichiarato, con anni e fonti espliciti
- Analisi automatizzate: ogni lettura è scritta e verificata a mano dal team del Lab
- Dati non verificabili: se non c'è il link alla fonte originale, non lo pubblichiamo

## Chi siamo

DataCivicLab è una comunità aperta di analisi civica sui dati pubblici italiani.
I dataset, le analisi e le discussioni sono pubblici su [GitHub](https://github.com/dataciviclab).

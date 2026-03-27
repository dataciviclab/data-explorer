---
title: IRPEF comunale
description: Lettura pubblica dei dati IRPEF comunali del MEF, con focus su contribuenti, reddito imponibile e confronto tra regioni e principali capoluoghi.
source: MEF / Finanze
last_modified: 2026-03-27
---

Questo dataset raccoglie i dati IRPEF comunali su contribuenti, reddito imponibile e imposta netta, aggregati per comune e regione nel periodo 2019-2023.

<div class="guide-question">Come si distribuisce la capacità fiscale IRPEF tra le regioni italiane, e come cambia il confronto tra alcuni principali capoluoghi nel periodo 2019-2023?</div>

```sql anni
SELECT DISTINCT anno FROM irpef_comunale.capacita_fiscale ORDER BY anno DESC
```

```sql regioni_distribuzione
SELECT
  regione,
  SUM(numero_contribuenti) AS numero_contribuenti,
  SUM(reddito_imponibile_eur) AS reddito_imponibile_totale_eur
FROM irpef_comunale.capacita_fiscale
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY regione
ORDER BY reddito_imponibile_totale_eur DESC, regione
```

```sql capoluoghi_confronto
SELECT
  comune,
  regione,
  numero_contribuenti,
  ROUND(reddito_imponibile_eur, 0) AS reddito_imponibile_totale_eur,
  ROUND(reddito_imponibile_eur / NULLIF(numero_contribuenti, 0), 0) AS reddito_imponibile_medio_per_contribuente_eur,
  ROUND(imposta_netta_eur / NULLIF(numero_contribuenti, 0), 0) AS imposta_netta_media_per_contribuente_eur
FROM irpef_comunale.capacita_fiscale
WHERE anno = '${inputs.anno_sel.value}'
  AND comune IN ('ROMA', 'MILANO', 'TORINO', 'GENOVA', 'NAPOLI', 'BOLOGNA', 'PALERMO', 'FIRENZE', 'BARI')
ORDER BY reddito_imponibile_medio_per_contribuente_eur DESC, numero_contribuenti DESC
```

<Dropdown name=anno_sel data={anni} value=anno>
</Dropdown>

## Distribuzione regionale

<div class="section-note">
Confrontando anni diversi tramite il filtro, tieni presente che i valori non sono deflazionati e non vanno letti come crescita reale del potere d'acquisto.
</div>

<BarChart data={regioni_distribuzione} x=regione y=reddito_imponibile_totale_eur yAxisTitle="Reddito imponibile totale" swapXY=true />

## Capoluoghi a confronto

L'imponibile medio è calcolato per contribuente e va letto insieme alla numerosità dei contribuenti.

La shortlist include nove principali capoluoghi: Roma, Milano, Torino, Genova, Napoli, Bologna, Palermo, Firenze e Bari.

<BarChart data={capoluoghi_confronto} x=comune y=reddito_imponibile_medio_per_contribuente_eur yAxisTitle="Imponibile medio per contribuente" swapXY=true />

## Dettaglio capoluoghi

Leggi questi dati come misura di capacità fiscale osservata, non come reddito pro capite dei residenti.

<DataTable data={capoluoghi_confronto} rows=20 search=true downloadable=true />

## Risorse e dati

- [Scarica il clean parquet 2023](https://storage.googleapis.com/dataciviclab-clean/irpef_comunale_2019_2023/2023/irpef_comunale_2019_2023_2023_clean.parquet)
- [Fonte originale: MEF / Finanze — Redditi e principali variabili IRPEF su base comunale](https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php?search_class%5B0%5D=cCOMUNE&opendata=yes)

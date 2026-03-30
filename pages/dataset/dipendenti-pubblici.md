---
title: Dipendenti pubblici per comparto
description: Lettura pubblica dei dati BDAP / RGS sul pubblico impiego, con focus su crescita, turnover e composizione dei comparti.
source: MEF / RGS / BDAP
last_modified: 2026-03-25
analisi_url: https://github.com/dataciviclab/dataciviclab/tree/main/analisi/dipendenti-pubblici
---

Questo dataset raccoglie i dati BDAP / RGS sui dipendenti pubblici italiani e li rende leggibili per comparto nel triennio 2021-2023.

<div class="guide-question">La crescita del pubblico impiego è diffusa oppure si concentra in pochi comparti?</div>

```sql stock_2023
SELECT
  comparto,
  SUM(donne_totali + uomini_totali) AS dipendenti_totali
FROM dipendenti_pubblici.occupazione
WHERE anno = '2023'
GROUP BY comparto
ORDER BY dipendenti_totali DESC
```

```sql delta_comparti
WITH comparti AS (
  SELECT
    anno,
    comparto,
    SUM(donne_totali + uomini_totali) AS dipendenti_totali
  FROM dipendenti_pubblici.occupazione
  GROUP BY anno, comparto
)
SELECT
  comparto,
  MAX(CASE WHEN anno = '2021' THEN dipendenti_totali END) AS dipendenti_2021,
  MAX(CASE WHEN anno = '2023' THEN dipendenti_totali END) AS dipendenti_2023,
  MAX(CASE WHEN anno = '2023' THEN dipendenti_totali END) - MAX(CASE WHEN anno = '2021' THEN dipendenti_totali END) AS delta_2023_vs_2021
FROM comparti
GROUP BY comparto
ORDER BY delta_2023_vs_2021 DESC
```

```sql turnover_2023
WITH base AS (
  SELECT
    anno,
    comparto,
    SUM(donne_totali + uomini_totali) AS dipendenti_totali,
    SUM(assunti_totali) AS assunti_totali,
    SUM(cessati_totali) AS cessati_totali,
    SUM(donne_totali) AS donne_totali
  FROM dipendenti_pubblici.occupazione
  GROUP BY anno, comparto
)
SELECT
  b23.comparto,
  b23.dipendenti_totali,
  b23.assunti_totali,
  b23.cessati_totali,
  b23.assunti_totali - b23.cessati_totali AS saldo_netto,
  ROUND(1.0 * b23.assunti_totali / NULLIF(b23.dipendenti_totali, 0), 4) AS tasso_assunzione_pct,
  ROUND(1.0 * b23.cessati_totali / NULLIF(b23.dipendenti_totali, 0), 4) AS tasso_uscita_pct,
  ROUND(1.0 * b23.donne_totali / NULLIF(b23.dipendenti_totali, 0), 4) AS quota_donne_pct,
  ROUND(1.0 * (b23.dipendenti_totali - b21.dipendenti_totali) / NULLIF(b21.dipendenti_totali, 0), 4) AS delta_pct_2023_vs_2021
FROM base b23
LEFT JOIN base b21
  ON b23.comparto = b21.comparto
 AND b21.anno = '2021'
WHERE b23.anno = '2023'
ORDER BY b23.dipendenti_totali DESC
```

## Dipendenti per comparto nel 2023

Una lettura della distribuzione di base: quanti dipendenti pubblici ci sono in ogni comparto nell'anno più recente disponibile.

<BarChart data={stock_2023} x=comparto y=dipendenti_totali yAxisTitle="Dipendenti totali" swapXY=true />

## Dove si concentra la crescita 2023 vs 2021

Il confronto mostra in quali comparti si concentra davvero l'aumento degli organici nel triennio.

<BarChart data={delta_comparti} x=comparto y=delta_2023_vs_2021 yAxisTitle="Delta dipendenti 2023 vs 2021" swapXY=true />

## Turnover e composizione nel 2023

La tabella finale aiuta a leggere insieme stock, saldo netto, tassi di entrata/uscita, quota donne e crescita percentuale 2023 vs 2021 per comparto.

<DataTable data={turnover_2023} rows=20 search=true downloadable=true />

## Approfondisci

- [Analisi completa](https://github.com/dataciviclab/dataciviclab/tree/main/analisi/dipendenti-pubblici) - notebook e metodologia

## Risorse e dati

- [Scarica il clean parquet 2023](https://storage.googleapis.com/dataciviclab-clean/dipendenti_pubblici_2021_2023/2023/dipendenti_pubblici_2021_2023_2023_clean.parquet)
- [Fonte originale: BDAP / RGS — Dipendenti pubblici](https://bdap-opendata.rgs.mef.gov.it/)

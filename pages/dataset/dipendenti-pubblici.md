---
title: Dipendenti pubblici per comparto
description: Lettura pubblica dei dati BDAP / RGS sul pubblico impiego, con focus su crescita, turnover e composizione dei comparti.
source: MEF / RGS / BDAP
last_modified: 2026-03-25
---

Questo dataset raccoglie i dati BDAP / RGS sui dipendenti pubblici italiani e li rende leggibili per comparto nel triennio 2021-2023.

<div class="guide-question">La crescita del pubblico impiego è diffusa oppure si concentra in pochi comparti?</div>

```sql comparti_list
SELECT
  ROW_NUMBER() OVER (ORDER BY dipendenti_2023 DESC, comparto) AS comparto_id,
  comparto
FROM (
  SELECT
    comparto,
    SUM(CASE WHEN anno = '2023' THEN donne_totali + uomini_totali ELSE 0 END) AS dipendenti_2023
  FROM dipendenti_pubblici.occupazione
  GROUP BY comparto
) t
ORDER BY dipendenti_2023 DESC, comparto
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

```sql quota_comparto_trend
WITH comparti_scelti AS (
  SELECT
    ROW_NUMBER() OVER (ORDER BY dipendenti_2023 DESC, comparto) AS comparto_id,
    comparto
  FROM (
    SELECT
      comparto,
      SUM(CASE WHEN anno = '2023' THEN donne_totali + uomini_totali ELSE 0 END) AS dipendenti_2023
    FROM dipendenti_pubblici.occupazione
    GROUP BY comparto
  ) t
),
base AS (
  SELECT
    anno,
    comparto,
    SUM(donne_totali + uomini_totali) AS dipendenti_totali
  FROM dipendenti_pubblici.occupazione
  GROUP BY anno, comparto
),
totale_annuo AS (
  SELECT
    anno,
    SUM(dipendenti_totali) AS totale_pa
  FROM base
  GROUP BY anno
)
SELECT
  CAST(b.anno AS INTEGER) AS anno,
  cs.comparto,
  ROUND(100.0 * b.dipendenti_totali / NULLIF(t.totale_pa, 0), 2) AS quota_su_totale_pct
FROM base b
JOIN comparti_scelti cs
  ON b.comparto = cs.comparto
JOIN totale_annuo t
  ON b.anno = t.anno
WHERE cs.comparto_id = ${inputs.comparto_sel.value}
ORDER BY anno
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
  ROUND(100.0 * b23.assunti_totali / NULLIF(b23.dipendenti_totali, 0), 2) AS tasso_assunzione_pct,
  ROUND(100.0 * b23.cessati_totali / NULLIF(b23.dipendenti_totali, 0), 2) AS tasso_uscita_pct,
  ROUND(100.0 * b23.donne_totali / NULLIF(b23.dipendenti_totali, 0), 2) AS quota_donne_pct,
  ROUND(100.0 * (b23.dipendenti_totali - b21.dipendenti_totali) / NULLIF(b21.dipendenti_totali, 0), 2) AS delta_pct_2023_vs_2021
FROM base b23
LEFT JOIN base b21
  ON b23.comparto = b21.comparto
 AND b21.anno = '2021'
WHERE b23.anno = '2023'
ORDER BY b23.dipendenti_totali DESC
```

## Dove si concentra la crescita 2023 vs 2021

Questo è il blocco principale della pagina: mostra in quali comparti si concentra davvero l'aumento degli organici nel triennio.

<BarChart data={delta_comparti} x=comparto y=delta_2023_vs_2021 yAxisTitle="Delta dipendenti 2023 vs 2021" swapXY=true />

<div class="section-note">
Il confronto usa il 2021 come anno base: è una scelta utile per leggere il triennio, ma va interpretata con cautela perché il primo anno resta ancora vicino alla fase post-COVID e ai suoi assestamenti.
</div>

## Quanto pesa il comparto selezionato nel totale

La linea mostra come cambia nel triennio la quota del comparto selezionato sul totale dei dipendenti pubblici.

<Dropdown name=comparto_sel data={comparti_list} value=comparto_id label=comparto defaultValue={1} />

<LineChart data={quota_comparto_trend} x=anno y=quota_su_totale_pct xAxisTitle="Anno" yAxisTitle="% sul totale dei dipendenti pubblici" />

<div class="section-note">
Il perimetro della pagina resta volutamente stretto: qui leggiamo la dinamica per comparto, non ancora la distribuzione ente per ente. Alcuni perimetri del pubblico impiego possono avere coperture o trattamenti diversi nella fonte BDAP / RGS, quindi qui conviene leggere i comparti come grandi aggregati comparabili, non come censimento totale di ogni amministrazione.
</div>

## Turnover e composizione nel 2023

La tabella finale aiuta a leggere insieme stock, saldo netto, tassi di entrata/uscita, quota donne e crescita percentuale 2023 vs 2021 per comparto.

<DataTable data={turnover_2023} rows=20 search=true downloadable=true />

## Risorse e dati

- [Scarica il clean parquet 2023](https://storage.googleapis.com/dataciviclab-clean/dipendenti_pubblici_2021_2023/2023/dipendenti_pubblici_2021_2023_2023_clean.parquet)
- [Fonte originale: BDAP / RGS — Dipendenti pubblici](https://bdap-opendata.rgs.mef.gov.it/)

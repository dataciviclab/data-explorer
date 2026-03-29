---
title: Rifiuti urbani nei comuni
description: Lettura pubblica dei dati ISPRA su rifiuti urbani, raccolta differenziata e volumi per territorio.
source: ISPRA
last_modified: 2026-03-24
discussion_url: https://github.com/dataciviclab/dataciviclab/discussions/22
analisi_url: https://github.com/dataciviclab/progetto-pilota
---

Questo dataset raccoglie i dati ISPRA sui rifiuti urbani dei comuni italiani.

<div class="guide-question">Il mio comune raccoglie bene i rifiuti?</div>

```sql anni
SELECT DISTINCT anno FROM ispra_ru.rifiuti ORDER BY anno DESC
```

<Dropdown name=anno_sel data={anni} value=anno>
</Dropdown>

```sql sintesi_regioni
SELECT
  regione,
  ROUND(SUM(totale_ru_tonnellate), 0) AS totale_ru_tonnellate,
  ROUND(SUM(totale_rd_tonnellate), 0) AS totale_rd_tonnellate,
  ROUND(SUM(totale_rd_tonnellate) / NULLIF(SUM(totale_ru_tonnellate), 0) * 100, 1) AS quota_rd
FROM ispra_ru.rifiuti
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY regione
ORDER BY quota_rd DESC
```

```sql grandi_comuni
SELECT
  regione,
  comune,
  popolazione,
  ROUND(percentuale_rd, 1) AS percentuale_rd,
  ROUND(totale_ru_tonnellate, 0) AS totale_ru_tonnellate
FROM ispra_ru.rifiuti
WHERE anno = '${inputs.anno_sel.value}'
  AND popolazione >= 100000
ORDER BY percentuale_rd DESC, totale_ru_tonnellate DESC
LIMIT 20
```

## Regioni: quota di raccolta differenziata

La classifica per regione usa una quota calcolata sui volumi complessivi, non una semplice media dei comuni. Questo rende il confronto più leggibile quando i comuni hanno dimensioni molto diverse.

<BarChart data={sintesi_regioni} x=regione y=quota_rd yAxisTitle="% raccolta differenziata" swapXY=true />

```sql regioni_select
SELECT 0 AS regione_id, 'Tutte le regioni' AS regione
UNION ALL
SELECT ROW_NUMBER() OVER (ORDER BY regione) AS regione_id, regione
FROM (
  SELECT DISTINCT regione
  FROM ispra_ru.rifiuti
) t
ORDER BY regione_id
```

<Dropdown name=regione_sel data={regioni_select} value=regione_id label=regione defaultValue={0} />

```sql comuni_scatter
WITH regioni_scelta AS (
  SELECT 0 AS regione_id, 'Tutte le regioni' AS regione
  UNION ALL
  SELECT ROW_NUMBER() OVER (ORDER BY regione) AS regione_id, regione
  FROM (
    SELECT DISTINCT regione
    FROM ispra_ru.rifiuti
  ) t
),
regione_scelta AS (
  SELECT regione
  FROM regioni_scelta
  WHERE regione_id = ${inputs.regione_sel.value}
),
base AS (
  SELECT
    regione,
    comune,
    popolazione,
    ROUND(percentuale_rd, 1) AS percentuale_rd,
    ROUND(CAST(totale_ru_tonnellate AS DOUBLE) * 1000.0 / NULLIF(popolazione, 0), 1) AS kg_per_abitante,
    ROUND(totale_ru_tonnellate, 0) AS totale_ru_tonnellate
  FROM ispra_ru.rifiuti
  WHERE anno = '${inputs.anno_sel.value}'
    AND (
      ${inputs.regione_sel.value} = 0
      OR regione = (SELECT regione FROM regione_scelta)
    )
)
SELECT *
FROM base
ORDER BY percentuale_rd DESC, kg_per_abitante DESC
```

## Scatter %RD vs kg/ab

La dispersione aiuta a leggere insieme qualità della raccolta e quantità prodotta per abitante. Il filtro regione controlla sia lo scatter sia la tabella di dettaglio.

<ScatterPlot data={comuni_scatter} x=kg_per_abitante y=percentuale_rd series=regione xAxisTitle="kg per abitante" yAxisTitle="% raccolta differenziata" pointSize=6 />

## Comuni della regione selezionata

La tabella usa lo stesso filtro della dispersione per scendere nel dettaglio dei comuni più interessanti nell'area scelta.

<DataTable data={comuni_scatter} rows=25 search=true downloadable=true />

## Grandi comuni

Tra i comuni con almeno 100 mila abitanti, la tabella aiuta a vedere dove la raccolta differenziata resta alta anche su volumi più grandi.

<DataTable data={grandi_comuni} rows=20 search=true downloadable=true />

## Approfondisci

- [Discussione civica](https://github.com/dataciviclab/dataciviclab/discussions/22) - domanda aperta e commenti della community
- [Analisi completa](https://github.com/dataciviclab/progetto-pilota) - notebook e metodologia

## Risorse e dati

- [Scarica il clean parquet 2024](https://storage.googleapis.com/dataciviclab-clean/ispra_ru_base/2024/ispra_ru_base_2024_clean.parquet)
- [Fonte originale: ISPRA Catasto Rifiuti Urbani](https://www.catasto-rifiuti.isprambiente.it)

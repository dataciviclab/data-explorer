---
title: Mix elettrico per regione
description: Lettura pubblica dei dati Terna sul mix elettrico regionale e sul peso delle fonti nel sistema nazionale.
source: Terna
last_modified: 2026-03-24
discussion_url: https://github.com/dataciviclab/dataciviclab/discussions/115
analisi_url: https://github.com/dataciviclab/dataciviclab/tree/main/analisi/terna-electricity-by-source
---

Questo dataset raccoglie i dati Terna sulla produzione elettrica per fonte e regione.

<div class="guide-question">Com'e' composto il mix elettrico della mia regione?</div>

```sql anni
SELECT DISTINCT anno FROM terna.energia ORDER BY anno DESC
```

<Dropdown name=anno_sel data={anni} value=anno>
</Dropdown>

```sql fonti_nazionali
SELECT
  fonte,
  SUM(produzione_gwh) AS produzione_gwh
FROM terna.energia
WHERE anno = '${inputs.anno_sel.value}'
  AND tipo_produzione = 'Netta'
GROUP BY fonte
ORDER BY produzione_gwh DESC
```

```sql regioni_totale
SELECT
  regione,
  SUM(produzione_gwh) AS produzione_gwh
FROM terna.energia
WHERE anno = '${inputs.anno_sel.value}'
  AND tipo_produzione = 'Netta'
GROUP BY regione
ORDER BY produzione_gwh DESC
```

```sql macro_fonte
SELECT 0 AS macro_fonte_id, 'Tutte le fonti' AS macro_fonte
UNION ALL
SELECT 1 AS macro_fonte_id, 'Rinnovabili' AS macro_fonte
UNION ALL
SELECT 2 AS macro_fonte_id, 'Fossili' AS macro_fonte
ORDER BY macro_fonte_id
```

<Dropdown name=macro_fonte_sel data={macro_fonte} value=macro_fonte_id label=macro_fonte defaultValue={0} />

```sql mix_regionale
WITH classificato AS (
  SELECT
    regione,
    fonte,
    produzione_gwh,
    CASE
      WHEN fonte = 'Termoelettrico' THEN 'Fossili'
      WHEN fonte IN ('Idrico', 'Eolico', 'Fotovoltaico', 'Geotermoelettrico') THEN 'Rinnovabili'
      ELSE 'Altre fonti / accumulo'
    END AS macro_fonte
  FROM terna.energia
  WHERE anno = '${inputs.anno_sel.value}'
    AND tipo_produzione = 'Netta'
),
filtrato AS (
  SELECT *
  FROM classificato
  WHERE ${inputs.macro_fonte_sel.value} = 0
     OR (${inputs.macro_fonte_sel.value} = 1 AND macro_fonte = 'Rinnovabili')
     OR (${inputs.macro_fonte_sel.value} = 2 AND macro_fonte = 'Fossili')
),
totali_regione AS (
  SELECT
    regione,
    SUM(produzione_gwh) AS totale_regionale
  FROM filtrato
  GROUP BY regione
)
SELECT
  f.regione,
  f.fonte,
  f.macro_fonte,
  SUM(f.produzione_gwh) AS produzione_gwh,
  ROUND(SUM(f.produzione_gwh) / NULLIF(t.totale_regionale, 0) * 100, 1) AS quota_percentuale
FROM filtrato f
JOIN totali_regione t
  ON f.regione = t.regione
GROUP BY f.regione, f.fonte, f.macro_fonte, t.totale_regionale
ORDER BY f.regione, quota_percentuale DESC, produzione_gwh DESC
```

<BarChart data={fonti_nazionali} x=fonte y=produzione_gwh yAxisTitle="Produzione GWh" />

<BarChart data={regioni_totale} x=regione y=produzione_gwh yAxisTitle="Produzione GWh" swapXY=true />

<BarChart data={mix_regionale} x=regione y=produzione_gwh series=fonte type="stacked100" swapXY=true yAxisTitle="% del totale regionale" xLabelWrap=12 />

<DataTable data={mix_regionale} rows=30 search=true downloadable=true />

## Approfondisci

- [Discussione civica](https://github.com/dataciviclab/dataciviclab/discussions/115)
- [Analisi completa](https://github.com/dataciviclab/dataciviclab/tree/main/analisi/terna-electricity-by-source)

## Risorse e dati

- [Scarica il clean parquet 2024](https://storage.googleapis.com/dataciviclab-clean/terna_capacita_rinnovabile/2024/terna_capacita_rinnovabile_2024_clean.parquet)
- [Fonte originale: Terna](https://dati.terna.it)

---
title: Rifiuti urbani nei comuni
---

Dati ISPRA sui rifiuti urbani dei comuni italiani. In questa pagina la domanda guida è semplice: dove la raccolta differenziata pesa di più e quali territori concentrano i volumi maggiori.

```sql anni
SELECT DISTINCT anno FROM ispra_ru.rifiuti ORDER BY anno DESC
```

<Dropdown name=anno_sel data={anni} value=anno>
  <DropdownOption value="2024" valueLabel="2024" />
  <DropdownOption value="2023" valueLabel="2023" />
  <DropdownOption value="2022" valueLabel="2022" />
  <DropdownOption value="2021" valueLabel="2021" />
  <DropdownOption value="2020" valueLabel="2020" />
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

<BarChart data={sintesi_regioni} x=regione y=quota_rd yAxisTitle="% raccolta differenziata" />

## Grandi comuni

Tra i comuni con almeno 100 mila abitanti, la tabella aiuta a vedere dove la raccolta differenziata resta alta anche su volumi più grandi.

<DataTable data={grandi_comuni} rows=20 search=true downloadable=true />

[Scarica il clean parquet 2024](https://storage.googleapis.com/dataciviclab-clean/ispra_ru_base/2024/ispra_ru_base_2024_clean.parquet)

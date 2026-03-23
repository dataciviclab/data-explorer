---
title: Rifiuti urbani nei comuni
---

# Rifiuti urbani nei comuni

Dati ISPRA sui rifiuti urbani dei comuni italiani. Il v0 permette di leggere rapidamente raccolta differenziata e volumi totali sul periodo 2020-2024.

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

```sql top_comuni
SELECT
  regione,
  comune,
  popolazione,
  ROUND(percentuale_rd, 1) AS percentuale_rd,
  totale_ru_tonnellate
FROM ispra_ru.rifiuti
WHERE anno = '${inputs.anno_sel.value}'
ORDER BY percentuale_rd DESC
LIMIT 20
```

```sql rd_per_regione
SELECT
  regione,
  ROUND(AVG(percentuale_rd), 1) AS media_rd
FROM ispra_ru.rifiuti
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY regione
ORDER BY media_rd DESC
```

## Raccolta differenziata media per regione

<BarChart data={rd_per_regione} x=regione y=media_rd yAxisTitle="% raccolta differenziata" />

## Comuni

<DataTable data={top_comuni} rows=20 search=true downloadable=true />

[Scarica il clean parquet 2024](https://storage.googleapis.com/dataciviclab-clean/ispra_ru_base/2024/ispra_ru_base_2024_clean.parquet)

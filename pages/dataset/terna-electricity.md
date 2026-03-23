---
title: Mix elettrico per regione
---

Dati Terna sulla produzione elettrica per fonte e regione. Il v0 permette di confrontare il mix regionale 2023-2024.

```sql anni
SELECT DISTINCT anno FROM terna.energia ORDER BY anno DESC
```

<Dropdown name=anno_sel data={anni} value=anno>
  <DropdownOption value="2024" valueLabel="2024" />
  <DropdownOption value="2023" valueLabel="2023" />
</Dropdown>

```sql fonti
SELECT
  regione,
  fonte,
  SUM(produzione_gwh) AS produzione_gwh
FROM terna.energia
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY regione, fonte
ORDER BY produzione_gwh DESC
```

```sql regioni_totale
SELECT
  regione,
  SUM(produzione_gwh) AS produzione_gwh
FROM terna.energia
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY regione
ORDER BY produzione_gwh DESC
```

## Produzione totale per regione

<BarChart data={regioni_totale} x=regione y=produzione_gwh yAxisTitle="Produzione GWh" />

## Mix per fonte

<DataTable data={fonti} rows=30 search=true downloadable=true />

[Scarica il clean parquet 2024](https://storage.googleapis.com/dataciviclab-clean/terna_electricity_by_source/2024/terna_electricity_by_source_2024_clean.parquet)

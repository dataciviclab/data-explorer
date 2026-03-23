---
title: Flussi della giustizia civile
---

# Flussi della giustizia civile

Dati del Ministero della Giustizia sui flussi civili. Nel v0 il focus è sugli anni disponibili nel clean pubblico e sui principali aggregati per distretto e materia.

```sql anni
SELECT DISTINCT anno FROM civile_flussi.flussi ORDER BY anno DESC
```

<Dropdown name=anno_sel data={anni} value=anno>
  <DropdownOption value="2024" valueLabel="2024" />
  <DropdownOption value="2023" valueLabel="2023" />
  <DropdownOption value="2022" valueLabel="2022" />
  <DropdownOption value="2021" valueLabel="2021" />
  <DropdownOption value="2020" valueLabel="2020" />
  <DropdownOption value="2019" valueLabel="2019" />
  <DropdownOption value="2018" valueLabel="2018" />
  <DropdownOption value="2017" valueLabel="2017" />
  <DropdownOption value="2016" valueLabel="2016" />
  <DropdownOption value="2015" valueLabel="2015" />
  <DropdownOption value="2014" valueLabel="2014" />
</Dropdown>

```sql distretti
SELECT
  distretto,
  SUM(sopravvenuti) AS sopravvenuti,
  SUM(definiti_totale) AS definiti_totale,
  SUM(pendenti_finali) AS pendenti_finali
FROM civile_flussi.flussi
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY distretto
ORDER BY pendenti_finali DESC
```

```sql materie
SELECT
  macromateria,
  SUM(sopravvenuti) AS sopravvenuti,
  SUM(definiti_totale) AS definiti_totale
FROM civile_flussi.flussi
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY macromateria
ORDER BY sopravvenuti DESC
LIMIT 15
```

## Pendenti finali per distretto

<BarChart data={distretti} x=distretto y=pendenti_finali yAxisTitle="Pendenti finali" />

## Macromaterie

<DataTable data={materie} rows=15 search=true downloadable=true />

[Scarica il clean parquet 2024](https://storage.googleapis.com/dataciviclab-clean/civile_flussi_2014_2024/2024/civile_flussi_2014_2024_2024_clean.parquet)

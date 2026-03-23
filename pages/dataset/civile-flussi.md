# Flussi della giustizia civile

Dati del Ministero della Giustizia sui flussi civili. Nel v0 il focus è sul 2024 e sui principali aggregati per distretto e materia.

```sql distretti
SELECT
  distretto,
  SUM(sopravvenuti) AS sopravvenuti,
  SUM(definiti_totale) AS definiti_totale,
  SUM(pendenti_finali) AS pendenti_finali
FROM civile_flussi.flussi
GROUP BY distretto
ORDER BY pendenti_finali DESC
```

```sql materie
SELECT
  macromateria,
  SUM(sopravvenuti) AS sopravvenuti,
  SUM(definiti_totale) AS definiti_totale
FROM civile_flussi.flussi
GROUP BY macromateria
ORDER BY sopravvenuti DESC
LIMIT 15
```

## Pendenti finali per distretto

<BarChart data={distretti} x=distretto y=pendenti_finali yAxisTitle="Pendenti finali" />

## Macromaterie

<DataTable data={materie} rows=15 search=true downloadable=true />

[Scarica il clean parquet 2024](https://storage.googleapis.com/dataciviclab-clean/civile_flussi_2014_2024/2024/civile_flussi_2014_2024_2024_clean.parquet)

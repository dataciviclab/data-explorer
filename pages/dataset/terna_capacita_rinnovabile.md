---
title: Mix elettrico per regione
description: Lettura pubblica dei dati Terna sulla capacita' rinnovabile installata per regione e fonte.
source: Terna
last_modified: 2026-03-24
discussion_url: https://github.com/dataciviclab/dataciviclab/discussions/115
analisi_url: https://github.com/dataciviclab/dataciviclab/tree/main/analisi/terna-electricity-by-source
---

Questo dataset raccoglie i dati Terna sulla capacita' di generazione rinnovabile installata per regione e fonte.

<div class="guide-question">Quali fonti rinnovabili hanno piu' capacita' installata nella mia regione?</div>

```sql anni
SELECT DISTINCT anno FROM terna.energia ORDER BY anno DESC
```

<Dropdown name=anno_sel data={anni} value=anno>
</Dropdown>

```sql fonti_nazionali
SELECT
  fonti,
  SUM(potenza_mw) AS potenza_mw
FROM terna.energia
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY fonti
ORDER BY potenza_mw DESC
```

```sql regioni_totale
SELECT
  regione,
  SUM(potenza_mw) AS potenza_mw
FROM terna.energia
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY regione
ORDER BY potenza_mw DESC
```

```sql mix_regionale
SELECT
  regione,
  fonti,
  SUM(potenza_mw) AS potenza_mw,
  ROUND(SUM(potenza_mw) / SUM(SUM(potenza_mw)) OVER (PARTITION BY regione) * 100, 1) AS quota_percentuale
FROM terna.energia
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY regione, fonti
ORDER BY regione, potenza_mw DESC
```

## Fonti per capacita' installata a livello nazionale

<BarChart data={fonti_nazionali} x=fonti y=potenza_mw yAxisTitle="Potenza installata (MW)" />

## Capacita' totale per regione

<BarChart data={regioni_totale} x=regione y=potenza_mw yAxisTitle="Potenza installata (MW)" swapXY=true />

## Mix regionale per fonte

<BarChart data={mix_regionale} x=regione y=potenza_mw series=fonti type="stacked100" swapXY=true yAxisTitle="% del totale regionale" xLabelWrap=12 />

<DataTable data={mix_regionale} rows=30 search=true downloadable=true />

## Approfondisci

- [Discussione civica](https://github.com/dataciviclab/dataciviclab/discussions/115)
- [Analisi completa](https://github.com/dataciviclab/dataciviclab/tree/main/analisi/terna-electricity-by-source)

## Risorse e dati

- [Scarica il clean parquet 2024](https://storage.googleapis.com/dataciviclab-clean/terna_capacita_rinnovabile/2024/terna_capacita_rinnovabile_2024_clean.parquet)
- [Fonte originale: Terna](https://dati.terna.it)

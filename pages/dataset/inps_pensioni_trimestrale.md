---
title: Pensioni INPS
description: Lettura pubblica delle pensioni INPS per gestione, regione, classe d'età e importo — 2020-2024.
source: INPS Open Data
last_modified: 2026-05-14
---

Questo dataset raccoglie il numero di pensioni INPS per gestione previdenziale, regione, sesso, classe d'età e classe di importo, con cadenza trimestrale dal 2020 al 2024.

<div class="guide-question">Come sono distribuite le pensioni INPS tra gestioni, aree geografiche e categorie?</div>

```sql anni
SELECT DISTINCT CAST(anno AS INTEGER) AS anno FROM inps_pensioni_trimestrale.pensioni ORDER BY anno DESC
```

<Dropdown name=anno_sel data={anni} value=anno>
</Dropdown>

```sql distribuzione_gestione
SELECT
  gestione,
  ROUND(SUM(numero_pensioni) / 1e6, 2) AS pensioni_milioni
FROM inps_pensioni_trimestrale.pensioni
WHERE CAST(anno AS INTEGER) = ${inputs.anno_sel.value}
GROUP BY gestione
ORDER BY pensioni_milioni DESC
```

```sql distribuzione_area
SELECT
  area_geografica,
  sesso,
  ROUND(SUM(numero_pensioni) / 1e6, 2) AS pensioni_milioni
FROM inps_pensioni_trimestrale.pensioni
WHERE CAST(anno AS INTEGER) = ${inputs.anno_sel.value}
GROUP BY area_geografica, sesso
ORDER BY area_geografica, sesso
```

```sql trend_pensioni
SELECT
  CAST(anno AS INTEGER) AS anno,
  ROUND(SUM(numero_pensioni) / 1e6, 2) AS pensioni_milioni
FROM inps_pensioni_trimestrale.pensioni
GROUP BY anno
ORDER BY anno
```

## Pensioni per gestione

<BarChart data={distribuzione_gestione} x=gestione y=pensioni_milioni yAxisTitle="Pensioni (milioni)" swapXY=true />

La gestione **FPLD** (Fondo Pensioni Lavoratori Dipendenti) è la componente prevalente, seguita dai Dipendenti Pubblici, Artigiani e Commercianti.

## Distribuzione per area geografica e sesso

<BarChart data={distribuzione_area} x=area_geografica y=pensioni_milioni series=sesso yAxisTitle="Pensioni (milioni)" />

## Andamento annuale

<LineChart data={trend_pensioni} x=anno y=pensioni_milioni yAxisTitle="Pensioni (milioni)" />

## Dettaglio

<DataTable data={distribuzione_gestione} rows=20 search=true downloadable=true />

## Risorse e dati

- [Scarica il clean parquet](https://storage.googleapis.com/dataciviclab-clean/inps_pensioni_trimestrale/2024/inps_pensioni_trimestrale_2024_clean.parquet)
- [Fonte originale: INPS](https://www.inps.it)

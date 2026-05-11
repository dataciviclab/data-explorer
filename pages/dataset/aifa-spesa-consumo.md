---
title: Spesa farmaceutica convenzionata
description: Lettura pubblica dei dati AIFA su spesa e consumo della farmaceutica convenzionata SSN per regione e classe terapeutica.
source: AIFA — Open Data Spesa e Consumo Farmaceutico
last_modified: 2026-05-11
---

Questo dataset raccoglie i dati AIFA sulla spesa e il consumo della farmaceutica convenzionata SSN, disaggregati per regione, mese e classe terapeutica ATC.

<div class="guide-question">Come cambia tra regioni e nel tempo la spesa farmaceutica per classi terapeutiche?</div>

```sql anni
SELECT DISTINCT CAST(anno AS INTEGER) AS anno FROM aifa_spesa_consumo.spesa ORDER BY anno DESC
```

<Dropdown name=anno_sel data={anni} value=anno>
</Dropdown>

```sql spesa_per_regione
SELECT
  regione,
  ROUND(SUM(spesa_convenzionata) / 1e6, 2) AS spesa_ml_eur,
  ROUND(SUM(numero_confezioni_convenzionata) / 1e6, 2) AS confezioni_ml
FROM aifa_spesa_consumo.spesa
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY regione
ORDER BY spesa_ml_eur DESC
```

```sql top_classi_atc1
SELECT
  descrizione_atc1,
  ROUND(SUM(spesa_convenzionata) / 1e6, 2) AS spesa_ml_eur
FROM aifa_spesa_consumo.spesa
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY descrizione_atc1
ORDER BY spesa_ml_eur DESC
LIMIT 10
```

```sql spesa_mensile
SELECT
  mese,
  regione,
  ROUND(SUM(spesa_convenzionata) / 1e6, 2) AS spesa_ml_eur,
  ROUND(SUM(numero_confezioni_convenzionata) / 1e6, 2) AS confezioni_ml
FROM aifa_spesa_consumo.spesa
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY mese, regione
ORDER BY mese, spesa_ml_eur DESC
```

## Spesa farmaceutica per regione

La classifica regionale mostra dove si concentra la spesa complessiva. Il valore è in milioni di euro.

<BarChart data={spesa_per_regione} x=regione y=spesa_ml_eur yAxisTitle="Spesa (M€)" swapXY=true />

## Top 10 classi terapeutiche ATC1

Le classi a maggiore spesa nell'anno selezionato, calcolate sul totale nazionale.

<BarChart data={top_classi_atc1} x=descrizione_atc1 y=spesa_ml_eur yAxisTitle="Spesa (M€)" swapXY=true />

## Andamento mensile

L'evoluzione della spesa mese per mese per le principali regioni.

<LineChart data={spesa_mensile} x=mese y=spesa_ml_eur series=regione yAxisTitle="Spesa (M€)" />

<div class="section-note">
I dati si riferiscono al canale della <strong>farmaceutica convenzionata</strong> (prescrizioni SSN dispensate in farmacia). Sono esclusi gli acquisti diretti e il canale tracciabilità.
</div>

## Dettaglio mensile per regione

<DataTable data={spesa_mensile} rows=30 search=true downloadable=true />

## Risorse e dati

- [Scarica il clean parquet 2024](https://storage.googleapis.com/dataciviclab-clean/aifa_spesa_consumo/2024/aifa_spesa_consumo_2024_clean.parquet)
- [Fonte originale: AIFA — Open Data Spesa e Consumo Farmaceutico](https://www.aifa.gov.it/documents/20142/847578/dati2024_04.12.2025.csv)
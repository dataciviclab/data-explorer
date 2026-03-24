---
title: Flussi della giustizia civile
description: Lettura pubblica dei flussi civili del Ministero della Giustizia, con focus su carico, pendenti e materie.
source: Ministero della Giustizia
last_modified: 2026-03-24
---

Questo dataset raccoglie i dati del Ministero della Giustizia sui flussi civili.

<div class="guide-question">La giustizia civile nel mio distretto sta migliorando?</div>

```sql anni
SELECT DISTINCT anno FROM civile_flussi.flussi ORDER BY anno DESC
```

<Dropdown name=anno_sel data={anni} value=anno>
</Dropdown>

```sql distretti
SELECT
  distretto,
  SUM(sopravvenuti) AS sopravvenuti,
  SUM(definiti_totale) AS definiti_totale,
  SUM(pendenti_finali) AS pendenti_finali,
  ROUND(SUM(definiti_totale) / NULLIF(SUM(sopravvenuti), 0), 2) AS rapporto_definiti_sopravvenuti
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

```sql distretti_tenuta
SELECT
  distretto,
  SUM(sopravvenuti) AS sopravvenuti,
  SUM(definiti_totale) AS definiti_totale,
  ROUND(SUM(definiti_totale) / NULLIF(SUM(sopravvenuti), 0), 2) AS rapporto_definiti_sopravvenuti
FROM civile_flussi.flussi
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY distretto
ORDER BY rapporto_definiti_sopravvenuti ASC, sopravvenuti DESC
LIMIT 15
```

## Pendenti finali per distretto

Questo è il blocco principale della pagina: mostra dove il carico finale resta più pesante nell'anno selezionato.

<BarChart data={distretti} x=distretto y=pendenti_finali yAxisTitle="Pendenti finali" swapXY=true />

```sql distretti_trend
SELECT
  ROW_NUMBER() OVER (ORDER BY distretto) AS distretto_id,
  distretto
FROM (
  SELECT DISTINCT distretto
  FROM civile_flussi.flussi
) t
ORDER BY distretto
```

<Dropdown name=distretto_sel data={distretti_trend} value=distretto_id label=distretto defaultValue={1} />

```sql pendenti_trend
WITH distretti_scelti AS (
  SELECT
    ROW_NUMBER() OVER (ORDER BY distretto) AS distretto_id,
    distretto
  FROM (
    SELECT DISTINCT distretto
    FROM civile_flussi.flussi
  ) t
)
SELECT
  CAST(anno AS INTEGER) AS anno,
  'Nazionale' AS serie,
  SUM(pendenti_finali) AS pendenti_finali
FROM civile_flussi.flussi
GROUP BY 1, 2
UNION ALL
SELECT
  CAST(f.anno AS INTEGER) AS anno,
  d.distretto AS serie,
  SUM(f.pendenti_finali) AS pendenti_finali
FROM civile_flussi.flussi f
JOIN distretti_scelti d
  ON f.distretto = d.distretto
WHERE d.distretto_id = ${inputs.distretto_sel.value}
GROUP BY 1, 2
ORDER BY anno, serie
```

## Pendenti nel tempo

La linea mette a confronto il totale nazionale con il distretto selezionato. Serve a capire se il carico finale si sta alleggerendo nel tempo o se il distretto resta sopra la media.

<LineChart data={pendenti_trend} x=anno y=pendenti_finali series=serie xAxisTitle="Anno" yAxisTitle="Pendenti finali" />

## Distretti dove i definiti tengono meno

Un rapporto vicino a `1` indica che i procedimenti definiti sono simili ai sopravvenuti dell'anno. Valori più bassi suggeriscono maggiore difficoltà a riassorbire il flusso in entrata.

<DataTable data={distretti_tenuta} rows=15 search=true downloadable=true />

## Macromaterie più pesanti

<div class="method-note">
Le <strong>Procedure concorsuali (pre-riforma)</strong> possono mostrare nuovi arrivi quasi nulli ma molti definiti:
non è un buco nei dati, ma l'effetto della riforma che ha chiuso progressivamente il perimetro precedente.
</div>

<div class="section-note">
Da qui cambia anche la granularità della lettura: non stiamo più confrontando i distretti,
ma le aree del contenzioso a livello nazionale nell'anno selezionato.
</div>

La tabella finale serve come terzo livello di lettura: aiuta a capire quali aree del contenzioso pesano di più nei flussi recenti.

<DataTable data={materie} rows=15 search=true downloadable=true />

## Risorse e dati

- [Scarica il clean parquet 2024](https://storage.googleapis.com/dataciviclab-clean/civile_flussi_2014_2024/2024/civile_flussi_2014_2024_2024_clean.parquet)
- [Fonte originale: Ministero della Giustizia — statistiche civili](https://datiestatistiche.giustizia.it)

---
title: Flussi della giustizia civile
description: Lettura pubblica dei flussi civili del Ministero della Giustizia, con focus su carico, pendenti e materie.
source: Ministero della Giustizia
last_modified: 2026-03-26
discussion_url: https://github.com/dataciviclab/dataciviclab/discussions/94
analisi_url: https://github.com/dataciviclab/dataciviclab/tree/main/analisi/civile-flussi
---

Questo dataset raccoglie i dati del Ministero della Giustizia sui flussi civili nei tribunali distrettuali italiani.

<div class="guide-question">Come si distribuisce il carico civile tra i distretti italiani?</div>

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

<BarChart data={distretti} x=distretto y=pendenti_finali yAxisTitle="Pendenti finali" swapXY=true />

<DataTable data={distretti_tenuta} rows=15 search=true downloadable=true />

<DataTable data={materie} rows=15 search=true downloadable=true />

## Approfondisci

- [Discussione civica](https://github.com/dataciviclab/dataciviclab/discussions/94)
- [Analisi completa](https://github.com/dataciviclab/dataciviclab/tree/main/analisi/civile-flussi)

## Risorse e dati

- [Scarica il clean parquet](https://storage.googleapis.com/dataciviclab-clean/civile_flussi/2025/civile_flussi_2025_clean.parquet)
- [Fonte originale: Ministero della Giustizia](https://datiestatistiche.giustizia.it)

---
title: Entrate dello Stato
description: Lettura pubblica delle entrate statali da BDAP, per titolo, natura e tipologia — 2008-2024.
source: MEF-BDAP
last_modified: 2026-04-26
discussion_url: https://github.com/dataciviclab/dataciviclab/discussions/218
---

Questo dataset raccoglie le entrate dello Stato italiano dal 2008 al 2024, aggregate per titolo, natura, tipologia e provento, secondo le previsioni definitive del bilancio dello Stato (competenza e cassa).

<div class="guide-question">Come si compongono le entrate dello Stato e come cambia la struttura nel tempo tra entrate tributarie, extra-tributarie e ricorso al debito?</div>

```sql anni
SELECT DISTINCT CAST(anno AS INTEGER) AS anno FROM bdap_entrate_stato.entrate ORDER BY anno DESC
```

<Dropdown name=anno_sel data={anni} value=anno>
</Dropdown>

```sql composizione_titoli
SELECT
  titolo,
  ROUND(SUM(previsioni_definitive_cp) / 1e9, 1) AS previsioni_mld
FROM bdap_entrate_stato.entrate
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY titolo, codice_titolo
ORDER BY codice_titolo
```

```sql trend_entrate
SELECT
  CAST(anno AS INTEGER) AS anno,
  ROUND(SUM(previsioni_definitive_cp) / 1e9, 1) AS entrate_totali_mld
FROM bdap_entrate_stato.entrate
GROUP BY anno
ORDER BY anno
```

```sql dettaglio_anno
SELECT
  titolo,
  natura,
  tipologia,
  ROUND(SUM(previsioni_definitive_cp) / 1e9, 2) AS previsioni_mld
FROM bdap_entrate_stato.entrate
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY titolo, natura, tipologia, codice_titolo
ORDER BY codice_titolo, previsioni_mld DESC
```

## Composizione entrate per titolo

<BarChart data={composizione_titoli} x=titolo y=previsioni_mld yAxisTitle="Previsioni (mld EUR)" swapXY=true />

La composizione delle entrate dello Stato si divide in quattro titoli: **entrate tributarie** (la componente principale, che include imposte dirette e indirette), **entrate extra-tributarie** (proventi da servizi, canoni, multe), **alienazione di beni** (cessione di beni patrimoniali e riscossione crediti), e **accensione di prestiti** (nuovo debito pubblico per coprire il fabbisogno).

## Serie storica entrate totali

<LineChart data={trend_entrate} x=anno y=entrate_totali_mld yAxisTitle="Entrate totali (mld EUR)" />

L'andamento delle entrate totali mostra una crescita strutturale ma con due salti significativi: il primo nel 2009-2010 (crisi finanziaria) e il secondo, più marcato, dal 2020 in poi (pandemia e Next Generation EU), dove l'accensione di prestiti ha ampliato significativamente il volume complessivo delle entrate in bilancio.

## Dettaglio per titolo, natura e tipologia

<DataTable data={dettaglio_anno} rows=30 search=true downloadable=true />

## Risorse e dati

- [Scarica il clean parquet](https://storage.googleapis.com/dataciviclab-clean/bdap_entrate_stato/2024/bdap_entrate_stato_2024_clean.parquet)
- [Fonte originale: MEF-BDAP](https://www.bdap-bilancio.tesoro.it/)
- [Discussione pubblica](https://github.com/dataciviclab/dataciviclab/discussions/218)

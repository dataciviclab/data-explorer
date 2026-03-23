---
title: Flussi della giustizia civile
description: Lettura pubblica dei flussi civili del Ministero della Giustizia, con focus su carico, pendenti e materie.
source: Ministero della Giustizia
last_modified: 2026-03-23
---

Questo dataset raccoglie i dati del Ministero della Giustizia sui flussi civili.

Domanda guida: dove il carico resta più alto e dove i procedimenti definiti tengono il passo dei nuovi arrivi.

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

<BarChart data={distretti} x=distretto y=pendenti_finali yAxisTitle="Pendenti finali" />

## Distretti dove i definiti tengono meno

Un rapporto vicino a `1` indica che i procedimenti definiti sono simili ai sopravvenuti dell'anno. Valori più bassi suggeriscono maggiore difficoltà a riassorbire il flusso in entrata.

<DataTable data={distretti_tenuta} rows=15 search=true downloadable=true />

## Macromaterie più pesanti

La tabella finale serve come terzo livello di lettura: aiuta a capire quali aree del contenzioso pesano di più nei flussi recenti.

<DataTable data={materie} rows=15 search=true downloadable=true />

[Scarica il clean parquet 2024](https://storage.googleapis.com/dataciviclab-clean/civile_flussi_2014_2024/2024/civile_flussi_2014_2024_2024_clean.parquet)

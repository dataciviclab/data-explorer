---
title: Mix elettrico per regione
description: Lettura pubblica dei dati Terna sul mix elettrico regionale e sul peso delle fonti nel sistema nazionale.
source: Terna
last_modified: 2026-03-24
---

Questo dataset raccoglie i dati Terna sulla produzione elettrica per fonte e regione.

*Domanda guida: quali fonti pesano di più nel mix nazionale e quali regioni concentrano la produzione.*

```sql anni
SELECT DISTINCT anno FROM terna.energia ORDER BY anno DESC
```

<Dropdown name=anno_sel data={anni} value=anno>
  <DropdownOption value="2024" valueLabel="2024" />
  <DropdownOption value="2023" valueLabel="2023" />
</Dropdown>

```sql fonti_nazionali
SELECT
  fonte,
  SUM(produzione_gwh) AS produzione_gwh
FROM terna.energia
WHERE anno = '${inputs.anno_sel.value}'
GROUP BY fonte
ORDER BY produzione_gwh DESC
```

```sql fonti_regionali
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

## Fonti più pesanti a livello nazionale

Aiuta a capire quali fonti dominano il mix complessivo nell'anno selezionato, prima di scendere nel dettaglio regionale.

<BarChart data={fonti_nazionali} x=fonte y=produzione_gwh yAxisTitle="Produzione GWh" />

## Produzione totale per regione

Il confronto tra regioni mostra dove si concentra la capacita' produttiva complessiva, indipendentemente dalla fonte.

<BarChart data={regioni_totale} x=regione y=produzione_gwh yAxisTitle="Produzione GWh" />

## Mix regionale per fonte

La tabella serve come terzo livello di lettura: dopo il quadro nazionale e quello regionale aggregato, permette di vedere dove ogni fonte pesa di più.

<DataTable data={fonti_regionali} rows=30 search=true downloadable=true />

## Risorse e dati

- [Scarica il clean parquet 2024](https://storage.googleapis.com/dataciviclab-clean/terna_electricity_by_source/2024/terna_electricity_by_source_2024_clean.parquet)
- [Fonte originale: Terna — Download Center](https://dati.terna.it)

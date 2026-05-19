---
title: DataCivicLab Explorer
description: Catalogo pubblico dei dataset civici del Lab
---

# DataCivicLab Explorer

Catalogo pubblico dei dataset civici. I dati sono puliti, documentati e disponibili in formato parquet.

```js
const catalog = await FileAttachment("data/catalog.json").json();
```

<div class="grid grid-cols-3">
  <div class="card"><h3>Totale</h3><span class="big">${catalog.total}</span></div>
  <div class="card"><h3>Pubblicati</h3><span class="big">${catalog.published}</span></div>
  <div class="card"><h3>In incubazione</h3><span class="big">${catalog.incubating}</span></div>
</div>

## Pagine curate

- [IRPEF comunale](/dataset/irpef-comunale) — capacità fiscale per comune e regione
- [Rifiuti urbani](/dataset/rifiuti-urbani) — produzione e raccolta differenziata per comune e regione
- [Flussi giustizia civile](/dataset/flussi-giustizia-civile) — sopravvenuti, definiti e pendenti per distretto
- [Dipendenti pubblici](/dataset/dipendenti-pubblici) — pubblico impiego per comparto (2010-2023)

<div style="margin-top: 2em; opacity: 0.6; font-size: 0.85em;">
Catalogo aggiornato: ${catalog.updated_at} · 
<a href="https://github.com/dataciviclab/dataset-incubator/tree/main/registry">clean_catalog.json</a>
</div>

---
title: Bandi di gara pubblici ANAC
description: "Bandi CIG 2016-2025 — lotti, importi, procedure e stazioni appaltanti (ANAC)"
source: ANAC - Autorità Nazionale Anticorruzione
source_url: https://dati.anticorruzione.it/
period: "2016–2025"
last_modified: 2026-08-20
dataset_slug: anac_bandi_gara
data_driven: true
---

# Bandi di gara pubblici — cosa ci dice l'ANAC

**In ${last} la PA italiana ha pubblicato ${num(lastTrend.n_lotti)} bandi di gara per un totale di ${numFix(lastTrend.importo_totale / 1e9, 0)} miliardi di euro di importo stimato. In 10 anni i lotti sono quadruplicati, ma l'importo medio si è dimezzato: è semplificazione del Codice Appalti o frammentazione della spesa?**

Bandi di gara registrati dall'ANAC attraverso il sistema CIG (Codice Identificativo Gara), 2016-2025. I dati mostrano quanti bandi vengono pubblicati, a quanto ammontano, come si distribuiscono per procedura e categoria, e dove finisce la spesa. I numeri sono calcolati dal dato a build-time: se si ripubblica il parquet, KPI e grafici si aggiornano da soli.

```js
import { num, numFix, pct, euroCompact, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/anac-bandi-gara.json").json();
const { trend, per_tipo: perTipo, per_oggetto: perOggetto, per_stato: perStato, top_sa: topSa } = data;
```

```js
const lastTrend = trend[trend.length - 1];
const firstTrend = trend[0];
const last = lastTrend.anno;
const first = firstTrend.anno;
```

```js
const trendN = trend.map(d => ({ anno: d.anno, lotti: d.n_lotti, importo: d.importo_totale }));
const tipoPerAnno = Array.from(
  d3.rollup(perTipo, v => ({ lotti: d3.sum(v, d => d.n_lotti), importo: d3.sum(v, d => d.importo) }), d => d.anno, d => d.tipo),
  ([anno, m]) => Array.from(m, ([tipo, v]) => ({ anno, tipo, ...v }))
).flat().sort((a, b) => a.anno - b.anno);
const tipoNorm = Array.from(
  d3.rollup(tipoPerAnno, v => {
    const tot = d3.sum(v, d => d.lotti);
    return { anno: v[0].anno, tipo: v[0].tipo, pct: tot ? v[0].lotti / tot * 100 : 0 };
  }),
  ([k, v]) => ({ anno: k[0], tipo: k[1], pct: v.pct })
).sort((a, b) => a.anno - b.anno);
const statoLast = perStato.filter(d => d.anno == last).sort((a, b) => b.n_lotti - a.n_lotti);
const saLast = topSa.filter(d => d.anno == last).sort((a, b) => b.importo - a.importo).slice(0, 20);
const mediaLotto = lastTrend.n_lotti > 0 ? lastTrend.importo_totale / lastTrend.n_lotti : null;
const deltaLottiPct = firstTrend.n_lotti ? ((lastTrend.n_lotti - firstTrend.n_lotti) / firstTrend.n_lotti * 100) : null;
```

<div class="grid grid-cols-4">
  <div class="card"><h3>Lotti ${last}</h3><span class="big">${num(lastTrend.n_lotti)}</span></div>
  <div class="card"><h3>Importo complessivo</h3><span class="big">${numFix(lastTrend.importo_totale / 1e9, 0)} mld</span></div>
  <div class="card"><h3>Media per lotto</h3><span class="big">${euroCompact(mediaLotto)}</span></div>
  <div class="card"><h3>Δ lotti ${first}→${last}</h3><span class="big">${deltaLottiPct >= 0 ? "+" : ""}${numFix(deltaLottiPct, 0)}%</span></div>
</div>

## 1. Trend decennale: una crescita esponenziale

Dal ${first} al ${last} il numero di bandi pubblicati è cresciuto costantemente, con un'accelerazione marcata dal 2023 in poi. L'importo totale segue lo stesso trend.

```js
const plot = await import("npm:@observablehq/plot");
```

```js
display(plot.plot({
  title: `Bandi di gara ANAC — lotti per anno (${first}–${last})`,
  width: 800, height: 350,
  x: {tickFormat: String, label: null},
  y: {grid: true, label: "Lotti"},
  marks: [
    plot.lineY(trendN, {x: "anno", y: "lotti", stroke: "#3182bd", strokeWidth: 2, tip: true}),
    plot.dot(trendN, {x: "anno", y: "lotti", fill: "#3182bd"}),
    plot.ruleY([0])
  ]
}))
```

La discontinuità dal 2023 riflette l'effetto del nuovo Codice Appalti (D.Lgs. 36/2023), che ha alzato le soglie per l'affidamento diretto, moltiplicando il numero di bandi mentre l'importo medio si dimezza.

---

## 2. Il mix delle procedure: dal ${first} al ${last}

Come cambia il tipo di procedura nel tempo? L'affidamento diretto è diventato la normalità — un cambiamento strutturale nel modo in cui la PA spende.

```js
display(plot.plot({
  title: "Mix procedurale per anno (100%)",
  width: 800, height: 400,
  x: {tickFormat: String, label: null},
  y: {grid: true, percent: true, label: "Quota su lotti"},
  color: {legend: true, scheme: "Set2"},
  marks: [
    plot.barY(tipoNorm, {x: "anno", y: "pct", fill: "tipo", stack: "normalize"})
  ]
}))
```

> Ogni barra è altezza 100% (tutti i lotti); i segmenti mostrano la quota relativa di ciascuna procedura. L'affidamento diretto cresce a scapito delle procedure aperte dopo il 2023.

---

## 3. Top stazioni appaltanti (${last})

Le stazioni appaltanti che gestiscono più bandi e valore. La Sezione Centrale ANAC (Consip e centrali di committenza) concentra la maggior parte della spesa.

```js
const { header, format } = tableFormat({
  denominazione: { label: "Stazione appaltante", fmt: "string" },
  n_lotti: { label: "Lotti", fmt: "num" },
  importo: { label: "Importo (€)", fmt: "euroCompact" }
});
```

```js
Inputs.table(saLast, {
  columns: ["denominazione", "n_lotti", "importo"],
  header, format, rows: 20, width: "100%",
  sort: "importo", reverse: true
})
```

---

## La domanda che resta

Il Codice Appalti 2023 ha semplificato le procedure, ma ha prodotto un effetto collaterale: la moltiplicazione degli affidamenti diretti con importi minori. È una semplificazione che riduce la concorrenza? E la qualità della spesa pubblica ne beneficia o ne risente?

---

## Limiti

- **Copertura**: 2016-2025; i dati sono i bandi pubblicati, non i contratti effettivamente stipulati
- **Importi**: valori stimati a pubblicazione; 65% dei lotti non ha `importo_lotto` — le somme escludono queste righe
- **Urgenza**: il flag urgenza è spesso compilato come "NON APPLICABILE"; vanno lette con cautela
- **Stato**: la Sezione Centrale ANAC corrisponde alla sede ANAC competente, non alla localizzazione della stazione appaltante

---

## Risorse

- [ANAC - dati aperti](https://dati.anticorruzione.it/)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/anac_bandi_gara/2024/anac_bandi_gara_2024_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/anac-bandi-gara)

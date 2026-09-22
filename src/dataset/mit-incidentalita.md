---
title: Incidenti stradali
description: Incidenti stradali, morti e feriti in Italia — serie mensile MIT 2001-2018, con indice di mortalità e stagionalità
source: MIT — Ministero delle Infrastrutture e dei Trasporti
source_url: https://www.mit.gov.it/
period: "2001–2018"
last_modified: 2026-06-02
dataset_slug: mit_incidentalita_mensile
data_driven: true
---

# Incidenti stradali

**Nel ${String(annoSel)} in Italia si sono registrati ${num(totIncidenti)} incidenti stradali, con ${num(totMorti)} morti e ${num(totFeriti)} feriti. Dal ${first} i morti sono diminuiti del ${numFix(caloMorti, 0)}%, ma la discesa si è fermata: nei ${SOGLIA - first} anni prima del ${SOGLIA} si risparmiavano ${num(viteAnnoPrima)} vite all'anno, nei ${last - SOGLIA} successivi appena ${num(Math.abs(viteAnnoDopo))}. Intanto ogni singolo incidente uccide meno — l'indice di mortalità cala del ${numFix(caloIndice, 0)}% — e ad ${mesePiuLetale.mese.toLowerCase()} è il ${numFix(letalitaExtra, 0)}% più letale che a ${meseMenoLetale.mese.toLowerCase()}.**

Serie mensile di incidenti stradali, morti e feriti in Italia. I dati mostrano l'evoluzione della sicurezza stradale dal ${first} al ${last} e quali mesi concentrano il rischio. Ogni numero di questa pagina è calcolato dal dato a build-time.

**Fonte**: [MIT](https://www.mit.gov.it/) · **Periodo**: ${first}–${last} · Dati mensili

```js
import { num, numFix, tableFormat } from "../import/format-utils.js";
```

```js
const data = await FileAttachment("../data/mit-incidentalita.json").json();
```

```js
const anni = [...new Set(data.map(d => d.anno))].sort((a, b) => b - a);
const annoSel = view(Inputs.select(new Map(anni.map(a => [String(a), a])), {label: "Anno", value: anni[0]}));
```

```js
const filtered = data.filter(d => d.anno === annoSel).map(d => ({
  ...d,
  indice_mortalita: d.incidenti ? (d.morti / d.incidenti) * 100 : null,
}));
const totIncidenti = d3.sum(filtered, d => d.incidenti);
const totMorti = d3.sum(filtered, d => d.morti);
const totFeriti = d3.sum(filtered, d => d.feriti);
const totMortali = d3.sum(filtered, d => d.incidenti_mortali);
const indiceAnno = totIncidenti ? (totMorti / totIncidenti) * 100 : null;
```

```js
// Trend annuale
const annuale = Array.from(
  d3.rollup(data, v => ({
    incidenti: d3.sum(v, d => d.incidenti),
    morti: d3.sum(v, d => d.morti),
    feriti: d3.sum(v, d => d.feriti),
    incidenti_mortali: d3.sum(v, d => d.incidenti_mortali),
  }), d => d.anno),
  ([anno, v]) => ({anno, ...v})
).sort((a, b) => a.anno - b.anno);
```

```js
// Serie annuale con l'indice di mortalità calcolato sul rapporto aggregato
// (morti / incidenti dell'anno), non come media dei valori mensili della fonte.
const serie = annuale.map(d => ({
  ...d,
  indice: d.incidenti ? (d.morti / d.incidenti) * 100 : null,
}));

const nAnni = serie.length;
const first = serie[0].anno;
const last = serie[nAnni - 1].anno;
const base = serie[0];
const ultimo = serie[nAnni - 1];

const caloMorti = (base.morti - ultimo.morti) / base.morti * 100;
const caloIncidenti = (base.incidenti - ultimo.incidenti) / base.incidenti * 100;
const caloFeriti = (base.feriti - ultimo.feriti) / base.feriti * 100;
const indiceBase = base.indice;
const indiceUltimo = ultimo.indice;
const caloIndice = (indiceBase - indiceUltimo) / indiceBase * 100;

// Punto di svolta: dal 2013 la discesa dei morti si esaurisce.
// viteAnnoPrima = vite risparmiate in media ogni anno fino alla soglia;
// viteAnnoDopo = saldo medio annuo dopo la soglia (vicino a zero).
const SOGLIA = 2013;
const prima = serie.filter(d => d.anno <= SOGLIA);
const dopo = serie.filter(d => d.anno >= SOGLIA);
const viteAnnoPrima = (prima[0].morti - prima[prima.length - 1].morti) / (prima[prima.length - 1].anno - prima[0].anno);
const viteAnnoDopo = (dopo[dopo.length - 1].morti - dopo[0].morti) / (dopo[dopo.length - 1].anno - dopo[0].anno);
const plateauDelta = ultimo.morti - dopo[0].morti;
```

```js
// Stagionalità: aggregato su tutti gli anni, mese per mese.
// morti_medi = morti per mese in un anno medio; indice = morti ogni 100 incidenti.
const stagionale = Array.from(
  d3.rollup(data, v => ({
    mese: v[0].mese,
    incidenti: d3.sum(v, d => d.incidenti),
    morti: d3.sum(v, d => d.morti),
  }), d => d.mese_numero),
  ([mese_numero, v]) => ({
    mese_numero,
    mese: v.mese,
    incidenti_medi: v.incidenti / nAnni,
    morti_medi: v.morti / nAnni,
    indice: v.incidenti ? (v.morti / v.incidenti) * 100 : null,
  })
).sort((a, b) => a.mese_numero - b.mese_numero);

const mesePiuMorti = stagionale.reduce((a, b) => (b.morti_medi > a.morti_medi ? b : a));
const mesePiuLetale = stagionale.reduce((a, b) => (b.indice > a.indice ? b : a));
const meseMenoLetale = stagionale.reduce((a, b) => (b.indice < a.indice ? b : a));
const letalitaExtra = (mesePiuLetale.indice / meseMenoLetale.indice - 1) * 100;

// Posizione dei due mesi chiave nella classifica per volume di incidenti:
// serve a mostrare che la letalità alta non dipende dal numero di incidenti.
const perIncidenti = [...stagionale].sort((a, b) => a.incidenti_medi - b.incidenti_medi);
const posIncidentiPiuLetale = perIncidenti.findIndex(d => d.mese === mesePiuLetale.mese) + 1;
```

```js
// Serie indicizzata base 2001 = 100: incidenti, morti e feriti hanno scale
// molto diverse, l'indice rende confrontabili i tre cali.
const indicizzato = serie.map(d => ({
  anno: d.anno,
  incidenti: d.incidenti / base.incidenti * 100,
  morti: d.morti / base.morti * 100,
  feriti: d.feriti / base.feriti * 100,
}));

const trendLines = indicizzato.flatMap(d => [
  {anno: d.anno, tipo: "Incidenti", valore: d.incidenti},
  {anno: d.anno, tipo: "Morti", valore: d.morti},
  {anno: d.anno, tipo: "Feriti", valore: d.feriti}
]);
```

<div class="grid grid-cols-4">
  <div class="card">
    <h3>Incidenti</h3>
    <span class="big">${num(totIncidenti)}</span>
    <small style="opacity:0.6">${String(annoSel)}</small>
  </div>
  <div class="card">
    <h3>Morti</h3>
    <span class="big">${num(totMorti)}</span>
  </div>
  <div class="card">
    <h3>Feriti</h3>
    <span class="big">${num(totFeriti)}</span>
  </div>
  <div class="card">
    <h3>Morti ogni 100 incidenti</h3>
    <span class="big">${numFix(indiceAnno, 2)}</span>
    <small style="opacity:0.6">indice di mortalità</small>
  </div>
</div>

---

## 1. Riepilogo annuale — ${String(annoSel)}

Il bilancio del ${String(annoSel)}: ${num(totIncidenti)} incidenti, di cui ${num(totMortali)} mortali, con ${num(totMorti)} morti e ${num(totFeriti)} feriti. L'indice di mortalità — morti ogni 100 incidenti — è di ${numFix(indiceAnno, 2)}.

```js
const riepilogo = [
  {voce: "Incidenti", valore: totIncidenti},
  {voce: "Incidenti mortali", valore: totMortali},
  {voce: "Morti", valore: totMorti},
  {voce: "Feriti", valore: totFeriti},
];
```

```js
Plot.plot({
  title: `Riepilogo incidenti stradali — ${String(annoSel)}`,
  width: 800,
  height: 200,
  marginLeft: 120,
  x: {grid: true, tickFormat: "~s"},
  y: {label: null, tickSize: 0},
  marks: [
    Plot.barX(riepilogo, {y: "voce", x: "valore", fill: "#4e79a7", sort: {y: null}, tip: true}),
    Plot.text(riepilogo, {y: "voce", x: "valore", text: d => num(d.valore), dx: 6, textAnchor: "start", fontSize: 12}),
    Plot.ruleX([0])
  ]
})
```

> **Nota di lettura**: il grafico mostra lo **stock** del ${String(annoSel)}: il numero totale di incidenti (di cui quelli mortali), morti e feriti nell'anno. Il trend è nei grafici successivi.

---

## 2. Il trend ${first}–${last}: i morti scendono più in fretta degli incidenti

Per confrontare grandezze con scale molto diverse, il grafico indicizza ogni serie al ${first} (base 100). Gli incidenti calano del ${numFix(caloIncidenti, 0)}%, i feriti del ${numFix(caloFeriti, 0)}%, i morti del ${numFix(caloMorti, 0)}%: la strada è diventata più sicura molto più di quanto sia diventata meno trafficata.

```js
Plot.plot({
  title: `Incidenti, morti e feriti — base ${first} = 100`,
  width: 800,
  height: 360,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, label: `% rispetto al ${first}`},
  color: {legend: true, scheme: "Set1"},
  marks: [
    Plot.ruleY([100], {stroke: "var(--theme-foreground-muted)", strokeDasharray: "4,4"}),
    Plot.line(trendLines, {x: "anno", y: "valore", z: "tipo", stroke: "tipo", tip: true}),
    Plot.dot(trendLines, {x: "anno", y: "valore", z: "tipo", fill: "tipo", r: 1.5}),
    Plot.text(trendLines.filter(d => d.anno === last), {
      x: "anno", y: "valore", text: d => numFix(d.valore, 0),
      dx: 6, textAnchor: "start", fill: "tipo", fontSize: 11
    })
  ]
})
```

La linea tratteggiata è il livello del ${first}. I tre cali non sono paralleli: i morti scendono quasi il doppio degli incidenti, i feriti ancora meno.

---

## 3. La discesa si ferma: le variazioni annue dal ${SOGLIA}

Il trend aggregato nasconde il dato più importante dell'ultimo tratto della serie. Guardando la **variazione rispetto all'anno precedente**, le barre blu — gli anni in cui i morti diminuivano — si accorciano fino quasi a sparire, e dal ${SOGLIA} diventano arancioni: non c'è più una tendenza, solo oscillazioni.

```js
const variazioni = serie.slice(1).map((d, i) => ({
  anno: d.anno,
  variazione: d.morti - serie[i].morti,
}));
const mediaVarPrima = d3.mean(variazioni.filter(d => d.anno <= SOGLIA), d => d.variazione);
const mediaVarDopo = d3.mean(variazioni.filter(d => d.anno > SOGLIA), d => d.variazione);
```

```js
Plot.plot({
  title: "Variazione annua dei morti rispetto all'anno precedente",
  width: 800,
  height: 300,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, label: "vite in meno (negativo) o in più (positivo)"},
  marks: [
    Plot.barY(variazioni, {
      x: "anno",
      y: "variazione",
      fill: d => (d.anno >= SOGLIA ? "#d95f0e" : "#4e79a7"),
      tip: true
    }),
    Plot.ruleY([0])
  ]
})
```

Fino al ${SOGLIA} ogni anno si contavano in media ${num(Math.abs(mediaVarPrima))} vittime in meno dell'anno precedente; dal ${SOGLIA} al ${last} il saldo medio scende a ${num(Math.abs(mediaVarDopo))} vite in meno l'anno, per un totale di ${num(Math.abs(plateauDelta))} in ${last - SOGLIA} anni. Il miglioramento non si è fermato perché la strada è tornata pericolosa: si è fermato perché la parte di riduzione "facile" era già stata fatta.

```js
// Discontinuità fra il 2012 e il 2013: gli incidenti rilevati calano di colpo
// mentre i morti calano molto meno, quindi l'indice di mortalità sale.
const annoBreak = serie.find(d => d.anno === SOGLIA);
const annoPreBreak = serie.find(d => d.anno === SOGLIA - 1);
const caloIncidentiBreak = (1 - annoBreak.incidenti / annoPreBreak.incidenti) * 100;
const saltoIndiceBreak = (annoBreak.indice / annoPreBreak.indice - 1) * 100;
```

---

## 4. Ogni incidente è meno letale: l'indice di mortalità

L'indice di mortalità — morti ogni 100 incidenti — misura la letalità di un incidente, indipendentemente da quanti ne avvengono. È la ragione per cui i morti calano più degli incidenti: è passato da ${numFix(indiceBase, 2)} nel ${first} a ${numFix(indiceUltimo, 2)} nel ${last}, il ${numFix(caloIndice, 0)}% in meno.

```js
Plot.plot({
  title: `Indice di mortalità — morti ogni 100 incidenti (${first}–${last})`,
  width: 800,
  height: 320,
  x: {tickFormat: d => String(d), label: null},
  y: {grid: true, label: "morti ogni 100 incidenti", domain: [0, null]},
  marks: [
    Plot.ruleY([indiceBase], {stroke: "var(--theme-foreground-muted)", strokeDasharray: "4,4"}),
    Plot.lineY(serie, {x: "anno", y: "indice", stroke: "#4e79a7", strokeWidth: 2, tip: true}),
    Plot.dot(serie, {x: "anno", y: "indice", fill: "#fff", stroke: "#4e79a7"}),
    Plot.dot(serie.filter(d => d.anno === last), {x: "anno", y: "indice", fill: "#d95f0e", r: 4, tip: true})
  ]
})
```

La linea tratteggiata è il livello del ${first}. Anche questo indicatore si appiattisce dal ${SOGLIA}: la letalità non scende più, oscilla intorno al valore raggiunto.

> **Come leggerlo**: fra il ${SOGLIA - 1} e il ${SOGLIA} gli incidenti rilevati calano del ${numFix(caloIncidentiBreak, 0)}% in un solo anno — un salto che segnala una discontinuità nella rilevazione, non solo un calo del traffico — e l'indice di mortalità sale del ${numFix(saltoIndiceBreak, 0)}% pur con ${num(Math.abs(annoPreBreak.morti - annoBreak.morti))} morti in meno. È un effetto di composizione, non un peggioramento improvviso delle strade.

---

## 5. La stagionalità: ${mesePiuLetale.mese.toLowerCase()} è il mese più letale

Il rischio segue la mobilità. ${mesePiuMorti.mese.toLowerCase()} è il mese con più vittime in assoluto (${num(mesePiuMorti.morti_medi)} al mese in media nei ${nAnni} anni della serie), ${meseMenoLetale.mese.toLowerCase()} quello con meno (${num(meseMenoLetale.morti_medi)}). Ma la lettura più utile è la **letalità**: ad ${mesePiuLetale.mese.toLowerCase()} ci sono meno incidenti — è il ${num(posIncidentiPiuLetale)}º mese su ${num(stagionale.length)} per numero di incidenti — eppure ogni incidente fa più vittime che in qualsiasi altro mese.

```js
Plot.plot({
  title: "Morti al mese in un anno medio",
  width: 800,
  height: 300,
  marginLeft: 60,
  x: {label: null},
  y: {grid: true, label: "morti al mese (media)"},
  marks: [
    Plot.barY(stagionale, {
      x: "mese",
      y: "morti_medi",
      fill: d => (d.mese === mesePiuMorti.mese ? "#d95f0e" : "#4e79a7"),
      tip: true
    }),
    Plot.text(stagionale, {x: "mese", y: "morti_medi", text: d => num(d.morti_medi), dy: -6, fontSize: 10}),
    Plot.ruleY([0])
  ]
})
```

```js
Plot.plot({
  title: "Quanto è letale un incidente, mese per mese",
  width: 800,
  height: 300,
  marginLeft: 60,
  x: {label: null},
  y: {grid: true, label: "morti ogni 100 incidenti", domain: [0, null]},
  marks: [
    Plot.lineY(stagionale, {x: "mese", y: "indice", stroke: "#9ecae1", strokeWidth: 2}),
    Plot.dot(stagionale, {
      x: "mese",
      y: "indice",
      fill: d => (d.mese === mesePiuLetale.mese ? "#d95f0e" : "#4e79a7"),
      r: 4,
      tip: true
    }),
    Plot.text(stagionale, {x: "mese", y: "indice", text: d => numFix(d.indice, 2), dy: -8, fontSize: 10})
  ]
})
```

Ad ${mesePiuLetale.mese.toLowerCase()} un incidente è il **${numFix(letalitaExtra, 0)}% più letale** che a ${meseMenoLetale.mese.toLowerCase()}: ${numFix(mesePiuLetale.indice, 2)} morti ogni 100 incidenti contro ${numFix(meseMenoLetale.indice, 2)}, la forbice più ampia dell'anno. Le spiegazioni più plausibili non stanno nei dati — strade più scorrevoli, spostamenti lunghi, velocità — ma il dato lascia una domanda civica aperta: **se il rischio si concentra in pochi mesi, perché le campagne di sicurezza sono distribuite su tutto l'anno?**

---

## Dettaglio mensile — ${String(annoSel)}

Ogni riga è un mese dell'anno selezionato. L'indice di mortalità è calcolato sul rapporto del mese (morti diviso incidenti), non come media dei valori già pubblicati dalla fonte.

```js
const { header, format } = tableFormat({
  mese: { label: "Mese", fmt: "string" },
  incidenti: { label: "Incidenti", fmt: "num" },
  incidenti_mortali: { label: "Incidenti mortali", fmt: "num" },
  morti: { label: "Morti", fmt: "num" },
  feriti: { label: "Feriti", fmt: "num" },
  indice_mortalita: { label: "Morti ogni 100 inc.", fmt: "num", decimals: 2 },
  indice_gravita: { label: "Indice di gravità", fmt: "num", decimals: 2 },
});
```

```js
Inputs.table(filtered, {
  columns: ["mese", "incidenti", "incidenti_mortali", "morti", "feriti", "indice_mortalita", "indice_gravita"],
  header,
  format,
  rows: 15,
  width: "100%"
})
```

---

## Serie annuale completa

```js
const { header: headerAnni, format: formatAnni } = tableFormat({
  anno: { label: "Anno", fmt: "string" },
  incidenti: { label: "Incidenti", fmt: "num" },
  incidenti_mortali: { label: "Incidenti mortali", fmt: "num" },
  morti: { label: "Morti", fmt: "num" },
  feriti: { label: "Feriti", fmt: "num" },
  indice: { label: "Morti ogni 100 inc.", fmt: "num", decimals: 2 },
});
```

```js
const tabellaAnni = serie.map(d => ({ ...d, anno: String(d.anno) }));
```

```js
Inputs.table(tabellaAnni, {
  columns: ["anno", "incidenti", "incidenti_mortali", "morti", "feriti", "indice"],
  header: headerAnni,
  format: formatAnni,
  rows: 18,
  width: "100%",
  sort: "anno",
  reverse: true
})
```

---

## Limiti

- **Copertura**: la serie copre ${first}–${last} (${nAnni * 12} mesi rilevati). Il dato dopo il ${last} non è in questo dataset: la fonte MIT ha cambiato metodologia.
- **Nazionale**: i dati sono aggregati a livello nazionale. Non è disponibile la disaggregazione regionale o provinciale, quindi non si possono confrontare i territori.
- **Discontinuità nella rilevazione**: fra il ${SOGLIA - 1} e il ${SOGLIA} gli incidenti rilevati calano del ${numFix(caloIncidentiBreak, 0)}% in un solo anno e l'indice di mortalità sale, pur con meno vittime. Il confronto degli indici prima e dopo quella soglia va letto con cautela.
- **Indici calcolati**: l'indice di mortalità e l'indice di lesività di questa pagina sono rapporti aggregati (morti o feriti diviso incidenti del periodo), non le medie mensili pre-calcolate dalla fonte.

---

## Risorse

- [MIT — Open Data](https://www.mit.gov.it/)
- [Esplora i dati con Query SQL](https://dataciviclab-dashboard.streamlit.app/Query_SQL)
- [Scarica il parquet pulito](https://storage.googleapis.com/dataciviclab-clean/mit_incidentalita_mensile/2001/mit_incidentalita_mensile_2001_clean.parquet)
- [Pipeline](https://github.com/dataciviclab/dataset-incubator/tree/main/candidates/mit-incidentalita-mensile-2001-2018)

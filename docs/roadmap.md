# Data Explorer — roadmap

Stato: **novembre 2026**. Aggiornare a ogni fase chiusa; le voci non fatte non
spariscono, si spostano. Ogni voce ha un criterio di chiusura verificabile.

## Principi (non negoziabili)

1. **Un dataset = un loader o una scheda.** Niente pagine scritte a mano per
   letture standard.
2. **Niente finta copertura.** Ogni dataset ha un livello dichiarato:
   *lettura guidata* (pagina o scheda) oppure *solo dati* (catalogo + Query SQL).
3. **Gli errori sono rumorosi.** Un loader vuoto, un mart assente, una pagina
   orfana fermano il build. Meglio rosso che numeri di ieri.
4. **Le viste sono economiche, i campi sono cari.** Filtri e raggruppamenti
   costano giorni; `source`, `license`, `level`, `last_run`, `semantic_type`
   costano settimane e vanno dichiarati una volta.
5. **La narrazione resta editoriale.** Schede e blocchi per i dati; pagine e
   analisi per le domande.

## Fatto (contesto, verificato)

- Schede incrementali (fingerprint), audit dei dati, refresh mirato per dataset,
  loader in parallelo, errori rumorosi su output vuoto.
- Palette del Lab applicata a schede e blocchi; brand (colori + simbolo) in DE.
- Navigazione: temi cliccabili, schede in sidebar, una route per i temi.
- RNA e OpenCoesione leggono i mart: −128 MB di colonne per build.
- Anni hardcoded: 11 loader convertiti a `years=None` (output identico) e Terna
  che legge il dataset pubblicato; restano 8 finestre editoriali e 2 loader a
  percorso canonico (`irpef-capoluoghi`, `votazioni-camera`).

---

## P1 — Progetti (in corso, il pezzo urgente)

Un progetto = un repo con `role: dati`. Pagina generata, non scritta a mano.

- [ ] L'override in `catalog/projects/*.yml` usa YAML vero (`yaml.safe_load`),
      non un parser riga-per-riga: serve per le liste.
- [ ] `questions: [...]` nel yml → blocco «Cosa risponde» sotto l'hook. È ciò
      che distingue un progetto da un repo con dataset.
- [ ] Tabella dataset: colonna **livello** (*lettura guidata* / *solo dati*) e,
      per «solo dati», il link a Query SQL e al parquet. Oggi 16 righe su 18 in
      `bilancio-pubblico` sono vicoli ciechi.
- [ ] «Periodo»: dichiarato vs coperto (3 progetti finiscono nel 2027).
- [ ] «Pubblicati»: separare *con lettura guidata* (superficie) da *con dati*.
- [ ] Indice `/progetti/`: filtro dominio + ricerca + `featured`, esclusi o
      marcati i 26 progetti con 0 superfici.
- [ ] Sul hub: `/progetti/*` diventa link/stub verso DE (toglie 37 pagine con
      numeri a mano).
- [ ] Test + `docs/projects.md` + PR.

**Chiuso quando**: 43 pagine, 17 con lettura guidata e 26 dichiarate «solo
dati», nessun numero scritto a mano, nessun link morto, hub allineato.

## P2 — Contratto dei campi (2-3 giorni)

Abilita catalogo e viste; senza, i filtri mentono.

- [ ] `source` (nome leggibile) ripristinato o fallback stabile a `source_id`.
- [ ] `license` per superficie (frontmatter e scheda); 1 scheda su 4 oggi.
- [ ] `level` nel catalogo: `page` / `card` / `data`.
- [ ] `last_run` esposto nel catalogo (dal registry del repo).
- [ ] `semantic_type` territoriale verificato: oggi regione 131/561,
      provincia 97, comune 53, ente 0.

**Chiuso quando**: ogni superficie ha fonte, licenza, livello; l'audit fallisce
se mancano.

## P3 — Catalogo a viste (1 settimana)

Una collezione, molte lenti. Dipende da P2.

- [ ] `/catalogo` con faccette (tema, territorio, periodo, fonte, livello),
      raggruppamento e URL con parametri.
- [ ] Home con 3-4 viste salvate («Appalti», «Il mio territorio», «Appena
      aggiornati», «Tutti»).
- [ ] Temi come viste con introduzione editoriale, non scaffali separati.
- [ ] «Solo dati» → link a Query SQL/parquet, mai vicolo cieco.

**Chiuso quando**: 561 dataset navigabili per tema e territorio; nessuna voce
senza prossimo passo.

## P4 — Palette e blocchi nelle pagine (1 settimana)

Il debito visivo: 48 pagine usano hex ad-hoc (`#2c7fb8`, `#d95f0e`, …).

- [ ] Palette del Lab nelle pagine dataset; i grafici ricorrenti passano dai
      blocchi.
- [ ] Regola d'audit: nessun colore letterale fuori dalla palette.
- [ ] Grafici bespoke solo dove i blocchi non arrivano (le analisi).

**Chiuso quando**: zero hex fuori palette; audit verde.

## P5 — Docs e pagine «about» in DE (1 giorno)

Contenuto già scritto nel hub: è un porting.

- [ ] 7 `docs/*.md` (contribuire, flusso dataset, glossario, governance, setup…).
- [ ] `chi-siamo`, `ecosistema`, home editoriale.
- [ ] Header con marchio + voci about (progetti, docs, chi siamo).

**Chiuso quando**: il hub non ha più contenuto unico.

## P6 — Dominio e switch (1 giorno + un mese di osservazione)

- [ ] `dataciviclab.org` → DE; `explorer.` come alias.
- [ ] Stub/redirect per i 44 URL del hub (OF non ha redirect).
- [ ] Sitemap generata da script su `dist/**/*.html`.
- [ ] Repo Astro in sola lettura dopo un mese.

**Rischio dichiarato**: il front door diventa il build dei dati (58 loader,
GCS, ACB). Se la pipeline si rompe il sito non si aggiorna. Mitigazione: le
pagine editoriali non hanno loader propri; il deploy tiene l'ultima versione.

**Chiuso quando**: i vecchi URL rispondono, la sitemap c'è, il dominio serve DE.

## P7 — Profondità (continuo)

- [ ] Pagina → scheda dove esiste il mart (oggi 37 pagine su 45 hanno un mart).
- [ ] Mart per i 6 dataset che non ne hanno: `mit-incidentalita`,
      `pensioni-inps`, `pensioni-pa-dag`, `posti-letto-stabilimento`,
      `reparti-ricovero`, `strutture-ricovero-asl`.
- [ ] Vista ente (`tax_code`/denominazione) solo quando l'identità è affidabile.
- [ ] Segnale di freschezza dell'indice ACB (oggi può essere indietro di ore:
      il caso `pensioni-pa-dag`).

## Fuori scope / decisioni aperte

- Marchio A/B (lab-ops #115) e rifinitura di Soglia.
- Palette v2 (slot 1 troppo vicino all'accento, lab-ops #114).
- Licenze per dataset (blocca la pagina Metodo).
- Mittenti dei dispatch (`data_updated`/`catalog_updated`).
- Dashboard Streamlit: si linkano dai progetti, non si incorporano.

## Metriche di successo

| | |
|---|---|
| Superfici senza fonte/licenza/livello | 0 |
| Pagine con period incoerente | 0 |
| Hex fuori palette | 0 |
| Dataset raggiungibili da un progetto | tutti i 561 |
| Full refresh del sito | < 5 minuti |
| Progetti con numeri scritti a mano | 0 |

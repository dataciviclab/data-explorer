## Sintesi

Descrivi in poche righe cosa cambia e perché.

## Contesto collegato

Closes #

## Cosa cambia

- [ ] Nuovo dataset — pagina explorer
- [ ] Bug fix frontend (data loader / layout / performance)
- [ ] Aggiornamento config / catalogo
- [ ] Modifica struttura dati upstream
- [ ] Documentazione
- [ ] Dipendenze o CI

## Checklist nuovo dataset

Se la PR aggiunge un nuovo dataset in explorer:

- [ ] **Data loader**: `src/data/<slug-url>.json.py` creato
- [ ] **Pagina**: `src/dataset/<slug-url>.md` creata
- [ ] **Registrazione**: voce aggiunta in `observablehq.config.js` sezione `pages`
- [ ] **Tema**: aggiornato `src/data/themes.json.py` (se nuovo tema)
- [ ] **Verifica locale**: `npm run dev` — pagina navigabile, dati caricati
- [ ] **Slug consistenti**: slug URL (trattini) e slug DI (underscore) allineati
- [ ] **Leggibilità**: pagina leggibile da un utente non tecnico
- [ ] **Clean catalog**: il dataset è presente in `clean_catalog.json` DI

## Verifica

Spiega come hai verificato il cambiamento.

```bash
npm run dev
```

- [ ] `npm run dev` produce output sensati
- [ ] Data loader non solleva errori
- [ ] Pagina si carica senza warning in console

## Checklist PR

- [ ] Perimetro stretto: una PR = un dataset o un fix mirato
- [ ] Issue collegata o motivazione dell'assenza

## Note per chi revisiona

Rischi, limiti, punti da controllare con attenzione.

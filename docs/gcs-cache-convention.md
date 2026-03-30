# GCS Cache Convention

Questa repo usa una convenzione locale per alcuni source Evidence che altrimenti leggerebbero parquet pubblici direttamente da GCS durante `npm run sources`.

## Obiettivo

Ridurre la dipendenza remota nel path `sources` senza cambiare il bucket pubblico o il layer `pages`.

Questa convenzione e':

- coerente con il modello Evidence `extract first, build after`
- specifica del repo
- non una feature nativa o una best practice ufficiale documentata di Evidence

## Path canonico

La cache locale vive in:

- `.evidence/gcs-cache/<technical_slug>/<anno>/...`

Il contenuto della cache non va versionato nel repo.

## Piano di cache

Il piano dei file sincronizzati vive in:

- `scripts/gcs-cache-plan.json`

Ogni entry dichiara:

- `slug`
- `files`
- `remoteUrl`
- `relativePath`

Lo script di sync legge questa configurazione e popola la cache locale prima di `npm run sources`.

## Refresh

Per default:

- se il file locale esiste e non e' vuoto, lo script usa `cache hit`
- se manca, lo scarica da GCS

Per forzare il refresh:

```powershell
$env:FORCE_GCS_SYNC=1
npm run sources
```

## Quando usare la cache locale

La cache locale va preferita quando un source:

- legge parquet remoti direttamente da GCS
- pesa in modo visibile su `npm run sources`
- introduce fragilita' o fetch ripetuti non necessari

Non tutti i dataset devono per forza usarla subito.

## Regola pratica

Prima di aggiungere un nuovo caso alla cache:

1. verificare che il source sia davvero un collo di bottiglia o una fragilita'
2. aggiungere i file al `gcs-cache-plan.json`
3. aggiornare il source SQL a leggere da `.evidence/gcs-cache/...`
4. verificare `npm run sources`
5. verificare `npm run build`

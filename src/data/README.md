# Data Loader

Ogni file `.json.py` in questa directory produce un JSON aggregato dai clean parquet su GCS, consumato dalle pagine Observable.

## Pattern di naming

I loader seguono due ruoli distinti.

### Loader base

Leggono direttamente il parquet GCS con lo slug del dataset-incubator.

- Nome: `<slug_di>.json.py` (underscore, come nello slug DI)
- Esempi: `aifa_spesa_consumo.json.py`, `civile_flussi.json.py`, `irpef_comunale.json.py`
- Prodotto: JSON col nome dello slug DI (es. `aifa_spesa_consumo.json`)

### Loader derivato

Producono una vista aggregata o rinominate per una pagina specifica.

- Nome: `<slug-url>.json.py` (trattini) oppure `<slug>-<vista>.json.py`
- Esempi:
  - `aifa-spesa.json.py` — rename per la pagina "Spesa farmaceutica"
  - `irpef-regioni.json.py` — vista aggregata per regione
  - `ispra-comuni.json.py` — vista aggregata per comune
- Prodotto: JSON col nome del file (es. `irpef-regioni.json`)

### Perché due ruoli?

I loader base mantengono il legame col catalogo DI (slug con underscore).
I loader derivati usano slug URL (con trattini) perché le pagine Observable li referenziano come `FileAttachment`.

Così è chiaro cosa è un loader "grezzo" e cosa è una vista pensata per una pagina.

## Utility condivisa

`_util.py` fornisce `load_dataset()` e `_parquet_exists()` per evitare di replicare logica GCS/DuckDB in ogni loader.

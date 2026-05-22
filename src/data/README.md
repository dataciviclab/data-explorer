# Data Loader

Ogni file `.json.py` in questa directory è un **data loader** creato a mano per una pagina specifica. Legge i clean parquet su GCS via DuckDB e produce JSON aggregato, consumato dalle pagine Observable.

## Naming

Il nome del file segue lo slug URL della pagina (con trattini), eventualmente con un suffisso che specifica la vista:

- `<slug-url>.json.py` — loader principale per una pagina
- `<slug-url>-<vista>.json.py` — loader per una vista specifica (es. per regione, per comune)

Esempi:
- `aifa-spesa.json.py` — loader per la pagina "Spesa farmaceutica"
- `irpef-regioni.json.py` — vista aggregata per regione
- `ispra-comuni.json.py` — vista aggregata per comune

Lo slug interno (con underscore, es. `aifa_spesa_consumo`) che identifica il parquet su GCS viene passato come parametro `slug=` a `load_dataset()` — non ha relazione col nome del file.

## Utility condivisa

`_util.py` fornisce `load_dataset()` e `_parquet_exists()` per evitare di replicare logica GCS/DuckDB in ogni loader.

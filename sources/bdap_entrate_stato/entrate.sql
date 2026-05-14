SELECT
  CAST(esercizio_finanziario AS VARCHAR) AS anno,
  titolo,
  codice_titolo,
  natura,
  tipologia,
  provento,
  previsioni_definitive_cp,
  previsioni_definitive_cs
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/bdap_entrate_stato/2024/bdap_entrate_stato_2024_clean.parquet'
)

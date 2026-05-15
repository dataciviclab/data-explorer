-- Il parquet 2024 contiene l'intero storico 2020-2024 (17 trimestri).
-- Se in futuro il dataset viene splittato per anno, aggiornare il path.
SELECT
  CAST(anno AS VARCHAR) AS anno,
  trimestre,
  sesso,
  classe_eta,
  classe_importo,
  area_geografica,
  gestione,
  tipo_gestione,
  categoria,
  regione,
  numero_pensioni
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/inps_pensioni_trimestrale/2024/inps_pensioni_trimestrale_2024_clean.parquet'
)

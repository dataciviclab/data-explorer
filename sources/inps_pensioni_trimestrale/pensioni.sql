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

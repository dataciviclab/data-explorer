SELECT *
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/civile_flussi_2014_2024/2024/civile_flussi_2014_2024_2024_clean.parquet'
)

SELECT
  CAST(anno AS VARCHAR) AS anno,
  tipo_produzione,
  regione,
  provincia,
  fonte,
  produzione_gwh
FROM read_parquet(
  [
    '.evidence/gcs-cache/terna_electricity_by_source/2023/terna_electricity_by_source_2023_clean.parquet',
    '.evidence/gcs-cache/terna_electricity_by_source/2024/terna_electricity_by_source_2024_clean.parquet'
  ]
)

SELECT
  CAST(anno AS VARCHAR) AS anno,
  tipo_capacita,
  regione,
  provincia,
  fonti,
  potenza_mw
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/terna_capacita_rinnovabile/2023/terna_capacita_rinnovabile_2023_clean.parquet'
)
UNION ALL
SELECT
  CAST(anno AS VARCHAR) AS anno,
  tipo_capacita,
  regione,
  provincia,
  fonti,
  potenza_mw
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/terna_capacita_rinnovabile/2024/terna_capacita_rinnovabile_2024_clean.parquet'
)

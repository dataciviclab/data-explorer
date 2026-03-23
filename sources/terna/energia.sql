SELECT *
FROM read_parquet(
  [
    'https://storage.googleapis.com/dataciviclab-clean/terna_electricity_by_source/2023/terna_electricity_by_source_2023_clean.parquet',
    'https://storage.googleapis.com/dataciviclab-clean/terna_electricity_by_source/2024/terna_electricity_by_source_2024_clean.parquet'
  ]
)

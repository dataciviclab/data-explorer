SELECT
  CAST(anno AS VARCHAR) AS anno,
  comparto,
  donne_totali,
  uomini_totali,
  assunti_totali,
  cessati_totali
FROM read_parquet(
  [
    'https://storage.googleapis.com/dataciviclab-clean/dipendenti_pubblici_2021_2023/2021/dipendenti_pubblici_2021_2023_2021_clean.parquet',
    'https://storage.googleapis.com/dataciviclab-clean/dipendenti_pubblici_2021_2023/2022/dipendenti_pubblici_2021_2023_2022_clean.parquet',
    'https://storage.googleapis.com/dataciviclab-clean/dipendenti_pubblici_2021_2023/2023/dipendenti_pubblici_2021_2023_2023_clean.parquet'
  ]
)
WHERE comparto IS NOT NULL

SELECT
  CAST(anno AS VARCHAR) AS anno,
  comparto,
  donne_totali,
  uomini_totali,
  assunti_totali,
  cessati_totali
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/dipendenti_pubblici/2021/dipendenti_pubblici_2021_clean.parquet'
)
UNION ALL
SELECT
  CAST(anno AS VARCHAR) AS anno,
  comparto,
  donne_totali,
  uomini_totali,
  assunti_totali,
  cessati_totali
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/dipendenti_pubblici/2022/dipendenti_pubblici_2022_clean.parquet'
)
UNION ALL
SELECT
  CAST(anno AS VARCHAR) AS anno,
  comparto,
  donne_totali,
  uomini_totali,
  assunti_totali,
  cessati_totali
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/dipendenti_pubblici/2023/dipendenti_pubblici_2023_clean.parquet'
)

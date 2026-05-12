SELECT
  CAST(anno_di_imposta AS VARCHAR) AS anno,
  regione,
  denominazione_comune AS comune,
  numero_contribuenti,
  reddito_imponibile_eur,
  imposta_netta_eur
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/irpef_comunale/2019/irpef_comunale_2019_clean.parquet'
)
UNION ALL
SELECT
  CAST(anno_di_imposta AS VARCHAR) AS anno,
  regione,
  denominazione_comune AS comune,
  numero_contribuenti,
  reddito_imponibile_eur,
  imposta_netta_eur
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/irpef_comunale/2020/irpef_comunale_2020_clean.parquet'
)
UNION ALL
SELECT
  CAST(anno_di_imposta AS VARCHAR) AS anno,
  regione,
  denominazione_comune AS comune,
  numero_contribuenti,
  reddito_imponibile_eur,
  imposta_netta_eur
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/irpef_comunale/2021/irpef_comunale_2021_clean.parquet'
)
UNION ALL
SELECT
  CAST(anno_di_imposta AS VARCHAR) AS anno,
  regione,
  denominazione_comune AS comune,
  numero_contribuenti,
  reddito_imponibile_eur,
  imposta_netta_eur
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/irpef_comunale/2022/irpef_comunale_2022_clean.parquet'
)
UNION ALL
SELECT
  CAST(anno_di_imposta AS VARCHAR) AS anno,
  regione,
  denominazione_comune AS comune,
  numero_contribuenti,
  reddito_imponibile_eur,
  imposta_netta_eur
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/irpef_comunale/2023/irpef_comunale_2023_clean.parquet'
)

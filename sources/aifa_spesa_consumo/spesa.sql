SELECT
  CAST(anno AS VARCHAR) AS anno,
  CAST(mese AS INTEGER) AS mese,
  codreg,
  regione,
  classe,
  atc1,
  descrizione_atc1,
  atc2,
  descrizione_atc2,
  atc3,
  descrizione_atc3,
  atc4,
  descrizione_atc4,
  numero_confezioni_traccia,
  spesa_flusso_tracciabilita,
  numero_confezioni_convenzionata,
  spesa_convenzionata
FROM read_parquet('https://storage.googleapis.com/dataciviclab-clean/aifa_spesa_consumo/2018/aifa_spesa_consumo_2018_clean.parquet')
UNION ALL
SELECT
  CAST(anno AS VARCHAR) AS anno,
  CAST(mese AS INTEGER) AS mese,
  codreg,
  regione,
  classe,
  atc1,
  descrizione_atc1,
  atc2,
  descrizione_atc2,
  atc3,
  descrizione_atc3,
  atc4,
  descrizione_atc4,
  numero_confezioni_traccia,
  spesa_flusso_tracciabilita,
  numero_confezioni_convenzionata,
  spesa_convenzionata
FROM read_parquet('https://storage.googleapis.com/dataciviclab-clean/aifa_spesa_consumo/2019/aifa_spesa_consumo_2019_clean.parquet')
UNION ALL
SELECT
  CAST(anno AS VARCHAR) AS anno,
  CAST(mese AS INTEGER) AS mese,
  codreg,
  regione,
  classe,
  atc1,
  descrizione_atc1,
  atc2,
  descrizione_atc2,
  atc3,
  descrizione_atc3,
  atc4,
  descrizione_atc4,
  numero_confezioni_traccia,
  spesa_flusso_tracciabilita,
  numero_confezioni_convenzionata,
  spesa_convenzionata
FROM read_parquet('https://storage.googleapis.com/dataciviclab-clean/aifa_spesa_consumo/2020/aifa_spesa_consumo_2020_clean.parquet')
UNION ALL
SELECT
  CAST(anno AS VARCHAR) AS anno,
  CAST(mese AS INTEGER) AS mese,
  codreg,
  regione,
  classe,
  atc1,
  descrizione_atc1,
  atc2,
  descrizione_atc2,
  atc3,
  descrizione_atc3,
  atc4,
  descrizione_atc4,
  numero_confezioni_traccia,
  spesa_flusso_tracciabilita,
  numero_confezioni_convenzionata,
  spesa_convenzionata
FROM read_parquet('https://storage.googleapis.com/dataciviclab-clean/aifa_spesa_consumo/2021/aifa_spesa_consumo_2021_clean.parquet')
UNION ALL
SELECT
  CAST(anno AS VARCHAR) AS anno,
  CAST(mese AS INTEGER) AS mese,
  codreg,
  regione,
  classe,
  atc1,
  descrizione_atc1,
  atc2,
  descrizione_atc2,
  atc3,
  descrizione_atc3,
  atc4,
  descrizione_atc4,
  numero_confezioni_traccia,
  spesa_flusso_tracciabilita,
  numero_confezioni_convenzionata,
  spesa_convenzionata
FROM read_parquet('https://storage.googleapis.com/dataciviclab-clean/aifa_spesa_consumo/2022/aifa_spesa_consumo_2022_clean.parquet')
UNION ALL
SELECT
  CAST(anno AS VARCHAR) AS anno,
  CAST(mese AS INTEGER) AS mese,
  codreg,
  regione,
  classe,
  atc1,
  descrizione_atc1,
  atc2,
  descrizione_atc2,
  atc3,
  descrizione_atc3,
  atc4,
  descrizione_atc4,
  numero_confezioni_traccia,
  spesa_flusso_tracciabilita,
  numero_confezioni_convenzionata,
  spesa_convenzionata
FROM read_parquet('https://storage.googleapis.com/dataciviclab-clean/aifa_spesa_consumo/2023/aifa_spesa_consumo_2023_clean.parquet')
UNION ALL
SELECT
  CAST(anno AS VARCHAR) AS anno,
  CAST(mese AS INTEGER) AS mese,
  codreg,
  regione,
  classe,
  atc1,
  descrizione_atc1,
  atc2,
  descrizione_atc2,
  atc3,
  descrizione_atc3,
  atc4,
  descrizione_atc4,
  numero_confezioni_traccia,
  spesa_flusso_tracciabilita,
  numero_confezioni_convenzionata,
  spesa_convenzionata
FROM read_parquet('https://storage.googleapis.com/dataciviclab-clean/aifa_spesa_consumo/2024/aifa_spesa_consumo_2024_clean.parquet')

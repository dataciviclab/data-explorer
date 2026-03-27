SELECT
  CAST(anno_imposta AS VARCHAR) AS anno,
  codice_istat_comune,
  comune,
  sigla_provincia,
  regione,
  codice_istat_regione,
  numero_contribuenti,
  reddito_imponibile_eur,
  imposta_netta_eur,
  addizionale_comunale_eur
FROM read_parquet(
  [
    'https://storage.googleapis.com/dataciviclab-clean/irpef_comunale_2019_2023/2019/irpef_comunale_2019_2023_2019_clean.parquet',
    'https://storage.googleapis.com/dataciviclab-clean/irpef_comunale_2019_2023/2020/irpef_comunale_2019_2023_2020_clean.parquet',
    'https://storage.googleapis.com/dataciviclab-clean/irpef_comunale_2019_2023/2021/irpef_comunale_2019_2023_2021_clean.parquet',
    'https://storage.googleapis.com/dataciviclab-clean/irpef_comunale_2019_2023/2022/irpef_comunale_2019_2023_2022_clean.parquet',
    'https://storage.googleapis.com/dataciviclab-clean/irpef_comunale_2019_2023/2023/irpef_comunale_2019_2023_2023_clean.parquet'
  ]
)
WHERE comune IS NOT NULL
  AND regione IS NOT NULL
  AND regione <> 'Mancante/errata'
  AND numero_contribuenti IS NOT NULL
  AND reddito_imponibile_eur IS NOT NULL

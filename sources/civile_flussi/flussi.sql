SELECT
  CAST(anno AS VARCHAR) AS anno,
  fonte,
  tipo_ufficio,
  distretto,
  sede,
  macromateria,
  materia,
  sopravvenuti,
  definiti_totale,
  pendenti_finali
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/civile_flussi_2014_2024/2024/civile_flussi_2014_2024_2024_clean.parquet'
)

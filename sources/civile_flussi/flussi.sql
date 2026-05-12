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
  'https://storage.googleapis.com/dataciviclab-clean/civile_flussi/2025/civile_flussi_2025_clean.parquet'
)

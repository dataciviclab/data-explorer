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
  '.evidence/gcs-cache/civile_flussi/2025/civile_flussi_2025_clean.parquet'
)

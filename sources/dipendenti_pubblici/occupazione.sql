SELECT
  CAST(anno AS VARCHAR) AS anno,
  comparto,
  (donne_tempo_pieno + donne_part_time_inf_50 + donne_part_time_sup_50) AS donne_totali,
  (uomini_tempo_pieno + uomini_part_time_inf_50 + uomini_part_time_sup_50) AS uomini_totali,
  (donne_assunte + uomini_assunti) AS assunti_totali,
  (donne_cessate + uomini_cessati) AS cessati_totali
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/dipendenti_pubblici/2021/dipendenti_pubblici_2021_clean.parquet'
)
UNION ALL
SELECT
  CAST(anno AS VARCHAR) AS anno,
  comparto,
  (donne_tempo_pieno + donne_part_time_inf_50 + donne_part_time_sup_50) AS donne_totali,
  (uomini_tempo_pieno + uomini_part_time_inf_50 + uomini_part_time_sup_50) AS uomini_totali,
  (donne_assunte + uomini_assunti) AS assunti_totali,
  (donne_cessate + uomini_cessati) AS cessati_totali
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/dipendenti_pubblici/2022/dipendenti_pubblici_2022_clean.parquet'
)
UNION ALL
SELECT
  CAST(anno AS VARCHAR) AS anno,
  comparto,
  (donne_tempo_pieno + donne_part_time_inf_50 + donne_part_time_sup_50) AS donne_totali,
  (uomini_tempo_pieno + uomini_part_time_inf_50 + uomini_part_time_sup_50) AS uomini_totali,
  (donne_assunte + uomini_assunti) AS assunti_totali,
  (donne_cessate + uomini_cessati) AS cessati_totali
FROM read_parquet(
  'https://storage.googleapis.com/dataciviclab-clean/dipendenti_pubblici/2023/dipendenti_pubblici_2023_clean.parquet'
)

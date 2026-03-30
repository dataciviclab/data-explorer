SELECT CAST(2020 AS VARCHAR) AS anno, * FROM read_parquet('.evidence/gcs-cache/ispra_ru_base/2020/ispra_ru_base_2020_clean.parquet')
UNION ALL
SELECT CAST(2021 AS VARCHAR) AS anno, * FROM read_parquet('.evidence/gcs-cache/ispra_ru_base/2021/ispra_ru_base_2021_clean.parquet')
UNION ALL
SELECT CAST(2022 AS VARCHAR) AS anno, * FROM read_parquet('.evidence/gcs-cache/ispra_ru_base/2022/ispra_ru_base_2022_clean.parquet')
UNION ALL
SELECT CAST(2023 AS VARCHAR) AS anno, * FROM read_parquet('.evidence/gcs-cache/ispra_ru_base/2023/ispra_ru_base_2023_clean.parquet')
UNION ALL
SELECT CAST(2024 AS VARCHAR) AS anno, * FROM read_parquet('.evidence/gcs-cache/ispra_ru_base/2024/ispra_ru_base_2024_clean.parquet')

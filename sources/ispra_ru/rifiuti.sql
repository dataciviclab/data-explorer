SELECT 2020 AS anno, * FROM read_parquet('https://storage.googleapis.com/dataciviclab-clean/ispra_ru_base/2020/ispra_ru_base_2020_clean.parquet')
UNION ALL
SELECT 2021 AS anno, * FROM read_parquet('https://storage.googleapis.com/dataciviclab-clean/ispra_ru_base/2021/ispra_ru_base_2021_clean.parquet')
UNION ALL
SELECT 2022 AS anno, * FROM read_parquet('https://storage.googleapis.com/dataciviclab-clean/ispra_ru_base/2022/ispra_ru_base_2022_clean.parquet')
UNION ALL
SELECT 2023 AS anno, * FROM read_parquet('https://storage.googleapis.com/dataciviclab-clean/ispra_ru_base/2023/ispra_ru_base_2023_clean.parquet')
UNION ALL
SELECT 2024 AS anno, * FROM read_parquet('https://storage.googleapis.com/dataciviclab-clean/ispra_ru_base/2024/ispra_ru_base_2024_clean.parquet')

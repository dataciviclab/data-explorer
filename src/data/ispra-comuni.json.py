#!/usr/bin/env python3
"""Data loader: ISPRA rifiuti urbani — comuni sopra 100k abitanti."""
import duckdb, json, sys

GCS_BASE = "https://storage.googleapis.com/dataciviclab-clean"
slug = "ispra_ru_base"
years = list(range(2020, 2025))

con = duckdb.connect()
parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet('{GCS_BASE}/{slug}/{y}/{slug}_{y}_clean.parquet')"
    for y in years
)

rows = con.sql(f"""
    SELECT anno, regione, comune, popolazione,
           totale_ru_tonnellate, totale_rd_tonnellate, percentuale_rd
    FROM ({parquet_refs})
    WHERE popolazione >= 100000
    ORDER BY anno, regione, comune
""").fetchall()

columns = ["anno", "regione", "comune", "popolazione", "totale_ru_tonnellate", "totale_rd_tonnellate", "percentuale_rd"]
data = [dict(zip(columns, row)) for row in rows]
json.dump(data, sys.stdout, ensure_ascii=False)

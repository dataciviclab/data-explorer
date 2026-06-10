#!/usr/bin/env python3
"""Data loader: BDAP Spese Stato — previsioni definitive per amministrazione e missione.

Singolo file parquet multi-anno (2008-2024)."""
import sys; sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs import object_exists
from lab_connectors.gcs.paths import https_url, CLEAN_BUCKET
import json

slug = "bdap_spese_stato"
year = 2024

if not object_exists(CLEAN_BUCKET, f"{slug}/{year}/{slug}_{year}_clean.parquet"):
    json.dump([], sys.stdout)
    sys.exit(0)

url = https_url("clean", "clean_parquet", slug=slug, year=year)

with safe_connect() as con:
    rows = con.sql(f"""
        SELECT esercizio_finanziario, amministrazione, missione,
               SUM(previsioni_definitive_cp) AS spesa_cp,
               SUM(previsioni_definitive_cs) AS spesa_cs
        FROM read_parquet('{url}')
        GROUP BY esercizio_finanziario, amministrazione, missione
        ORDER BY esercizio_finanziario, amministrazione
    """).fetchall()

data = [
    {"anno": int(r[0]), "amministrazione": r[1], "missione": r[2],
     "spesa_cp": float(r[3]) if r[3] else 0,
     "spesa_cs": float(r[4]) if r[4] else 0}
    for r in rows
]

json.dump(data, sys.stdout, ensure_ascii=False)

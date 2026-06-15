#!/usr/bin/env python3
"""Data loader: Pensioni Pubblica Amministrazione — per qualifica, regione, anno.

Singolo file parquet multi-anno (2014-2024)."""
import sys; sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs import object_exists
from lab_connectors.gcs.paths import https_url, CLEAN_BUCKET
import json

slug = "pensioni_pa_dag"
year = 2024

if not object_exists(CLEAN_BUCKET, f"{slug}/{year}/{slug}_{year}_clean.parquet"):
    json.dump([], sys.stdout)
    sys.exit(0)

url = https_url("clean", "clean_parquet", slug=slug, year=year)

with safe_connect() as con:
    rows = con.sql(f"""
        SELECT anno, qualifica, regione,
               COUNT(*) AS numero_pensioni,
               AVG(importo_mensile) AS importo_medio_mensile
        FROM read_parquet('{url}')
        GROUP BY anno, qualifica, regione
        ORDER BY anno DESC, numero_pensioni DESC
    """).fetchall()

data = [
    {"anno": int(r[0]), "qualifica": r[1], "regione": r[2],
     "numero_pensioni": int(r[3]),
     "importo_medio_mensile": float(r[4]) if r[4] else 0}
    for r in rows
]

json.dump(data, sys.stdout, ensure_ascii=False)

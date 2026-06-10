#!/usr/bin/env python3
"""Data loader: ISTAT housing crowding — componenti per 100 mq per titolo godimento."""
import json, sys
sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs.paths import https_url

url = https_url("clean", "clean_parquet", slug="istat_housing_crowding", year=2024)
with safe_connect() as con:
    rows = con.sql(f"SELECT * FROM read_parquet('{url}') ORDER BY anno, titolo_godimento").fetchall()
data = [{"anno": int(r[0]), "titolo_godimento": r[1], "componenti_per_100mq": float(r[2])} for r in rows]
json.dump(data, sys.stdout, ensure_ascii=False)

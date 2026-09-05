#!/usr/bin/env python3
"""Data loader: ISTAT Housing Crowding — densità abitativa per anno e titolo godimento."""
import json, sys
sys.path.insert(0, "src/data")
from _util import get_location, _parquet_refs
from lab_connectors.duckdb import safe_connect

slug = "istat_housing_crowding"
location = get_location(slug)
url = _parquet_refs(slug, [2024], location)[0]

with safe_connect() as con:
    rows = con.sql(f"""
        SELECT anno, titolo_godimento,
               AVG(componenti_per_100mq) AS componenti_per_100mq
        FROM read_parquet('{url}')
        WHERE titolo_godimento IS NOT NULL
        GROUP BY anno, titolo_godimento
        ORDER BY anno, titolo_godimento
    """).fetchall()

data = [
    {"anno": int(r[0]), "titolo_godimento": r[1],
     "componenti_per_100mq": float(r[2])}
    for r in rows
]

json.dump(data, sys.stdout, ensure_ascii=False)

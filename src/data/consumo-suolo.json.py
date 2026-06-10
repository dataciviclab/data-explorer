#!/usr/bin/env python3
"""Data loader: ISPRA consumo suolo — aggregazione regionale.
Stock% usa AVG, gli altri usano SUM.
Loader custom perche' load_dataset() usa SUM su tutte le metriche."""
import json, sys
sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs import object_exists
from lab_connectors.gcs.paths import https_url

slug = "ispra_consumo_suolo"
year = 2024

if not object_exists("dataciviclab-clean", f"{slug}/{year}/{slug}_{year}_clean.parquet"):
    json.dump([], sys.stdout)
    sys.exit(0)

with safe_connect() as con:
    rows = con.sql(f"""
        SELECT regione,
               AVG(stock_pct_2024) AS stock_pct_2024,
               SUM(stock_ha_2024) AS stock_ha_2024,
               SUM(incremento_netto_ha_2023_2024) AS incremento_netto_ha_2023_2024,
               SUM(incremento_lordo_ha_2023_2024) AS incremento_lordo_ha_2023_2024
        FROM read_parquet('{https_url("clean", "clean_parquet", slug=slug, year=year)}')
        WHERE regione IS NOT NULL AND regione != ''
        GROUP BY regione
        ORDER BY regione
    """).fetchall()

data = [
    {"regione": r[0], "stock_pct_2024": float(r[1]), "stock_ha_2024": float(r[2]),
     "incremento_netto_ha_2023_2024": float(r[3]), "incremento_lordo_ha_2023_2024": float(r[4])}
    for r in rows
]

json.dump(data, sys.stdout, ensure_ascii=False)

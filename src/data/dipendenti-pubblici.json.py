#!/usr/bin/env python3
"""Data loader: Dipendenti pubblici — aggregazione per comparto e anno."""
import json, sys
sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs import object_exists
from lab_connectors.gcs.paths import https_url

slug = "dipendenti_pubblici"
years = list(range(2010, 2024))

valid_years = [y for y in years if object_exists(
    "dataciviclab-clean", f"{slug}/{y}/{slug}_{y}_clean.parquet")]
if not valid_years:
    json.dump([], sys.stdout)
    sys.exit(0)

parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet('{https_url('clean', 'clean_parquet', slug=slug, year=y)}')"
    for y in valid_years
)

with safe_connect() as con:
    rows = con.sql(f"""
        SELECT anno, comparto,
               SUM(donne_tempo_pieno) + SUM(donne_part_time_inf_50) + SUM(donne_part_time_sup_50) AS donne_totali,
               SUM(uomini_tempo_pieno) + SUM(uomini_part_time_inf_50) + SUM(uomini_part_time_sup_50) AS uomini_totali
        FROM ({parquet_refs})
        GROUP BY anno, comparto
        ORDER BY anno, comparto
    """).fetchall()

data = [{"anno": r[0], "comparto": r[1], "donne": int(r[2]), "uomini": int(r[3]), "totale": int(r[2] + r[3])} for r in rows]
json.dump(data, sys.stdout, ensure_ascii=False)

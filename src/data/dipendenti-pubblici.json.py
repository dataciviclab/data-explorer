#!/usr/bin/env python3
"""Data loader: Dipendenti pubblici — aggregazione per comparto e anno."""
import sys
sys.path.insert(0, "src/data")
from _util import get_location, _parquet_exists, _parquet_refs
from _views import available_years, write
from lab_connectors.duckdb import safe_connect

slug = "dipendenti_pubblici"
# Anni dichiarati nel registry del repo: niente range hardcoded.
years = available_years(slug)

location = get_location(slug)
valid_years = [y for y in years if _parquet_exists(slug, y, location)]
if not valid_years:
    write([])
    sys.exit(0)

parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet(\'{url}\')" for url in _parquet_refs(slug, valid_years, location))

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
write(data)

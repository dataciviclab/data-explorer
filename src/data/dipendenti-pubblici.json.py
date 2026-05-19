#!/usr/bin/env python3
"""Data loader: Dipendenti pubblici — aggregazione per comparto e anno."""
import duckdb, json, sys

GCS_BASE = "https://storage.googleapis.com/dataciviclab-clean"
slug = "dipendenti_pubblici"
years = list(range(2010, 2024))

con = duckdb.connect()
parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet('{GCS_BASE}/{slug}/{y}/{slug}_{y}_clean.parquet')"
    for y in years
)

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

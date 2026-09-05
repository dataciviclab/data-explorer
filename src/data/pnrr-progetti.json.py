#!/usr/bin/env python3
"""Data loader: PNRR Progetti — stato di avanzamento dei progetti PNRR.

Singolo file parquet (2026). Aggrega progetti per stato, missione e finanziamento.
"""
import sys; sys.path.insert(0, "src/data")
from _util import get_location, _parquet_exists, _parquet_refs
from lab_connectors.duckdb import safe_connect
import json

slug = "pnrr_progetti"
year = 2026

location = get_location(slug)
if not _parquet_exists(slug, year, location):
    json.dump({"error": "parquet not found"}, sys.stdout)
    sys.exit(0)

url = _parquet_refs(slug, [year], location)[0]

with safe_connect() as con:
    # KPI totali
    kpi_row = con.sql(f"""
        SELECT COUNT(*) AS n_progetti,
               COUNT(DISTINCT cup) AS n_cup,
               ROUND(COALESCE(SUM(fin_totale), 0) / 1e9, 2) AS fin_mld,
               ROUND(COALESCE(SUM(fin_pnrr), 0) / 1e9, 2) AS fin_pnrr_mld
        FROM read_parquet('{url}')
    """).fetchone()

    kpi = {
        "n_progetti": int(kpi_row[0]),
        "n_cup": int(kpi_row[1]),
        "fin_mld": float(kpi_row[2]),
        "fin_pnrr_mld": float(kpi_row[3]),
    }

    # Progetti per stato
    stato_rows = con.sql(f"""
        SELECT stato_avanzamento,
               COUNT(*) AS n,
               ROUND(COALESCE(SUM(fin_totale), 0) / 1e9, 1) AS fin_mld
        FROM read_parquet('{url}')
        WHERE stato_avanzamento IS NOT NULL AND stato_avanzamento != ''
        GROUP BY 1 ORDER BY 2 DESC
    """).fetchall()

    per_stato = [
        {"stato": r[0], "n": int(r[1]), "fin_mld": float(r[2])}
        for r in stato_rows
    ]

    # Progetti per missione
    miss_rows = con.sql(f"""
        SELECT missione || ' — ' || descrizione_missione AS missione,
               COUNT(*) AS n,
               ROUND(COALESCE(SUM(fin_totale), 0) / 1e9, 1) AS fin_mld
        FROM read_parquet('{url}')
        WHERE missione IS NOT NULL
        GROUP BY 1 ORDER BY 3 DESC
    """).fetchall()

    per_missione = [
        {"missione": r[0], "n": int(r[1]), "fin_mld": float(r[2])}
        for r in miss_rows
    ]

    # Progetti per fase iter
    fase_rows = con.sql(f"""
        SELECT descrizione_fase_iter AS fase,
               COUNT(*) AS n,
               ROUND(COALESCE(SUM(fin_totale), 0) / 1e9, 1) AS fin_mld
        FROM read_parquet('{url}')
        WHERE descrizione_fase_iter IS NOT NULL AND descrizione_fase_iter != ''
        GROUP BY 1 ORDER BY 2 DESC
    """).fetchall()

    per_fase = [
        {"fase": r[0], "n": int(r[1]), "fin_mld": float(r[2])}
        for r in fase_rows
    ]

json.dump({"kpi": kpi, "per_stato": per_stato, "per_missione": per_missione,
           "per_fase": per_fase}, sys.stdout, ensure_ascii=False)

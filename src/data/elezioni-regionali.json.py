#!/usr/bin/env python3
"""Data loader: Elezioni Regionali — risultati 2018-2024.

Parquet multi-anno. Aggrega affluenza, presidenti eletti e top liste.
"""
import sys; sys.path.insert(0, "src/data")
from _util import get_location, _parquet_exists, _parquet_refs
from lab_connectors.duckdb import safe_connect
import json

slug = "elezioni_regionali"
years = [2018, 2020, 2024]

location = get_location(slug)
valid_years = [y for y in years if _parquet_exists(slug, y, location)]
if not valid_years:
    json.dump({"error": "no data"}, sys.stdout)
    sys.exit(0)

parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet(\'{url}\')" for url in _parquet_refs(slug, valid_years, location))

with safe_connect() as con:
    # 1. Affluenza per regione (ultima elezione disponibile per ogni regione)
    regioni = con.sql(f"""
        WITH ranked AS (
            SELECT regione, elettori, votanti,
                   EXTRACT(YEAR FROM data_elezione)::INT AS anno,
                   ROW_NUMBER() OVER (PARTITION BY regione ORDER BY EXTRACT(YEAR FROM data_elezione) DESC) AS rk
            FROM ({parquet_refs})
            WHERE elettori > 0
        )
        SELECT regione, elettori, votanti, anno
        FROM ranked WHERE rk = 1
        ORDER BY elettori DESC
    """).fetchall()

    per_regione = [
        {"regione": r[0], "elettori": int(r[1]), "votanti": int(r[2]),
         "anno": int(r[3]),
         "affluenza": round(int(r[2]) / int(r[1]) * 100, 1) if int(r[1]) > 0 else 0}
        for r in regioni
    ]

    # 3. Top 5 liste per elezione
    liste = con.sql(f"""
        WITH ranked AS (
            SELECT anno, lista, tot_voti,
                   ROW_NUMBER() OVER (PARTITION BY anno ORDER BY tot_voti DESC) AS rk
            FROM (
                SELECT EXTRACT(YEAR FROM data_elezione)::INT AS anno,
                       lista, SUM(voti_lista) AS tot_voti
                FROM ({parquet_refs})
                WHERE lista IS NOT NULL AND voti_lista > 0
                GROUP BY 1, 2
            )
        )
        SELECT anno, lista, tot_voti FROM ranked WHERE rk <= 5
        ORDER BY anno, tot_voti DESC
    """).fetchall()

    per_lista = [
        {"anno": int(r[0]), "lista": r[1], "voti": int(r[2])}
        for r in liste
    ]

    # KPI
    tot_regioni = len(per_regione)
    aff_media = round(sum(r["affluenza"] for r in per_regione) / len(per_regione), 1) if per_regione else 0

json.dump({
    "kpi": {
        "tot_regioni": tot_regioni,
        "first_year": min(valid_years),
        "last_year": max(valid_years),
        "aff_media": aff_media,
    },
    "per_regione": per_regione,
    "per_lista": per_lista,
}, sys.stdout, ensure_ascii=False)

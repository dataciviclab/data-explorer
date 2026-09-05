#!/usr/bin/env python3
"""Data loader: Elezioni Europee — risultati 1979-2024.

Parquet multi-anno. Aggrega affluenza, top liste e tendenze per circoscrizione.
"""
import sys; sys.path.insert(0, "src/data")
from _util import get_location, _parquet_exists, _parquet_refs
from lab_connectors.duckdb import safe_connect
import json

slug = "elezioni_europee"
years = list(range(1979, 2025, 5))  # europee ogni 5 anni

location = get_location(slug)
valid_years = [y for y in years if _parquet_exists(slug, y, location)]
if not valid_years:
    json.dump({"error": "no data"}, sys.stdout)
    sys.exit(0)

parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet(\'{url}\')" for url in _parquet_refs(slug, valid_years, location))

with safe_connect() as con:
    # 1. Affluenza per anno
    affluenza = con.sql(f"""
        SELECT EXTRACT(YEAR FROM data_elezione)::INT AS anno,
               SUM(elettori) AS elettori,
               SUM(votanti) AS votanti
        FROM ({parquet_refs})
        WHERE elettori > 0
        GROUP BY 1 ORDER BY 1
    """).fetchall()

    trend = [
        {"anno": int(r[0]), "elettori": int(r[1]), "votanti": int(r[2]),
         "affluenza": round(int(r[2]) / int(r[1]) * 100, 1) if int(r[1]) > 0 else 0}
        for r in affluenza
    ]

    # 2. Top 10 liste per elezione
    liste = con.sql(f"""
        WITH ranked AS (
            SELECT anno, lista, tot_voti,
                   ROW_NUMBER() OVER (PARTITION BY anno ORDER BY tot_voti DESC) AS rk
            FROM (
                SELECT EXTRACT(YEAR FROM data_elezione)::INT AS anno,
                       lista,
                       SUM(voti_lista) AS tot_voti
                FROM ({parquet_refs})
                WHERE lista IS NOT NULL AND voti_lista > 0
                GROUP BY 1, 2
            )
        )
        SELECT anno, lista, tot_voti FROM ranked WHERE rk <= 10
        ORDER BY anno, tot_voti DESC
    """).fetchall()

    per_lista = [
        {"anno": int(r[0]), "lista": r[1], "voti": int(r[2])}
        for r in liste
    ]

    # 3. Affluenza per circoscrizione (ultima elezione)
    circ = con.sql(f"""
        SELECT circoscrizione,
               SUM(elettori) AS elettori,
               SUM(votanti) AS votanti
        FROM ({parquet_refs})
        WHERE EXTRACT(YEAR FROM data_elezione) = (SELECT MAX(EXTRACT(YEAR FROM data_elezione)) FROM ({parquet_refs}))
          AND elettori > 0
        GROUP BY 1 ORDER BY 2 DESC
    """).fetchall()

    per_circoscrizione = [
        {"circoscrizione": r[0], "elettori": int(r[1]), "votanti": int(r[2]),
         "affluenza": round(int(r[2]) / int(r[1]) * 100, 1) if int(r[1]) > 0 else 0}
        for r in circ
    ]

    # KPI
    first = min(trend, key=lambda x: x["anno"]) if trend else None
    last = max(trend, key=lambda x: x["anno"]) if trend else None

json.dump({
    "kpi": {
        "first_year": first["anno"] if first else 0,
        "last_year": last["anno"] if last else 0,
        "affluenza_first": first["affluenza"] if first else 0,
        "affluenza_last": last["affluenza"] if last else 0,
    },
    "trend": trend,
    "per_lista": per_lista,
    "per_circoscrizione": per_circoscrizione,
}, sys.stdout, ensure_ascii=False)

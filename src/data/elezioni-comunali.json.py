#!/usr/bin/env python3
"""Data loader: Elezioni Comunali — risultati 2016-2024.

Parquet multi-anno. Aggrega affluenza, top sindaci e tendenze per regione.
"""
import sys; sys.path.insert(0, "src/data")
from _util import get_location, _parquet_exists, _parquet_refs
from lab_connectors.duckdb import safe_connect
import json

slug = "elezioni_comunali"
years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

location = get_location(slug)
valid_years = [y for y in years if _parquet_exists(slug, y, location)]
if not valid_years:
    json.dump({"error": "no data"}, sys.stdout)
    sys.exit(0)

parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet('{url}')" for url in _parquet_refs(slug, valid_years, location))

with safe_connect() as con:
    # 1. Affluenza per anno
    affluenza = con.sql(f"""
        SELECT EXTRACT(YEAR FROM data_elezione)::INT AS anno,
               SUM(elettori) AS elettori,
               SUM(votanti) AS votanti
        FROM ({parquet_refs})
        WHERE turno = 1 AND elettori > 0
        GROUP BY 1 ORDER BY 1
    """).fetchall()

    trend = [
        {"anno": int(r[0]), "elettori": int(r[1]), "votanti": int(r[2]),
         "affluenza": round(int(r[2]) / int(r[1]) * 100, 1) if int(r[1]) > 0 else 0}
        for r in affluenza
    ]

    # 2. Affluenza per regione (ultima elezione)
    regioni = con.sql(f"""
        SELECT regione,
               SUM(elettori) AS elettori,
               SUM(votanti) AS votanti,
               COUNT(DISTINCT comune) AS comuni
        FROM ({parquet_refs})
        WHERE EXTRACT(YEAR FROM data_elezione) = (SELECT MAX(EXTRACT(YEAR FROM data_elezione)) FROM ({parquet_refs}))
          AND turno = 1 AND elettori > 0
        GROUP BY 1 ORDER BY 2 DESC
    """).fetchall()

    per_regione = [
        {"regione": r[0], "elettori": int(r[1]), "votanti": int(r[2]),
         "comuni": int(r[3]),
         "affluenza": round(int(r[2]) / int(r[1]) * 100, 1) if int(r[1]) > 0 else 0}
        for r in regioni
    ]

    # 3. Top sindaci eletti (per voti assoluti, deduplicati)
    sindaci = con.sql(f"""
        SELECT comune, regione, candidato,
               FIRST(lista ORDER BY voti_lista DESC) AS lista,
               MAX(voti_candidato) AS voti_candidato,
               MAX(elettori) AS elettori
        FROM ({parquet_refs})
        WHERE turno = 1 AND voti_candidato > 0
        GROUP BY 1, 2, 3
        ORDER BY voti_candidato DESC
        LIMIT 20
    """).fetchall()

    top_sindaci = [
        {"comune": r[0], "regione": r[1], "candidato": r[2], "lista": r[3],
         "voti": int(r[4]), "elettori": int(r[5])}
        for r in sindaci
    ]

    # KPI
    first = min(trend, key=lambda x: x["anno"]) if trend else None
    last = max(trend, key=lambda x: x["anno"]) if trend else None
    tot_comuni = con.sql(f"SELECT COUNT(DISTINCT comune) FROM ({parquet_refs}) WHERE turno = 1").fetchone()[0]

json.dump({
    "kpi": {
        "tot_comuni": int(tot_comuni),
        "first_year": first["anno"] if first else 0,
        "last_year": last["anno"] if last else 0,
        "affluenza_first": first["affluenza"] if first else 0,
        "affluenza_last": last["affluenza"] if last else 0,
    },
    "trend": trend,
    "per_regione": per_regione,
    "top_sindaci": top_sindaci,
}, sys.stdout, ensure_ascii=False)

#!/usr/bin/env python3
"""Data loader: Elezioni Referendum — risultati 1995-2022.

Parquet multi-anno. Aggrega affluenza, esito SI/NO e tendenze per regione.
"""
import sys; sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs import object_exists
from lab_connectors.gcs.paths import https_url, CLEAN_BUCKET
import json

slug = "elezioni_referendum"
years = list(range(1995, 2023, 1))

valid_years = [y for y in years if object_exists(
    CLEAN_BUCKET, f"{slug}/{y}/{slug}_{y}_clean.parquet")]
if not valid_years:
    json.dump({"error": "no data"}, sys.stdout)
    sys.exit(0)

parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet('{https_url('clean', 'clean_parquet', slug=slug, year=y)}')"
    for y in valid_years
)

with safe_connect() as con:
    # 1. Affluenza e esito per anno e quesito
    risultati = con.sql(f"""
        SELECT EXTRACT(YEAR FROM data_elezione)::INT AS anno,
               num_quesito,
               SUM(elettori) AS elettori,
               SUM(votanti) AS votanti,
               SUM(voti_si) AS si,
               SUM(voti_no) AS no
        FROM ({parquet_refs})
        WHERE elettori > 0 AND num_quesito IS NOT NULL
        GROUP BY 1, 2
        ORDER BY 1, 2
    """).fetchall()

    trend = [
        {"anno": int(r[0]), "quesito": int(r[1]) if r[1] else 1,
         "elettori": int(r[2]), "votanti": int(r[3]),
         "si": int(r[4]), "no": int(r[5]),
         "affluenza": round(int(r[3]) / int(r[2]) * 100, 1) if int(r[2]) > 0 else 0,
         "pct_si": round(int(r[4]) / (int(r[4]) + int(r[5])) * 100, 1) if (int(r[4]) + int(r[5])) > 0 else 0}
        for r in risultati
    ]

    # 2. Affluenza per regione (ultima elezione)
    regioni = con.sql(f"""
        SELECT regione,
               SUM(elettori) AS elettori,
               SUM(votanti) AS votanti,
               SUM(voti_si) AS si,
               SUM(voti_no) AS no
        FROM ({parquet_refs})
        WHERE EXTRACT(YEAR FROM data_elezione) = (SELECT MAX(EXTRACT(YEAR FROM data_elezione)) FROM ({parquet_refs}))
          AND num_quesito = 1
          AND elettori > 0
        GROUP BY 1 ORDER BY 2 DESC
    """).fetchall()

    per_regione = [
        {"regione": r[0], "elettori": int(r[1]), "votanti": int(r[2]),
         "si": int(r[3]), "no": int(r[4]),
         "affluenza": round(int(r[2]) / int(r[1]) * 100, 1) if int(r[1]) > 0 else 0,
         "pct_si": round(int(r[3]) / (int(r[3]) + int(r[4])) * 100, 1) if (int(r[3]) + int(r[4])) > 0 else 0}
        for r in regioni
    ]

    # KPI
    first = min(trend, key=lambda x: x["anno"]) if trend else None
    last = max(trend, key=lambda x: x["anno"]) if trend else None

json.dump({
    "kpi": {
        "first_year": first["anno"] if first else 0,
        "last_year": last["anno"] if last else 0,
        "tot_referendum": len(set((t["anno"], t["quesito"]) for t in trend)),
    },
    "trend": trend,
    "per_regione": per_regione,
}, sys.stdout, ensure_ascii=False)

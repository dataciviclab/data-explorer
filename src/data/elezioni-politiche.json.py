#!/usr/bin/env python3
"""Data loader: Elezioni Politiche — risultati 1948-2022.

Singolo file parquet (2022) con tutti i dati storici. Aggrega affluenza,
top liste e tendenze per camera/senato.
"""
import sys; sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs import object_exists
from lab_connectors.gcs.paths import https_url, CLEAN_BUCKET
import json

slug = "elezioni_politiche"
year = 2022

if not object_exists(CLEAN_BUCKET, f"{slug}/{year}/{slug}_{year}_clean.parquet"):
    json.dump({"error": "parquet not found"}, sys.stdout)
    sys.exit(0)

url = https_url("clean", "clean_parquet", slug=slug, year=year)

with safe_connect() as con:
    # 1. Affluenza per anno e camera/senato
    affluenza = con.sql(f"""
        SELECT EXTRACT(YEAR FROM data_elezione)::INT AS anno,
               camera_senato,
               MAX(elettori_totali) AS elettori,
               MAX(votanti_totali) AS votanti
        FROM read_parquet('{url}')
        WHERE elettori_totali > 0 AND votanti_totali > 0
        GROUP BY 1, 2
        ORDER BY 1, 2
    """).fetchall()

    trend_affluenza = [
        {"anno": int(r[0]), "camera_senato": r[1],
         "elettori": int(r[2]), "votanti": int(r[3]),
         "affluenza": round(int(r[3]) / int(r[2]) * 100, 1) if int(r[2]) > 0 else 0}
        for r in affluenza
    ]

    # 2. Top 10 liste per elezione (solo Camera)
    liste = con.sql(f"""
        WITH ranked AS (
            SELECT anno, lista, tot_voti,
                   ROW_NUMBER() OVER (PARTITION BY anno ORDER BY tot_voti DESC) AS rk
            FROM (
                SELECT EXTRACT(YEAR FROM data_elezione)::INT AS anno,
                       lista,
                       SUM(voti_lista) AS tot_voti
                FROM read_parquet('{url}')
                WHERE camera_senato = 'C' AND lista IS NOT NULL AND voti_lista > 0
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

    # 3. Affluenza per circoscrizione (ultime elezioni)
    circ = con.sql(f"""
        SELECT circoscrizione,
               MAX(elettori_totali) AS elettori,
               MAX(votanti_totali) AS votanti
        FROM read_parquet('{url}')
        WHERE EXTRACT(YEAR FROM data_elezione) >= 2008
          AND elettori_totali > 0 AND votanti_totali > 0
          AND camera_senato = 'C'
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT 15
    """).fetchall()

    per_circoscrizione = [
        {"circoscrizione": r[0], "elettori": int(r[1]), "votanti": int(r[2]),
         "affluenza": round(int(r[2]) / int(r[1]) * 100, 1) if int(r[1]) > 0 else 0}
        for r in circ
    ]

    # KPI
    tot_anni = len(set(int(r[0]) for r in affluenza))
    first = min(int(r[0]) for r in affluenza) if affluenza else 0
    last = max(int(r[0]) for r in affluenza) if affluenza else 0
    last_aff = next((r for r in trend_affluenza if r["anno"] == last and r["camera_senato"] == "C"), None)
    first_aff = next((r for r in trend_affluenza if r["anno"] == first and r["camera_senato"] == "C"), None)

json.dump({
    "kpi": {
        "tot_anni": tot_anni,
        "first": first, "last": last,
        "affluenza_first": first_aff["affluenza"] if first_aff else 0,
        "affluenza_last": last_aff["affluenza"] if last_aff else 0,
    },
    "trend_affluenza": trend_affluenza,
    "per_lista": per_lista,
    "per_circoscrizione": per_circoscrizione,
}, sys.stdout, ensure_ascii=False)

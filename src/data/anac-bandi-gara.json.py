#!/usr/bin/env python3
"""Data loader: ANAC Bandi di Gara (CIG) — aggregazioni per anno.

Legge tutti gli anni disponibili (2016-2025) e produce un JSON con:
- trend: [{anno, n_gare, n_lotti, importo_totale}]
- per_tipo: [{anno, tipo, n_lotti, importo}]  (tipo_scelta_contraente)
- per_oggetto: [{anno, oggetto, n_lotti, importo}]  (oggetto_principale_contratto)
- per_stato: [{anno, stato, n_lotti, importo}]  (stato della gara)
- top_sa: [{anno, denominazione, importo}]  (top stazioni appaltanti)
- anni: [2016, ...]
"""
import sys, json
sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs import object_exists
from lab_connectors.gcs.paths import https_url

SLUG = "anac_bandi_gara"
YEARS = list(range(2016, 2026))

valid = [
    y for y in YEARS
    if object_exists("dataciviclab-clean", f"{SLUG}/{y}/{SLUG}_{y}_clean.parquet")
]
if not valid:
    json.dump({}, sys.stdout)
    sys.exit(0)

refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet('{https_url('clean', 'clean_parquet', slug=SLUG, year=y)}')"
    for y in valid
)

with safe_connect() as con:
    trend = [
        {"anno": r[0], "n_lotti": int(r[1]), "importo_totale": float(r[2] or 0)}
        for r in con.sql(f"""
            SELECT anno_pubblicazione as anno,
                   COUNT(*) as n_lotti,
                   SUM(COALESCE(importo_lotto, 0)) as importo_totale
            FROM ({refs}) GROUP BY anno_pubblicazione ORDER BY anno_pubblicazione
        """).fetchall()
    ]

    per_tipo = [
        {"anno": r[0], "tipo": r[1], "n_lotti": int(r[2]), "importo": float(r[3] or 0)}
        for r in con.sql(f"""
            SELECT anno_pubblicazione, tipo_scelta_contraente,
                   COUNT(*) as n_lotti, SUM(COALESCE(importo_lotto, 0)) as importo
            FROM ({refs}) WHERE tipo_scelta_contraente IS NOT NULL
            GROUP BY anno_pubblicazione, tipo_scelta_contraente ORDER BY anno_pubblicazione, importo DESC
        """).fetchall()
    ]

    per_oggetto = [
        {"anno": r[0], "oggetto": r[1], "n_lotti": int(r[2]), "importo": float(r[3] or 0)}
        for r in con.sql(f"""
            SELECT anno_pubblicazione, oggetto_principale_contratto,
                   COUNT(*) as n_lotti, SUM(COALESCE(importo_lotto, 0)) as importo
            FROM ({refs}) WHERE oggetto_principale_contratto IS NOT NULL
            GROUP BY anno_pubblicazione, oggetto_principale_contratto ORDER BY anno_pubblicazione, importo DESC
        """).fetchall()
    ]

    per_stato = [
        {"anno": r[0], "stato": r[1], "n_lotti": int(r[2]), "importo": float(r[3] or 0)}
        for r in con.sql(f"""
            SELECT anno_pubblicazione, stato,
                   COUNT(*) as n_lotti, SUM(COALESCE(importo_lotto, 0)) as importo
            FROM ({refs}) WHERE stato IS NOT NULL
            GROUP BY anno_pubblicazione, stato ORDER BY anno_pubblicazione, n_lotti DESC
        """).fetchall()
    ]

    top_sa = [
        {"anno": r[0], "denominazione": r[1], "n_lotti": int(r[2]), "importo": float(r[3] or 0)}
        for r in con.sql(f"""
            SELECT anno_pubblicazione,
                   COALESCE(denominazione_amministrazione_appaltante, 'NON CLASSIFICATA') as sa,
                   COUNT(*) as n_lotti, SUM(COALESCE(importo_lotto, 0)) as importo
            FROM ({refs})
            GROUP BY anno_pubblicazione, sa ORDER BY anno_pubblicazione, importo DESC
        """).fetchall()
    ]

json.dump({
    "trend": trend,
    "per_tipo": per_tipo,
    "per_oggetto": per_oggetto,
    "per_stato": per_stato,
    "top_sa": top_sa,
    "anni": valid,
}, sys.stdout, ensure_ascii=False)

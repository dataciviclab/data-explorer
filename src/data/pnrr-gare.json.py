#!/usr/bin/env python3
"""Data loader: PNRR Gare — gare d'appalto dei progetti PNRR (Italia Domani).

Singolo file parquet (2026). Aggrega trend annuale, top submisure e mix procedure.
"""
import sys; sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs import object_exists
from lab_connectors.gcs.paths import https_url, CLEAN_BUCKET
import json

slug = "pnrr_gare"
year = 2026

if not object_exists(CLEAN_BUCKET, f"{slug}/{year}/{slug}_{year}_clean.parquet"):
    json.dump({"error": "parquet not found"}, sys.stdout)
    sys.exit(0)

url = https_url("clean", "clean_parquet", slug=slug, year=year)

with safe_connect() as con:
    # KPI totali
    kpi_row = con.sql(f"""
        SELECT COUNT(*) AS n_gare,
               COUNT(DISTINCT cup) AS n_progetti,
               ROUND(COALESCE(SUM(importo_complessivo_gara), 0) / 1e9, 2) AS importo_mld,
               ROUND(COALESCE(SUM(importo_aggiudicazione), 0) / 1e9, 2) AS aggiudicato_mld,
               MIN(data_pubblicazione_cig) AS min_data,
               MAX(data_pubblicazione_cig) AS max_data
        FROM read_parquet('{url}')
    """).fetchone()

    kpi = {
        "n_gare": int(kpi_row[0]),
        "n_progetti": int(kpi_row[1]),
        "importo_mld": float(kpi_row[2]),
        "aggiudicato_mld": float(kpi_row[3]),
        "min_data": str(kpi_row[4])[:10] if kpi_row[4] else None,
        "max_data": str(kpi_row[5])[:10] if kpi_row[5] else None,
    }

    # Trend gare per anno (con % aggiudicazione)
    trend_rows = con.sql(f"""
        SELECT EXTRACT(YEAR FROM data_pubblicazione_cig)::INT AS anno,
               COUNT(*) AS n_gare,
               ROUND(COALESCE(SUM(importo_complessivo_gara), 0) / 1e9, 2) AS importo_mld,
               ROUND(COALESCE(SUM(importo_aggiudicazione), 0) / 1e9, 2) AS aggiudicato_mld
        FROM read_parquet('{url}')
        WHERE data_pubblicazione_cig IS NOT NULL
          AND EXTRACT(YEAR FROM data_pubblicazione_cig) >= 2018
        GROUP BY 1 ORDER BY 1
    """).fetchall()

    trend = []
    for r in trend_rows:
        imp = float(r[2])
        agg = float(r[3])
        pct = round(agg / imp * 100, 1) if imp > 0 else 0
        trend.append({
            "anno": int(r[0]), "n_gare": int(r[1]),
            "importo_mld": imp, "aggiudicato_mld": agg,
            "pct_aggiudicazione": pct
        })

    # Top 10 submisure per importo
    sub_rows = con.sql(f"""
        SELECT descrizione_submisura,
               COUNT(*) AS n_gare,
               ROUND(COALESCE(SUM(importo_complessivo_gara), 0) / 1e6, 1) AS importo_mln,
               ROUND(COALESCE(SUM(importo_aggiudicazione), 0) / 1e6, 1) AS aggiudicato_mln
        FROM read_parquet('{url}')
        WHERE descrizione_submisura IS NOT NULL
        GROUP BY 1 ORDER BY 3 DESC LIMIT 10
    """).fetchall()

    per_submisura = [
        {"submisura": r[0], "n_gare": int(r[1]),
         "importo_mln": float(r[2]), "aggiudicato_mln": float(r[3])}
        for r in sub_rows
    ]

    # Mix procedura
    proc_rows = con.sql(f"""
        SELECT descrizione_procedura_aggiudicazione AS procedura,
               COUNT(*) AS n_gare
        FROM read_parquet('{url}')
        WHERE descrizione_procedura_aggiudicazione IS NOT NULL
        GROUP BY 1 ORDER BY 2 DESC
    """).fetchall()

    per_procedura = [
        {"procedura": r[0] or "N/D", "n_gare": int(r[1])}
        for r in proc_rows
    ]

json.dump({"kpi": kpi, "trend": trend, "per_submisura": per_submisura,
           "per_procedura": per_procedura}, sys.stdout, ensure_ascii=False)

#!/usr/bin/env python3
"""Data loader: PNRR Pagamenti — stato dei pagamenti dei progetti PNRR.

Singolo file parquet (2026). Aggrega finanziamento vs pagamento per submisura
e composizione pagamenti per fonte.
"""
import sys; sys.path.insert(0, "src/data")
from _util import get_location, _parquet_exists, _parquet_refs
from lab_connectors.duckdb import safe_connect
import json

slug = "pnrr_pagamenti"
year = 2026

location = get_location(slug)
if not _parquet_exists(slug, year, location):
    json.dump({"error": "parquet not found"}, sys.stdout)
    sys.exit(0)

url = _parquet_refs(slug, [year], location)[0]

with safe_connect() as con:
    # KPI totali
    kpi_row = con.sql(f"""
        SELECT COUNT(*) AS n_record,
               COUNT(DISTINCT cup) AS n_progetti,
               ROUND(COALESCE(SUM(finanziamento_totale), 0) / 1e9, 2) AS fin_mld,
               ROUND(COALESCE(SUM(pagamento_totale), 0) / 1e9, 2) AS pag_mld,
               ROUND(COALESCE(SUM(pagamento_pnrr), 0) / 1e9, 2) AS pag_pnrr_mld
        FROM read_parquet('{url}')
    """).fetchone()

    fin_totale = float(kpi_row[2])
    pag_totale = float(kpi_row[3])
    pct = round(pag_totale / fin_totale * 100, 1) if fin_totale > 0 else 0

    kpi = {
        "n_record": int(kpi_row[0]),
        "n_progetti": int(kpi_row[1]),
        "fin_mld": fin_totale,
        "pag_mld": pag_totale,
        "pag_pnrr_mld": float(kpi_row[4]),
        "pct_erogata": pct,
    }

    # Finanziamento vs Pagamento per submisura (top 10)
    sub_rows = con.sql(f"""
        SELECT descrizione_submisura,
               ROUND(COALESCE(SUM(finanziamento_totale), 0) / 1e6, 1) AS fin_mln,
               ROUND(COALESCE(SUM(pagamento_totale), 0) / 1e6, 1) AS pag_mln
        FROM read_parquet('{url}')
        WHERE descrizione_submisura IS NOT NULL
        GROUP BY 1 ORDER BY 2 DESC LIMIT 10
    """).fetchall()

    per_submisura = [
        {"submisura": r[0], "fin_mln": float(r[1]), "pag_mln": float(r[2]),
         "pct": round(float(r[2]) / float(r[1]) * 100, 1) if float(r[1]) > 0 else 0}
        for r in sub_rows
    ]

    # Composizione pagamenti per fonte
    fonti_rows = con.sql(f"""
        SELECT
            ROUND(COALESCE(SUM(pagamento_stato), 0) / 1e9, 2) AS stato,
            ROUND(COALESCE(SUM(pagamento_ue), 0) / 1e9, 2) AS ue,
            ROUND(COALESCE(SUM(pagamento_fpop), 0) / 1e9, 2) AS fpop,
            ROUND(COALESCE(SUM(pagamento_regione), 0) / 1e9, 2) AS regione,
            ROUND(COALESCE(SUM(pagamento_privato), 0) / 1e9, 2) AS privato,
            ROUND(COALESCE(SUM(pagamento_comune + pagamento_provincia + pagamento_altro_pubblico + pagamento_pnc + pagamento_altri_fondi + pagamento_da_reperire), 0) / 1e9, 2) AS altro
        FROM read_parquet('{url}')
    """).fetchone()

    fonti = [
        {"fonte": "Stato", "mld": float(fonti_rows[0])},
        {"fonte": "UE (non PNRR)", "mld": float(fonti_rows[1])},
        {"fonte": "FPOP", "mld": float(fonti_rows[2])},
        {"fonte": "Regione", "mld": float(fonti_rows[3])},
        {"fonte": "Privato", "mld": float(fonti_rows[4])},
        {"fonte": "Altro", "mld": float(fonti_rows[5])},
    ]

json.dump({"kpi": kpi, "per_submisura": per_submisura, "fonti": fonti},
          sys.stdout, ensure_ascii=False)

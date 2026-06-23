#!/usr/bin/env python3
"""Data loader: 5x1000 — beneficiari e importi per ente (Agenzia delle Entrate)."""
import json, sys
sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs.paths import https_url

SLUG = "ade_cinque_per_mille"
YEARS = [2024]

parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet('{https_url('clean', 'clean_parquet', slug=SLUG, year=y)}')"
    for y in YEARS
)

def _query(sql):
    rel = con.sql(sql)
    cols = [desc[0] for desc in rel.description]
    return [dict(zip(cols, row)) for row in rel.fetchall()]

with safe_connect() as con:
    per_regione = _query(f"""
        SELECT regione,
               COUNT(*) AS num_enti,
               SUM(numero_scelte) AS tot_scelte,
               ROUND(SUM(COALESCE(importo_totale_erogabile, 0)), 0) AS importo_totale
        FROM ({parquet_refs})
        WHERE regione IS NOT NULL
        GROUP BY regione
        ORDER BY importo_totale DESC
    """)

    per_categoria = _query(f"""
        SELECT
            CASE
                WHEN flag_ets_onlus = true AND flag_asd = false AND flag_comune = false
                     AND flag_ricerca_scientifica = false AND flag_ricerca_sanitaria = false THEN 'ETS / ONLUS'
                WHEN flag_ets_onlus = true AND flag_asd = false AND flag_comune = false
                     AND flag_ricerca_scientifica = true AND flag_ricerca_sanitaria = true THEN 'ETS + Ricerca scientifica e sanitaria'
                WHEN flag_ets_onlus = true AND flag_asd = false AND flag_comune = false
                     AND flag_ricerca_scientifica = true THEN 'ETS + Ricerca scientifica'
                WHEN flag_ets_onlus = true AND flag_asd = false AND flag_comune = false
                     AND flag_ricerca_sanitaria = true THEN 'ETS + Ricerca sanitaria'
                WHEN flag_asd = true THEN 'Sportive dilettantistiche'
                WHEN flag_ricerca_scientifica = true AND flag_ricerca_sanitaria = true THEN 'Ricerca scientifica e sanitaria'
                WHEN flag_ricerca_scientifica = true THEN 'Ricerca scientifica'
                WHEN flag_ricerca_sanitaria = true THEN 'Ricerca sanitaria'
                WHEN flag_comune = true THEN 'Comuni'
                WHEN flag_beni_culturali = true THEN 'Beni culturali'
                WHEN flag_area_protetta = true THEN 'Aree protette'
                ELSE 'Altro'
            END AS categoria,
            COUNT(*) AS num_enti,
            ROUND(SUM(COALESCE(importo_totale_erogabile, 0)), 0) AS importo_totale
        FROM ({parquet_refs})
        GROUP BY categoria
        ORDER BY importo_totale DESC
    """)

    top_enti = _query(f"""
        SELECT denominazione, regione, sigla_provincia, comune,
               numero_scelte,
               ROUND(COALESCE(importo_totale_erogabile, 0), 0) AS importo_totale
        FROM ({parquet_refs})
        ORDER BY importo_totale_erogabile DESC NULLS LAST
        LIMIT 500
    """)

    tot = _query(f"""
        SELECT COUNT(*) AS num_enti,
               SUM(numero_scelte) AS tot_scelte,
               ROUND(SUM(importo_totale_erogabile), 0) AS importo_totale
        FROM ({parquet_refs})
    """)[0]

output = {
    "anno": 2024,
    "num_enti": tot["num_enti"],
    "tot_scelte": tot["tot_scelte"],
    "importo_totale": tot["importo_totale"],
    "per_regione": per_regione,
    "per_categoria": per_categoria,
    "top_enti": top_enti,
}

json.dump(output, sys.stdout, ensure_ascii=False)

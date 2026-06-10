#!/usr/bin/env python3
"""Data loader: MEF Partecipazioni — per anno, categoria e settore.
Deduplica gli addetti per partecipata (evita doppio conteggio quando piu PA
hanno quote nella stessa societa).
Loader custom perche' serve subquery di dedup non supportata da _util.py."""
import json, sys
sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs import object_exists
from lab_connectors.gcs.paths import https_url

slug = "mef_partecipazioni"
years = list(range(2020, 2024))

valid_years = [y for y in years if object_exists(
    "dataciviclab-clean", f"{slug}/{y}/{slug}_{y}_clean.parquet")]
if not valid_years:
    json.dump([], sys.stdout)
    sys.exit(0)

parquet_refs = " UNION ALL ".join(
    "SELECT * FROM read_parquet('"
    + https_url("clean", "clean_parquet", slug=slug, year=y)
    + "')" for y in valid_years
)

with safe_connect() as con:
    rows = con.sql(f"""
        SELECT anno, amministrazione_categoria, partecipata_settore_attivita,
               COUNT(*) AS num_partecipate,
               AVG(quota_partecipazione_diretta) AS quota_media,
               SUM(totale_oneri_importo_impegnato) AS totale_oneri,
               SUM(addetti_dedup) AS totale_addetti
        FROM (
            SELECT anno, amministrazione_categoria, partecipata_settore_attivita,
                   totale_oneri_importo_impegnato, quota_partecipazione_diretta,
                   MAX(CASE WHEN partecipata_numero_di_addetti > 0
                       THEN partecipata_numero_di_addetti ELSE 0 END) AS addetti_dedup
            FROM ({parquet_refs})
            WHERE amministrazione_categoria IS NOT NULL
              AND partecipata_settore_attivita IS NOT NULL
            GROUP BY anno, amministrazione_categoria, partecipata_settore_attivita,
                     partecipata_denominazione, totale_oneri_importo_impegnato,
                     quota_partecipazione_diretta
        )
        GROUP BY anno, amministrazione_categoria, partecipata_settore_attivita
        ORDER BY anno, amministrazione_categoria
    """).fetchall()

data = [
    {"anno": int(r[0]), "categoria": r[1], "settore": r[2],
     "num_partecipate": int(r[3]),
     "quota_media": float(r[4]) if r[4] else 0,
     "totale_oneri": float(r[5]) if r[5] else 0,
     "totale_addetti": float(r[6]) if r[6] else 0}
    for r in rows
]

json.dump(data, sys.stdout, ensure_ascii=False)

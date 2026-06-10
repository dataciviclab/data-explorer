#!/usr/bin/env python3
"""Data loader: Camera Votazioni — esito e conteggi per votazione.
Custom loader perché la colonna data (DATE) non è JSON-serializzabile."""
import json, sys
sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs.paths import https_url

slug = "camera_votazioni_sparql"
years = list(range(2018, 2026))

parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet('{https_url('clean', 'clean_parquet', slug=slug, year=y)}')"
    for y in years
)

with safe_connect() as con:
    rows = con.sql(f"""
        SELECT
            votazione,
            CAST(data AS VARCHAR) AS data,
            legislatura,
            titolo,
            approvato,
            richiesta_fiducia,
            votazione_finale,
            favorevoli,
            contrari,
            astenuti,
            votanti,
            presenti,
            maggioranza
        FROM ({parquet_refs})
        WHERE approvato IS NOT NULL
        ORDER BY data DESC
    """).fetchall()

columns = ["votazione", "data", "legislatura", "titolo", "approvato",
           "richiesta_fiducia", "votazione_finale", "favorevoli", "contrari",
           "astenuti", "votanti", "presenti", "maggioranza"]

data = [dict(zip(columns, [int(v) if isinstance(v, float) and v == v and v == int(v) else v for v in row])) for row in rows]
json.dump(data, sys.stdout, ensure_ascii=False)

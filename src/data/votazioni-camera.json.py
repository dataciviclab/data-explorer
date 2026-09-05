#!/usr/bin/env python3
"""Data loader: Camera Votazioni — esito e conteggi per votazione.
Custom loader perché la colonna data (DATE) non è JSON-serializzabile."""
import json, sys
sys.path.insert(0, "src/data")
from _util import get_location, _parquet_refs
from lab_connectors.duckdb import safe_connect

slug = "camera_votazioni_sparql"
years = list(range(2018, 2026))

location = get_location(slug)
parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet(\'{url}\')" for url in _parquet_refs(slug, years, location))

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

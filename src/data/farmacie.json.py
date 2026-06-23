#!/usr/bin/env python3
"""Data loader: anagrafica farmacie italiane — conteggio per regione, provincia, tipologia."""
import json, sys
sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs.paths import https_url

SLUG = "farmacie"
YEARS = [2026]

parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet('{https_url('clean', 'clean_parquet', slug=SLUG, year=y)}')"
    for y in YEARS
)

def _query(sql):
    """Esegue SQL e restituisce lista di dict — senza pandas/numpy."""
    rel = con.sql(sql)
    cols = [desc[0] for desc in rel.description]
    return [dict(zip(cols, row)) for row in rel.fetchall()]

with safe_connect() as con:
    per_regione = _query(f"""
        SELECT regione, COUNT(*) AS totale_farmacie,
               COUNT(DISTINCT comune) AS comuni_con_farmacie
        FROM ({parquet_refs})
        GROUP BY regione
        ORDER BY regione
    """)
    per_tipologia = _query(f"""
        SELECT descrizione_tipologia, COUNT(*) AS totale
        FROM ({parquet_refs})
        GROUP BY descrizione_tipologia
        ORDER BY totale DESC
    """)
    per_provincia = _query(f"""
        SELECT provincia, sigla_provincia, regione, COUNT(*) AS totale
        FROM ({parquet_refs})
        GROUP BY provincia, sigla_provincia, regione
        ORDER BY totale DESC
        LIMIT 30
    """)

    # Anno
    anno = YEARS[0]

output = {
    "anno": anno,
    "totale_farmacie": sum(r["totale_farmacie"] for r in per_regione),
    "per_regione": per_regione,
    "per_tipologia": per_tipologia,
    "per_provincia": per_provincia,
}

json.dump(output, sys.stdout, ensure_ascii=False)

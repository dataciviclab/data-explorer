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

with safe_connect() as con:
    # Dati per regione
    per_regione = con.sql(f"""
        SELECT regione, COUNT(*) AS totale_farmacie,
               COUNT(DISTINCT comune) AS comuni_con_farmacie
        FROM ({parquet_refs})
        GROUP BY regione
        ORDER BY regione
    """).fetchdf().to_dict(orient="records")

    # Dati per tipologia
    per_tipologia = con.sql(f"""
        SELECT descrizione_tipologia, COUNT(*) AS totale
        FROM ({parquet_refs})
        GROUP BY descrizione_tipologia
        ORDER BY totale DESC
    """).fetchdf().to_dict(orient="records")

    # Dati per provincia (top 30)
    per_provincia = con.sql(f"""
        SELECT provincia, sigla_provincia, regione, COUNT(*) AS totale
        FROM ({parquet_refs})
        GROUP BY provincia, sigla_provincia, regione
        ORDER BY totale DESC
        LIMIT 30
    """).fetchdf().to_dict(orient="records")

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

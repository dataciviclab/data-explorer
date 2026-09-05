#!/usr/bin/env python3
"""Data loader: IRPEF — capoluoghi di regione (per confronto chart)."""
import json
import sys
sys.path.insert(0, "src/data")
from _util import get_location, _parquet_refs
from lab_connectors.duckdb import safe_connect

slug = "irpef_comunale"
years = list(range(2019, 2024))
CAPOLUOGHI = ["ROMA", "MILANO", "TORINO", "GENOVA", "NAPOLI", "BOLOGNA", "PALERMO",
              "FIRENZE", "BARI", "VENEZIA", "TRIESTE", "L'AQUILA", "ANCONA", "PERUGIA",
              "CAMPOBASSO", "POTENZA", "CAGLIARI", "TRENTO"]

location = get_location(slug)
parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet('{url}')" for url in _parquet_refs(slug, years, location))

# Safe quoting for SQL IN clause
quoted = ", ".join("'" + c.replace("'", "''") + "'" for c in CAPOLUOGHI)
with safe_connect() as con:
    rows = con.sql(f"""
        SELECT anno_di_imposta AS anno, regione, denominazione_comune AS comune,
               numero_contribuenti, reddito_imponibile_eur, imposta_netta_eur
        FROM ({parquet_refs})
        WHERE denominazione_comune IN ({quoted})
        ORDER BY anno, regione, comune
    """).fetchall()

columns = ["anno", "regione", "comune", "numero_contribuenti", "reddito_imponibile_eur", "imposta_netta_eur"]
data = [dict(zip(columns, row)) for row in rows]
json.dump(data, sys.stdout, ensure_ascii=False)

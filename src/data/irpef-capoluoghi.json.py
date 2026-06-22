#!/usr/bin/env python3
"""Data loader: IRPEF — capoluoghi di regione (per confronto chart)."""
import duckdb
import json
import sys
from lab_connectors.gcs.paths import https_url

slug = "irpef_comunale"
years = list(range(2019, 2024))
CAPOLUOGHI = ["ROMA", "MILANO", "TORINO", "GENOVA", "NAPOLI", "BOLOGNA", "PALERMO",
              "FIRENZE", "BARI", "VENEZIA", "TRIESTE", "L'AQUILA", "ANCONA", "PERUGIA",
              "CAMPOBASSO", "POTENZA", "CAGLIARI", "TRENTO"]

con = duckdb.connect()
parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet('{https_url('clean', 'clean_parquet', slug=slug, year=y)}')"
    for y in years
)

# Safe quoting for SQL IN clause
quoted = ", ".join("'" + c.replace("'", "''") + "'" for c in CAPOLUOGHI)
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

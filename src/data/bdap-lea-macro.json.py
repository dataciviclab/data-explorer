#!/usr/bin/env python3
"""Data loader: BDAP LEA — spesa per regione e macro-area (prevenzione, distrettuale, ospedaliera, ricerca).

Deriva la macro-area dal primo carattere del codice voce contabile:
  1 = Prevenzione collettiva e sanità pubblica
  2 = Assistenza distrettuale
  3 = Assistenza ospedaliera
  (4 = Ricerca — non ha voci di dettaglio nei dati correnti)
"""
import json, sys
sys.path.insert(0, "src/data")
from _util import get_location, _parquet_exists, _parquet_refs
from lab_connectors.duckdb import safe_connect

slug = "bdap_lea"
years = list(range(2019, 2025))

location = get_location(slug)
valid_years = [y for y in years if _parquet_exists(slug, y, location)]
if not valid_years:
    json.dump([], sys.stdout)
    sys.exit(0)

parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet(\'{url}\')" for url in _parquet_refs(slug, valid_years, location))

with safe_connect() as con:
    rows = con.sql(f"""
        SELECT
            anno_riferimento AS anno,
            descrizione_regione,
            macro_area AS descrizione_voce_contabile,
            SUM(importo_totale) AS importo_totale
        FROM (
            SELECT *,
                CASE LEFT(codice_voce_contabile, 1)
                    WHEN '1' THEN 'Prevenzione e sanità pubblica'
                    WHEN '2' THEN 'Assistenza distrettuale'
                    WHEN '3' THEN 'Assistenza ospedaliera'
                    WHEN '4' THEN 'Ricerca'
                END AS macro_area
            FROM ({parquet_refs})
        )
        WHERE codice_ente_ssn NOT IN ('000', '999')
          AND macro_area IS NOT NULL
        GROUP BY anno_riferimento, descrizione_regione, macro_area
        ORDER BY anno_riferimento, descrizione_regione, macro_area
    """).fetchall()

data = [
    {"anno": int(r[0]), "descrizione_regione": r[1],
     "descrizione_voce_contabile": r[2], "importo_totale": float(r[3])}
    for r in rows
]

json.dump(data, sys.stdout, ensure_ascii=False)

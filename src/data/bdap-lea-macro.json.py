#!/usr/bin/env python3
"""Data loader: BDAP LEA — spesa per regione e macro-area (prevenzione, distrettuale, ospedaliera, ricerca).

Deriva la macro-area dal primo carattere del codice voce contabile:
  1 = Prevenzione collettiva e sanità pubblica
  2 = Assistenza distrettuale
  3 = Assistenza ospedaliera
  (4 = Ricerca — non ha voci di dettaglio nei dati correnti)
"""
import json
import sys
import duckdb

from lab_connectors.gcs.paths import https_url

slug = "bdap_lea"
year = 2024
url = https_url("clean", "clean_parquet", slug=slug, year=year)

con = duckdb.connect()
rows = con.sql(f"""
    SELECT
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
        FROM read_parquet('{url}')
    )
    WHERE codice_ente_ssn NOT IN ('000', '999')
      AND macro_area IS NOT NULL
    GROUP BY descrizione_regione, macro_area
    ORDER BY descrizione_regione, macro_area
""").fetchall()

data = [
    {
        "descrizione_regione": r[0],
        "descrizione_voce_contabile": r[1],
        "importo_totale": float(r[2]),
    }
    for r in rows
]

json.dump(data, sys.stdout, ensure_ascii=False)

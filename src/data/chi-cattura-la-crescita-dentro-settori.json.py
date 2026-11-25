#!/usr/bin/env python3
"""Cross-view: Chi cattura la crescita — dentro i settori.

Legge i mart SBS `mart_sbs_size` (classi dimensionali) e
`mart_sbs_distribuzione` (quartili Q1/Q2/Q3) e restituisce l'ultimo anno
disponibile. Nessun path GCS e nessun anno scritto nel loader.
"""

import json
import sys

sys.path.insert(0, "src/data")
from _views import mart_urls
from lab_connectors.duckdb import safe_connect

SIZE = "istat_sbs_imprese__mart_sbs_size"
DIST = "istat_sbs_imprese__mart_sbs_distribuzione"


def latest_year_rows(urls: list[str]) -> list[dict]:
    """Righe dell'ultimo anno presente nel mart."""
    refs = ", ".join("'" + url.replace("'", "''") + "'" for url in urls)
    query = f"""
        WITH src AS (SELECT * FROM read_parquet([{refs}], union_by_name = true))
        SELECT * FROM src WHERE anno = (SELECT MAX(anno) FROM src)
    """
    with safe_connect() as con:
        cursor = con.sql(query)
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


size_rows = latest_year_rows(mart_urls(SIZE))
dist_rows = latest_year_rows(mart_urls(DIST))
anno = max(row["anno"] for row in size_rows)

json.dump(
    {
        "anno": anno,
        "size": size_rows,
        "distribuzione": dist_rows,
    },
    sys.stdout,
    ensure_ascii=False,
)

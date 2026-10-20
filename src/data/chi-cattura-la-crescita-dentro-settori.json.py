#!/usr/bin/env python3
"""Cross-view: Chi cattura la crescita — dentro i settori.

Legge i mart SBS `mart_sbs_size` (classi dimensionali) e
`mart_sbs_distribuzione` (quartili Q1/Q2/Q3) per il 2023.
"""

import json
import sys

import requests

sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect

SIZE_URL = (
    "https://storage.googleapis.com/dataciviclab-mart/"
    "istat_sbs_imprese/2024/mart_sbs_size.parquet"
)
DIST_URL = (
    "https://storage.googleapis.com/dataciviclab-mart/"
    "istat_sbs_imprese/2024/mart_sbs_distribuzione.parquet"
)


def available(url: str) -> bool:
    try:
        return requests.head(url, timeout=20).status_code == 200
    except Exception:
        return False


if not available(SIZE_URL) or not available(DIST_URL):
    json.dump({"size": [], "distribuzione": []}, sys.stdout)
    sys.exit(0)

with safe_connect() as con:
    size_rows = con.execute(
        f"SELECT * FROM read_parquet('{SIZE_URL}') WHERE anno = 2023"
    ).fetchall()
    size_cols = [d[0] for d in con.execute(f"SELECT * FROM read_parquet('{SIZE_URL}') LIMIT 0").description]

    dist_rows = con.execute(
        f"SELECT * FROM read_parquet('{DIST_URL}') WHERE anno = 2023"
    ).fetchall()
    dist_cols = [d[0] for d in con.execute(f"SELECT * FROM read_parquet('{DIST_URL}') LIMIT 0").description]

json.dump(
    {
        "size": [dict(zip(size_cols, row)) for row in size_rows],
        "distribuzione": [dict(zip(dist_cols, row)) for row in dist_rows],
    },
    sys.stdout,
    ensure_ascii=False,
)

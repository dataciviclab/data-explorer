#!/usr/bin/env python3
"""Cross-view: Chi cattura la crescita — settori (v2).

Legge il mart settoriale SBS (`istat_sbs_imprese__mart_sbs_settore`) e il
deflatore GVA Eurostat per NACE, e produce la matrice 2014-2024 con valori
reali per ora e quote settoriali.
"""

import json
import pathlib
import sys

import requests

sys.path.insert(0, "src/data")
from _util import _parquet_exists, _parquet_refs, get_location
from lab_connectors.duckdb import safe_connect

# Mart pubblico del candidate SBS (2024). Il path è il contratto del producer:
# gs://dataciviclab-mart/istat_sbs_imprese/2024/mart_sbs_settore.parquet
SBS_MART_URL = (
    "https://storage.googleapis.com/dataciviclab-mart/"
    "istat_sbs_imprese/2024/mart_sbs_settore.parquet"
)

GVA_YEARS = [2026]

gva_loc = get_location("eurostat_gva_nuts3")
gva_years = [
    y for y in GVA_YEARS if _parquet_exists("eurostat_gva_nuts3", y, gva_loc)
]

try:
    sbs_ok = requests.head(SBS_MART_URL, timeout=20).status_code == 200
except Exception:
    sbs_ok = False

if not sbs_ok or not gva_years:
    json.dump([], sys.stdout)
    sys.exit(0)

sql_path = (
    pathlib.Path(__file__).resolve().parents[2]
    / "cross-views"
    / "defs"
    / "chi-cattura-la-crescita-settori.sql"
)
sql_template = sql_path.read_text()

cte_sbs = f"SELECT * FROM read_parquet('{SBS_MART_URL}')"
cte_gva = " UNION ALL ".join(
    f"SELECT * FROM read_parquet('{r}')"
    for r in _parquet_refs("eurostat_gva_nuts3", gva_years, gva_loc)
)

sql = sql_template.replace("{cte_sbs}", cte_sbs).replace("{cte_gva}", cte_gva)

with safe_connect() as con:
    rows = con.sql(sql).fetchall()
    columns = [d[0] for d in con.sql(sql).description]

json.dump([dict(zip(columns, row)) for row in rows], sys.stdout, ensure_ascii=False)

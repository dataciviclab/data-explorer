#!/usr/bin/env python3
"""Cross-view: Chi cattura la crescita — settori (v2).

Legge il mart settoriale SBS (`istat_sbs_imprese__mart_sbs_settore`) e il
deflatore GVA Eurostat per NACE, e produce la matrice con valori reali per
ora e quote settoriali.

Nessun path GCS e nessun anno scritto nel loader: i mart vengono dal registry
e gli anni da `available_years`.
"""

import json
import pathlib
import sys

sys.path.insert(0, "src/data")
from _util import _parquet_exists, _parquet_refs, get_location
from _views import available_years, mart_urls
from lab_connectors.duckdb import safe_connect

sbs_urls = mart_urls("istat_sbs_imprese__mart_sbs_settore")

gva_loc = get_location("eurostat_gva_nuts3")
gva_years = [
    year
    for year in available_years("eurostat_gva_nuts3")
    if _parquet_exists("eurostat_gva_nuts3", year, gva_loc)
][-1:]
if not gva_years:
    raise RuntimeError(
        "chi-cattura-la-crescita-settori: nessun parquet GVA pubblicato per eurostat_gva_nuts3"
    )

sql_path = (
    pathlib.Path(__file__).resolve().parents[2]
    / "cross-views"
    / "defs"
    / "chi-cattura-la-crescita-settori.sql"
)
sql_template = sql_path.read_text()

cte_sbs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet('{url}')" for url in sbs_urls
)
cte_gva = " UNION ALL ".join(
    f"SELECT * FROM read_parquet('{ref}')"
    for ref in _parquet_refs("eurostat_gva_nuts3", gva_years, gva_loc)
)

sql = sql_template.replace("{cte_sbs}", cte_sbs).replace("{cte_gva}", cte_gva)

with safe_connect() as con:
    rows = con.sql(sql).fetchall()
    columns = [description[0] for description in con.sql(sql).description]

json.dump([dict(zip(columns, row)) for row in rows], sys.stdout, ensure_ascii=False)

#!/usr/bin/env python3
"""Cross-view: Chi cattura la crescita — settori.

Incrocia valore aggiunto per addetto (SBS + ASIA) e retribuzioni private
(INPS) per sezione ATECO, 2014-2023.
"""

import json
import pathlib
import sys

sys.path.insert(0, "src/data")
from _util import _parquet_exists, _parquet_refs, get_location
from lab_connectors.duckdb import safe_connect

SBS_YEARS = [2023]
ASIA_YEARS = [2024]
INPS_YEARS = [2026]

sbs_loc = get_location("istat_sbs_imprese")
asia_loc = get_location("istat_asia_imprese_addetti")
inps_loc = get_location("inps_retribuzioni")

sbs_years = [y for y in SBS_YEARS if _parquet_exists("istat_sbs_imprese", y, sbs_loc)]
asia_years = [
    y for y in ASIA_YEARS if _parquet_exists("istat_asia_imprese_addetti", y, asia_loc)
]
inps_years = [y for y in INPS_YEARS if _parquet_exists("inps_retribuzioni", y, inps_loc)]

if not sbs_years or not asia_years or not inps_years:
    json.dump([], sys.stdout)
    sys.exit(0)

sql_path = (
    pathlib.Path(__file__).resolve().parents[2]
    / "cross-views"
    / "defs"
    / "chi-cattura-la-crescita-settori.sql"
)
sql_template = sql_path.read_text()


def cte(refs: list[str]) -> str:
    return " UNION ALL ".join(f"SELECT * FROM read_parquet('{r}')" for r in refs)


sql = (
    sql_template.replace(
        "{cte_sbs}", cte(_parquet_refs("istat_sbs_imprese", sbs_years, sbs_loc))
    )
    .replace(
        "{cte_asia}",
        cte(_parquet_refs("istat_asia_imprese_addetti", asia_years, asia_loc)),
    )
    .replace(
        "{cte_inps}",
        cte(_parquet_refs("inps_retribuzioni", inps_years, inps_loc)),
    )
)

with safe_connect() as con:
    rows = con.sql(sql).fetchall()
    columns = [d[0] for d in con.sql(sql).description]

json.dump([dict(zip(columns, row)) for row in rows], sys.stdout, ensure_ascii=False)

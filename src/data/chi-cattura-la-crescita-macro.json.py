#!/usr/bin/env python3
"""Cross-view: Chi cattura la crescita — macro.

Legge NAMA10 (quota lavoro/capitale, salari, deflatore), produttività per
persona (Eurostat) e dipendenti (Eurostat) e produce la serie 1995-2024.
"""

import json
import pathlib
import sys

sys.path.insert(0, "src/data")
from _util import _parquet_exists, _parquet_refs, get_location
from lab_connectors.duckdb import safe_connect

NAMA_YEARS = [2026]
PROD_YEARS = [2026]
EMP_YEARS = [2026]

nama_loc = get_location("eurostat_nama10_gdp")
prod_loc = get_location("eurostat_labour_productivity_nuts3")
emp_loc = get_location("eurostat_emp_nuts3")

nama_years = [y for y in NAMA_YEARS if _parquet_exists("eurostat_nama10_gdp", y, nama_loc)]
prod_years = [
    y for y in PROD_YEARS if _parquet_exists("eurostat_labour_productivity_nuts3", y, prod_loc)
]
emp_years = [y for y in EMP_YEARS if _parquet_exists("eurostat_emp_nuts3", y, emp_loc)]

if not nama_years or not prod_years or not emp_years:
    json.dump([], sys.stdout)
    sys.exit(0)

sql_path = (
    pathlib.Path(__file__).resolve().parents[2]
    / "cross-views"
    / "defs"
    / "chi-cattura-la-crescita-macro.sql"
)
sql_template = sql_path.read_text()


def cte(refs: list[str]) -> str:
    return " UNION ALL ".join(f"SELECT * FROM read_parquet('{r}')" for r in refs)


sql = (
    sql_template.replace(
        "{cte_nama}", cte(_parquet_refs("eurostat_nama10_gdp", nama_years, nama_loc))
    )
    .replace(
        "{cte_prod}",
        cte(_parquet_refs("eurostat_labour_productivity_nuts3", prod_years, prod_loc)),
    )
    .replace("{cte_emp}", cte(_parquet_refs("eurostat_emp_nuts3", emp_years, emp_loc)))
)

with safe_connect() as con:
    rows = con.sql(sql).fetchall()
    columns = [d[0] for d in con.sql(sql).description]

json.dump([dict(zip(columns, row)) for row in rows], sys.stdout, ensure_ascii=False)

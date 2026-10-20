#!/usr/bin/env python3
"""Cross-view: Chi cattura la crescita — cuneo fiscale e distribuzione IRPEF.

OECD Taxing Wages (single, 100% salario medio) + fasce IRPEF MEF, 2015-2023.
"""

import json
import pathlib
import sys

sys.path.insert(0, "src/data")
from _util import _parquet_exists, _parquet_refs, get_location
from lab_connectors.duckdb import safe_connect

OECD_YEARS = [2026]
IRPEF_YEARS = list(range(2015, 2024))

oecd_loc = get_location("oecd_taxing_wages")
irpef_loc = get_location("irpef_comunale")

oecd_years = [y for y in OECD_YEARS if _parquet_exists("oecd_taxing_wages", y, oecd_loc)]
irpef_years = [y for y in IRPEF_YEARS if _parquet_exists("irpef_comunale", y, irpef_loc)]

if not oecd_years or not irpef_years:
    json.dump([], sys.stdout)
    sys.exit(0)

sql_path = (
    pathlib.Path(__file__).resolve().parents[2]
    / "cross-views"
    / "defs"
    / "chi-cattura-la-crescita-cuneo.sql"
)
sql_template = sql_path.read_text()


def cte(refs: list[str]) -> str:
    return " UNION ALL ".join(f"SELECT * FROM read_parquet('{r}')" for r in refs)


sql = sql_template.replace(
    "{cte_oecd}", cte(_parquet_refs("oecd_taxing_wages", oecd_years, oecd_loc))
).replace(
    "{cte_irpef}", cte(_parquet_refs("irpef_comunale", irpef_years, irpef_loc))
)

with safe_connect() as con:
    rows = con.sql(sql).fetchall()
    columns = [d[0] for d in con.sql(sql).description]

json.dump([dict(zip(columns, row)) for row in rows], sys.stdout, ensure_ascii=False)

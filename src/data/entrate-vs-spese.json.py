#!/usr/bin/env python3
"""Cross-view: Entrate vs Spese — Il Bilancio dello Stato.

Legge la definizione SQL da cross-views/defs/ e la esegue con DuckDB
su parquet GCS di bdap_entrate_stato + bdap_spese_stato.

Nota: entrambi i dataset hanno un UNICO file multi-anno (2024 contiene 2008-2024).
"""
import json
import pathlib
import sys

sys.path.insert(0, "src/data")
from _util import _parquet_refs
from lab_connectors.duckdb import safe_connect

# Entrambi i dataset hanno un unico file multi-anno (il 2024 contiene tutti gli anni)
ENTRATE_YEARS = [2024]
SPESE_YEARS = [2024]

# Carica definizione SQL
sql_path = pathlib.Path(__file__).resolve().parents[2] / "cross-views" / "defs" / "entrate-vs-spese.sql"
sql_template = sql_path.read_text()

# Costruisci CTE con UNION ALL (un file per dataset)
entrate_refs = _parquet_refs("bdap_entrate_stato", ENTRATE_YEARS)
spese_refs = _parquet_refs("bdap_spese_stato", SPESE_YEARS)

cte_entrate = " UNION ALL ".join(f"SELECT * FROM read_parquet('{r}')" for r in entrate_refs)
cte_spese = " UNION ALL ".join(f"SELECT * FROM read_parquet('{r}')" for r in spese_refs)

sql = sql_template.replace("{cte_entrate}", cte_entrate).replace("{cte_spese}", cte_spese)

with safe_connect() as con:
    rows = con.sql(sql).fetchall()
    columns = [d[0] for d in con.sql(sql).description]

data = [dict(zip(columns, row)) for row in rows]
json.dump(data, sys.stdout, ensure_ascii=False)

#!/usr/bin/env python3
"""Cross-view: Previsione vs Consuntivo per Missione di spesa.

Legge la definizione SQL da cross-views/defs/ e la esegue con DuckDB
su parquet GCS di bdap_spese_stato + bdap_pagamenti_stato.

Nota: bdap_spese_stato ha un UNICO file multi-anno (2024 contiene 2008-2024).
bdap_pagamenti_stato ha file per-anno (2014-2025).
"""
import json
import pathlib
import sys

sys.path.insert(0, "src/data")
from _util import _parquet_refs, _parquet_exists
from lab_connectors.duckdb import safe_connect

# bdap_spese_stato: unico file multi-anno (contiene tutti gli anni dal 2008)
SPESE_YEARS = [2024]
# bdap_pagamenti_stato: file per-anno, overlap 2014-2024
PAGAMENTI_YEARS = [y for y in range(2014, 2025) if _parquet_exists("bdap_pagamenti_stato", y)]

if not SPESE_YEARS or not PAGAMENTI_YEARS:
    json.dump([], sys.stdout)
    sys.exit(0)

# Carica definizione SQL
sql_path = pathlib.Path(__file__).resolve().parents[2] / "cross-views" / "defs" / "previsione-vs-consuntivo.sql"
sql_template = sql_path.read_text()

# Costruisci CTE con UNION ALL multi-anno
spese_refs = _parquet_refs("bdap_spese_stato", SPESE_YEARS)
pagamenti_refs = _parquet_refs("bdap_pagamenti_stato", PAGAMENTI_YEARS)

cte_spese = " UNION ALL ".join(f"SELECT * FROM read_parquet('{r}')" for r in spese_refs)
cte_pagamenti = " UNION ALL ".join(f"SELECT * FROM read_parquet('{r}')" for r in pagamenti_refs)

sql = sql_template.replace("{cte_spese}", cte_spese).replace("{cte_pagamenti}", cte_pagamenti)

with safe_connect() as con:
    rows = con.sql(sql).fetchall()
    columns = [d[0] for d in con.sql(sql).description]

data = [dict(zip(columns, row)) for row in rows]
json.dump(data, sys.stdout, ensure_ascii=False)

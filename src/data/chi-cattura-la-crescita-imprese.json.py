#!/usr/bin/env python3
"""Cross-view: Chi cattura la crescita — imprese e redditi dichiarati.

Confronta reddito imponibile IRES (imprese), reddito da lavoro dipendente
IRPEF e margine IVA (fatturato vs valore aggiunto fiscale), 2015-2024.
"""

import json
import pathlib
import sys

sys.path.insert(0, "src/data")
from _util import _parquet_exists, _parquet_refs, get_location
from lab_connectors.duckdb import safe_connect

IRES_YEARS = list(range(2015, 2025))
IRPEF_YEARS = list(range(2015, 2025))
# I file sono per anno di pubblicazione: il file 2024 contiene l'anno di
# imposta 2023. Il file 2025 (anno 2024) è escluso per il cambio di copertura.
IVA_YEARS = list(range(2015, 2025))

ires_loc = get_location("ires_redditi_regione")
irpef_loc = get_location("irpef_comunale")
iva_loc = get_location("iva_sez_attivita")

ires_years = [
    y for y in IRES_YEARS if _parquet_exists("ires_redditi_regione", y, ires_loc)
]
irpef_years = [y for y in IRPEF_YEARS if _parquet_exists("irpef_comunale", y, irpef_loc)]
iva_years = [y for y in IVA_YEARS if _parquet_exists("iva_sez_attivita", y, iva_loc)]

if not ires_years or not irpef_years:
    json.dump([], sys.stdout)
    sys.exit(0)

sql_path = (
    pathlib.Path(__file__).resolve().parents[2]
    / "cross-views"
    / "defs"
    / "chi-cattura-la-crescita-imprese.sql"
)
sql_template = sql_path.read_text()


def cte(refs: list[str]) -> str:
    return " UNION ALL ".join(f"SELECT * FROM read_parquet('{r}')" for r in refs)


sql = (
    sql_template.replace(
        "{cte_ires}",
        cte(_parquet_refs("ires_redditi_regione", ires_years, ires_loc)),
    )
    .replace(
        "{cte_irpef}",
        cte(_parquet_refs("irpef_comunale", irpef_years, irpef_loc)),
    )
    .replace(
        "{cte_iva}",
        cte(_parquet_refs("iva_sez_attivita", iva_years, iva_loc))
        if iva_years
        else "SELECT NULL AS anno, NULL AS volume_affari_eur, NULL AS va_fiscale_eur, NULL AS acquisti_eur WHERE FALSE",
    )
)

with safe_connect() as con:
    rows = con.sql(sql).fetchall()
    columns = [d[0] for d in con.sql(sql).description]

json.dump([dict(zip(columns, row)) for row in rows], sys.stdout, ensure_ascii=False)

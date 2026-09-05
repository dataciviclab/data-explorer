#!/usr/bin/env python3
"""Data loader: SILOS — infrastrutture strategiche e prioritarie.

Produce dati curati per la pagina Observable Framework. Il dataset SILOS è
gerarchico: la pagina deve distinguere i livelli invece di sommarli insieme.
"""
import json
import sys
sys.path.insert(0, "src/data")
from _util import get_location, _parquet_refs
from lab_connectors.duckdb import safe_connect


SLUG = "silos_infrastrutture"
YEAR = 2024
location = get_location(SLUG)
URL = _parquet_refs(SLUG, [YEAR], location)[0]


def rows(con, query: str) -> list[dict]:
    rel = con.sql(query)
    cols = [c[0] for c in rel.description]
    return [dict(zip(cols, row)) for row in rel.fetchall()]


with safe_connect() as con:
    table = f"read_parquet('{URL}')"

    output = {
        "meta": {
            "slug": SLUG,
            "year": YEAR,
            "source_parquet": URL,
            "note": "SILOS è gerarchico: i livelli vanno letti separatamente per evitare doppio conteggio.",
        },
        "per_livello": rows(
            con,
            f"""
            SELECT
              livello,
              COUNT(*) AS righe,
              COUNT(cup) AS righe_con_cup,
              SUM(COALESCE(costi_mln_euro, 0)) AS costi_mln_euro,
              SUM(COALESCE(disponibilita_mln_euro, 0)) AS disponibilita_mln_euro,
              SUM(COALESCE(fabbisogno_mln_euro, 0)) AS fabbisogno_mln_euro
            FROM {table}
            GROUP BY livello
            ORDER BY livello
            """,
        ),
        "interventi": rows(
            con,
            f"""
            SELECT
              livello,
              progressivo,
              cup,
              denominazione,
              COALESCE(sistema_infrastrutturale, 'Non indicato') AS sistema_infrastrutturale,
              COALESCE(soggetto_competente, 'Non indicato') AS soggetto_competente,
              COALESCE(luogo_lavori, 'Non indicato') AS luogo_lavori,
              COALESCE(stato_attuazione, 'Non indicato') AS stato_attuazione,
              anno_ultimazione_previsto,
              costi_mln_euro,
              disponibilita_mln_euro,
              fabbisogno_mln_euro,
              link_scheda
            FROM {table}
            ORDER BY livello, costi_mln_euro DESC
            """,
        ),
    }

json.dump(output, sys.stdout, ensure_ascii=False)

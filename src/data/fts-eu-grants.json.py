#!/usr/bin/env python3
"""Data loader: FTS EU Grants — finanziamenti UE a beneficiari italiani."""
import json
import sys

sys.path.insert(0, "src/data")

from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs.paths import https_url


SLUG = "fts_eu_grants"
YEARS = [2020, 2021, 2022, 2023, 2024]


parquet_refs = " UNION ALL ".join(
    f"SELECT * FROM read_parquet('{https_url('clean', 'clean_parquet', slug=SLUG, year=y)}')"
    for y in YEARS
)


PROGRAM_CASE = """
    CASE
        WHEN nome_programma ILIKE '%Recovery and Resilience%' THEN 'Recovery and resilience'
        WHEN nome_programma ILIKE '%Horizon%' THEN 'Ricerca (Horizon)'
        WHEN nome_programma ILIKE '%Erasmus%' THEN 'Istruzione (Erasmus+)'
        WHEN nome_programma ILIKE '%Digital Europe%' THEN 'Digitale'
        WHEN nome_programma ILIKE '%Creative Europe%' OR nome_programma ILIKE '%Culture%' THEN 'Cultura'
        WHEN nome_programma ILIKE '%LIFE%' THEN 'Ambiente (LIFE)'
        WHEN nome_programma ILIKE '%CERV%' OR nome_programma ILIKE '%Citizens%' THEN 'Cittadinanza'
        WHEN nome_programma ILIKE '%Health%' OR nome_programma ILIKE '%EU4H%' THEN 'Salute'
        WHEN nome_programma ILIKE '%Humanitarian%' THEN 'Aiuti umanitari'
        WHEN nome_programma ILIKE '%Migration%' OR nome_programma ILIKE '%AMIF%' THEN 'Migrazione'
        WHEN nome_programma ILIKE '%Connecting Europe Facility%' THEN 'Infrastrutture (CEF)'
        WHEN nome_programma ILIKE '%Defence Fund%' THEN 'Difesa'
        ELSE 'Altri programmi'
    END
"""


ENTITY_CASE = """
    CASE
        WHEN LOWER(flag_no_profit) IN ('true', 'yes') THEN 'Non-profit'
        WHEN LOWER(flag_ong) IN ('true', 'yes') THEN 'ONG'
        WHEN tipo_beneficiario ILIKE '%university%'
          OR tipo_beneficiario ILIKE '%research%'
          OR tipo_beneficiario ILIKE '%higher%' THEN 'Ricerca/Università'
        WHEN tipo_beneficiario ILIKE '%SME%'
          OR tipo_beneficiario ILIKE '%enterprise%'
          OR tipo_beneficiario ILIKE '%company%' THEN 'Impresa'
        WHEN tipo_beneficiario ILIKE '%public%'
          OR tipo_beneficiario ILIKE '%government%' THEN 'Pubblica amministrazione'
        ELSE 'Altro'
    END
"""


def _query(con, sql):
    rel = con.sql(sql)
    cols = [desc[0] for desc in rel.description]
    rows = []
    for row in rel.fetchall():
        rows.append(
            {
                col: int(val) if isinstance(val, float) and val == int(val) else val
                for col, val in zip(cols, row)
            }
        )
    return rows


with safe_connect() as con:
    base = f"({parquet_refs})"

    totali = _query(
        con,
        f"""
        SELECT
            COUNT(*) AS numero_grant,
            COUNT(DISTINCT beneficiario_nome) AS beneficiari,
            ROUND(SUM(COALESCE(importo_contrattato, 0)), 0) AS importo_totale
        FROM {base}
        """,
    )[0]

    per_anno = _query(
        con,
        f"""
        SELECT
            anno,
            COUNT(*) AS numero_grant,
            COUNT(DISTINCT beneficiario_nome) AS beneficiari,
            ROUND(SUM(COALESCE(importo_contrattato, 0)), 0) AS importo_totale
        FROM {base}
        GROUP BY anno
        ORDER BY anno
        """,
    )

    per_programma = _query(
        con,
        f"""
        SELECT
            anno,
            {PROGRAM_CASE} AS categoria_programma,
            COUNT(*) AS numero_grant,
            COUNT(DISTINCT beneficiario_nome) AS beneficiari,
            ROUND(SUM(COALESCE(importo_contrattato, 0)), 0) AS importo_totale
        FROM {base}
        GROUP BY anno, categoria_programma
        ORDER BY anno, importo_totale DESC
        """,
    )

    per_tipo_ente = _query(
        con,
        f"""
        SELECT
            anno,
            {ENTITY_CASE} AS tipo_ente,
            COUNT(*) AS numero_grant,
            COUNT(DISTINCT beneficiario_nome) AS beneficiari,
            ROUND(SUM(COALESCE(importo_contrattato, 0)), 0) AS importo_totale
        FROM {base}
        GROUP BY anno, tipo_ente
        ORDER BY anno, importo_totale DESC
        """,
    )

    per_citta = _query(
        con,
        f"""
        SELECT
            anno,
            CASE
                WHEN beneficiario_citta IS NULL OR beneficiario_citta IN ('', '-') THEN 'Non indicata'
                ELSE beneficiario_citta
            END AS citta,
            COUNT(*) AS numero_grant,
            COUNT(DISTINCT beneficiario_nome) AS beneficiari,
            ROUND(SUM(COALESCE(importo_contrattato, 0)), 0) AS importo_totale
        FROM {base}
        GROUP BY anno, citta
        QUALIFY ROW_NUMBER() OVER (PARTITION BY anno ORDER BY importo_totale DESC) <= 30
        ORDER BY anno, importo_totale DESC
        """,
    )

    top_beneficiari = _query(
        con,
        f"""
        SELECT
            anno,
            COALESCE(beneficiario_nome, 'Non indicato') AS beneficiario_nome,
            CASE
                WHEN beneficiario_citta IS NULL OR beneficiario_citta IN ('', '-') THEN 'Non indicata'
                ELSE beneficiario_citta
            END AS beneficiario_citta,
            {PROGRAM_CASE} AS categoria_programma,
            {ENTITY_CASE} AS tipo_ente,
            COUNT(*) AS numero_grant,
            ROUND(SUM(COALESCE(importo_contrattato, 0)), 0) AS importo_totale
        FROM {base}
        GROUP BY anno, beneficiario_nome, beneficiario_citta, categoria_programma, tipo_ente
        QUALIFY ROW_NUMBER() OVER (PARTITION BY anno ORDER BY importo_totale DESC) <= 100
        ORDER BY anno, importo_totale DESC
        """,
    )


output = {
    "anni": YEARS,
    "totali": totali,
    "per_anno": per_anno,
    "per_programma": per_programma,
    "per_tipo_ente": per_tipo_ente,
    "per_citta": per_citta,
    "top_beneficiari": top_beneficiari,
}

json.dump(output, sys.stdout, ensure_ascii=False)

#!/usr/bin/env python3
"""Data loader: Voti dei Deputati — singoli voti aggregati per gruppo e deputato.

Legge camera_voti (7.7M righe) e produce JSON con:
- trend: votazioni per anno (da mart_sintesi)
- per_gruppo: % favorevoli per gruppo per anno
- top_coerenti: deputati più coerenti con il proprio gruppo
- top_dissidenti: deputati più spesso contro il proprio gruppo
"""
import os, sys; sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs import object_exists
from lab_connectors.gcs.paths import https_url, CLEAN_BUCKET
import json

LOCAL_BASE = os.path.expanduser("~/dev/dataciviclab-workspace/open-politica/out/data/clean")

def _resolve(slug, year=2026):
    """Ritorna il path GCS se esiste (anche sotto open-politica/ prefix), altrimenti locale."""
    gcs_key = f"{slug}/{year}/{slug}_{year}_clean.parquet"
    if object_exists(CLEAN_BUCKET, gcs_key):
        return https_url("clean", "clean_parquet", slug=slug, year=year)
    gcs_key_op = f"open-politica/{slug}/{year}/{slug}_{year}_clean.parquet"
    if object_exists(CLEAN_BUCKET, gcs_key_op):
        return f"https://storage.googleapis.com/{CLEAN_BUCKET}/{gcs_key_op}"
    local = os.path.join(LOCAL_BASE, gcs_key)
    if os.path.exists(local):
        return local
    return None

def _resolve_mart(slug, mart, year=2026):
    """Ritorna il path del mart (GCS o locale)."""
    gcs_key = f"{slug}/{year}/{mart}.parquet"
    if object_exists(CLEAN_BUCKET, gcs_key):
        return f"https://storage.googleapis.com/{CLEAN_BUCKET}/{gcs_key}"
    gcs_key_op = f"open-politica/{slug}/{year}/{mart}.parquet"
    if object_exists(CLEAN_BUCKET, gcs_key_op):
        return f"https://storage.googleapis.com/{CLEAN_BUCKET}/{gcs_key_op}"
    local = os.path.join(LOCAL_BASE, gcs_key)
    if os.path.exists(local):
        return local
    return None

voti_path = _resolve("camera_voti")
deputati_path = _resolve("camera_deputati_legislature")
trend_mart = _resolve_mart("camera_voti", "mart_sintesi")

if not voti_path:
    json.dump({"error": "camera_voti parquet not found (GCS or local)"}, sys.stdout)
    sys.exit(0)

with safe_connect() as con:
    con.sql("SET preserve_insertion_order = false")
    con.sql("SET threads = 2")

    # 1. Trend: usa mart se disponibile, altrimenti calcola da raw
    if trend_mart:
        trend = con.sql(f"""
            SELECT anno, n_votazioni FROM read_parquet('{trend_mart}') ORDER BY 1
        """).fetchall()
    else:
        trend = con.sql(f"""
            SELECT EXTRACT(YEAR FROM data) AS anno,
                   COUNT(DISTINCT votazione) AS n_votazioni
            FROM read_parquet('{voti_path}')
            WHERE data IS NOT NULL
            GROUP BY 1 ORDER BY 1
        """).fetchall()

    trend_data = [{"anno": int(r[0]), "n_votazioni": int(r[1])} for r in trend]

    # 2. Per gruppo: ultimi 2 anni (limita memoria)
    per_gruppo = con.sql(f"""
        SELECT EXTRACT(YEAR FROM v.data) AS anno,
               v.sigla_gruppo,
               COUNT(*) AS n_voti,
               SUM(CASE WHEN v.voto = 'FAVOREVOLE' THEN 1 ELSE 0 END) AS n_fav,
               SUM(CASE WHEN v.voto = 'CONTRARIO' THEN 1 ELSE 0 END) AS n_contr,
               SUM(CASE WHEN v.voto = 'ASTENUTO' THEN 1 ELSE 0 END) AS n_ast
        FROM read_parquet('{voti_path}') v
        WHERE v.data IS NOT NULL
          AND v.sigla_gruppo IS NOT NULL
          AND EXTRACT(YEAR FROM v.data) >= 2024
        GROUP BY 1, 2
        ORDER BY 1, 3 DESC
    """).fetchall()

    gruppo_data = []
    for r in per_gruppo:
        n = int(r[2])
        gruppo_data.append({
            "anno": int(r[0]),
            "gruppo": r[1],
            "n_voti": n,
            "favorevoli": int(r[3]),
            "contrari": int(r[4]),
            "astenuti": int(r[5]),
            "pct_fav": round(int(r[3]) / n * 100, 1) if n > 0 else 0
        })

    # 3. Coerenza: semplificata — conta favorevoli/contrari per deputato
    #    e confronta con la linea di gruppo (maggioranza)
    coerent = con.sql(f"""
        WITH fav_per_dep AS (
            SELECT deputato_id, sigla_gruppo,
                   COUNT(*) AS n_voti,
                   SUM(CASE WHEN voto = 'FAVOREVOLE' THEN 1 ELSE 0 END) AS n_fav,
                   ROUND(SUM(CASE WHEN voto = 'FAVOREVOLE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_fav
            FROM read_parquet('{voti_path}')
            WHERE voto IN ('FAVOREVOLE', 'CONTRARIO')
              AND sigla_gruppo IS NOT NULL
            GROUP BY 1, 2
            HAVING COUNT(*) >= 100
        ),
        fav_per_gruppo AS (
            SELECT sigla_gruppo,
                   ROUND(SUM(CASE WHEN voto = 'FAVOREVOLE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_fav_gruppo
            FROM read_parquet('{voti_path}')
            WHERE voto IN ('FAVOREVOLE', 'CONTRARIO')
              AND sigla_gruppo IS NOT NULL
            GROUP BY 1
        )
        SELECT f.deputato_id, f.sigla_gruppo, f.n_voti, f.pct_fav,
               g.pct_fav_gruppo,
               ROUND(ABS(f.pct_fav - g.pct_fav_gruppo), 1) AS distanza,
               d.nome, d.cognome
        FROM fav_per_dep f
        JOIN fav_per_gruppo g ON f.sigla_gruppo = g.sigla_gruppo
        LEFT JOIN read_parquet('{deputati_path}') d ON f.deputato_id = d.persona_id
           AND d.legislatura = 'repubblica_19'
        ORDER BY f.pct_fav DESC
        LIMIT 20
    """).fetchall()

    top_coerenti = [
        {"id": int(r[0]), "gruppo": r[1], "n_voti": int(r[2]),
         "pct_fav": float(r[3]), "pct_gruppo": float(r[4]),
         "nome": r[6] or "", "cognome": r[7] or ""}
        for r in coerent
    ]

    # 4. Dissidenti: meno favorevoli della media gruppo
    diss = con.sql(f"""
        WITH fav_per_dep AS (
            SELECT deputato_id, sigla_gruppo,
                   COUNT(*) AS n_voti,
                   SUM(CASE WHEN voto = 'FAVOREVOLE' THEN 1 ELSE 0 END) AS n_fav,
                   ROUND(SUM(CASE WHEN voto = 'FAVOREVOLE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_fav
            FROM read_parquet('{voti_path}')
            WHERE voto IN ('FAVOREVOLE', 'CONTRARIO')
              AND sigla_gruppo IS NOT NULL
            GROUP BY 1, 2
            HAVING COUNT(*) >= 100
        ),
        fav_per_gruppo AS (
            SELECT sigla_gruppo,
                   ROUND(SUM(CASE WHEN voto = 'FAVOREVOLE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_fav_gruppo
            FROM read_parquet('{voti_path}')
            WHERE voto IN ('FAVOREVOLE', 'CONTRARIO')
              AND sigla_gruppo IS NOT NULL
            GROUP BY 1
        )
        SELECT f.deputato_id, f.sigla_gruppo, f.n_voti, f.pct_fav,
               g.pct_fav_gruppo,
               ROUND(ABS(f.pct_fav - g.pct_fav_gruppo), 1) AS distanza,
               d.nome, d.cognome
        FROM fav_per_dep f
        JOIN fav_per_gruppo g ON f.sigla_gruppo = g.sigla_gruppo
        LEFT JOIN read_parquet('{deputati_path}') d ON f.deputato_id = d.persona_id
           AND d.legislatura = 'repubblica_19'
        ORDER BY f.pct_fav ASC
        LIMIT 20
    """).fetchall()

    top_dissidenti = [
        {"id": int(r[0]), "gruppo": r[1], "n_voti": int(r[2]),
         "pct_fav": float(r[3]), "pct_gruppo": float(r[4]),
         "nome": r[6] or "", "cognome": r[7] or ""}
        for r in diss
    ]

    # KPI
    tot_voti = sum(t["n_votazioni"] for t in trend_data)
    anni = len(trend_data)
    media_voti = round(tot_voti / anni) if anni > 0 else 0

json.dump({
    "kpi": {
        "tot_votazioni": tot_voti,
        "anni": anni,
        "media_annuale": media_voti,
    },
    "trend": trend_data,
    "per_gruppo": gruppo_data,
    "top_coerenti": top_coerenti,
    "top_dissidenti": top_dissidenti,
}, sys.stdout, ensure_ascii=False)

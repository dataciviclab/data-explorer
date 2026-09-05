#!/usr/bin/env python3
"""Data loader: Voti dei Deputati — singoli voti aggregati per gruppo e deputato.

Legge camera_voti (7.7M righe) e produce JSON con:
- trend: votazioni per anno (da mart_sintesi)
- per_gruppo: % favorevoli per gruppo per anno
- top_coerenti: deputati più coerenti con il proprio gruppo
- top_dissidenti: deputati più spesso contro il proprio gruppo
"""
import sys; sys.path.insert(0, "src/data")
from _util import get_location, _parquet_exists, _parquet_refs, _load_manifest
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs.paths import CLEAN_BUCKET
import json

anni = [2022, 2023, 2024, 2025, 2026]

def _find_mart(slug, year, mart_name):
    """Cerca il mart nel manifest (MART_BUCKET, non CLEAN_BUCKET)."""
    manifest = _load_manifest()
    loc = get_location(slug)
    if loc and loc.get("path", "").startswith("gs://"):
        # Derive mart path from location prefix
        path = loc["path"]
        # Clean path: gs://bucket/prefix/slug/year/file → prefix/slug/year/file
        key = path[len("gs://"):].partition("/")[2]
        prefix = key.rpartition("/")[0].rpartition("/")[0]  # up to slug level
        mart_key = f"{prefix}/{year}/{mart_name}.parquet"
    else:
        mart_key = f"{slug}/{year}/{mart_name}.parquet"
    for f in manifest.get("files", []):
        if f["bucket"] == CLEAN_BUCKET and f["path"] == mart_key:
            return f"https://storage.googleapis.com/{CLEAN_BUCKET}/{f['path']}"
    return None

# Trova parquet
voti_loc = get_location("camera_voti")
dep_loc = get_location("camera_deputati_legislature")
voti_url = _parquet_refs("camera_voti", [2026], voti_loc)[0] if _parquet_exists("camera_voti", 2026, voti_loc) else None
dep_url = _parquet_refs("camera_deputati_legislature", [2026], dep_loc)[0] if _parquet_exists("camera_deputati_legislature", 2026, dep_loc) else None
mart_url = _find_mart("camera_voti", 2026, "mart_sintesi")

if not voti_url:
    json.dump({"error": "camera_voti parquet not found in manifest"}, sys.stdout)
    sys.exit(0)

with safe_connect() as con:
    con.sql("SET preserve_insertion_order = false")
    con.sql("SET threads = 2")

    # 1. Trend
    if mart_url:
        trend = con.sql(f"SELECT anno, n_votazioni FROM read_parquet('{mart_url}') ORDER BY 1").fetchall()
    else:
        trend = con.sql(f"""
            SELECT EXTRACT(YEAR FROM data) AS anno,
                   COUNT(DISTINCT votazione) AS n_votazioni
            FROM read_parquet('{voti_url}')
            WHERE data IS NOT NULL
            GROUP BY 1 ORDER BY 1
        """).fetchall()

    trend_data = [{"anno": int(r[0]), "n_votazioni": int(r[1])} for r in trend]

    # 2. Per gruppo: ultimi 2 anni
    per_gruppo = con.sql(f"""
        SELECT EXTRACT(YEAR FROM v.data) AS anno,
               v.sigla_gruppo,
               COUNT(*) AS n_voti,
               SUM(CASE WHEN v.voto = 'FAVOREVOLE' THEN 1 ELSE 0 END) AS n_fav,
               SUM(CASE WHEN v.voto = 'CONTRARIO' THEN 1 ELSE 0 END) AS n_contr,
               SUM(CASE WHEN v.voto = 'ASTENUTO' THEN 1 ELSE 0 END) AS n_ast
        FROM read_parquet('{voti_url}') v
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

    # 3. Coerenza
    if dep_url:
        coerent = con.sql(f"""
            WITH fav_per_dep AS (
                SELECT deputato_id, sigla_gruppo,
                       COUNT(*) AS n_voti,
                       ROUND(SUM(CASE WHEN voto = 'FAVOREVOLE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_fav
                FROM read_parquet('{voti_url}')
                WHERE voto IN ('FAVOREVOLE', 'CONTRARIO')
                  AND sigla_gruppo IS NOT NULL
                GROUP BY 1, 2
                HAVING COUNT(*) >= 100
            ),
            fav_per_gruppo AS (
                SELECT sigla_gruppo,
                       ROUND(SUM(CASE WHEN voto = 'FAVOREVOLE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_fav_gruppo
                FROM read_parquet('{voti_url}')
                WHERE voto IN ('FAVOREVOLE', 'CONTRARIO')
                  AND sigla_gruppo IS NOT NULL
                GROUP BY 1
            )
            SELECT f.deputato_id, f.sigla_gruppo, f.n_voti, f.pct_fav,
                   g.pct_fav_gruppo, d.nome, d.cognome
            FROM fav_per_dep f
            JOIN fav_per_gruppo g ON f.sigla_gruppo = g.sigla_gruppo
            LEFT JOIN read_parquet('{dep_url}') d ON f.deputato_id = d.persona_id
               AND d.legislatura = 'repubblica_19'
            ORDER BY f.pct_fav DESC
            LIMIT 20
        """).fetchall()
    else:
        coerent = []

    top_coerenti = [
        {"id": int(r[0]), "gruppo": r[1], "n_voti": int(r[2]),
         "pct_fav": float(r[3]), "pct_gruppo": float(r[4]),
         "nome": r[5] or "", "cognome": r[6] or ""}
        for r in coerent
    ]

    # 4. Dissidenti
    if dep_url:
        diss = con.sql(f"""
            WITH fav_per_dep AS (
                SELECT deputato_id, sigla_gruppo,
                       COUNT(*) AS n_voti,
                       ROUND(SUM(CASE WHEN voto = 'FAVOREVOLE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_fav
                FROM read_parquet('{voti_url}')
                WHERE voto IN ('FAVOREVOLE', 'CONTRARIO')
                  AND sigla_gruppo IS NOT NULL
                GROUP BY 1, 2
                HAVING COUNT(*) >= 100
            ),
            fav_per_gruppo AS (
                SELECT sigla_gruppo,
                       ROUND(SUM(CASE WHEN voto = 'FAVOREVOLE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_fav_gruppo
                FROM read_parquet('{voti_url}')
                WHERE voto IN ('FAVOREVOLE', 'CONTRARIO')
                  AND sigla_gruppo IS NOT NULL
                GROUP BY 1
            )
            SELECT f.deputato_id, f.sigla_gruppo, f.n_voti, f.pct_fav,
                   g.pct_fav_gruppo, d.nome, d.cognome
            FROM fav_per_dep f
            JOIN fav_per_gruppo g ON f.sigla_gruppo = g.sigla_gruppo
            LEFT JOIN read_parquet('{dep_url}') d ON f.deputato_id = d.persona_id
               AND d.legislatura = 'repubblica_19'
            ORDER BY f.pct_fav ASC
            LIMIT 20
        """).fetchall()
    else:
        diss = []

    top_dissidenti = [
        {"id": int(r[0]), "gruppo": r[1], "n_voti": int(r[2]),
         "pct_fav": float(r[3]), "pct_gruppo": float(r[4]),
         "nome": r[5] or "", "cognome": r[6] or ""}
        for r in diss
    ]

    tot_voti = sum(t["n_votazioni"] for t in trend_data)
    anni_count = len(trend_data)
    media_voti = round(tot_voti / anni_count) if anni_count > 0 else 0

json.dump({
    "kpi": {
        "tot_votazioni": tot_voti,
        "anni": anni_count,
        "media_annuale": media_voti,
    },
    "trend": trend_data,
    "per_gruppo": gruppo_data,
    "top_coerenti": top_coerenti,
    "top_dissidenti": top_dissidenti,
}, sys.stdout, ensure_ascii=False)

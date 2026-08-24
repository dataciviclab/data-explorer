#!/usr/bin/env python3
"""Data loader: Attività in Aula — interventi e relatori della Camera.

Legge camera_interventi + camera_relatori (multi-anno) e produce JSON con:
- trend: interventi e relazioni per anno
- top_parlanti: deputati più attivi in aula
- top_relatori: deputati che relazionano di più
"""
import sys; sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs.paths import CLEAN_BUCKET
from _util import _load_manifest
import json

anni = [2022, 2023, 2024, 2025, 2026]

def _find_parquet(slug, year):
    manifest = _load_manifest()
    root_key = f"{slug}/{year}/{slug}_{year}_clean.parquet"
    op_key = f"open-politica/{slug}/{year}/{slug}_{year}_clean.parquet"
    for f in manifest.get("files", []):
        if f["bucket"] == CLEAN_BUCKET and f["path"] in (root_key, op_key):
            return f"https://storage.googleapis.com/{CLEAN_BUCKET}/{f['path']}"
    return None

def _find_many(slug, years):
    refs = []
    for y in years:
        url = _find_parquet(slug, y)
        if url:
            refs.append((y, url))
    return refs

inter_refs = _find_many("camera_interventi", anni)
rel_refs = _find_many("camera_relatori", anni)
dep_url = _find_parquet("camera_deputati_legislature", 2026)

with safe_connect() as con:
    con.sql("SET preserve_insertion_order = false")
    con.sql("SET threads = 2")

    # --- Interventi ---
    if inter_refs:
        inter_union = " UNION ALL ".join(f"SELECT * FROM read_parquet('{r}')" for _, r in inter_refs)
        trend_inter = con.sql(f"""
            SELECT EXTRACT(YEAR FROM data) AS anno,
                   COUNT(*) AS n_interventi,
                   COUNT(DISTINCT deputato_id) AS n_parlanti
            FROM ({inter_union})
            WHERE data IS NOT NULL
            GROUP BY 1 ORDER BY 1
        """).fetchall()
    else:
        trend_inter = []

    # --- Relatori ---
    if rel_refs:
        rel_union = " UNION ALL ".join(f"SELECT * FROM read_parquet('{r}')" for _, r in rel_refs)
        trend_rel = con.sql(f"""
            SELECT EXTRACT(YEAR FROM data) AS anno,
                   COUNT(*) AS n_relat,
                   COUNT(DISTINCT deputato_id) AS n_relatori
            FROM ({rel_union})
            WHERE data IS NOT NULL
            GROUP BY 1 ORDER BY 1
        """).fetchall()
    else:
        trend_rel = []

    # Merge trend
    trend_map = {}
    for r in trend_inter:
        a = int(r[0])
        trend_map[a] = {"anno": a, "n_interventi": int(r[1]), "n_parlanti": int(r[2]), "n_relat": 0, "n_relatori": 0}
    for r in trend_rel:
        a = int(r[0])
        if a in trend_map:
            trend_map[a]["n_relat"] = int(r[1])
            trend_map[a]["n_relatori"] = int(r[2])
        else:
            trend_map[a] = {"anno": a, "n_interventi": 0, "n_parlanti": 0, "n_relat": int(r[1]), "n_relatori": int(r[2])}
    trend = sorted(trend_map.values(), key=lambda x: x["anno"])

    # --- Top parlanti (2024-2026) ---
    if inter_refs and dep_url:
        top_parl = con.sql(f"""
            SELECT i.deputato_id, COUNT(*) AS n_interventi,
                   d.nome, d.cognome
            FROM ({inter_union}) i
            LEFT JOIN read_parquet('{dep_url}') d
              ON i.deputato_id = d.persona_id AND d.legislatura = 'repubblica_19'
            WHERE EXTRACT(YEAR FROM i.data) >= 2024
            GROUP BY 1, 3, 4
            ORDER BY 2 DESC
            LIMIT 15
        """).fetchall()
    else:
        top_parl = []

    top_parlanti = [
        {"id": int(r[0]), "n_interventi": int(r[1]), "nome": r[2] or "", "cognome": r[3] or ""}
        for r in top_parl
    ]

    # --- Top relatori (2024-2026) ---
    if rel_refs and dep_url:
        top_rel = con.sql(f"""
            SELECT r.deputato_id, COUNT(*) AS n_relat,
                   d.nome, d.cognome
            FROM ({rel_union}) r
            LEFT JOIN read_parquet('{dep_url}') d
              ON r.deputato_id = d.persona_id AND d.legislatura = 'repubblica_19'
            WHERE EXTRACT(YEAR FROM r.data) >= 2024
            GROUP BY 1, 3, 4
            ORDER BY 2 DESC
            LIMIT 15
        """).fetchall()
    else:
        top_rel = []

    top_relatori = [
        {"id": int(r[0]), "n_relat": int(r[1]), "nome": r[2] or "", "cognome": r[3] or ""}
        for r in top_rel
    ]

    tot_inter = sum(t["n_interventi"] for t in trend if t["anno"] in [2024, 2025])
    tot_rel = sum(t["n_relat"] for t in trend if t["anno"] in [2024, 2025])
    parlanti_2025 = next((t["n_parlanti"] for t in trend if t["anno"] == 2025), 0)

json.dump({
    "kpi": {
        "tot_interventi": tot_inter,
        "tot_relazioni": tot_rel,
        "parlanti_2025": parlanti_2025,
    },
    "trend": trend,
    "top_parlanti": top_parlanti,
    "top_relatori": top_relatori,
}, sys.stdout, ensure_ascii=False)

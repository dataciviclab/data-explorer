#!/usr/bin/env python3
"""Data loader: Camera dei Deputati — unificato (gruppi + incarichi + deputati).

Combina 3 dataset open-politica in un JSON unico per la pagina Camera.
"""
import sys; sys.path.insert(0, "src/data")
from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs import object_exists
from lab_connectors.gcs.paths import https_url, CLEAN_BUCKET
import json

def url(slug, year=2026):
    return https_url("clean", "clean_parquet", slug=slug, year=year)

# Verifica parquet
slugs = {"gruppi": ("camera_gruppi", 2026), "incarichi": ("camera_incarichi", 2026), "deputati": ("camera_deputati_legislature", 2026)}
for name, (s, y) in slugs.items():
    if not object_exists(CLEAN_BUCKET, f"{s}/{y}/{s}_{y}_clean.parquet"):
        json.dump({"error": f"parquet {name} not found"}, sys.stdout)
        sys.exit(0)

with safe_connect() as con:
    # 1. Gruppi per legislatura
    gruppi = con.sql(f"""
        SELECT legislatura, COUNT(DISTINCT gruppo) AS n_gruppi,
               COUNT(*) AS n_deputati_gruppo
        FROM read_parquet('{url('camera_gruppi')}')
        WHERE legislatura IS NOT NULL
        GROUP BY 1 ORDER BY 1
    """).fetchall()

    per_legislatura = [
        {"legislatura": r[0], "n_gruppi": int(r[1]), "n_deputati": int(r[2])}
        for r in gruppi
    ]

    # 2. Incarichi più frequenti (ultima legislatura)
    incarichi = con.sql(f"""
        SELECT incarico, ruolo, COUNT(*) AS n
        FROM read_parquet('{url('camera_incarichi')}')
        WHERE incarico IS NOT NULL
        GROUP BY 1, 2 ORDER BY 3 DESC
        LIMIT 15
    """).fetchall()

    top_incarichi = [
        {"incarico": r[0], "ruolo": r[1] or "", "n": int(r[2])}
        for r in incarichi
    ]

    # 3. Deputati per legislatura (conteggio)
    dep_per_leg = con.sql(f"""
        SELECT legislatura, COUNT(*) AS n_deputati,
               SUM(CASE WHEN LOWER(gender) = 'male' THEN 1 ELSE 0 END) AS uomini,
               SUM(CASE WHEN LOWER(gender) = 'female' THEN 1 ELSE 0 END) AS donne
        FROM read_parquet('{url('camera_deputati_legislature')}')
        WHERE legislatura IS NOT NULL
        GROUP BY 1 ORDER BY 1
    """).fetchall()

    deputati_per_legislatura = [
        {"legislatura": r[0], "n": int(r[1]),
         "uomini": int(r[2]) if r[2] else 0,
         "donne": int(r[3]) if r[3] else 0,
         "pct_donne": round(int(r[3]) / int(r[1]) * 100, 1) if r[1] and int(r[1]) > 0 else 0}
        for r in dep_per_leg
    ]

    # 4. Ultima legislatura: deputati per gruppo
    ultima_leg = con.sql(f"""
        SELECT legislatura FROM read_parquet('{url('camera_deputati_legislature')}')
        WHERE legislatura IS NOT NULL
        GROUP BY 1 ORDER BY 1 DESC LIMIT 1
    """).fetchone()

    if ultima_leg:
        gruppi_list = con.sql(f"""
            SELECT
                CASE
                    WHEN g.nome LIKE '%(%' THEN TRIM(SPLIT_PART(g.nome, '(', 1))
                    ELSE g.nome
                END AS nome_gruppo
            FROM read_parquet('{url('camera_gruppi')}') g
            WHERE g.legislatura = '{ultima_leg[0]}'
              AND g.nome IS NOT NULL
            ORDER BY 1
        """).fetchall()

        dep_per_gruppo = [
            {"gruppo": r[0]}
            for r in gruppi_list
        ]
        ultima = ultima_leg[0]
    else:
        dep_per_gruppo = []
        ultima = ""

    # KPI
    tot_legislature = len(per_legislatura)
    tot_deputati_oggi = deputati_per_legislatura[-1]["n"] if deputati_per_legislatura else 0
    pct_donne_oggi = deputati_per_legislatura[-1]["pct_donne"] if deputati_per_legislatura else 0

json.dump({
    "kpi": {
        "tot_legislature": tot_legislature,
        "ultima": ultima,
        "tot_deputati": tot_deputati_oggi,
        "pct_donne": pct_donne_oggi,
    },
    "per_legislatura": per_legislatura,
    "top_incarichi": top_incarichi,
    "deputati_per_legislatura": deputati_per_legislatura,
    "dep_per_gruppo": dep_per_gruppo,
}, sys.stdout, ensure_ascii=False)

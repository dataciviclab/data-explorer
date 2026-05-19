#!/usr/bin/env python3
"""Utility condivisa per data loader Observable. Legge parquet da GCS via DuckDB e produce JSON."""
import json, sys, duckdb, requests

GCS_BASE = "https://storage.googleapis.com/dataciviclab-clean"  # riusabile: from _util import GCS_BASE


def _parquet_exists(slug, year):
    """Verifica se il parquet esiste su GCS (HEAD request)."""
    url = f"{GCS_BASE}/{slug}/{year}/{slug}_{year}_clean.parquet"
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def load_dataset(slug, years, group_cols, metric_cols, where=""):
    """
    Legge parquet GCS per un dataset, raggruppa per group_cols,
    somma metric_cols, output JSON su stdout.
    Salta gli anni in cui il parquet non esiste.
    """
    con = duckdb.connect()
    
    valid_years = [y for y in years if _parquet_exists(slug, y)]
    if not valid_years:
        json.dump([], sys.stdout)
        return
    
    parquet_refs = " UNION ALL ".join(
        f"SELECT * FROM read_parquet('{GCS_BASE}/{slug}/{y}/{slug}_{y}_clean.parquet')"
        for y in valid_years
    )
    
    group_sql = ", ".join(group_cols)
    metrics_sql = ", ".join(f"SUM({m}) AS {m}" for m in metric_cols)
    where_sql = f"WHERE {where}" if where else ""
    
    query = f"""
        SELECT {group_sql}, {metrics_sql}
        FROM ({parquet_refs})
        {where_sql}
        GROUP BY {group_sql}
        ORDER BY {group_sql}
    """
    
    rows = con.sql(query).fetchall()
    columns = group_cols + metric_cols
    data = [dict(zip(columns, [int(v) if isinstance(v, float) and v == v else v for v in row])) for row in rows]
    
    json.dump(data, sys.stdout, ensure_ascii=False)

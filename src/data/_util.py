#!/usr/bin/env python3
"""Utility condivisa per data loader Observable Framework.

Legge clean parquet da GCS via DuckDB e produce JSON per il frontend.

I path GCS seguono il path contract canonico definito in:
    lab-connectors/lab_connectors/gcs/paths.py  (paths.json)
Pattern usato: clean_parquet → {slug}/{year}/{slug}_{year}_clean.parquet
"""
import json
import sys

from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs import object_exists
from lab_connectors.gcs.paths import CLEAN_BUCKET, https_url

# GCS_BASE: backward compat per data loader che lo importano direttamente.
# Calcolato dal contratto invece che hardcoded.
GCS_BASE = f"https://storage.googleapis.com/{CLEAN_BUCKET}"


def _parquet_exists(slug: str, year: int) -> bool:
    """Verifica se il parquet esiste su GCS via object_exists()."""
    return object_exists(
        CLEAN_BUCKET,
        f"{slug}/{year}/{slug}_{year}_clean.parquet",
        auth=False,
    )


def load_dataset(
    slug: str,
    years: list[int],
    group_cols: list[str],
    metric_cols: list[str],
    where: str = "",
) -> None:
    """
    Legge parquet GCS per un dataset, raggruppa per group_cols,
    somma metric_cols, output JSON su stdout.
    Salta gli anni in cui il parquet non esiste.
    """
    valid_years = [y for y in years if _parquet_exists(slug, y)]
    if not valid_years:
        json.dump([], sys.stdout)
        return

    parquet_refs = " UNION ALL ".join(
        "SELECT * FROM read_parquet('"
        + https_url("clean", "clean_parquet", slug=slug, year=y)
        + "')"
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

    with safe_connect() as con:
        rows = con.sql(query).fetchall()

    columns = group_cols + metric_cols
    data = [
        dict(zip(columns, [int(v) if isinstance(v, float) and v == v and v == int(v) else v for v in row]))
        for row in rows
    ]

    json.dump(data, sys.stdout, ensure_ascii=False)

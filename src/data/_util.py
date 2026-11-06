#!/usr/bin/env python3
"""Utility condivisa per data loader Observable Framework.

Legge clean parquet da GCS via DuckDB e produce JSON per il frontend.

I path GCS seguono il path contract canonico definito in:
    lab-connectors/lab_connectors/gcs/paths.py  (paths.json)
Pattern usato: clean_parquet → {slug}/{year}/{slug}_{year}_clean.parquet

Per i dataset di repo dominio (siope, eurostat, conto-annuale, ...) il path
reale può divergere (prefix per repo). In quel caso il loader passa
``location`` (dict dal registry: ``{type, path, multi_file}``) e
``load_dataset`` deriva le refs HTTPS per-anno dal location.

OUTPUT: array JSON di righe aggregate (v1 contract, backward compat).
  Le pagine consumano direttamente l'array.
  TODO (Fase 3): aggiungere metadata years_available/missing in un campo _meta
  senza rompere il contratto array.
"""
import json
import re
import sys

from lab_connectors.duckdb import safe_connect
from lab_connectors.gcs import object_exists
from lab_connectors.gcs.paths import (
    CLEAN_BUCKET,
    https_url,
    location_urls,
    parse_gs_url,
    resolve,
)

# GCS_BASE: backward compat per data loader che lo importano direttamente.
# Calcolato dal contratto invece che hardcoded.
GCS_BASE = f"https://storage.googleapis.com/{CLEAN_BUCKET}"

_LOCATION_CACHE: dict[str, dict | None] = {}


def get_location(slug: str) -> dict | None:
    """Load location for a slug from the fused registry (cached per process)."""
    if slug in _LOCATION_CACHE:
        return _LOCATION_CACHE[slug]
    try:
        from _registry import load_registry
        reg = load_registry()
        for ds in reg.get("datasets", []):
            if ds.get("slug") == slug:
                loc = ds.get("location")
                _LOCATION_CACHE[slug] = loc
                return loc
    except Exception:
        pass
    _LOCATION_CACHE[slug] = None
    return None

# Regex per il segmento anno in un path (es. "/2024/", "/2026/").
_LOCATION_YEAR = re.compile(r"/(\d{4})/")


def _location_path(location: dict | None) -> str:
    """Path ``gs://`` di una voce location del registry (o stringa vuota)."""
    if not location:
        return ""
    return str(location.get("path") or "")


def _year_of(url: str) -> int | None:
    """Anno dal segmento ``/YYYY/`` di un URL (None se assente)."""
    match = _LOCATION_YEAR.search(url)
    return int(match.group(1)) if match else None


def _canonical_exists(slug: str, year: int) -> bool:
    """HEAD sul path canonico ``{slug}/{year}/{slug}_{year}_clean.parquet``."""
    key = resolve("clean_parquet", slug=slug, year=year)
    return object_exists(CLEAN_BUCKET, key)


def _parquet_exists(slug: str, year: int, location: dict | None = None) -> bool:
    """True se il parquet dell'anno esiste su GCS.

    Con ``location`` del registry non serve il manifest: path puntuale → HEAD
    sul file, glob → una listing per dataset e match sull'anno. Se la listing
    fallisce si ricade su HEAD del singolo anno.
    """
    path = _location_path(location)
    if path.startswith("gs://"):
        if "*" not in path:
            return object_exists(*parse_gs_url(path))
        try:
            urls = location_urls(location)
        except Exception:
            return object_exists(*parse_gs_url(path.replace("*", str(year))))
        return any(_year_of(url) == year for url in urls)
    return _canonical_exists(slug, year)


def _parquet_refs(slug: str, years: list[int], location: dict | None = None) -> list[str]:
    """Refs HTTPS dei parquet per gli anni richiesti.

    Con ``location`` del registry delega a ``location_urls`` (path puntuale,
    glob per anno o glob espanso). Senza location usa il pattern canonico.
    """
    path = _location_path(location)
    if path.startswith("gs://"):
        if "*" not in path:
            return [location_urls(location)[0]]
        return location_urls(location, years=years)
    return [https_url("clean", "clean_parquet", slug=slug, year=year) for year in years]


def load_dataset(
    slug: str,
    years: list[int],
    group_cols: list[str],
    metric_cols: list[str],
    where: str = "",
    location: dict | None = None,
) -> None:
    """
    Legge parquet GCS per un dataset, raggruppa per group_cols,
    somma metric_cols, output JSON su stdout.
    Salta gli anni in cui il parquet non esiste.

    ``location``: dict opzionale dal registry ({type, path, multi_file}).
    Se assente, usa il pattern canonico (dataset-incubator).

    Output: array JSON di righe aggregate (v1 contract).
    """
    valid_years = [y for y in years if _parquet_exists(slug, y, location)]
    if not valid_years:
        json.dump([], sys.stdout)
        return

    refs = _parquet_refs(slug, valid_years, location)
    parquet_refs = " UNION ALL ".join(
        f"SELECT * FROM read_parquet('{ref}')" for ref in refs
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


def raw_sample(
    slug: str,
    years: list[int],
    limit: int = 5000,
    where: str = "",
    location: dict | None = None,
) -> None:
    """Legge un campione raw di righe dal parquet (senza aggregare).

    Restituisce le righe raw senza aggregare; trend/rank/choropleth vengono
    calcolati a valle nelle pagine. Il loader resta "stupido" e generico.

    Output: array JSON di righe (v1 contract), dedup su chiavi uguali
    per evitare righe duplicate nei glob multi-anno.
    """
    valid_years = [y for y in years if _parquet_exists(slug, y, location)]
    if not valid_years:
        json.dump([], sys.stdout)
        return

    refs = _parquet_refs(slug, valid_years, location)
    # Campiona casualmente distribuito tra i file per-anno: con LIMIT su un
    # UNION ALL prenderemmo le prime righe del primo file (grafici distorti).
    # USING SAMPLE ROWS dà un campione casuale rappresentativo per anno.
    if len(refs) > 1:
        per_year = max(1, limit // len(refs))
        union = " UNION ALL ".join(
            f"(SELECT * FROM read_parquet('{ref}') USING SAMPLE {per_year} ROWS)" for ref in refs
        )
    else:
        union = " UNION ALL ".join(f"SELECT * FROM read_parquet('{ref}')" for ref in refs)
    where_sql = f"WHERE {where}" if where else ""
    query = f"SELECT * FROM ({union}) {where_sql} LIMIT {limit}"

    with safe_connect() as con:
        rows = con.sql(query).fetchall()
        columns = [d[0] for d in con.sql(query).description]

    data = []
    seen: set[tuple] = set()
    for row in rows:
        key = tuple(row)
        if key in seen:
            continue
        seen.add(key)
        data.append(dict(zip(columns, row)))

    json.dump(data, sys.stdout, ensure_ascii=False)

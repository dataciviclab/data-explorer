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
from lab_connectors.gcs.manifest import read_manifest
from lab_connectors.gcs.paths import CLEAN_BUCKET, https_url

# GCS_BASE: backward compat per data loader che lo importano direttamente.
# Calcolato dal contratto invece che hardcoded.
GCS_BASE = f"https://storage.googleapis.com/{CLEAN_BUCKET}"

# Cache processo: manifest caricato una volta per loader (ogni loader è
# un processo Python separato, quindi non serve thread safety).
_MANIFEST: dict | None = None
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
_YEAR_SEGMENT = re.compile(r"/(\d{4})/")


def _load_manifest() -> dict:
    """Carica gcs_manifest.json da GCS, con cache di processo."""
    global _MANIFEST
    if _MANIFEST is not None:
        return _MANIFEST
    try:
        _MANIFEST = read_manifest()
    except Exception:
        _MANIFEST = {"files": []}
    return _MANIFEST


def _target_path(slug: str, year: int, location: dict | None = None) -> str:
    """Key GCS (relativa al bucket) del parquet per un anno.

    Fallback: pattern canonico ``{slug}/{year}/{slug}_{year}_clean.parquet``.
    Con ``location`` dal registry: deriva la key dal path reale (prefix
    per repo e multi_file glob ``*`` → sostituzione con l'anno).
    """
    if location:
        path = (location.get("path") or "")
        if path.startswith("gs://"):
            key = path[len("gs://"):].partition("/")[2]  # via il bucket
            if location.get("multi_file") and "*" in key:
                return key.replace("*", str(year))
            m = _YEAR_SEGMENT.search(key)
            if m:
                prefix = key[: m.start()]
                return f"{prefix}/{year}/{slug}_{year}_clean.parquet"
            if key.endswith("/"):
                return f"{key}{slug}_{year}_clean.parquet"
            return key
    return f"{slug}/{year}/{slug}_{year}_clean.parquet"


def _parquet_exists(slug: str, year: int, location: dict | None = None) -> bool:
    """Verifica se il parquet esiste su GCS.

    Fast path: gcs_manifest.json (una GET, lookup in memoria) —
    se il manifest contiene il file, esiste sicuro.
    Slow path (su miss del manifest): object_exists() via HEAD.
    Il fallback evita falsi negativi quando un parquet è stato
    pubblicato dopo l'ultimo refresh del manifest (daily).

    Con ``location`` (dal registry) la verifica usa il path reale del
    repo (gestisce prefix tipo ``conto-annuale/...``, ``siope/...``).
    """
    target_path = _target_path(slug, year, location)

    manifest = _load_manifest()
    if manifest.get("files"):
        if any(
            f["bucket"] == CLEAN_BUCKET and f["path"] == target_path
            for f in manifest["files"]
        ):
            return True
        # Non trovato nel manifest — potrebbe essere stato appena
        # pubblicato. Cadiamo nel fallback GCS live.

    from lab_connectors.gcs import object_exists

    return object_exists(
        CLEAN_BUCKET,
        target_path,
    )


def _location_https_prefix(location: dict, slug: str) -> str | None:
    """Prefix HTTPS base di un dataset dal location registry.

    Converte ``location.path`` (gs://.../{slug}/{year}/file.parquet) nel
    prefix HTTPS fino alla dir dell'anno (esclusa): le refs per-anno si
    ottengono appendendo ``{year}/{slug}_{year}_clean.parquet``.

    Returns:
        Str prefix (es. ``https://storage.googleapis.com/dataciviclab-clean/conto-annuale/anzianita``)
        o ``None`` se il location non è utilizzabile.
    """
    path = (location or {}).get("path") or ""
    if not path.startswith("gs://"):
        return None
    key = path[len("gs://"):]
    # Rimuovi il bucket (primo segmento) e tieni il resto.
    _, sep, rest = key.partition("/")
    if not sep:
        return None
    m = _YEAR_SEGMENT.search(rest)
    if m:
        rest = rest[: m.start()]  # taglia via "/{year}/..."
    rest = rest.rstrip("/")
    return f"https://storage.googleapis.com/{CLEAN_BUCKET}/{rest}" if rest else GCS_BASE


def _parquet_refs(slug: str, years: list[int], location: dict | None = None) -> list[str]:
    """Refs HTTPS per-anno dei parquet del dataset.

    Se ``location`` è fornito (dal registry) deriva le refs dal path reale
    (gestisce prefix per repo e multi_file glob ``*``); altrimenti fallback
    al pattern canonico ``{slug}/{year}/{slug}_{year}_clean.parquet``.
    """
    if location:
        path = (location.get("path") or "")
        if path.startswith("gs://"):
            base = "https://storage.googleapis.com/" + path[len("gs://"):]
            # multi_file: glob con * → sostituiamo ogni * con l'anno.
            if location.get("multi_file"):
                return [base.replace("*", str(y)) for y in years]
            # Path con segmento anno → deriviamo il prefix e appendiamo per-anno.
            prefix = _location_https_prefix(location, slug)
            if prefix:
                return [f"{prefix}/{year}/{slug}_{year}_clean.parquet" for year in years]
    return [
        https_url("clean", "clean_parquet", slug=slug, year=year)
        for year in years
    ]


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

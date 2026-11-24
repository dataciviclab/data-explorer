#!/usr/bin/env python3
"""Contratto dati dei loader Explorer: mart del Lab + anni reali.

Perché esiste: una pagina non deve contenere SQL né ``range(YYYY, YYYY)``.
Il loader dichiara **quale mart** e **quali colonne**; qui vivono la
risoluzione del path, gli anni pubblicati e la serializzazione JSON.

Uso tipico in un loader di pagina (5-8 righe):

    import sys
    sys.path.insert(0, "src/data")
    from _views import group_rows, mart_rows, write

    trend = mart_rows(
        "anac_bandi_gara__mart_annuale",
        select={"anno": "anno", "n_lotti": "n_lotti"},
        since=2016,
    )
    write({"trend": trend})

Le aggregazioni vivono nei mart della pipeline: qui non si scrive SQL.
Se un mart non è dichiarato nel registry del repo, il loader **fallisce**
con un errore leggibile invece di pubblicare una pagina vuota.

Contratto degli anni
--------------------
- ``since`` / ``until`` accettano un intero oppure ``"last_complete"``
  (anno corrente - 1: le partizioni dell'anno in corso sono parziali).
- Senza filtri si usano tutti gli anni presenti nel path del mart.
- Se il filtro non seleziona nessun anno, è un errore (non un silenzio).
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from collections.abc import Iterable, Mapping, Sequence
from datetime import date, datetime
from decimal import Decimal
from functools import lru_cache
from typing import Any

# Permette `from _registry import ...` quando il loader gira da repo root
# (Observable esegue `python3 src/data/<slug>.json.py`).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_YEAR_IN_PATH = re.compile(r"/(\d{4})/")

_CACHE_TTL = 3600  # 1 ora, come _registry.fetch_json
_CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    ".observable",
    "cache",
)


# ── Anni ────────────────────────────────────────────────────────────────────


def last_complete_year(today: date | None = None) -> int:
    """Ultimo anno completo: le partizioni dell'anno in corso sono parziali."""
    return (today or date.today()).year - 1


def years_in(urls: Iterable[str]) -> list[int]:
    """Anni ricavati dal segmento ``/YYYY/`` degli URL (ordinati, unici)."""
    years = set()
    for url in urls:
        match = _YEAR_IN_PATH.search(url)
        if match:
            years.add(int(match.group(1)))
    return sorted(years)


def select_years(
    available: Sequence[int],
    *,
    since: int | None = None,
    until: int | str | None = None,
    today: date | None = None,
) -> list[int]:
    """Filtra gli anni disponibili per perimetro editoriale.

    ``until="last_complete"`` usa ``last_complete_year(today)``.
    """
    if until == "last_complete":
        until = last_complete_year(today)
    if until is not None and not isinstance(until, int):
        raise ValueError(f"_views: 'until' non valido: {until!r}")
    selected = [
        year
        for year in available
        if (since is None or year >= since) and (until is None or year <= until)
    ]
    if available and not selected:
        raise RuntimeError(
            f"_views: nessun anno nel perimetro (since={since}, until={until}); "
            f"disponibili: {available[0]}–{available[-1]}"
        )
    return selected


# ── Registry del repo che possiede il mart ──────────────────────────────────


@lru_cache(maxsize=None)
def _dataset_meta(slug: str) -> dict[str, Any]:
    """Voce del catalogo ACB per slug (cache di processo)."""
    from _registry import load_registry

    for ds in load_registry().get("datasets", []):
        if ds.get("slug") == slug:
            return ds
    raise RuntimeError(f"_views: dataset {slug!r} assente dal catalogo ACB")


def _cache_path(repo: str) -> str:
    return os.path.join(_CACHE_DIR, f"registry_{repo}.json")


def _read_cache(repo: str) -> Any | None:
    path = _cache_path(repo)
    if not os.path.exists(path):
        return None
    try:
        age = time.time() - os.path.getmtime(path)
        if age >= _CACHE_TTL:
            return None
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def _write_cache(repo: str, payload: dict[str, Any]) -> None:
    path = _cache_path(repo)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)
    except OSError:
        pass  # cache best-effort: non deve rompere il build


@lru_cache(maxsize=None)
def _repo_registry(repo: str):
    """Registry tipizzato del repo, con cache su disco (TTL 1h).

    Fallback: se GitHub non risponde ma esiste una cache scaduta, la usa
    con un warning su stderr (il build prosegue; l'errore è visibile).
    """
    from lab_connectors.registry.client import (
        load_registry_github,
        registry_to_dict,
    )
    from lab_connectors.registry.models import Registry

    cached = _read_cache(repo)
    if cached is not None:
        return Registry.from_dict(cached)

    try:
        registry = load_registry_github(repo)
    except Exception as exc:
        stale_path = _cache_path(repo)
        if os.path.exists(stale_path):
            print(
                f"_views: registry {repo!r} non raggiungibile ({exc}); uso cache scaduta",
                file=sys.stderr,
            )
            with open(stale_path, encoding="utf-8") as handle:
                return Registry.from_dict(json.load(handle))
        raise RuntimeError(f"_views: registry del repo {repo!r} non leggibile: {exc}") from exc

    _write_cache(repo, registry_to_dict(registry))
    return registry


# ── Mart ────────────────────────────────────────────────────────────────────


def parse_mart_ref(ref: str) -> tuple[str, str]:
    """``<dataset>__<table>`` → ``(dataset, table)`` (convenzione del registry).

    Lo split è sull'**ultimo** ``__``: gli slug dei dataset contengono
    underscore (``anac_bandi_gara``), quindi il primo separatore è ambiguo.
    La validazione forte è nel catalogo: ``mart_location`` rifiuta gli slug
    che non esistono.
    """
    slug, sep, table = ref.rpartition("__")
    if not sep or not slug or not table:
        raise ValueError(
            f"_views: mart_ref non valido {ref!r}; atteso '<dataset>__<table>' "
            "(es. 'anac_bandi_gara__mart_annuale')"
        )
    return slug, table


@lru_cache(maxsize=None)
def mart_location(ref: str) -> dict[str, Any]:
    """Location GCS dichiarata nel registry del repo (fonte unica del path)."""
    slug, _ = parse_mart_ref(ref)
    repo = _dataset_meta(slug).get("registry_source") or ""
    if not repo:
        raise RuntimeError(f"_views: dataset {slug!r} senza 'registry_source' nel catalogo")

    for mart in _repo_registry(repo).marts:
        if mart.slug == ref:
            if not mart.location.path:
                # v2 non scrive `location` sui mart: il path si deriva da
                # `layout` + `gcs.prefix` (lab-connectors `locations.py`).
                raise RuntimeError(
                    f"_views: mart {ref!r} senza location nel registry: "
                    "serve lab-connectors con sintesi path per registry v2"
                )
            return {
                "type": mart.location.type,
                "path": mart.location.path,
                "multi_file": mart.location.multi_file,
            }
    raise RuntimeError(
        f"_views: mart {ref!r} non dichiarato nel registry di {repo!r}. "
        "Aggiungilo nella sezione mart del dataset.yml, non nel frontend."
    )


def mart_urls(ref: str, *, years: Sequence[int] | None = None) -> list[str]:
    """URL HTTPS dei parquet del mart (glob espanso via lab-connectors)."""
    from lab_connectors.gcs.paths import location_urls

    urls = location_urls(mart_location(ref), years=list(years) if years else None)
    if not urls:
        raise RuntimeError(f"_views: nessun parquet trovato per {ref!r}")
    return urls


def _read_parquet(urls: Sequence[str]) -> list[dict[str, Any]]:
    """Legge i parquet in un'unica scansione DuckDB e restituisce righe."""
    from lab_connectors.duckdb import safe_connect

    quoted = ", ".join("'" + url.replace("'", "''") + "'" for url in urls)
    sql = f"SELECT * FROM read_parquet([{quoted}], union_by_name = true)"
    with safe_connect() as connection:
        cursor = connection.sql(sql)
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def project(
    rows: Sequence[Mapping[str, Any]],
    select: Mapping[str, str] | None,
) -> list[dict[str, Any]]:
    """Sottrae/rinomina colonne: ``{nome_output: colonna_sorgente}``."""
    if not select:
        return [dict(row) for row in rows]
    if not rows:
        return []
    missing = sorted(set(select.values()) - set(rows[0]))
    if missing:
        raise RuntimeError(
            f"_views: colonne {missing} assenti nel mart (disponibili: {sorted(rows[0])})"
        )
    return [{out: row.get(src) for out, src in select.items()} for row in rows]


def mart_rows(
    ref: str,
    *,
    select: Mapping[str, str] | None = None,
    since: int | None = None,
    until: int | str | None = None,
    years: Sequence[int] | None = None,
    today: date | None = None,
) -> list[dict[str, Any]]:
    """Righe di un mart, filtrate per anno e proiettate su ``select``.

    Con ``years`` espliciti vince il perimetro del chiamante (che deve
    comunque esistere nei file pubblicati). I mart *flat* (path senza
    ``/YYYY/``) non hanno anni da filtrare: ``available`` è vuoto e i filtri
    vengono ignorati — in quel caso filtra a valle con ``project``/``group_rows``.
    """
    available = years_in(mart_urls(ref))
    if years is not None:
        selected = [year for year in years if not available or year in available]
        if not selected:
            raise RuntimeError(f"_views: anni {list(years)} assenti per {ref!r}")
    else:
        selected = select_years(available, since=since, until=until, today=today)

    urls = mart_urls(ref, years=selected) if selected else mart_urls(ref)
    return project(_read_parquet(urls), select)


# ── Aggregazioni (pure, testabili senza rete) ───────────────────────────────


def _metric(source: str | tuple[str, str], name: str) -> tuple[str, str]:
    if isinstance(source, str):
        return name, source
    column, agg = source
    return column, agg


def group_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    by: Sequence[str],
    metrics: Mapping[str, str | tuple[str, str]],
    sort_by: str | Sequence[str] | None = None,
    descending: bool = False,
) -> list[dict[str, Any]]:
    """Raggruppa righe con aggregazioni dichiarative.

    ``metrics``: ``{nome_output: "sum"|"count"|"min"|"max"}`` oppure
    ``{nome_output: (colonna, "sum")}``. ``count`` conta le righe del gruppo.
    Le righe con un valore nullo in una chiave di ``by`` sono scartate
    (stesso comportamento del vecchio ``WHERE ... IS NOT NULL``).
    """
    allowed = {"sum", "count", "min", "max"}
    resolved = {name: _metric(spec, name) for name, spec in metrics.items()}
    for column, agg in resolved.values():
        if agg not in allowed:
            raise ValueError(f"_views: aggregazione non supportata {agg!r} ({allowed})")

    groups: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        key = tuple(row.get(column) for column in by)
        if any(value is None for value in key):
            continue
        bucket = groups.get(key)
        if bucket is None:
            bucket = {column: row.get(column) for column in by}
            bucket.update({name: None for name in resolved})
            groups[key] = bucket
        for name, (column, agg) in resolved.items():
            value = row.get(column)
            if agg == "count":
                bucket[name] = (bucket[name] or 0) + 1
            elif value is None:
                continue
            elif agg == "sum":
                bucket[name] = (bucket[name] or 0) + value
            elif agg == "min":
                bucket[name] = value if bucket[name] is None else min(bucket[name], value)
            else:  # max
                bucket[name] = value if bucket[name] is None else max(bucket[name], value)

    result = list(groups.values())
    if sort_by is not None:
        keys = (sort_by,) if isinstance(sort_by, str) else tuple(sort_by)
        key = lambda row: tuple(row.get(name) for name in keys)  # noqa: E731
        result.sort(key=key, reverse=descending)
    return result


# ── Anni dichiarati/pubblicati da un dataset ────────────────────────────────


def available_years(slug: str, *, published: bool = False) -> list[int]:
    """Anni del dataset dal registry del repo che lo possiede.

    ``published=False`` (default) usa l'intervallo dichiarato (nessuna rete).
    ``published=True`` verifica le partizioni presenti su GCS (HEAD per anno).
    Con registry v2 (topic_index v8) gli anni arrivano da ``partitions`` e non
    c'è nessuna chiamata di rete. Sostituisce i ``range(YYYY, YYYY)``.
    """
    meta = _dataset_meta(slug)
    partitions = meta.get("partitions")
    if isinstance(partitions, dict) and partitions:
        years = sorted(int(key) for key in partitions if str(key).isdigit())
        if years:
            return years

    from lab_connectors.registry.availability import published_years, year_range

    repo = meta.get("registry_source") or ""
    if not repo:
        raise RuntimeError(f"_views: dataset {slug!r} senza 'registry_source' nel catalogo")
    registry = _repo_registry(repo)
    if published:
        years = published_years(registry, slug)
    else:
        years = year_range(registry, slug=slug)
    if not years:
        raise RuntimeError(
            f"_views: nessun anno dichiarato per {slug!r} nel registry di {repo!r}"
        )
    return years


# ── Provenienza / ultima esecuzione ─────────────────────────────────────────


def latest_run(slug: str) -> dict[str, Any]:
    """Ultima esecuzione di pipeline del dataset.

    Preferisce ``last_run`` del catalogo (topic_index v8: niente più
    ``signals`` nei registry). Con v1 ricade sui ``signals`` del repo.
    Campi: ``run_id``, ``status``, ``finished_at``, ``quality``, ``rows``.
    """
    meta = _dataset_meta(slug)
    last = meta.get("last_run")
    if isinstance(last, dict) and last:
        return {
            "run_id": last.get("run_id", ""),
            "status": last.get("status", ""),
            "finished_at": last.get("at") or last.get("finished_at") or "",
            "quality": last.get("quality") or {},
            "rows": last.get("rows") or {},
        }
    repo = meta.get("registry_source") or ""
    if not repo:
        return {}
    for signal in _repo_registry(repo).signals:
        if signal.id != slug or signal.run is None:
            continue
        run = signal.run
        return {
            "run_id": run.run_id,
            "status": run.status,
            "finished_at": run.finished_at,
            "quality": run.quality_score,
            "rows": run.output_rows,
        }
    return {}


# ── Output JSON ─────────────────────────────────────────────────────────────


def jsonable(value: Any) -> Any:
    """Converte i tipi DuckDB in JSON valido (NaN → null, date → ISO)."""
    if isinstance(value, Mapping):
        return {key: jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, float) and value != value:
        return None
    return value


def write(payload: Any, stream: Any | None = None) -> None:
    """Serializza su stdout nel contratto dei data loader (v1)."""
    json.dump(jsonable(payload), stream or sys.stdout, ensure_ascii=False)

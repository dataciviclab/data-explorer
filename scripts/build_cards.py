#!/usr/bin/env python3
"""Genera le schede dataset statiche consumate da `/schede/[slug]`.

La cura editoriale vive in `catalog/cards/<url_slug>.yml` (opzionale): il file
referenzia lo slug del dataset e dichiara **solo** ciò che il catalogo non ha.

La pagina è una composizione di **blocchi** dichiarati nel file (v0: `kpi`,
`series`, `ranking`). Il produttore risolve i dati dai mart e li scrive nel
card JSON: il build del sito non interroga GCS.

Le schede sono **incrementali**: ognuna porta un `fingerprint` degli input
(file editoriale, campi del catalogo usati, `last_run` della pipeline, hash del
produttore). Se il fingerprint non cambia, la scheda precedente viene riusata
così com'è: zero query ai mart. A 100–200 schede un deploy che non le tocca non
costa nulla.

Uso:
    python3 scripts/build_cards.py                 # aggiorna solo ciò che è cambiato
    python3 scripts/build_cards.py --dry-run       # mostra le scelte, non scrive
    python3 scripts/build_cards.py --only anac-bandi-gara,entrate-stato
    python3 scripts/build_cards.py --force         # ignora le schede in cache
    python3 scripts/build_cards.py --new anac_bandi_gara   # stub editoriale

`--only` non filtra l'output: **forza** il rebuild di quei dataset e riusa gli
altri (serve a un `data_updated` mirato). Le schede non più dichiarate in
`catalog/cards/` spariscono dall'artefatto.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Callable

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "data"))

from _registry import build_catalog, load_registry  # noqa: E402
from _views import jsonable, last_complete_year, latest_run, mart_rows  # noqa: E402

CARDS_DIR = ROOT / "catalog" / "cards"
OUTPUT = ROOT / "src" / "data" / "cards.json"
QUERY_SQL_URL = "https://dataciviclab-dashboard.streamlit.app/Query_SQL"

Fetch = Callable[[str, dict], list[dict]]

ALLOWED_KEYS = {
    "dataset",
    "title",
    "description",
    "source",
    "source_url",
    "license",
    "view",
    "blocks",
    "intro",
    "notes",
}

# Campi che vivono nel catalogo: copiarli qui crea drift.
CATALOG_KEYS = {
    "name",
    "period",
    "rows",
    "rows_clean",
    "clean_rows",
    "columns",
    "stage",
    "category",
    "registry_source",
    "source_id",
    "mart_refs",
    "location",
    "slug",
    "url_slug",
}

VIEW_KEYS = {
    "mart",
    "x",
    "y",
    "x_label",
    "y_label",
    "y_format",
    "y2",
    "y2_label",
    "y2_format",
}
VIEW_REQUIRED = {"mart", "x", "y"}

MEASURE_KEYS = {"mart", "x", "y", "label", "format", "delta", "where"}

BLOCK_KEYS: dict[str, set[str]] = {
    "kpi": {"type", "title", "measures"},
    "series": {"type", "title", "note", "mart", "x", "x_label", "y", "y_label", "y_format", "where"},
    "composition": {
        "type",
        "title",
        "note",
        "mart",
        "x",
        "x_label",
        "y",
        "y_label",
        "y_format",
        "by",
        "by_label",
        "normalize",
        "where",
    },
    "map": {
        "type",
        "title",
        "note",
        "mart",
        "x",
        "dimension",
        "dimension_label",
        "measure",
        "measure_label",
        "measure_format",
        "where",
    },
    "ranking": {
        "type",
        "title",
        "note",
        "mart",
        "x",
        "dimension",
        "dimension_label",
        "measure",
        "measure_label",
        "measure_format",
        "top",
        "where",
    },
}
BLOCK_REQUIRED: dict[str, set[str]] = {
    "kpi": {"measures"},
    "series": {"mart", "x", "y"},
    "composition": {"mart", "x", "y", "by"},
    "map": {"mart", "dimension", "measure"},
    "ranking": {"mart", "dimension", "measure"},
}

DEFAULT_X_LABEL = "Anno"
DEFAULT_FORMAT = "num"
DEFAULT_TOP = 20

# Cambia quando cambia la forma della scheda: invalida tutte le schede.
SCHEMA_VERSION = 2

# Campi del catalogo che finiscono nella scheda: se cambiano, la scheda va rifatta.
FINGERPRINT_ENTRY_KEYS = (
    "slug",
    "url_slug",
    "name",
    "description",
    "category",
    "theme",
    "theme_name",
    "published",
    "period",
    "source",
    "source_id",
    "registry_source",
    "clean_rows",
    "mart_refs",
    "location",
    "columns",
)


# ── Validazione dei file editoriali ─────────────────────────────────────────


def _validate_view(path: Path, view: dict, entry: dict, errors: list[str]) -> None:
    if not isinstance(view, dict):
        errors.append(f"{path.name}: 'view' deve essere una mappa")
        return
    missing = VIEW_REQUIRED - set(view)
    if missing:
        errors.append(f"{path.name}: view manca {sorted(missing)}")
    unknown = set(view) - VIEW_KEYS
    if unknown:
        errors.append(f"{path.name}: view ha campi non ammessi {sorted(unknown)}")
    _validate_mart(path, view.get("mart"), entry, errors)


def _validate_mart(path: Path, mart: str | None, entry: dict, errors: list[str]) -> None:
    if mart and mart not in (entry.get("mart_refs") or []):
        errors.append(f"{path.name}: mart {mart!r} non tra i mart_refs di {entry['slug']!r}")


def _validate_where(path: Path, where: object, errors: list[str]) -> None:
    """`where` è uguaglianza colonna → scalare. Niente operatori, niente SQL."""
    if where is None:
        return
    if not isinstance(where, dict):
        errors.append(f"{path.name}: 'where' deve essere una mappa colonna: valore")
        return
    for key, value in where.items():
        if not isinstance(value, (str, int, float, bool)):
            errors.append(f"{path.name}: where[{key!r}] deve essere uno scalare")


def _validate_block(path: Path, block: dict, entry: dict, errors: list[str]) -> None:
    if not isinstance(block, dict):
        errors.append(f"{path.name}: ogni blocco deve essere una mappa")
        return
    kind = block.get("type")
    if kind not in BLOCK_KEYS:
        errors.append(f"{path.name}: tipo blocco non supportato {kind!r} (kpi|series|ranking)")
        return
    missing = BLOCK_REQUIRED[kind] - set(block)
    if missing:
        errors.append(f"{path.name}: blocco {kind} manca {sorted(missing)}")
    unknown = set(block) - BLOCK_KEYS[kind]
    if unknown:
        errors.append(f"{path.name}: blocco {kind} ha campi non ammessi {sorted(unknown)}")
    _validate_where(path, block.get("where"), errors)
    if kind == "kpi":
        measures = block.get("measures")
        if not isinstance(measures, list) or not measures:
            errors.append(f"{path.name}: blocco kpi richiede 'measures' non vuoto")
            return
        for measure in measures:
            if not isinstance(measure, dict) or {"mart", "x", "y"} - set(measure):
                errors.append(f"{path.name}: misura kpi incompleta (mart/x/y)")
                continue
            unknown = set(measure) - MEASURE_KEYS
            if unknown:
                errors.append(f"{path.name}: misura kpi ha campi non ammessi {sorted(unknown)}")
            _validate_where(path, measure.get("where"), errors)
            _validate_mart(path, measure.get("mart"), entry, errors)
        return
    _validate_mart(path, block.get("mart"), entry, errors)


def load_specs(catalog_by_slug: dict[str, dict]) -> tuple[dict[str, dict], list[str]]:
    """Legge `catalog/cards/*.yml` e valida i contratti. Ritorna (specs, errori)."""
    specs: dict[str, dict] = {}
    errors: list[str] = []
    if not CARDS_DIR.exists():
        return specs, errors

    for path in sorted(CARDS_DIR.glob("*.yml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(raw, dict):
            errors.append(f"{path.name}: il file deve essere una mappa YAML")
            continue

        unknown = set(raw) - ALLOWED_KEYS
        if unknown:
            errors.append(f"{path.name}: campi non ammessi {sorted(unknown)}")
        duplicated = set(raw) & CATALOG_KEYS
        if duplicated:
            errors.append(
                f"{path.name}: campi che appartengono al catalogo {sorted(duplicated)}"
            )

        slug = raw.get("dataset")
        if not slug:
            errors.append(f"{path.name}: manca 'dataset'")
            continue
        entry = catalog_by_slug.get(str(slug))
        if entry is None:
            errors.append(f"{path.name}: dataset {slug!r} assente dal catalogo ACB")
            continue
        if path.stem != entry["url_slug"]:
            errors.append(f"{path.name}: il nome file dovrebbe essere {entry['url_slug']}.yml")
        if entry["slug"] in specs:
            errors.append(f"{path.name}: dataset {slug!r} già dichiarato in un altro file")

        if raw.get("view") and raw.get("blocks"):
            errors.append(f"{path.name}: usa 'blocks' oppure 'view', non entrambi")

        if raw.get("view") is not None:
            _validate_view(path, raw["view"], entry, errors)

        blocks = raw.get("blocks")
        if blocks is not None:
            if not isinstance(blocks, list) or not blocks:
                errors.append(f"{path.name}: 'blocks' deve essere una lista non vuota")
            else:
                for block in blocks:
                    _validate_block(path, block, entry, errors)

        specs[entry["slug"]] = raw

    return specs, errors


# ── Blocchi: dati dal mart ──────────────────────────────────────────────────


def _where(block: dict) -> dict:
    return block.get("where") or {}


def _apply_where(rows: list[dict], where: dict) -> list[dict]:
    if not where:
        return rows
    return [row for row in rows if all(row.get(key) == value for key, value in where.items())]


def _columns(where: dict, **aliases: str) -> dict:
    return {**aliases, **{key: key for key in where}}


def _points(rows: list[dict], until: int) -> list[dict]:
    """Serie ordinata, dedup per x, al più fino all'ultimo anno completo."""
    by_x: dict = {}
    for row in rows:
        x, y = row.get("x"), row.get("y")
        if x is None or y is None or not isinstance(x, (int, float)) or x > until:
            continue
        by_x[int(x)] = {"x": int(x), "y": y}
    return [by_x[x] for x in sorted(by_x)]


def _kpi_block(block: dict, fetch: Fetch) -> dict:
    items = []
    until = last_complete_year()
    for measure in block["measures"]:
        where = _where(measure)
        rows = _apply_where(
            fetch(measure["mart"], _columns(where, x=measure["x"], y=measure["y"])), where
        )
        points = _points(rows, until)
        if not points:
            continue
        last = points[-1]
        items.append(
            {
                "label": measure.get("label") or measure["y"],
                "value": last["y"],
                "format": measure.get("format") or DEFAULT_FORMAT,
            }
        )
        if measure.get("delta") and points[0]["y"]:
            delta = (last["y"] - points[0]["y"]) / points[0]["y"] * 100
            items.append(
                {
                    "label": f"Δ {points[0]['x']}→{last['x']}",
                    "value": round(delta, 1),
                    "format": "deltaPct",
                }
            )
    return {"type": "kpi", "title": block.get("title", ""), "items": items}


def _series_block(block: dict, fetch: Fetch) -> dict:
    where = _where(block)
    rows = _apply_where(
        fetch(block["mart"], _columns(where, x=block["x"], y=block["y"])), where
    )
    points = _points(rows, last_complete_year())
    return {
        "type": "series",
        "title": block.get("title", ""),
        "note": block.get("note", ""),
        "x_label": block.get("x_label") or DEFAULT_X_LABEL,
        "y_label": block.get("y_label") or block["y"],
        "y_format": block.get("y_format") or DEFAULT_FORMAT,
        "data": points,
    }


def _composition_block(block: dict, fetch: Fetch) -> dict:
    where = _where(block)
    rows = _apply_where(
        fetch(
            block["mart"],
            _columns(where, x=block["x"], group=block["by"], y=block["y"]),
        ),
        where,
    )
    until = last_complete_year()
    totals: dict[tuple[int, str], float] = {}
    for row in rows:
        x, group, value = row.get("x"), row.get("group"), row.get("y")
        if x is None or group is None or value is None:
            continue
        if not isinstance(x, (int, float)) or x > until:
            continue
        key = (int(x), str(group))
        totals[key] = totals.get(key, 0) + value
    data = [
        {"x": x, "group": group, "y": value}
        for (x, group), value in sorted(totals.items())
    ]
    groups = sorted({point["group"] for point in data})
    return {
        "type": "composition",
        "title": block.get("title", ""),
        "note": block.get("note", ""),
        "x_label": block.get("x_label") or DEFAULT_X_LABEL,
        "y_label": block.get("y_label") or "Quota",
        "y_format": block.get("y_format") or DEFAULT_FORMAT,
        "by_label": block.get("by_label") or block["by"],
        "normalize": bool(block.get("normalize", True)),
        "groups": groups,
        "data": data,
    }


def _map_block(block: dict, fetch: Fetch) -> dict:
    where = _where(block)
    columns = _columns(where, region=block["dimension"], value=block["measure"])
    if block.get("x"):
        columns["x"] = block["x"]
    rows = _apply_where(fetch(block["mart"], columns), where)
    year = None
    if block.get("x"):
        years = [
            int(row["x"])
            for row in rows
            if isinstance(row.get("x"), (int, float)) and row["x"] <= last_complete_year()
        ]
        if years:
            year = max(years)
            rows = [row for row in rows if row.get("x") == year]
    totals: dict[str, float] = {}
    for row in rows:
        region, value = row.get("region"), row.get("value")
        if region is None or value is None:
            continue
        totals[str(region)] = totals.get(str(region), 0) + value
    return {
        "type": "map",
        "title": block.get("title", ""),
        "note": block.get("note", ""),
        "year": year,
        "dimension_label": block.get("dimension_label") or block["dimension"],
        "measure_label": block.get("measure_label") or block["measure"],
        "measure_format": block.get("measure_format") or DEFAULT_FORMAT,
        "data": [{"region": region, "value": value} for region, value in sorted(totals.items())],
    }


def _ranking_block(block: dict, fetch: Fetch) -> dict:
    where = _where(block)
    columns = _columns(where, label=block["dimension"], value=block["measure"])
    if block.get("x"):
        columns["x"] = block["x"]
    rows = _apply_where(fetch(block["mart"], columns), where)
    year = None
    if block.get("x"):
        years = [row["x"] for row in rows if isinstance(row.get("x"), (int, float))]
        years = [int(y) for y in years if y <= last_complete_year()]
        if years:
            year = max(years)
            rows = [row for row in rows if row.get("x") == year]
    data = [
        {"label": row["label"], "value": row["value"]}
        for row in rows
        if row.get("label") is not None and row.get("value") is not None
    ]
    data.sort(key=lambda row: row["value"], reverse=True)
    top = int(block.get("top") or DEFAULT_TOP)
    return {
        "type": "ranking",
        "title": block.get("title", ""),
        "note": block.get("note", ""),
        "year": year,
        "dimension_label": block.get("dimension_label") or block["dimension"],
        "measure_label": block.get("measure_label") or block["measure"],
        "measure_format": block.get("measure_format") or DEFAULT_FORMAT,
        "data": data[:top],
    }


def _legacy_blocks(spec: dict) -> list[dict]:
    """`view` (formato singolo) → kpi + series. Compatibilità con i file v0."""
    view = spec.get("view")
    if not view:
        return []
    measures = [
        {
            "mart": view["mart"],
            "x": view["x"],
            "y": view["y"],
            "label": view.get("y_label"),
            "format": view.get("y_format"),
            "delta": True,
        }
    ]
    if view.get("y2"):
        measures.append(
            {
                "mart": view["mart"],
                "x": view["x"],
                "y": view["y2"],
                "label": view.get("y2_label"),
                "format": view.get("y2_format"),
            }
        )
    return [
        {"type": "kpi", "measures": measures},
        {
            "type": "series",
            "mart": view["mart"],
            "x": view["x"],
            "y": view["y"],
            "x_label": view.get("x_label"),
            "y_label": view.get("y_label"),
            "y_format": view.get("y_format"),
        },
    ]


def _spec_blocks(spec: dict) -> list[dict]:
    return spec["blocks"] if spec.get("blocks") is not None else _legacy_blocks(spec)


def _marts_used(spec: dict) -> list[str]:
    marts: set[str] = set()
    for block in _spec_blocks(spec):
        if block.get("type") == "kpi":
            marts.update(measure["mart"] for measure in block["measures"])
        elif block.get("mart"):
            marts.add(block["mart"])
    return sorted(marts)


def _build_blocks(spec: dict, fetch: Fetch) -> list[dict]:
    built = []
    for block in _spec_blocks(spec):
        kind = block["type"]
        if kind == "kpi":
            built.append(_kpi_block(block, fetch))
        elif kind == "series":
            built.append(_series_block(block, fetch))
        elif kind == "composition":
            built.append(_composition_block(block, fetch))
        elif kind == "map":
            built.append(_map_block(block, fetch))
        elif kind == "ranking":
            built.append(_ranking_block(block, fetch))
    return built


# ── Costruzione della scheda ────────────────────────────────────────────────


def _links(entry: dict) -> dict:
    path = (entry.get("location") or {}).get("path") or ""
    repo = entry.get("registry_source") or ""
    return {
        "pipeline": f"https://github.com/dataciviclab/{repo}" if repo else "",
        "parquet": path.replace("gs://", "https://storage.googleapis.com/"),
        "query": QUERY_SQL_URL,
    }


def _warnings(card: dict, spec: dict) -> list[str]:
    warnings = []
    if not card["description"]:
        warnings.append("Descrizione del dataset non disponibile.")
    if not card["source"]:
        warnings.append(f"Nome della fonte non disponibile (source_id: {card['source_id']}).")
    if not card["license"]:
        warnings.append("Licenza non dichiarata.")
    if not spec.get("title"):
        warnings.append("Titolo editoriale non dichiarato: uso il nome del catalogo.")
    if not card["blocks"]:
        warnings.append("Nessun blocco dichiarato: scheda senza grafici.")
    if not card["links"]["parquet"]:
        warnings.append("Percorso del parquet clean non disponibile.")
    return warnings


def build_card(entry: dict, spec: dict, fetch: Fetch, *, fingerprint: str = "") -> dict:
    """Compone la scheda: catalogo + override editoriali + blocchi dai mart."""
    card = {
        "slug": entry["slug"],
        "url_slug": entry["url_slug"],
        "name": spec.get("title") or entry.get("name") or entry["slug"],
        "description": spec.get("description") or entry.get("description") or "",
        "intro": spec.get("intro") or "",
        "notes": [str(note) for note in spec.get("notes") or []],
        "category": entry.get("category", ""),
        "theme": entry.get("theme", ""),
        "theme_name": entry.get("theme_name", ""),
        "published": bool(entry.get("published", entry.get("stage") == "published")),
        "period": entry.get("period") or {},
        "source": spec.get("source") or entry.get("source") or "",
        "source_url": spec.get("source_url") or "",
        "license": spec.get("license") or "",
        "source_id": entry.get("source_id", ""),
        "registry_source": entry.get("registry_source", ""),
        "rows_clean": entry.get("clean_rows"),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "fingerprint": fingerprint,
        "marts": _marts_used(spec),
        "blocks": _build_blocks(spec, fetch),
        "dictionary": entry.get("columns") or [],
        "links": _links(entry),
        "run": latest_run(entry["slug"]) or None,
    }
    card["warnings"] = _warnings(card, spec)
    return card


# ── Fingerprint e riuso (schede incrementali) ───────────────────────────────


def _spec_text(entry: dict) -> str:
    """File editoriale grezzo: ogni modifica deve invalidare la scheda."""
    try:
        return (CARDS_DIR / f"{entry['url_slug']}.yml").read_text(encoding="utf-8")
    except OSError:
        return ""


@lru_cache(maxsize=1)
def producer_version() -> str:
    """Hash del produttore + contratti dati: cambia il codice, cambiano le schede."""
    digest = hashlib.sha256()
    for path in (
        Path(__file__).resolve(),
        ROOT / "src" / "data" / "_views.py",
        ROOT / "src" / "data" / "_registry.py",
    ):
        digest.update(path.read_bytes())
    return digest.hexdigest()[:16]


def card_fingerprint(entry: dict, spec_text: str, *, producer: str = "") -> str:
    """Identità della scheda: stessi input ⇒ stesso fingerprint ⇒ si riusa.

    Input: contratto del produttore, file editoriale, campi del catalogo usati
    dalla scheda, ultima esecuzione della pipeline (``last_run``) e ultimo anno
    completo (a gennaio le serie cambiano perimetro).
    """
    payload = {
        "schema": SCHEMA_VERSION,
        "producer": producer or producer_version(),
        "spec": spec_text,
        "dataset": {key: entry.get(key) for key in FINGERPRINT_ENTRY_KEYS},
        "run": latest_run(entry["slug"]),
        "last_complete_year": last_complete_year(),
    }
    serialized = json.dumps(jsonable(payload), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:32]


def load_cards(path: Path | None = None) -> dict[str, dict]:
    """Schede già generate (artefatto): base per il riuso incrementale."""
    try:
        data = json.loads((path or OUTPUT).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def build_all(
    specs: dict[str, dict],
    by_slug: dict[str, dict],
    previous: dict[str, dict],
    fetch: Fetch,
    *,
    force: bool = False,
    only: frozenset[str] = frozenset(),
    producer: str = "",
) -> tuple[dict[str, dict], list[dict]]:
    """Costruisce le schede riusando quelle il cui fingerprint non è cambiato.

    ``only`` non filtra l'output: forza il rebuild di quei dataset e riusa gli
    altri. Le schede non più dichiarate in ``catalog/cards/`` non entrano
    nell'artefatto (niente code morte).
    """
    cards: dict[str, dict] = {}
    report: list[dict] = []
    producer = producer or producer_version()

    for slug, spec in sorted(specs.items()):
        entry = by_slug[slug]
        url_slug = entry["url_slug"]
        fingerprint = card_fingerprint(entry, _spec_text(entry), producer=producer)
        forced = force or slug in only or url_slug in only
        cached = previous.get(url_slug)
        if not forced and isinstance(cached, dict) and cached.get("fingerprint") == fingerprint:
            card, state = cached, "riuso"
        else:
            card, state = build_card(entry, spec, fetch, fingerprint=fingerprint), "query"
        cards[url_slug] = card
        blocks = card.get("blocks") or []
        report.append(
            {
                "url_slug": url_slug,
                "name": card.get("name", ""),
                "blocks": len(blocks),
                "marts": len(card.get("marts") or []),
                "points": sum(
                    len(block.get("data") or [])
                    for block in blocks
                    if block.get("type") == "series"
                ),
                "state": state,
            }
        )
    return cards, report


# ── CLI ─────────────────────────────────────────────────────────────────────


def _catalog() -> tuple[list[dict], dict[str, dict]]:
    datasets = build_catalog(load_registry())["datasets"]
    return datasets, {entry["slug"]: entry for entry in datasets}


def _find_entry(datasets: list[dict], key: str) -> dict | None:
    for entry in datasets:
        if key in (entry["slug"], entry["url_slug"]):
            return entry
    return None


def _mart_fetch() -> Fetch:
    cache: dict[tuple, list[dict]] = {}

    def fetch(mart: str, columns: dict) -> list[dict]:
        key = (mart, tuple(sorted(columns.items())))
        if key not in cache:
            cache[key] = mart_rows(mart, select=columns)
        return cache[key]

    return fetch


def new_stub(datasets: list[dict], key: str) -> int:
    entry = _find_entry(datasets, key)
    if entry is None:
        print(f"! {key!r}: dataset assente dal catalogo ACB", file=sys.stderr)
        return 1
    path = CARDS_DIR / f"{entry['url_slug']}.yml"
    if path.exists():
        print(f"! {path.relative_to(ROOT)} esiste già", file=sys.stderr)
        return 1
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    marts = entry.get("mart_refs") or []
    lines = [
        f"# Scheda editoriale — {entry['url_slug']}",
        "# Compila solo ciò che il catalogo non ha: titolo, intro, note,",
        "# e i blocchi (kpi/series/ranking). Metadati e colonne dal catalogo.",
        f"dataset: {entry['slug']}",
        '# title: "..."',
        '# intro: "..."',
        "# blocks:",
        "#   - type: series",
        f"#     mart: {marts[0] if marts else '<mart>'}" ,
        "#     x: anno",
        "#     y: <misura>",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✓ creato {path.relative_to(ROOT)}")
    return 0


def main(argv: list[str]) -> int:
    datasets, by_slug = _catalog()

    if "--new" in argv:
        index = argv.index("--new")
        if index + 1 >= len(argv):
            print("! --new richiede uno slug", file=sys.stderr)
            return 1
        return new_stub(datasets, argv[index + 1])

    only: set[str] = set()
    if "--only" in argv:
        index = argv.index("--only")
        if index + 1 >= len(argv):
            print("! --only richiede una lista di slug", file=sys.stderr)
            return 1
        only = {part.strip() for part in argv[index + 1].split(",") if part.strip()}

    specs, errors = load_specs(by_slug)
    if errors:
        for error in errors:
            print(f"! {error}", file=sys.stderr)
        return 1

    dry_run = "--dry-run" in argv
    force = "--force" in argv or "--refresh" in argv
    fetch = _mart_fetch()
    cards, report = build_all(
        specs,
        by_slug,
        load_cards(),
        fetch,
        force=force,
        only=frozenset(only),
        producer=producer_version(),
    )
    reused = sum(1 for row in report if row["state"] == "riuso")

    if dry_run:
        print(f"{'scheda':26s} {'blocchi':>7s} {'mart':>4s} {'punti':>5s}  {'stato':6s} titolo")
        for row in report:
            print(
                f"{row['url_slug']:26s} {row['blocks']:7d} {row['marts']:4d} "
                f"{row['points']:5d}  {row['state']:6s} {row['name']}"
            )
        with_blocks = sum(1 for card in cards.values() if card.get("blocks"))
        print(f"\n{len(report)} schede; {reused} da cache; {with_blocks} con blocchi")
        return 0

    OUTPUT.write_text(json.dumps(jsonable(cards), ensure_ascii=False, indent=1), encoding="utf-8")
    print(
        f"✓ {len(cards) - reused} aggiornate, {reused} riusate "
        f"in {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size} byte)"
    )
    for row in report:
        print(
            f"  · {row['url_slug']}: {row['blocks']} blocchi, {row['marts']} mart, "
            f"{row['points']} punti [{row['state']}]"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

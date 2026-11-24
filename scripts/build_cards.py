#!/usr/bin/env python3
"""Genera le schede dataset statiche consumate da `/schede/[slug]`.

La cura editoriale vive in `catalog/cards/<url_slug>.yml` (opzionale): il file
referenzia lo slug del dataset e dichiara **solo** ciò che il catalogo non ha
(titolo, intro, eventuale vista, note). Tutto il resto viene dal catalogo ACB.

Il produttore gira **fuori** dal build del sito e scrive un artefatto piccolo
(`src/data/cards.json`): il build non interroga GCS.

Uso:
    python3 scripts/build_cards.py                 # genera tutte le schede
    python3 scripts/build_cards.py --dry-run       # mostra le scelte, non scrive
    python3 scripts/build_cards.py --only anac-bandi-gara,entrate-stato
    python3 scripts/build_cards.py --new anac_bandi_gara   # stub editoriale
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "data"))

from _registry import build_catalog, load_registry  # noqa: E402
from _views import jsonable, last_complete_year, latest_run, mart_rows  # noqa: E402

CARDS_DIR = ROOT / "catalog" / "cards"
OUTPUT = ROOT / "src" / "data" / "cards.json"
QUERY_SQL_URL = "https://dataciviclab-dashboard.streamlit.app/Query_SQL"

# Campi ammessi nel file editoriale. Tutto il resto è un errore (typo o
# duplicazione di un campo che appartiene al catalogo).
ALLOWED_KEYS = {
    "dataset",
    "title",
    "description",
    "source",
    "source_url",
    "license",
    "view",
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

DEFAULT_X_LABEL = "Anno"
DEFAULT_FORMAT = "num"


# ── File editoriali ─────────────────────────────────────────────────────────


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
    mart = view.get("mart")
    if mart and mart not in (entry.get("mart_refs") or []):
        errors.append(
            f"{path.name}: mart {mart!r} non tra i mart_refs di {entry['slug']!r}"
        )


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

        view = raw.get("view")
        if view is not None:
            _validate_view(path, view, entry, errors)

        specs[entry["slug"]] = raw

    return specs, errors


# ── Costruzione della scheda ────────────────────────────────────────────────


def _points(rows: list[dict], until: int, has_y2: bool) -> list[dict]:
    """Serie ordinata, dedup per x, al più fino all'ultimo anno completo."""
    by_x: dict = {}
    for row in rows:
        x, y = row.get("x"), row.get("y")
        if x is None or y is None or not isinstance(x, (int, float)) or x > until:
            continue
        point = {"x": int(x), "y": y}
        if has_y2 and row.get("y2") is not None:
            point["y2"] = row["y2"]
        by_x[int(x)] = point
    return [by_x[x] for x in sorted(by_x)]


def _kpis(points: list[dict], view: dict) -> list[dict]:
    if not points:
        return []
    first, last = points[0], points[-1]
    kpis = [
        {
            "label": view.get("y_label") or view["y"],
            "value": last["y"],
            "format": view.get("y_format") or DEFAULT_FORMAT,
        }
    ]
    if first["y"]:
        delta = (last["y"] - first["y"]) / first["y"] * 100
        kpis.append(
            {
                "label": f"Δ {first['x']}→{last['x']}",
                "value": round(delta, 1),
                "format": "deltaPct",
            }
        )
    if view.get("y2") and last.get("y2") is not None:
        kpis.append(
            {
                "label": view.get("y2_label") or view["y2"],
                "value": last["y2"],
                "format": view.get("y2_format") or DEFAULT_FORMAT,
            }
        )
    return kpis


def _links(entry: dict) -> dict:
    path = (entry.get("location") or {}).get("path") or ""
    repo = entry.get("registry_source") or ""
    return {
        "pipeline": f"https://github.com/dataciviclab/{repo}" if repo else "",
        "parquet": path.replace("gs://", "https://storage.googleapis.com/"),
        "query": QUERY_SQL_URL,
    }


def _warnings(card: dict, spec: dict, has_view: bool) -> list[str]:
    warnings = []
    if not card["description"]:
        warnings.append("Descrizione del dataset non disponibile.")
    if not card["source"]:
        warnings.append(f"Nome della fonte non disponibile (source_id: {card['source_id']}).")
    if not card["license"]:
        warnings.append("Licenza non dichiarata.")
    if not spec.get("title"):
        warnings.append("Titolo editoriale non dichiarato: uso il nome del catalogo.")
    if not has_view:
        warnings.append("Vista base non dichiarata: scheda senza grafico.")
    if not card["links"]["parquet"]:
        warnings.append("Percorso del parquet clean non disponibile.")
    return warnings


def build_card(entry: dict, spec: dict, rows: list[dict]) -> dict:
    """Compone la scheda: catalogo + override editoriali + fatti dal mart."""
    view = spec.get("view") or {}
    has_view = bool(view)
    points = _points(rows, last_complete_year(), bool(view.get("y2"))) if has_view else []

    card = {
        "slug": entry["slug"],
        "url_slug": entry["url_slug"],
        "name": spec.get("title") or entry.get("name") or entry["slug"],
        "description": spec.get("description") or entry.get("description") or "",
        "intro": spec.get("intro") or "",
        "notes": [str(note) for note in spec.get("notes") or []],
        "category": entry.get("category", ""),
        "stage": entry.get("stage", ""),
        "period": entry.get("period") or {},
        "source": spec.get("source") or entry.get("source") or "",
        "source_url": spec.get("source_url") or "",
        "license": spec.get("license") or "",
        "source_id": entry.get("source_id", ""),
        "registry_source": entry.get("registry_source", ""),
        "rows_clean": entry.get("clean_rows"),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "mart": {"ref": view.get("mart", ""), "table": view.get("mart", "").split("__", 1)[-1]},
        "x": {"field": view.get("x", ""), "label": view.get("x_label") or DEFAULT_X_LABEL},
        "y": {"label": view.get("y_label") or view.get("y", ""), "format": view.get("y_format") or DEFAULT_FORMAT},
        "series": points,
        "kpis": _kpis(points, view) if has_view else [],
        "dictionary": entry.get("columns") or [],
        "links": _links(entry),
        "run": latest_run(entry["slug"]) or None,
    }
    card["warnings"] = _warnings(card, spec, has_view)
    return card


# ── CLI ─────────────────────────────────────────────────────────────────────


def _catalog() -> tuple[list[dict], dict[str, dict]]:
    datasets = build_catalog(load_registry())["datasets"]
    return datasets, {entry["slug"]: entry for entry in datasets}


def _find_entry(datasets: list[dict], key: str) -> dict | None:
    for entry in datasets:
        if key in (entry["slug"], entry["url_slug"]):
            return entry
    return None


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
        "# e (se serve) la vista. Metadati e colonne vengono dal catalogo.",
        f"dataset: {entry['slug']}",
        '# title: "..."',
        '# intro: "..."',
    ]
    if marts:
        lines += [
            "# view:",
            f"#   mart: {marts[0]}",
            "#   x: anno",
            "#   y: <misura>",
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
        only = {part.strip() for part in argv[index + 1].split(",") if part.strip()}

    specs, errors = load_specs(by_slug)
    if errors:
        for error in errors:
            print(f"! {error}", file=sys.stderr)
        return 1

    dry_run = "--dry-run" in argv
    cards: dict[str, dict] = {}
    rows_out: list[tuple[str, str, str, str, int, str]] = []

    for slug, spec in sorted(specs.items()):
        entry = by_slug[slug]
        if only and entry["url_slug"] not in only and slug not in only:
            continue
        view = spec.get("view")
        rows: list[dict] = []
        if view:
            columns = {"x": view["x"], "y": view["y"]}
            if view.get("y2"):
                columns["y2"] = view["y2"]
            rows = mart_rows(view["mart"], select=columns)
        card = build_card(entry, spec, rows)
        cards[entry["url_slug"]] = card
        rows_out.append(
            (
                entry["url_slug"],
                (view or {}).get("mart", "—"),
                (view or {}).get("x", "—"),
                (view or {}).get("y", "—"),
                len(card["series"]),
                card["name"],
            )
        )

    if dry_run:
        print(f"{'scheda':26s} {'mart':40s} {'x':10s} {'y':22s} {'punti':>5s}  titolo")
        for row in rows_out:
            print(f"{row[0]:26s} {row[1]:40s} {row[2]:10s} {row[3]:22s} {row[4]:5d}  {row[5]}")
        print(f"\n{len(rows_out)} schede; {sum(len(c['series']) > 0 for c in cards.values())} con grafico")
        return 0

    OUTPUT.write_text(json.dumps(jsonable(cards), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ scrivete {len(cards)} schede in {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size} byte)")
    for row in rows_out:
        print(f"  · {row[0]}: {row[4]} punti da {row[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

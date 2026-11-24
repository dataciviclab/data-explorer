#!/usr/bin/env python3
"""Genera le schede dataset statiche consumate da `/schede/[slug]`.

Perché non è un data loader: il build del sito non deve interrogare GCS.
Questo script gira **prima** del build (job separato in CI) e scrive un
artefatto piccolo e leggibile: `src/data/cards.json`.

Costo: una query per scheda. Oggi 3 schede pilota; quando il modello sarà
stabile, si estende ai dataset published con mart (33, di cui 27 con mart).

Il perimetro della vista è **dichiarato** in `SPECS` (che mart, quale asse,
quale misura). Nel modello finale questa dichiarazione vive nel `dataset.yml`
del repo che possiede il dato, non qui.

Uso:
    python3 scripts/build-cards.py [--only slug1,slug2]
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "data"))

from _registry import build_catalog, load_registry  # noqa: E402
from _views import jsonable, last_complete_year, latest_run, mart_rows  # noqa: E402

QUERY_SQL_URL = "https://dataciviclab-dashboard.streamlit.app/Query_SQL"

# Dichiarazione della vista base per i piloti. Struttura minima:
# mart + asse temporale + misura; `y2` è una seconda misura (facoltativa).
SPECS: dict[str, dict] = {
    "anac-bandi-gara": {
        "mart": "anac_bandi_gara__mart_annuale",
        "x": "anno",
        "x_label": "Anno di pubblicazione",
        "y": "n_lotti",
        "y_label": "Lotti pubblicati",
        "y_format": "num",
        "y2": "importo_totale",
        "y2_label": "Importo stimato",
        "y2_format": "euroCompact",
    },
    "entrate-stato": {
        "mart": "bdap_entrate_stato__mart_entrate_anno",
        "x": "anno",
        "x_label": "Esercizio finanziario",
        "y": "entrate_totali_cp",
        "y_label": "Entrate totali (competenza)",
        "y_format": "euroCompact",
    },
    "cinque-per-mille": {
        "mart": "ade_cinque_per_mille__five_per_mille_trend",
        "x": "anno",
        "x_label": "Anno",
        "y": "importo_totale",
        "y_label": "Importo erogato",
        "y_format": "euroCompact",
    },
}


def _points(rows: list[dict], spec: dict) -> list[dict]:
    """Serie ordinata, dedup per x, al più fino all'ultimo anno completo."""
    until = last_complete_year()
    by_x: dict = {}
    for row in rows:
        x, y = row.get("x"), row.get("y")
        if x is None or y is None or not isinstance(x, (int, float)) or x > until:
            continue
        point = {"x": int(x), "y": y}
        if spec.get("y2") and row.get("y2") is not None:
            point["y2"] = row["y2"]
        by_x[int(x)] = point
    return [by_x[x] for x in sorted(by_x)]


def _kpis(points: list[dict], spec: dict) -> list[dict]:
    if not points:
        return []
    first, last = points[0], points[-1]
    kpis = [{"label": spec["y_label"], "value": last["y"], "format": spec["y_format"]}]
    if first["y"]:
        delta = (last["y"] - first["y"]) / first["y"] * 100
        kpis.append(
            {
                "label": f"Δ {first['x']}→{last['x']}",
                "value": round(delta, 1),
                "format": "deltaPct",
            }
        )
    if spec.get("y2") and last.get("y2") is not None:
        kpis.append(
            {
                "label": spec["y2_label"],
                "value": last["y2"],
                "format": spec["y2_format"],
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


def _warnings(entry: dict) -> list[str]:
    warnings = []
    if not (entry.get("description") or "").strip():
        warnings.append("Descrizione del dataset non disponibile.")
    if not (entry.get("source") or "").strip():
        warnings.append(f"Nome della fonte non disponibile (source_id: {entry.get('source_id')}).")
    if not (entry.get("location") or {}).get("path"):
        warnings.append("Percorso del parquet clean non disponibile.")
    return warnings


def build_card(entry: dict, spec: dict, rows: list[dict]) -> dict:
    """Compone la scheda: metadati dal catalogo, fatti dal mart."""
    points = _points(rows, spec)
    return {
        "slug": entry["slug"],
        "url_slug": entry["url_slug"],
        "name": entry.get("name", ""),
        "description": entry.get("description", ""),
        "category": entry.get("category", ""),
        "stage": entry.get("stage", ""),
        "period": entry.get("period") or {},
        "source": entry.get("source", ""),
        "source_id": entry.get("source_id", ""),
        "registry_source": entry.get("registry_source", ""),
        "rows_clean": entry.get("clean_rows"),
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "mart": {"ref": spec["mart"], "table": spec["mart"].split("__", 1)[1]},
        "x": {"field": spec["x"], "label": spec["x_label"]},
        "y": {"label": spec["y_label"], "format": spec["y_format"]},
        "series": points,
        "kpis": _kpis(points, spec),
        "dictionary": entry.get("columns") or [],
        "links": _links(entry),
        "run": latest_run(entry["slug"]) or None,
        "warnings": _warnings(entry),
    }


def main(argv: list[str]) -> int:
    only = set()
    if "--only" in argv:
        index = argv.index("--only")
        only = {part.strip() for part in argv[index + 1].split(",") if part.strip()}

    catalog = {
        entry["url_slug"]: entry
        for entry in build_catalog(load_registry())["datasets"]
    }

    cards: dict[str, dict] = {}
    for url_slug, spec in SPECS.items():
        if only and url_slug not in only:
            continue
        entry = catalog.get(url_slug)
        if entry is None:
            print(f"! {url_slug}: assente dal catalogo, salto", file=sys.stderr)
            continue
        columns = {"x": spec["x"], "y": spec["y"]}
        if spec.get("y2"):
            columns["y2"] = spec["y2"]
        rows = mart_rows(spec["mart"], select=columns)
        cards[url_slug] = build_card(entry, spec, rows)
        print(f"✓ {url_slug}: {len(cards[url_slug]['series'])} punti da {spec['mart']}")

    out = ROOT / "src" / "data" / "cards.json"
    out.write_text(json.dumps(jsonable(cards), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ scrivete {len(cards)} schede in {out.relative_to(ROOT)} ({out.stat().st_size} byte)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

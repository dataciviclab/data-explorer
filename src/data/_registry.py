#!/usr/bin/env python3
"""Registry fusion via ACB → catalogo e temi explorer.

Helper condiviso dai data loader `catalog.json.py` e `themes.json.py`.

Consuma `topic_index.json` generato da agent-context-builder (ACB) come
single source of truth per i dataset di TUTTI i repo del Lab. ACB fonde
i registry.json di ogni repo, applica dedup e produce un indice aggregato.

Questo modulo aggiunge solo la logica editoriale-specifica di explorer:
- URL slug pubblici (override editoriali) — fonte unica: lab_connectors.registry.to_url_slug
- Temi da catalog/themes.json (config editoriale)
- Risoluzione pagine esistenti in src/dataset/

## Flusso dati

ACB (context branch)
  → topic_index.json (datasets{} raggruppati per source, con location, columns, registry_source)
  → _registry.load_registry() (flat list + signals_by_id)
  → build_catalog() / build_themes()
  → catalog.json.py / themes.json.py (Observable Framework data loaders)
"""
import json
import os
import re
import time

import requests
from lab_connectors.registry import to_url_slug

# ROOT: repo root, calcolato da __file__ per non dipendere dal cwd
# (questo file sta in src/data/, quindi 3 livelli sopra).
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
THEMES_CONFIG_PATH = os.path.join(ROOT, "catalog", "themes.json")
PAGES_DIR = os.path.join(ROOT, "src", "dataset")
CARDS_DIR = os.path.join(ROOT, "catalog", "cards")

_CARD_SLUG = re.compile(r"^dataset:\s*([A-Za-z0-9_\-]+)", re.MULTILINE)
_CARD_TITLE = re.compile(r"^title:\s*(.+)$", re.MULTILINE)
_CARD_DESCRIPTION = re.compile(r"^description:\s*(.+)$", re.MULTILINE)

# Local cache for topic_index.json — avoids N HTTP requests (one per loader).
_CACHE_DIR = os.path.join(ROOT, ".observable", "cache")
_CACHE_PATH = os.path.join(_CACHE_DIR, "topic_index.json")
_CACHE_TTL = 3600  # 1 hour

# ACB topic_index.json — single source of truth per i registry fusion.
ACB_TOPIC_INDEX_URL = (
    "https://raw.githubusercontent.com/dataciviclab/"
    "agent-context-builder/context/topic_index.json"
)

# Cache di processo: il registry viene caricato una volta per processo.
_REGISTRY_CACHE: dict | None = None


def fetch_json(url: str) -> dict:
    """Fetch JSON with local file cache to avoid N HTTP requests per build."""
    # Try local cache first
    if os.path.exists(_CACHE_PATH):
        try:
            age = time.time() - os.path.getmtime(_CACHE_PATH)
            if age < _CACHE_TTL:
                with open(_CACHE_PATH, encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass

    # Fetch from remote
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()

    # Write to cache (best-effort)
    try:
        os.makedirs(_CACHE_DIR, exist_ok=True)
        with open(_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass

    return data


def load_registry() -> dict:
    """Carica topic_index.json da ACB e produce un flat registry (cache di processo).

    Ritorna un dict con la forma attesa da build_catalog() e build_themes():
      - datasets[]: flat list con tutti i dataset, ognuno con
        slug, name, description, stage, period, source, source_id,
        category, tags, registry_source, location, columns, clean_rows
      - signals_by_id: dict slug → run info (per clean_rows in build_catalog)
      - updated_at: timestamp di generazione di topic_index.json
    """
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is not None:
        return _REGISTRY_CACHE

    data = fetch_json(ACB_TOPIC_INDEX_URL)

    # Flatten datasets: topic_index li raggruppa per source, noi serviamo flat
    flat_datasets: list[dict] = []
    for source, ds_list in data.get("datasets", {}).items():
        for ds in ds_list:
            flat_datasets.append(ds)

    # Build signals_by_id per clean_rows (run.output_rows.clean)
    signals_by_id: dict[str, dict] = {}
    for source, ds_list in data.get("datasets", {}).items():
        for ds in ds_list:
            slug = ds.get("slug", "")
            clean_rows = ds.get("clean_rows")
            if clean_rows is not None:
                signals_by_id[slug] = {"output_rows": {"clean": clean_rows}}

    _REGISTRY_CACHE = {
        "datasets": flat_datasets,
        "signals_by_id": signals_by_id,
        "analyses_by_dataset": data.get("analyses_by_dataset") or {},
        "updated_at": data.get("generated_at", ""),
    }
    return _REGISTRY_CACHE


def resolve_url_slug(di_slug: str) -> str:
    """Risolve lo slug DI (underscore) in URL slug pubblico.

    Fonte unica: ``lab_connectors.registry.to_url_slug`` (meccanico _ → -,
    con gli override editoriali). Alias mantenuto per i consumer interni.
    """
    return to_url_slug(di_slug)


def load_themes_config() -> list[dict]:
    """Legge la config editoriale dei temi (catalog/themes.json).

    Formato: {"schema_version": 1, "temi": [{slug, name, description,
    categories: [category registry ...]}]}
    """
    with open(THEMES_CONFIG_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    temi = raw.get("temi")
    if isinstance(temi, list):
        return temi
    # Backward compat: se il file è un array nudo
    if isinstance(raw, list):
        return raw
    raise ValueError(f"{THEMES_CONFIG_PATH}: manca la chiave 'temi'")


def has_explorer_page(url_slug: str) -> bool:
    """True se esiste la pagina explorer src/dataset/{url_slug}.md."""
    return os.path.exists(os.path.join(PAGES_DIR, f"{url_slug}.md"))


def local_cards() -> dict[str, dict[str, str]]:
    """Schede editoriali in ``catalog/cards/*.yml``: slug DI → {title, description}.

    Una scheda è una superficie pubblica esplicita: il dataset va contato come
    pubblicato anche se ACB (v7/v8) non lo sa, e il ``title`` editoriale è il
    nome pubblico (catalogo, temi, home), non lo slug del registry.
    """
    cards: dict[str, dict[str, str]] = {}
    if not os.path.isdir(CARDS_DIR):
        return cards
    for name in sorted(os.listdir(CARDS_DIR)):
        if not name.endswith((".yml", ".yaml")):
            continue
        try:
            with open(os.path.join(CARDS_DIR, name), encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            continue
        slug_match = _CARD_SLUG.search(text)
        if not slug_match:
            continue
        title_match = _CARD_TITLE.search(text)
        title = title_match.group(1).strip() if title_match else ""
        if len(title) >= 2 and title[0] == title[-1] and title[0] in ("'", '"'):
            title = title[1:-1]
        description_match = _CARD_DESCRIPTION.search(text)
        description = description_match.group(1).strip() if description_match else ""
        if len(description) >= 2 and description[0] == description[-1] and description[0] in ("'", '"'):
            description = description[1:-1]
        cards[slug_match.group(1)] = {"title": title, "description": description}
    return cards


def local_card_slugs() -> set[str]:
    """Slug DI con una scheda (compat: usa ``local_cards``)."""
    return set(local_cards())


def build_catalog(registry: dict | None = None) -> dict:
    """Costruisce il catalogo explorer (output di catalog.json.py).

    Ogni entry espone slug DI + url_slug DE (to_url_slug), stato,
    periodo, metadati editoriali (category, tags), il repo di provenienza
    (registry_source), il location GCS e le colonne (con role/semantic_type)
    per il rendering data-driven delle pagine.
    Consumato da index, temi page e generate-config (sidebar).
    """
    if registry is None:
        registry = load_registry()

    signals = registry.get("signals_by_id", {})
    analyses = registry.get("analyses_by_dataset") or {}
    cards = local_cards()
    theme_by_category = {
        category: (theme.get("slug", ""), theme.get("name", ""))
        for theme in load_themes_config()
        for category in theme.get("categories", [])
    }

    datasets = []
    for ds in registry.get("datasets", []):
        period = ds.get("period") or {}
        slug = ds["slug"]
        url_slug = resolve_url_slug(slug)
        run = signals.get(slug, {})
        clean_rows = run.get("output_rows", {}).get("clean")
        has_page = has_explorer_page(url_slug)
        has_card = slug in cards
        # Pubblicato se: c'è una scheda editoriale in DE (superficie esplicita),
        # oppure ACB v8 lo dice, oppure c'è una pagina (v7), oppure lo stage
        # storico (v1).
        if has_card:
            published = True
        elif "published" in ds:
            published = bool(ds["published"])
        else:
            published = (slug in analyses) or ds.get("stage") == "published"
        theme_slug, theme_name = theme_by_category.get(ds.get("category", ""), ("", ""))
        card = cards.get(slug) or {}
        datasets.append({
            "slug": slug,
            "url_slug": url_slug,
            "name": card.get("title") or ds.get("name", ""),
            "description": (card.get("description") or ds.get("description", ""))[:150],
            "stage": ds.get("stage", ""),
            "published": published,
            "has_page": has_page,
            "has_card": has_card,
            # Supersficie pubblica del dataset: pagina curata o scheda.
            "page_url": (
                f"/dataset/{url_slug}" if has_page else f"/schede/{url_slug}" if has_card else None
            ),
            "theme": theme_slug,
            "theme_name": theme_name,
            "years": f"{period.get('start', '?')}–{period.get('end', '?')}" if period else "?",
            "period": {"start": period.get("start"), "end": period.get("end")},
            "source": ds.get("source", ""),
            "source_id": ds.get("source_id", ""),
            "category": ds.get("category", ""),
            "tags": ds.get("tags", []),
            "registry_source": ds.get("registry_source", ""),
            "clean_rows": clean_rows,
            "mart_refs": ds.get("mart_refs", []),
            "location": ds.get("location", {}),
            "columns": [
                {
                    "name": c.get("name"),
                    "type": c.get("type"),
                    "role": c.get("role", ""),
                    "semantic_type": c.get("semantic_type", ""),
                    "description": c.get("description", ""),
                }
                for c in ds.get("columns", [])
            ],
        })
    published = sum(1 for d in datasets if d["published"])
    return {
        "updated_at": registry.get("updated_at", ""),
        "total": len(datasets),
        "published": published,
        "incubating": len(datasets) - published,
        "total_clean_rows": sum(d["clean_rows"] or 0 for d in datasets),
        "datasets": datasets,
    }


def build_themes(registry: dict | None = None, page_exists=None) -> list[dict]:
    """Deriva i temi dal registry usando la config editoriale.

    Un dataset entra in un tema se ha una **superficie pubblica** (pagina
    explorer o scheda `catalog/cards/`) E la sua `category` è mappata in
    catalog/themes.json. Lo stage registry è irrilevante: la superficie è
    l'intento editoriale di esposizione.

    I dataset senza pagina non entrano nei temi: finiscono in "Altri dataset"
    (sidebar) o semplicemente non vengono linkati dalle pagine tema.

    page_exists: callable url_slug → bool (default: has_explorer_page),
    iniettabile nei test.
    """
    if registry is None:
        registry = load_registry()
    if page_exists is None:
        page_exists = has_explorer_page
    cards = local_cards()

    # category → url_slug (dataset con pagina o scheda)
    by_category: dict[str, list[str]] = {}
    for ds in registry.get("datasets", []):
        category = ds.get("category")
        if not category:
            continue
        url_slug = resolve_url_slug(ds["slug"])
        if not (page_exists(url_slug) or ds["slug"] in cards):
            continue
        by_category.setdefault(category, []).append(url_slug)

    themes = []
    for theme in load_themes_config():
        datasets: list[str] = []
        seen: set[str] = set()
        for category in theme.get("categories", []):
            for url_slug in by_category.get(category, []):
                if url_slug not in seen:
                    seen.add(url_slug)
                    datasets.append(url_slug)
        themes.append({
            "slug": theme["slug"],
            "name": theme["name"],
            "icon": theme.get("icon", ""),
            "description": theme.get("description", ""),
            "datasets": datasets,
        })
    return themes


def theme_for_category(category: str) -> str | None:
    """Risolve la categoria registry → slug tema (o None se non mappata)."""
    for theme in load_themes_config():
        if category in theme.get("categories", []):
            return theme["slug"]
    return None

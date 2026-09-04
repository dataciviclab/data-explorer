#!/usr/bin/env python3
"""Registry fusion via ACB → catalogo e temi explorer.

Helper condiviso dai data loader `catalog.json.py` e `themes.json.py`.

Consuma `topic_index.json` generato da agent-context-builder (ACB) come
single source of truth per i dataset di TUTTI i repo del Lab. ACB fonde
i registry.json di ogni repo, applica dedup e produce un indice aggregato.

Questo modulo aggiunge solo la logica editoriale-specifica di explorer:
- URL_SLUG_OVERRIDES (slug URL pubblici che divergono dagli slug DI)
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

import requests

# ROOT: repo root, calcolato da __file__ per non dipendere dal cwd
# (questo file sta in src/data/, quindi 3 livelli sopra).
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
THEMES_CONFIG_PATH = os.path.join(ROOT, "catalog", "themes.json")
PAGES_DIR = os.path.join(ROOT, "src", "dataset")

# ACB topic_index.json — single source of truth per i registry fusion.
ACB_TOPIC_INDEX_URL = (
    "https://raw.githubusercontent.com/dataciviclab/"
    "agent-context-builder/context/topic_index.json"
)

# URL_SLUG_OVERRIDES: mapping eccezioni per slug URL pubblici.
#
# La regola di default converte meccanicamente lo slug DI (underscore)
# in URL slug (hyphen):  "aifa_spesa_consumo" → "aifa-spesa-consumo".
#
# Per i dataset ereditati dalla fase Evidence, gli slug URL sono stati
# scelti editorialmente e NON seguono lo slug DI. Ogni entry qui sotto
# documenta questa divergenza.
#
# Per i NUOVI dataset: se l'URL slug meccanico va bene, non serve aggiungere
# nulla qui. Se serve un nome URL diverso, aggiungi l'override con commento.
URL_SLUG_OVERRIDES = {
    "aifa_spesa_consumo": "spesa-farmaceutica",             # editoriale: nome tema
    "ispra_ru_base": "rifiuti-urbani",                      # editoriale: nome tema
    "civile_flussi": "flussi-giustizia-civile",             # editoriale: specifica tema
    "terna_capacita_rinnovabile": "capacita-rinnovabile",   # editoriale: nome tema
    "terna_electricity_by_source": "produzione-elettrica-fonti",  # editoriale: nome tema
    "camera_votazioni_sparql": "votazioni-camera",          # editoriale: nome tema
    "camera_deputati_legislature": "camera-deputati",       # editoriale: nome pagina
    "camera_interventi": "attivita-aula",                   # editoriale: pagina combinata
    "camera_voti": "voti-deputati",                         # editoriale: nome pagina
    "bdap_entrate_stato": "entrate-stato",                  # editoriale: nome tema
    "inps_pensioni_trimestrale": "pensioni-inps",           # editoriale: nome tema
    "ade_cinque_per_mille": "cinque-per-mille",             # editoriale: nome tema
    "istat_housing_crowding": "housing-crowding",           # editoriale: slug pagina ereditato
    "mit_incidentalita_mensile": "mit-incidentalita",       # editoriale: slug pagina ereditato
    "opencivitas_fsc_2025_rso": "opencivitas-fsc-2025",     # editoriale: slug pagina ereditato
    "popolazione_istat_comunale_2019_2025": "popolazione-istat",  # editoriale: slug pagina ereditato
}

# Cache di processo: il registry viene caricato una volta per processo.
_REGISTRY_CACHE: dict | None = None


def fetch_json(url: str) -> dict:
    """Fetch JSON remoto via requests."""
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json()


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
        "updated_at": data.get("generated_at", ""),
    }
    return _REGISTRY_CACHE


def resolve_url_slug(di_slug: str) -> str:
    """Risolve lo slug DI (underscore) in URL slug (hyphen).

    Default: sostituzione meccanica _ → -.
    Override: se presente in URL_SLUG_OVERRIDES.
    """
    return URL_SLUG_OVERRIDES.get(di_slug, di_slug.replace("_", "-"))


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


def build_catalog(registry: dict | None = None) -> dict:
    """Costruisce il catalogo explorer (output di catalog.json.py).

    Ogni entry espone slug DI + url_slug DE (URL_SLUG_OVERRIDES), stato,
    periodo, metadati editoriali (category, tags), il repo di provenienza
    (registry_source), il location GCS e le colonne (con role/semantic_type)
    per il rendering data-driven delle pagine.
    Consumato da index, temi page e generate-config (sidebar).
    """
    if registry is None:
        registry = load_registry()

    signals = registry.get("signals_by_id", {})

    datasets = []
    for ds in registry.get("datasets", []):
        period = ds.get("period") or {}
        slug = ds["slug"]
        url_slug = resolve_url_slug(slug)
        run = signals.get(slug, {})
        clean_rows = run.get("output_rows", {}).get("clean")
        datasets.append({
            "slug": slug,
            "url_slug": url_slug,
            "name": ds.get("name", ""),
            "description": ds.get("description", "")[:150],
            "stage": ds.get("stage", ""),
            "years": f"{period.get('start', '?')}–{period.get('end', '?')}" if period else "?",
            "period": {"start": period.get("start"), "end": period.get("end")},
            "source": ds.get("source", ""),
            "source_id": ds.get("source_id", ""),
            "category": ds.get("category", ""),
            "tags": ds.get("tags", []),
            "registry_source": ds.get("registry_source", ""),
            "clean_rows": clean_rows,
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
    return {
        "updated_at": registry.get("updated_at", ""),
        "total": len(datasets),
        "published": sum(1 for d in datasets if d["stage"] == "published"),
        "incubating": sum(1 for d in datasets if d["stage"] == "incubating"),
        "total_clean_rows": sum(d["clean_rows"] or 0 for d in datasets),
        "datasets": datasets,
    }


def build_themes(registry: dict | None = None, page_exists=None) -> list[dict]:
    """Deriva i temi dal registry usando la config editoriale.

    Un dataset entra in un tema se ha una pagina explorer (url_slug) E la
    sua `category` è mappata in catalog/themes.json. Lo stage registry è
    irrilevante: la presenza di una pagina è l'intento editoriale di
    esposizione (alcune pagine esistono per dataset ancora incubating).

    I dataset senza pagina non entrano nei temi: finiscono in "Altri dataset"
    (sidebar) o semplicemente non vengono linkati dalle pagine tema.

    page_exists: callable url_slug → bool (default: has_explorer_page),
    iniettabile nei test.
    """
    if registry is None:
        registry = load_registry()
    if page_exists is None:
        page_exists = has_explorer_page

    # category → url_slug (solo dataset con pagina explorer)
    by_category: dict[str, list[str]] = {}
    for ds in registry.get("datasets", []):
        category = ds.get("category")
        if not category:
            continue
        url_slug = resolve_url_slug(ds["slug"])
        if not page_exists(url_slug):
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

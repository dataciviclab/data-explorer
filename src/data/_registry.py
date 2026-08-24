#!/usr/bin/env python3
"""Registry multi-repo (fusion) → catalogo e temi explorer.

Helper condiviso dai data loader `catalog.json.py` e `themes.json.py`.

Legge i registry fusion di TUTTI i repo del Lab (ogni repo committa
`registry/registry.json`, fusion ADR), li fonde in un unico catalogo e
risolve gli URL slug editoriali (URL_SLUG_OVERRIDES) e i temi dal campo
`category` di ogni dataset usando la config editoriale `catalog/themes.json`
(single source of truth).

## Fusion e dedup

REGISTRY_REPOS è ordinato per priorità: in caso di slug duplicato tra repo
(es. migrazioni dataset-incubator → open-politica), vince il repo che compare
per primo. Ogni entry del catalogo porta `registry_source` (repo di provenienza).

Contratto registry (schema_version 1):
  datasets[]: slug, name, description, source, source_id, period,
              columns[] (name, type, role, semantic_type), location,
              stage, tags, category, mart_refs, run
"""
import json
import os

import requests

# Repo con registry fusion (priorità decrescente in caso di slug duplicato).
# dataset-incubator primo: è la fonte storica con stage published; gli altri
# repo (dominio) entrano con i loro slug unici. Se un slug duplicato diventa
# canonicale in un altro repo, sposta quel repo sopra in questa lista.
REGISTRY_REPOS = [
    "dataset-incubator",
    "open-politica",
    "open-conto-annuale",
    "eurostat",
    "dcl-bologna",
    "open-siope",
    "rna-aiuti-stato",
]

REGISTRY_URL_TEMPLATE = (
    "https://raw.githubusercontent.com/dataciviclab/"
    "{repo}/main/registry/registry.json"
)

# ROOT: repo root, calcolato da __file__ per non dipendere dal cwd
# (questo file sta in src/data/, quindi 3 livelli sopra).
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
THEMES_CONFIG_PATH = os.path.join(ROOT, "catalog", "themes.json")
PAGES_DIR = os.path.join(ROOT, "src", "dataset")

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

# Cache di processo: i registry vengono caricati una volta per processo.
_REGISTRY_CACHE: dict | None = None


def fetch_json(url: str) -> dict:
    """Fetch JSON remoto via requests."""
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json()


def _registry_url(repo: str) -> str:
    """URL raw del registry fusion di un repo."""
    return REGISTRY_URL_TEMPLATE.format(repo=repo)


def load_registry() -> dict:
    """Carica e fonde i registry di tutti i repo (cache di processo).

    Ritorna un dict con la stessa forma di un registry singolo (schema v1):
      - datasets[]: dedup per slug, con priorità = ordine REGISTRY_REPOS,
        ogni entry arricchita con `registry_source` (repo di provenienza)
      - updated_at: il più recente tra i repo
      - repos[]: lista dei repo letti
    """
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is None:
        _REGISTRY_CACHE = fuse_registries(REGISTRY_REPOS)
    return _REGISTRY_CACHE


def fuse_registries(repos: list[str] | None = None) -> dict:
    """Fonde i registry dei repo: dedup per slug, priorità = ordine lista.

    Il primo repo che contiene uno slug vince; alle entry vinte viene
    aggiunto `registry_source` (nome repo). I repo senza registry.json
    (non pubblicato o unreachable) vengono saltati senza errore.
    """
    repos = repos or REGISTRY_REPOS
    seen: set[str] = set()
    datasets: list[dict] = []
    updated_at: str | None = None

    for repo in repos:
        try:
            payload = fetch_json(_registry_url(repo))
        except Exception:
            # Repo senza registry o unreachable: lo saltiamo, il resto funziona.
            continue
        for ds in payload.get("datasets", []):
            slug = ds["slug"]
            if slug in seen:
                continue
            seen.add(slug)
            datasets.append({**ds, "registry_source": repo})
        repo_updated = payload.get("updated_at", "")
        if repo_updated and (updated_at is None or repo_updated > updated_at):
            updated_at = repo_updated

    return {
        "schema_version": 1,
        "updated_at": updated_at or "",
        "repos": repos,
        "datasets": datasets,
    }


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

    datasets = []
    for ds in registry.get("datasets", []):
        period = ds.get("period") or {}
        slug = ds["slug"]
        url_slug = resolve_url_slug(slug)
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

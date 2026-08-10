"""Test per _registry.py — registry dataset-incubator → catalogo e temi.

Contratto:
  - resolve_url_slug(): slug DI (underscore) → URL slug (hyphen), con override editoriali
  - build_themes(): temi dinamici da category registry; entrano i dataset
    con pagina explorer e categoria mappata (lo stage registry è irrilevante)
  - theme_for_category()/load_themes_config(): config editoriale catalog/themes.json
  - build_catalog(): output consumato da index/temi/sidebar
"""
import os

from src.data._registry import (
    THEMES_CONFIG_PATH,
    build_catalog,
    build_themes,
    load_themes_config,
    resolve_url_slug,
    theme_for_category,
)


def _registry_entry(slug, category, stage="published", name=None):
    return {
        "slug": slug,
        "name": name or slug,
        "category": category,
        "stage": stage,
        "period": {"start": 2020, "end": 2024},
        "source": "Fonte",
    }


class TestResolveUrlSlug:
    def test_default_mechanical(self):
        assert resolve_url_slug("aci_prime_iscrizioni_autovetture") == "aci-prime-iscrizioni-autovetture"

    def test_editorial_override(self):
        assert resolve_url_slug("ispra_ru_base") == "rifiuti-urbani"
        assert resolve_url_slug("ade_cinque_per_mille") == "cinque-per-mille"
        assert resolve_url_slug("mit_incidentalita_mensile") == "mit-incidentalita"


class TestThemesConfig:
    def test_config_exists_and_has_temi(self):
        assert os.path.exists(THEMES_CONFIG_PATH)
        temi = load_themes_config()
        assert len(temi) >= 6
        slugs = {t["slug"] for t in temi}
        assert {"territorio-ambiente", "sanita", "giustizia"} <= slugs

    def test_theme_for_category_mapped(self):
        assert theme_for_category("ambiente") == "territorio-ambiente"
        assert theme_for_category("sanita") == "sanita"

    def test_theme_for_category_unmapped(self):
        assert theme_for_category("normativa") is None
        assert theme_for_category("politica") is None


class TestBuildThemes:
    def test_page_e_mapped_category_indipendentemente_dallo_stage(self):
        registry = {"datasets": [
            _registry_entry("rifiuti_urbani", "ambiente"),         # override → rifiuti-urbani
            _registry_entry("capacita_rinnovabile", "energia"),    # → capacita-rinnovabile
            _registry_entry("incubante", "ambiente", stage="incubating"),  # pagina + cat mappata → incluso
            _registry_entry("senza_pagina", "ambiente"),           # senza pagina explorer → escluso
            _registry_entry("politico", "politica"),               # category non mappata → escluso
        ]}
        has_page = {"rifiuti-urbani", "capacita-rinnovabile", "incubante"}
        themes = build_themes(registry, page_exists=lambda s: s in has_page)
        ta = next(t for t in themes if t["slug"] == "territorio-ambiente")
        assert sorted(ta["datasets"]) == ["capacita-rinnovabile", "incubante", "rifiuti-urbani"]

    def test_tema_senza_risultati_resta_con_datasets_vuoti(self):
        registry = {"datasets": [_registry_entry("politico", "politica")]}
        themes = build_themes(registry, page_exists=lambda s: True)
        assert len(themes) == len(load_themes_config())
        assert all(isinstance(t["datasets"], list) for t in themes)


class TestBuildCatalog:
    def test_catalog_contract(self):
        registry = {"updated_at": "2026-08-08", "datasets": [
            _registry_entry("rifiuti_urbani", "ambiente"),
            _registry_entry("incubante", "ambiente", stage="incubating"),
        ]}
        cat = build_catalog(registry)
        assert cat["updated_at"] == "2026-08-08"
        assert cat["total"] == 2
        assert cat["published"] == 1
        assert cat["incubating"] == 1

        d = next(x for x in cat["datasets"] if x["slug"] == "rifiuti_urbani")
        assert d["url_slug"] == "rifiuti-urbani"
        assert d["category"] == "ambiente"
        assert d["stage"] == "published"
        assert d["source"]
        assert "–" in d["years"]

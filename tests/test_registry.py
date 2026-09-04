"""Test per _registry.py — catalogo e temi explorer.

Contratto:
  - load_registry(): carica topic_index.json da ACB, flat list + signals_by_id
  - resolve_url_slug(): slug DI (underscore) → URL slug (hyphen), con override editoriali
  - build_themes(): temi dinamici da category registry; entrano i dataset
    con pagina explorer e categoria mappata (lo stage registry è irrilevante)
  - theme_for_category()/load_themes_config(): config editoriale catalog/themes.json
  - build_catalog(): output consumato da index/temi/sidebar
"""
import os
from unittest.mock import patch

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


class TestLoadRegistry:
    def test_loads_from_acb_and_flattens(self):
        """load_registry() fetches topic_index.json from ACB and flattens datasets."""
        import src.data._registry as mod
        # Reset cache
        mod._REGISTRY_CACHE = None

        fake_topic_index = {
            "generated_at": "2026-09-04T10:00:00",
            "datasets": {
                "source-a": [
                    {"slug": "ds_a", "name": "DS A", "stage": "published",
                     "registry_source": "repo-a", "category": "ambiente",
                     "location": {"type": "gcs", "path": "gs://b/ds_a"}},
                ],
                "source-b": [
                    {"slug": "ds_b", "name": "DS B", "stage": "incubating",
                     "registry_source": "repo-b", "category": "sanita"},
                ],
            },
        }
        with patch.object(mod, "fetch_json", return_value=fake_topic_index):
            reg = mod.load_registry()

        assert len(reg["datasets"]) == 2
        slugs = {d["slug"] for d in reg["datasets"]}
        assert slugs == {"ds_a", "ds_b"}
        # registry_source preserved
        by_slug = {d["slug"]: d for d in reg["datasets"]}
        assert by_slug["ds_a"]["registry_source"] == "repo-a"
        assert by_slug["ds_b"]["registry_source"] == "repo-b"
        # clean_rows not in signals when absent
        assert "ds_a" not in reg["signals_by_id"]

    def test_cache_returns_same_object(self):
        """load_registry() caches per process."""
        import src.data._registry as mod
        mod._REGISTRY_CACHE = None

        fake = {"generated_at": "t", "datasets": {"s": [{"slug": "x"}]}}
        with patch.object(mod, "fetch_json", return_value=fake):
            r1 = mod.load_registry()
            r2 = mod.load_registry()
        assert r1 is r2


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
        assert theme_for_category("politica") == "politica"


class TestBuildThemes:
    def test_page_e_mapped_category_indipendentemente_dallo_stage(self):
        registry = {"datasets": [
            _registry_entry("rifiuti_urbani", "ambiente"),         # override → rifiuti-urbani
            _registry_entry("capacita_rinnovabile", "energia"),    # → capacita-rinnovabile
            _registry_entry("incubante", "ambiente", stage="incubating"),  # pagina + cat mappata → incluso
            _registry_entry("senza_pagina", "ambiente"),           # senza pagina explorer → escluso
            _registry_entry("politico", "politica"),               # category mappata ma senza pagina → escluso
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
            {**_registry_entry("rifiuti_urbani", "ambiente"), "registry_source": "repo-x",
             "location": {"type": "gcs", "path": "gs://b/r/2024/r_2024.parquet"}},
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
        assert d["registry_source"] == "repo-x"
        assert d["location"]["path"].startswith("gs://")

        d2 = next(x for x in cat["datasets"] if x["slug"] == "incubante")
        assert d2["registry_source"] == ""

    def test_catalog_exposes_columns(self):
        registry = {"updated_at": "2026-08-08", "datasets": [{
            **_registry_entry("ds_cols", "ambiente"),
            "columns": [
                {"name": "anno", "type": "INTEGER", "role": "dimension",
                 "semantic_type": "year", "description": "Anno"},
                {"name": "valore", "type": "DOUBLE", "role": "metric",
                 "semantic_type": "", "description": ""},
            ],
        }]}
        cat = build_catalog(registry)
        d = cat["datasets"][0]
        assert d["period"] == {"start": 2020, "end": 2024}
        assert d["columns"][0] == {
            "name": "anno", "type": "INTEGER", "role": "dimension",
            "semantic_type": "year", "description": "Anno",
        }
        assert d["columns"][1]["semantic_type"] == ""
        assert d["columns"][1]["description"] == ""

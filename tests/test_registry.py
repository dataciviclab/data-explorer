"""Test per _registry.py — registry multi-repo (fusion) → catalogo e temi.

Contratto:
  - fuse_registries(): merge dei registry repo, dedup per slug con priorità
    = ordine lista, entry arricchite con registry_source
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
    fuse_registries,
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


class TestFuseRegistries:
    def test_merges_and_tags_registry_source(self):
        reg_a = {"updated_at": "2026-08-01", "datasets": [
            _registry_entry("slug_a", "ambiente"),
        ]}
        reg_b = {"updated_at": "2026-08-10", "datasets": [
            _registry_entry("slug_b", "sanita"),
        ]}
        with patch("src.data._registry.fetch_json", side_effect=[reg_a, reg_b]):
            fused = fuse_registries(["repo-a", "repo-b"])

        assert len(fused["datasets"]) == 2
        assert {d["slug"] for d in fused["datasets"]} == {"slug_a", "slug_b"}
        assert fused["datasets"][0]["registry_source"] == "repo-a"
        assert fused["datasets"][1]["registry_source"] == "repo-b"

    def test_dedup_first_repo_wins(self):
        reg_a = {"updated_at": "2026-08-01", "datasets": [
            _registry_entry("dupl", "ambiente", stage="published"),
        ]}
        reg_b = {"updated_at": "2026-08-05", "datasets": [
            _registry_entry("dupl", "ambiente", stage="incubating"),
            _registry_entry("unico_b", "sanita"),
        ]}

        with patch("src.data._registry.fetch_json", side_effect=[reg_a, reg_b]):
            fused = fuse_registries(["repo-a", "repo-b"])

        assert len(fused["datasets"]) == 2
        by_slug = {d["slug"]: d for d in fused["datasets"]}
        assert by_slug["dupl"]["stage"] == "published"      # primo repo vince
        assert by_slug["dupl"]["registry_source"] == "repo-a"
        assert by_slug["unico_b"]["registry_source"] == "repo-b"

    def test_updated_at_most_recent(self):
        reg_a = {"updated_at": "2026-08-01", "datasets": []}
        reg_b = {"updated_at": "2026-08-15", "datasets": []}
        with patch("src.data._registry.fetch_json", side_effect=[reg_a, reg_b]):
            fused = fuse_registries(["repo-a", "repo-b"])
        assert fused["updated_at"] == "2026-08-15"

    def test_skips_unreachable_repo(self):
        reg_a = {"updated_at": "2026-08-01", "datasets": [
            _registry_entry("slug_a", "ambiente"),
        ]}
        with patch("src.data._registry.fetch_json", side_effect=[reg_a, Exception("boom")]):
            fused = fuse_registries(["repo-a", "repo-b"])
        assert len(fused["datasets"]) == 1
        assert fused["datasets"][0]["registry_source"] == "repo-a"


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

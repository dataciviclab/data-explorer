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

    def test_description_dalla_pagina_se_acb_non_la_ha(self, tmp_path, monkeypatch):
        """ACB non pubblica `description`: si usa quella del frontmatter di pagina."""
        import src.data._registry as mod

        monkeypatch.setattr(mod, "PAGES_DIR", str(tmp_path))
        monkeypatch.setattr(mod, "_PAGE_DESCRIPTIONS", {})
        (tmp_path / "demo.md").write_text(
            '---\ntitle: Demo\ndescription: "Testo editoriale della pagina"\n---\n',
            encoding="utf-8",
        )
        entry = _registry_entry("demo", "ambiente")
        entry.pop("description", None)
        cat = build_catalog({"updated_at": "t", "datasets": [entry]})
        assert cat["datasets"][0]["description"] == "Testo editoriale della pagina"

    def test_description_assente_ovunque_resta_vuota(self, tmp_path, monkeypatch):
        import src.data._registry as mod

        monkeypatch.setattr(mod, "PAGES_DIR", str(tmp_path))
        monkeypatch.setattr(mod, "_PAGE_DESCRIPTIONS", {})
        entry = _registry_entry("nessuna_pagina", "ambiente")
        entry.pop("description", None)
        cat = build_catalog({"updated_at": "t", "datasets": [entry]})
        assert cat["datasets"][0]["description"] == ""

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


class TestPublishedV2:
    """v2: `published` deriva dalle pagine; lo `stage` storico resta fallback."""

    def test_da_analyses_by_dataset(self):
        registry = {
            "datasets": [_registry_entry("anac", "appalti", stage="incubating")],
            "analyses_by_dataset": {"anac": ["anac-bandi-gara"]},
        }
        cat = build_catalog(registry)
        assert cat["published"] == 1
        assert cat["datasets"][0]["published"] is True

    def test_campo_published_v8_prevale(self):
        registry = {
            "datasets": [
                {**_registry_entry("x", "appalti", stage="published"), "published": False},
            ]
        }
        cat = build_catalog(registry)
        assert cat["published"] == 0
        assert cat["datasets"][0]["published"] is False


class TestSchedaPubblicata:
    """Una scheda in catalog/cards/*.yml è una superficie pubblica esplicita."""

    def test_scheda_locale_marca_published(self, monkeypatch):
        import src.data._registry as mod

        monkeypatch.setattr(mod, "local_cards", lambda: {"x": {"title": "Titolo editoriale", "description": ""}})
        registry = {"datasets": [_registry_entry("x", "appalti", stage="incubating")]}
        cat = mod.build_catalog(registry)
        assert cat["datasets"][0]["published"] is True
        assert cat["published"] == 1

    def test_campo_v8_false_senza_scheda(self, monkeypatch):
        import src.data._registry as mod

        monkeypatch.setattr(mod, "local_cards", lambda: {})
        registry = {
            "datasets": [{**_registry_entry("x", "appalti", stage="published"), "published": False}]
        }
        cat = mod.build_catalog(registry)
        assert cat["datasets"][0]["published"] is False


class TestSuperficiPubbliche:
    """Pagina curata e scheda sono due superfici; il link deve seguire quella."""

    def test_page_url_e_superfici(self, monkeypatch):
        import src.data._registry as mod

        monkeypatch.setattr(mod, "has_explorer_page", lambda url: url == "pagina")
        monkeypatch.setattr(mod, "local_cards", lambda: {"scheda": {"title": "Scheda editoriale", "description": "Descrizione scheda"}})
        registry = {
            "datasets": [
                _registry_entry("pagina", "appalti"),
                _registry_entry("scheda", "appalti", stage="incubating"),
                _registry_entry("nessuna", "appalti", stage="incubating"),
            ]
        }
        cat = mod.build_catalog(registry)
        by_slug = {d["url_slug"]: d for d in cat["datasets"]}
        assert by_slug["pagina"]["page_url"] == "/dataset/pagina"
        assert by_slug["scheda"]["page_url"] == "/schede/scheda"
        assert by_slug["nessuna"]["page_url"] is None
        assert by_slug["scheda"]["published"] is True
        assert by_slug["scheda"]["name"] == "Scheda editoriale"
        assert by_slug["scheda"]["description"] == "Descrizione scheda"

    def test_tema_include_dataset_con_scheda(self, monkeypatch):
        import src.data._registry as mod

        monkeypatch.setattr(mod, "local_cards", lambda: {"senza_pagina": {"title": "", "description": ""}})
        registry = {"datasets": [_registry_entry("senza_pagina", "ambiente")]}
        themes = mod.build_themes(registry, page_exists=lambda url: False)
        ta = next(t for t in themes if t["slug"] == "territorio-ambiente")
        assert "senza-pagina" in ta["datasets"]

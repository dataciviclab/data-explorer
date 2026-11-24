"""Test per scripts/build_cards.py — contratto delle schede editoriali.

Copre senza rete: validazione dei file `catalog/cards/*.yml`, merge
catalogo/override, scelta dei punti e dei KPI. Le query ai mart sono
verificate dal dry-run/CI, non qui.
"""

import textwrap

import pytest
from scripts import build_cards as bc


@pytest.fixture
def entry():
    return {
        "slug": "anac_bandi_gara",
        "url_slug": "anac-bandi-gara",
        "name": "Anac Bandi Gara",
        "description": "descrizione dal catalogo",
        "source": "",
        "source_id": "anac",
        "category": "appalti",
        "stage": "incubating",
        "period": {"start": 2016, "end": 2025},
        "registry_source": "appalti-pubblici",
        "clean_rows": 123,
        "mart_refs": ["anac_bandi_gara__mart_annuale"],
        "location": {"path": "gs://bucket/anac/x.parquet"},
        "columns": [{"name": "anno", "type": "INTEGER"}],
    }


@pytest.fixture
def catalog(entry):
    return {entry["slug"]: entry}


@pytest.fixture(autouse=True)
def cards_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(bc, "CARDS_DIR", tmp_path)
    return tmp_path


def _write(cards_dir, name, text):
    (cards_dir / f"{name}.yml").write_text(textwrap.dedent(text), encoding="utf-8")


class TestLoadSpecs:
    def test_minimo_valido(self, cards_dir, catalog):
        _write(cards_dir, "anac-bandi-gara", "dataset: anac_bandi_gara\n")
        specs, errors = bc.load_specs(catalog)
        assert errors == []
        assert specs["anac_bandi_gara"]["dataset"] == "anac_bandi_gara"

    def test_dataset_sconosciuto(self, cards_dir, catalog):
        _write(cards_dir, "x", "dataset: non_esiste\n")
        _, errors = bc.load_specs(catalog)
        assert any("assente dal catalogo" in e for e in errors)

    def test_campo_del_catalogo_vietato(self, cards_dir, catalog):
        _write(cards_dir, "anac-bandi-gara", "dataset: anac_bandi_gara\nperiod: 2020\n")
        _, errors = bc.load_specs(catalog)
        assert any("appartengono al catalogo" in e for e in errors)

    def test_campo_non_ammesso(self, cards_dir, catalog):
        _write(cards_dir, "anac-bandi-gara", "dataset: anac_bandi_gara\ntitolo: typo\n")
        _, errors = bc.load_specs(catalog)
        assert any("non ammessi" in e for e in errors)

    def test_mart_fuori_dai_refs(self, cards_dir, catalog):
        _write(
            cards_dir,
            "anac-bandi-gara",
            """
            dataset: anac_bandi_gara
            view:
              mart: altro__mart
              x: anno
              y: n
            """,
        )
        _, errors = bc.load_specs(catalog)
        assert any("non tra i mart_refs" in e for e in errors)

    def test_nome_file_deve_essere_url_slug(self, cards_dir, catalog):
        _write(cards_dir, "sbagliato", "dataset: anac_bandi_gara\n")
        _, errors = bc.load_specs(catalog)
        assert any("nome file" in e for e in errors)

    def test_dataset_duplicato(self, cards_dir, catalog):
        _write(cards_dir, "anac-bandi-gara", "dataset: anac_bandi_gara\n")
        _write(cards_dir, "duplicato", "dataset: anac_bandi_gara\n")
        _, errors = bc.load_specs(catalog)
        assert any("già dichiarato" in e for e in errors)

    def test_view_incompleta(self, cards_dir, catalog):
        _write(
            cards_dir,
            "anac-bandi-gara",
            "dataset: anac_bandi_gara\nview:\n  mart: anac_bandi_gara__mart_annuale\n",
        )
        _, errors = bc.load_specs(catalog)
        assert any("view manca" in e for e in errors)


class TestBuildCard:
    def test_override_editoriali_vincono(self, entry, monkeypatch):
        monkeypatch.setattr(bc, "latest_run", lambda slug: {})
        spec = {
            "dataset": entry["slug"],
            "title": "Titolo editoriale",
            "description": "descrizione editoriale",
            "source": "Fonte leggibile",
            "license": "CC-BY",
        }
        card = bc.build_card(entry, spec, [])
        assert card["name"] == "Titolo editoriale"
        assert card["description"] == "descrizione editoriale"
        assert card["source"] == "Fonte leggibile"
        assert card["license"] == "CC-BY"
        assert card["rows_clean"] == 123  # dal catalogo

    def test_default_dal_catalogo(self, entry, monkeypatch):
        monkeypatch.setattr(bc, "latest_run", lambda slug: {})
        card = bc.build_card(entry, {"dataset": entry["slug"]}, [])
        assert card["name"] == "Anac Bandi Gara"
        assert card["description"] == "descrizione dal catalogo"

    def test_senza_vista_niente_serie(self, entry, monkeypatch):
        monkeypatch.setattr(bc, "latest_run", lambda slug: {})
        card = bc.build_card(entry, {"dataset": entry["slug"]}, [])
        assert card["series"] == []
        assert card["kpis"] == []
        assert any("Vista base non dichiarata" in w for w in card["warnings"])

    def test_vista_completa(self, entry, monkeypatch):
        monkeypatch.setattr(bc, "latest_run", lambda slug: {})
        monkeypatch.setattr(bc, "last_complete_year", lambda: 2025)
        spec = {
            "dataset": entry["slug"],
            "view": {
                "mart": "anac_bandi_gara__mart_annuale",
                "x": "anno",
                "y": "n_lotti",
                "y_label": "Lotti",
                "y_format": "num",
            },
        }
        rows = [
            {"x": 2024, "y": 10},
            {"x": 2025, "y": 20},
            {"x": 2026, "y": 999},  # anno in corso: escluso
        ]
        card = bc.build_card(entry, spec, rows)
        assert [p["x"] for p in card["series"]] == [2024, 2025]
        assert card["kpis"][0] == {"label": "Lotti", "value": 20, "format": "num"}
        assert card["kpis"][1]["value"] == 100.0


class TestPoints:
    def test_filtra_anno_corrente_e_dedup(self):
        rows = [{"x": 2024, "y": 1}, {"x": 2025, "y": 2}, {"x": 2025, "y": 3}]
        assert bc._points(rows, until=2025, has_y2=False) == [
            {"x": 2024, "y": 1},
            {"x": 2025, "y": 3},
        ]

    def test_scarta_righe_senza_misura(self):
        rows = [{"x": 2024, "y": None}, {"x": 2025, "y": 2}]
        assert bc._points(rows, until=2025, has_y2=False) == [{"x": 2025, "y": 2}]

    def test_y2_inclusa_solo_se_presente(self):
        rows = [{"x": 2025, "y": 2, "y2": 9}]
        assert bc._points(rows, until=2025, has_y2=True) == [{"x": 2025, "y": 2, "y2": 9}]

"""Test per scripts/build_cards.py — contratto delle schede editoriali.

Copre senza rete: validazione dei file `catalog/cards/*.yml`, merge
catalogo/override, blocchi (kpi/series/ranking). Le query ai mart sono
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
        "mart_refs": ["anac_bandi_gara__mart_annuale", "anac_bandi_gara__mart_top_stazioni"],
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


def _fetch(data):
    def fetch(mart, columns):
        return data.get(mart, [])

    return fetch


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

    def test_view_e_blocks_insieme(self, cards_dir, catalog):
        _write(
            cards_dir,
            "anac-bandi-gara",
            """
            dataset: anac_bandi_gara
            view:
              mart: anac_bandi_gara__mart_annuale
              x: anno
              y: n_lotti
            blocks:
              - type: series
                mart: anac_bandi_gara__mart_annuale
                x: anno
                y: n_lotti
            """,
        )
        _, errors = bc.load_specs(catalog)
        assert any("usa 'blocks' oppure 'view'" in e for e in errors)

    def test_blocco_sconosciuto(self, cards_dir, catalog):
        _write(
            cards_dir,
            "anac-bandi-gara",
            """
            dataset: anac_bandi_gara
            blocks:
              - type: mappa
                mart: anac_bandi_gara__mart_annuale
            """,
        )
        _, errors = bc.load_specs(catalog)
        assert any("tipo blocco non supportato" in e for e in errors)

    def test_blocco_incompleto(self, cards_dir, catalog):
        _write(
            cards_dir,
            "anac-bandi-gara",
            """
            dataset: anac_bandi_gara
            blocks:
              - type: ranking
                mart: anac_bandi_gara__mart_top_stazioni
            """,
        )
        _, errors = bc.load_specs(catalog)
        assert any("blocco ranking manca" in e for e in errors)

    def test_kpi_senza_measures(self, cards_dir, catalog):
        _write(
            cards_dir,
            "anac-bandi-gara",
            """
            dataset: anac_bandi_gara
            blocks:
              - type: kpi
                measures: []
            """,
        )
        _, errors = bc.load_specs(catalog)
        assert any("richiede 'measures'" in e for e in errors)


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
        card = bc.build_card(entry, spec, _fetch({}))
        assert card["name"] == "Titolo editoriale"
        assert card["description"] == "descrizione editoriale"
        assert card["source"] == "Fonte leggibile"
        assert card["license"] == "CC-BY"
        assert card["rows_clean"] == 123  # dal catalogo

    def test_default_dal_catalogo(self, entry, monkeypatch):
        monkeypatch.setattr(bc, "latest_run", lambda slug: {})
        card = bc.build_card(entry, {"dataset": entry["slug"]}, _fetch({}))
        assert card["name"] == "Anac Bandi Gara"
        assert card["description"] == "descrizione dal catalogo"

    def test_senza_blocchi(self, entry, monkeypatch):
        monkeypatch.setattr(bc, "latest_run", lambda slug: {})
        card = bc.build_card(entry, {"dataset": entry["slug"]}, _fetch({}))
        assert card["blocks"] == []
        assert any("Nessun blocco dichiarato" in w for w in card["warnings"])

    def test_vista_legacy_diventa_kpi_e_series(self, entry, monkeypatch):
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
                "y2": "importo_totale",
            },
        }
        rows = {"anac_bandi_gara__mart_annuale": [{"x": 2024, "y": 10}, {"x": 2025, "y": 20}]}
        card = bc.build_card(entry, spec, _fetch(rows))
        assert [block["type"] for block in card["blocks"]] == ["kpi", "series"]
        kpi = card["blocks"][0]
        assert kpi["items"][0] == {"label": "Lotti", "value": 20, "format": "num"}
        assert kpi["items"][1]["value"] == 100.0
        assert [p["x"] for p in card["blocks"][1]["data"]] == [2024, 2025]

    def test_blocchi_espliciti(self, entry, monkeypatch):
        monkeypatch.setattr(bc, "latest_run", lambda slug: {})
        monkeypatch.setattr(bc, "last_complete_year", lambda: 2025)
        spec = {
            "dataset": entry["slug"],
            "blocks": [
                {
                    "type": "series",
                    "mart": "anac_bandi_gara__mart_annuale",
                    "x": "anno",
                    "y": "n_lotti",
                    "title": "Serie",
                },
                {
                    "type": "ranking",
                    "mart": "anac_bandi_gara__mart_top_stazioni",
                    "x": "anno",
                    "dimension": "denominazione",
                    "measure": "importo",
                    "top": 2,
                    "title": "Top",
                },
            ],
        }
        rows = {
            "anac_bandi_gara__mart_annuale": [{"x": 2024, "y": 1}, {"x": 2025, "y": 2}],
            "anac_bandi_gara__mart_top_stazioni": [
                {"x": 2024, "label": "vecchia", "value": 99},
                {"x": 2025, "label": "a", "value": 10},
                {"x": 2025, "label": "b", "value": 30},
                {"x": 2025, "label": "c", "value": 20},
            ],
        }
        card = bc.build_card(entry, spec, _fetch(rows))
        ranking = card["blocks"][1]
        assert ranking["year"] == 2025
        assert [row["label"] for row in ranking["data"]] == ["b", "c"]
        assert card["marts"] == [
            "anac_bandi_gara__mart_annuale",
            "anac_bandi_gara__mart_top_stazioni",
        ]


class TestPoints:
    def test_filtra_anno_corrente_e_dedup(self):
        rows = [{"x": 2024, "y": 1}, {"x": 2025, "y": 2}, {"x": 2025, "y": 3}]
        assert bc._points(rows, until=2025) == [
            {"x": 2024, "y": 1},
            {"x": 2025, "y": 3},
        ]

    def test_scarta_righe_senza_misura(self):
        rows = [{"x": 2024, "y": None}, {"x": 2025, "y": 2}]
        assert bc._points(rows, until=2025) == [{"x": 2025, "y": 2}]


class TestComposition:
    def test_aggrega_per_anno_e_gruppo(self, entry, monkeypatch):
        monkeypatch.setattr(bc, "latest_run", lambda slug: {})
        monkeypatch.setattr(bc, "last_complete_year", lambda: 2025)
        spec = {
            "dataset": entry["slug"],
            "blocks": [
                {
                    "type": "composition",
                    "mart": "anac_bandi_gara__mart_annuale",
                    "x": "anno",
                    "y": "valore",
                    "by": "gruppo",
                }
            ],
        }
        rows = {
            "anac_bandi_gara__mart_annuale": [
                {"x": 2024, "group": "a", "y": 1},
                {"x": 2024, "group": "a", "y": 2},
                {"x": 2025, "group": "b", "y": 4},
                {"x": 2026, "group": "c", "y": 99},
            ]
        }
        card = bc.build_card(entry, spec, _fetch(rows))
        block = card["blocks"][0]
        assert block["normalize"] is True
        assert block["groups"] == ["a", "b"]
        assert block["data"] == [
            {"x": 2024, "group": "a", "y": 3},
            {"x": 2025, "group": "b", "y": 4},
        ]


class TestMap:
    def test_ultimo_anno_e_somma_per_regione(self, entry, monkeypatch):
        monkeypatch.setattr(bc, "latest_run", lambda slug: {})
        monkeypatch.setattr(bc, "last_complete_year", lambda: 2025)
        spec = {
            "dataset": entry["slug"],
            "blocks": [
                {
                    "type": "map",
                    "mart": "anac_bandi_gara__mart_annuale",
                    "x": "anno",
                    "dimension": "regione",
                    "measure": "valore",
                }
            ],
        }
        rows = {
            "anac_bandi_gara__mart_annuale": [
                {"x": 2024, "region": "Lazio", "value": 99},
                {"x": 2025, "region": "Lazio", "value": 1},
                {"x": 2025, "region": "Lazio", "value": 2},
                {"x": 2025, "region": "Lombardia", "value": 3},
                {"x": 2026, "region": "Sicilia", "value": 100},
            ]
        }
        block = bc.build_card(entry, spec, _fetch(rows))["blocks"][0]
        assert block["year"] == 2025
        assert block["data"] == [
            {"region": "Lazio", "value": 3},
            {"region": "Lombardia", "value": 3},
        ]


class TestWhere:
    def test_filtra_le_righe(self, entry, monkeypatch):
        monkeypatch.setattr(bc, "latest_run", lambda slug: {})
        monkeypatch.setattr(bc, "last_complete_year", lambda: 2025)
        spec = {
            "dataset": entry["slug"],
            "blocks": [
                {
                    "type": "series",
                    "mart": "anac_bandi_gara__mart_annuale",
                    "x": "anno",
                    "y": "valore",
                    "where": {"livello": "nazionale"},
                }
            ],
        }
        rows = {
            "anac_bandi_gara__mart_annuale": [
                {"x": 2024, "y": 10, "livello": "nazionale"},
                {"x": 2025, "y": 20, "livello": "nazionale"},
                {"x": 2025, "y": 999, "livello": "provincia"},
            ]
        }
        block = bc.build_card(entry, spec, _fetch(rows))["blocks"][0]
        assert block["data"] == [{"x": 2024, "y": 10}, {"x": 2025, "y": 20}]

    def test_where_non_mappa(self, cards_dir, catalog):
        _write(
            cards_dir,
            "anac-bandi-gara",
            """
            dataset: anac_bandi_gara
            blocks:
              - type: series
                mart: anac_bandi_gara__mart_annuale
                x: anno
                y: n_lotti
                where: [livello, nazionale]
            """,
        )
        _, errors = bc.load_specs(catalog)
        assert any("'where' deve essere una mappa" in e for e in errors)

    def test_where_valore_non_scalare(self, cards_dir, catalog):
        _write(
            cards_dir,
            "anac-bandi-gara",
            """
            dataset: anac_bandi_gara
            blocks:
              - type: series
                mart: anac_bandi_gara__mart_annuale
                x: anno
                y: n_lotti
                where: {livello: [nazionale]}
            """,
        )
        _, errors = bc.load_specs(catalog)
        assert any("deve essere uno scalare" in e for e in errors)

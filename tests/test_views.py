"""Test per _views.py — contratto dati dei loader Explorer.

Prova del fuoco: se questi contratti si rompono, le pagine che leggono i mart
(ANAC in primis) pubblicano numeri sbagliati o vuoti senza errore di build.

Coperti senza rete: parsing dei mart_ref, perimetro anni, proiezione colonne,
aggregazioni, serializzazione JSON. Le funzioni che parlano con GCS/GitHub
(mart_rows, available_years) sono verificate dal build CI, non qui.
"""

from datetime import date
from decimal import Decimal

import pytest
from src.data._views import (
    group_rows,
    jsonable,
    last_complete_year,
    parse_mart_ref,
    project,
    select_years,
    years_in,
)


class TestParseMartRef:
    def test_valido(self):
        assert parse_mart_ref("anac_bandi_gara__mart_annuale") == (
            "anac_bandi_gara",
            "mart_annuale",
        )

    @pytest.mark.parametrize("ref", ["senza_separatore", "solo__", "__table", ""])
    def test_non_valido(self, ref):
        with pytest.raises(ValueError, match="mart_ref non valido"):
            parse_mart_ref(ref)


class TestYearsIn:
    def test_anni_dal_path(self):
        urls = [
            "https://storage.googleapis.com/b/slug/2024/mart.parquet",
            "https://storage.googleapis.com/b/slug/2023/mart.parquet",
            "https://storage.googleapis.com/b/slug/2024/mart.parquet",
        ]
        assert years_in(urls) == [2023, 2024]

    def test_path_flat_senza_anno(self):
        assert years_in(["https://storage.googleapis.com/b/slug/mart.parquet"]) == []


class TestSelectYears:
    def test_since_until(self):
        assert select_years([2018, 2019, 2020, 2021], since=2019, until=2020) == [2019, 2020]

    def test_last_complete(self):
        # today iniettato: l'anno in corso (2026) è escluso
        assert select_years(
            [2024, 2025, 2026], until="last_complete", today=date(2026, 11, 24)
        ) == [2024, 2025]

    def test_last_complete_year(self):
        assert last_complete_year(date(2026, 1, 1)) == 2025

    def test_senza_filtri_tiene_tutto(self):
        assert select_years([2019, 2020]) == [2019, 2020]

    def test_perimetro_vuoto_e_errore(self):
        with pytest.raises(RuntimeError, match="nessun anno nel perimetro"):
            select_years([2019, 2020], since=2021)

    def test_until_non_valido(self):
        with pytest.raises(ValueError, match="'until' non valido"):
            select_years([2020], until="boh")


class TestProject:
    def test_rinomina_e_sottrae(self):
        rows = [{"anno": 2020, "n_lotti": 3, "altro": "x"}]
        assert project(rows, {"anno": "anno", "lotti": "n_lotti"}) == [
            {"anno": 2020, "lotti": 3}
        ]

    def test_senza_select_copia(self):
        rows = [{"anno": 2020}]
        out = project(rows, None)
        assert out == rows and out[0] is not rows[0]

    def test_colonna_mancante_e_errore(self):
        with pytest.raises(RuntimeError, match="assenti nel mart"):
            project([{"anno": 2020}], {"importo": "importo_totale"})

    def test_righe_vuote(self):
        assert project([], {"anno": "anno"}) == []


class TestGroupRows:
    def test_sum(self):
        rows = [
            {"anno": 2020, "tipo": "a", "n": 2, "importo": 10.0},
            {"anno": 2020, "tipo": "a", "n": 3, "importo": 5.0},
            {"anno": 2020, "tipo": "b", "n": 1, "importo": 7.0},
        ]
        out = group_rows(rows, by=["anno", "tipo"], metrics={"n": "sum", "importo": "sum"})
        assert {(r["tipo"], r["n"], r["importo"]) for r in out} == {
            ("a", 5, 15.0),
            ("b", 1, 7.0),
        }

    def test_metric_con_colonna_diversa(self):
        rows = [{"anno": 2020, "importo_totale": 4.0}]
        out = group_rows(rows, by=["anno"], metrics={"importo": ("importo_totale", "sum")})
        assert out == [{"anno": 2020, "importo": 4.0}]

    def test_chiave_nulla_scartata(self):
        rows = [{"anno": 2020, "tipo": None, "n": 1}, {"anno": 2020, "tipo": "a", "n": 2}]
        out = group_rows(rows, by=["anno", "tipo"], metrics={"n": "sum"})
        assert out == [{"anno": 2020, "tipo": "a", "n": 2}]

    def test_valore_nullo_ignorato_nel_sum(self):
        rows = [{"anno": 2020, "n": 2}, {"anno": 2020, "n": None}]
        out = group_rows(rows, by=["anno"], metrics={"n": "sum"})
        assert out[0]["n"] == 2

    def test_count_conta_le_righe(self):
        rows = [{"anno": 2020}, {"anno": 2020}, {"anno": 2021}]
        out = group_rows(rows, by=["anno"], metrics={"n": "count"})
        assert out == [{"anno": 2020, "n": 2}, {"anno": 2021, "n": 1}]

    def test_min_max(self):
        rows = [{"k": "a", "v": 3}, {"k": "a", "v": 1}, {"k": "a", "v": 2}]
        out = group_rows(rows, by=["k"], metrics={"vmin": ("v", "min"), "vmax": ("v", "max")})
        assert out == [{"k": "a", "vmin": 1, "vmax": 3}]

    def test_sort(self):
        rows = [{"k": "b", "v": 1}, {"k": "a", "v": 2}]
        out = group_rows(rows, by=["k"], metrics={"v": "sum"}, sort_by="k")
        assert [r["k"] for r in out] == ["a", "b"]

    def test_aggregazione_non_supportata(self):
        with pytest.raises(ValueError, match="aggregazione non supportata"):
            group_rows([{"k": "a", "v": 1}], by=["k"], metrics={"v": "median"})


class TestJsonable:
    def test_nan_diventa_null(self):
        assert jsonable({"x": float("nan")}) == {"x": None}

    def test_decimal_diventa_float(self):
        assert jsonable({"x": Decimal("1.5")}) == {"x": 1.5}

    def test_data_iso(self):
        assert jsonable({"x": date(2024, 1, 2)}) == {"x": "2024-01-02"}

    def test_strutture_annidate(self):
        assert jsonable([{"a": [1, None]}]) == [{"a": [1, None]}]

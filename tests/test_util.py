"""
Test per _util.py — data loader condiviso per Observable Framework.

Contratto:
  - _parquet_exists(): verifica esistenza del parquet su GCS da location.path
    (HEAD per file singolo, listing+match anno per glob)
  - load_dataset(): produce JSON valido su stdout con aggregazioni corrette,
    salta anni senza parquet, gestisce where clause

Prova del fuoco: se cancello questi test, un refactor di _util.py
può rompere tutti i data loader senza preavviso.
"""
import io
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from lab_connectors.gcs.paths import CLEAN_BUCKET

# ── _parquet_exists ──────────────────────────────────────────────────────────


class TestParquetExists:
    """Contratto: HEAD sul file (canonico o location); glob derivato dal registry."""

    def test_canonical_fallback_uses_head(self):
        with patch("src.data._util.object_exists", return_value=True) as mock_exists:
            from src.data._util import _parquet_exists

            assert _parquet_exists("test-slug", 2023) is True
        mock_exists.assert_called_once_with(
            CLEAN_BUCKET, "test-slug/2023/test-slug_2023_clean.parquet"
        )

    def test_canonical_missing(self):
        with patch("src.data._util.object_exists", return_value=False):
            from src.data._util import _parquet_exists

            assert _parquet_exists("test-slug", 2023) is False

    def test_single_file_location_head_on_concrete_path(self):
        loc = {
            "path": f"gs://{CLEAN_BUCKET}/siope/siope_x/2026/siope_x_2026_clean.parquet"
        }
        with patch("src.data._util.object_exists", return_value=True) as mock_exists:
            from src.data._util import _parquet_exists

            assert _parquet_exists("siope_x", 2026, loc) is True
        mock_exists.assert_called_once_with(
            CLEAN_BUCKET, "siope/siope_x/2026/siope_x_2026_clean.parquet"
        )

    def test_single_file_location_e_year_aware(self):
        loc = {
            "path": f"gs://{CLEAN_BUCKET}/open-politica/camera_voti/2025/camera_voti_2025_clean.parquet"
        }
        with patch("src.data._util.object_exists", return_value=True) as mock_exists:
            from src.data._util import _parquet_exists

            assert _parquet_exists("camera_voti", 2024, loc) is False
            assert _parquet_exists("camera_voti", 2025, loc) is True
        # l'anno sbagliato non fa nemmeno la HEAD
        mock_exists.assert_called_once()

    def test_glob_location_matches_year(self):
        loc = {
            "path": f"gs://{CLEAN_BUCKET}/p/s/*/s_*_clean.parquet",
            "multi_file": True,
        }
        urls = [
            f"https://storage.googleapis.com/{CLEAN_BUCKET}/p/s/{year}/s_{year}_clean.parquet"
            for year in (2023, 2024)
        ]
        with patch("src.data._util.location_urls", return_value=urls):
            from src.data._util import _parquet_exists

            assert _parquet_exists("s", 2024, loc) is True
            assert _parquet_exists("s", 2022, loc) is False

    def test_glob_listing_failure_falls_back_to_head(self):
        loc = {
            "path": f"gs://{CLEAN_BUCKET}/p/s/*/s_*_clean.parquet",
            "multi_file": True,
        }
        with patch("src.data._util.location_urls", side_effect=RuntimeError("rete")):
            with patch("src.data._util.object_exists", return_value=True) as mock_exists:
                from src.data._util import _parquet_exists

                assert _parquet_exists("s", 2024, loc) is True
        mock_exists.assert_called_once_with(CLEAN_BUCKET, "p/s/2024/s_2024_clean.parquet")


class TestParquetRefs:
    """Contratto: _parquet_refs produce una ref HTTPS per anno dal location."""

    def _refs(self, slug, years, location=None):
        from src.data._util import _parquet_refs

        return _parquet_refs(slug, years, location)

    def test_canonical_fallback(self):
        refs = self._refs("test-slug", [2022, 2023])
        assert refs == [
            f"https://storage.googleapis.com/{CLEAN_BUCKET}/test-slug/2022/test-slug_2022_clean.parquet",
            f"https://storage.googleapis.com/{CLEAN_BUCKET}/test-slug/2023/test-slug_2023_clean.parquet",
        ]

    def test_from_location_prefixed(self):
        loc = {"path": f"gs://{CLEAN_BUCKET}/siope/siope_x/2026/siope_x_2026_clean.parquet"}
        refs = self._refs("siope_x", [2026], loc)
        assert refs == [
            f"https://storage.googleapis.com/{CLEAN_BUCKET}/siope/siope_x/2026/siope_x_2026_clean.parquet"
        ]

    def test_multi_file_glob_per_year(self):
        loc = {
            "path": f"gs://{CLEAN_BUCKET}/conto-annuale/anzianita/*/anzianita_*_clean.parquet",
            "multi_file": True,
        }
        refs = self._refs("anzianita", [2023, 2024], loc)
        assert refs == [
            f"https://storage.googleapis.com/{CLEAN_BUCKET}/conto-annuale/anzianita/2023/anzianita_2023_clean.parquet",
            f"https://storage.googleapis.com/{CLEAN_BUCKET}/conto-annuale/anzianita/2024/anzianita_2024_clean.parquet",
        ]


class TestRawSample:
    """Contratto: raw_sample produce JSON raw distribuito tra gli anni."""

    def setup_method(self):
        self._saved_stdout = sys.stdout

    def teardown_method(self):
        sys.stdout = self._saved_stdout

    @patch("src.data._util.safe_connect")
    @patch("src.data._util._parquet_exists", return_value=True)
    @patch("src.data._util._parquet_refs", return_value=["ref1", "ref2"])
    def test_distributes_sample_per_year(self, mock_refs, mock_exists, mock_safe_connect):
        """Con più refs, il campione è distribuito con USING SAMPLE per-anno."""
        con = MagicMock()
        con.sql.return_value.description = [("anno",), ("valore",)]
        con.sql.return_value.fetchall.return_value = [("2020", 1.0), ("2021", 2.0)]
        mock_safe_connect.return_value.__enter__.return_value = con
        from src.data._util import raw_sample

        buf = io.StringIO()
        sys.stdout = buf
        raw_sample("test-slug", [2020, 2021], limit=1000)

        sql_call = con.sql.call_args_list[0][0][0]
        assert "USING SAMPLE 500 ROWS" in sql_call  # 1000 / 2 refs
        output = json.loads(buf.getvalue())
        assert len(output) == 2
        assert output[0]["valore"] == 1

    @patch("src.data._util.safe_connect")
    @patch("src.data._util._parquet_exists", return_value=False)
    def test_empty_when_no_years(self, mock_exists, mock_safe_connect):
        from src.data._util import raw_sample

        buf = io.StringIO()
        sys.stdout = buf
        raw_sample("test-slug", [2020, 2021])
        assert json.loads(buf.getvalue()) == []
        mock_safe_connect.assert_not_called()


# ── load_dataset ─────────────────────────────────────────────────────────────


@pytest.fixture
def mock_con():
    """Fixture: mock DuckDB connection con fetchall controllabile."""
    con = MagicMock()
    con.sql.return_value.fetchall.return_value = [
        ("2020", "Lombardia", 100.0),
        ("2020", "Lazio", 50.0),
        ("2021", "Lombardia", 120.0),
    ]
    return con


class TestLoadDataset:
    """Contratto: load_dataset produce JSON su stdout con aggregazioni."""

    def setup_method(self):
        self._saved_stdout = sys.stdout

    def teardown_method(self):
        sys.stdout = self._saved_stdout

    @patch("src.data._util.safe_connect")
    @patch("src.data._util._parquet_exists", return_value=True)
    def test_loads_all_valid_years(self, mock_exists, mock_safe_connect, mock_con):
        """Tutti gli anni validi → DuckDB query con UNION ALL."""
        mock_safe_connect.return_value.__enter__.return_value = mock_con
        from src.data._util import load_dataset

        buf = io.StringIO()
        sys.stdout = buf

        load_dataset(
            slug="test-slug",
            years=[2020, 2021],
            group_cols=["anno", "regione"],
            metric_cols=["valore"],
        )

        output = json.loads(buf.getvalue())
        assert len(output) == 3
        assert output[0] == {"anno": "2020", "regione": "Lombardia", "valore": 100}
        assert output[1] == {"anno": "2020", "regione": "Lazio", "valore": 50}
        assert output[2] == {"anno": "2021", "regione": "Lombardia", "valore": 120}

        # Verifica che DuckDB sia stata chiamata con UNION ALL
        sql_call = mock_con.sql.call_args[0][0]
        assert "UNION ALL" in sql_call
        assert "test-slug" in sql_call

    @patch("src.data._util.safe_connect")
    @patch("src.data._util._parquet_exists", side_effect=lambda s, y, loc=None: y == 2021)
    def test_skips_missing_years(self, mock_exists, mock_safe_connect, mock_con):
        """Anno senza parquet → saltato, no errore."""
        mock_safe_connect.return_value.__enter__.return_value = mock_con
        from src.data._util import load_dataset

        # mock_con ha solo 2020 e 2021, ma _parquet_exists torna True solo per 2021
        # Quindi solo 2021 viene usato
        mock_con.sql.return_value.fetchall.return_value = [
            ("2021", "Lombardia", 120.0),
        ]

        buf = io.StringIO()
        sys.stdout = buf

        load_dataset(
            slug="test-slug",
            years=[2020, 2021, 2022],
            group_cols=["anno", "regione"],
            metric_cols=["valore"],
        )

        output = json.loads(buf.getvalue())
        assert len(output) == 1
        assert output[0]["anno"] == "2021"

    @patch("src.data._util.safe_connect")
    @patch("src.data._util._parquet_exists", return_value=False)
    def test_empty_when_no_valid_years(self, mock_exists, mock_safe_connect, mock_con):
        """Nessun anno valido → array JSON vuoto."""
        mock_safe_connect.return_value.__enter__.return_value = mock_con
        from src.data._util import load_dataset

        buf = io.StringIO()
        sys.stdout = buf

        load_dataset(
            slug="test-slug",
            years=[2020, 2021],
            group_cols=["anno"],
            metric_cols=["valore"],
        )

        output = json.loads(buf.getvalue())
        assert output == []
        # DuckDB non deve essere chiamata
        mock_con.sql.assert_not_called()

    @patch("src.data._util.safe_connect")
    @patch("src.data._util._parquet_exists", return_value=True)
    def test_applies_where_clause(self, mock_exists, mock_safe_connect, mock_con):
        """Where clause → filtrata nella query SQL."""
        mock_safe_connect.return_value.__enter__.return_value = mock_con
        from src.data._util import load_dataset

        buf = io.StringIO()
        sys.stdout = buf

        load_dataset(
            slug="test-slug",
            years=[2020],
            group_cols=["regione"],
            metric_cols=["valore"],
            where="regione = 'Lombardia'",
        )

        sql_call = mock_con.sql.call_args[0][0]
        assert "WHERE" in sql_call
        assert "regione = 'Lombardia'" in sql_call

    @patch("src.data._util.safe_connect")
    @patch("src.data._util._parquet_exists", return_value=True)
    def test_converts_float_to_int_when_whole(self, mock_exists, mock_safe_connect, mock_con):
        """Float interi (es. 100.0) → convertiti a int nel JSON."""
        mock_con.sql.return_value.fetchall.return_value = [
            ("cat1", 100.0),
            ("cat2", 200.0),
        ]
        mock_safe_connect.return_value.__enter__.return_value = mock_con
        from src.data._util import load_dataset

        buf = io.StringIO()
        sys.stdout = buf

        load_dataset(
            slug="test-slug",
            years=[2020],
            group_cols=["categoria"],
            metric_cols=["valore"],
        )

        output = json.loads(buf.getvalue())
        assert output[0]["valore"] == 100  # int, non 100.0
        assert isinstance(output[0]["valore"], int)

    @patch("src.data._util.safe_connect")
    @patch("src.data._util._parquet_exists", return_value=True)
    def test_preserves_float_when_not_whole(self, mock_exists, mock_safe_connect, mock_con):
        """Float non interi (es. 100.5) → restano float, non troncati."""
        mock_con.sql.return_value.fetchall.return_value = [
            ("cat1", 100.5),
            ("cat2", 200.7),
        ]
        mock_safe_connect.return_value.__enter__.return_value = mock_con
        from src.data._util import load_dataset

        buf = io.StringIO()
        sys.stdout = buf

        load_dataset(
            slug="test-slug",
            years=[2020],
            group_cols=["categoria"],
            metric_cols=["valore"],
        )

        output = json.loads(buf.getvalue())
        assert output[0]["valore"] == 100.5
        assert isinstance(output[0]["valore"], float)
        assert output[1]["valore"] == 200.7
        assert isinstance(output[1]["valore"], float)

    @patch("src.data._util.safe_connect")
    @patch("src.data._util._parquet_exists", return_value=True)
    def test_handles_nan_values(self, mock_exists, mock_safe_connect, mock_con):
        """NaN in DuckDB → resta NaN nel JSON (v == v è False, skip conversione).

        json.dump serializza NaN come NaN (non JSON standard). Il valore NaN
        non viene filtrato né convertito.
        """
        mock_con.sql.return_value.fetchall.return_value = [
            ("cat1", float("nan")),
            ("cat2", 50.0),
        ]
        mock_safe_connect.return_value.__enter__.return_value = mock_con
        from src.data._util import load_dataset

        buf = io.StringIO()
        sys.stdout = buf

        load_dataset(
            slug="test-slug",
            years=[2020],
            group_cols=["categoria"],
            metric_cols=["valore"],
        )

        output = json.loads(buf.getvalue())
        # NaN non viene filtrato — resta nel JSON serializzato come NaN
        assert len(output) == 2
        assert output[0]["categoria"] == "cat1"
        assert isinstance(output[0]["valore"], float)
        # NaN != NaN, ma json.loads lo riporta come float
        assert output[0]["valore"] != output[0]["valore"]  # è NaN
        assert output[1]["categoria"] == "cat2"
        assert output[1]["valore"] == 50

    @patch("src.data._util.safe_connect")
    @patch("src.data._util._parquet_exists", return_value=True)
    def test_query_includes_group_and_metric_columns(
        self, mock_exists, mock_safe_connect, mock_con
    ):
        """La query SQL include SELECT con group e SUM(metric)."""
        mock_safe_connect.return_value.__enter__.return_value = mock_con
        mock_con.sql.return_value.fetchall.return_value = []
        from src.data._util import load_dataset

        buf = io.StringIO()
        sys.stdout = buf

        load_dataset(
            slug="test-slug",
            years=[2020],
            group_cols=["regione"],
            metric_cols=["spesa", "quantita"],
        )

        sql_call = mock_con.sql.call_args[0][0]
        assert "SELECT regione" in sql_call
        assert "SUM(spesa) AS spesa" in sql_call
        assert "SUM(quantita) AS quantita" in sql_call
        assert "GROUP BY regione" in sql_call
        assert "ORDER BY regione" in sql_call


class TestLoaderCompat:
    """I loader non devono importare simboli privati rimossi dal refactor."""

    def test_loader_non_usano_simboli_rimossi(self):
        data_dir = Path(__file__).resolve().parents[1] / "src" / "data"
        removed = ("_load_manifest", "_target_path", "_location_https_prefix")
        for loader in sorted(data_dir.glob("*.json.py")):
            text = loader.read_text(encoding="utf-8")
            for symbol in removed:
                assert symbol not in text, f"{loader.name} usa {symbol}"

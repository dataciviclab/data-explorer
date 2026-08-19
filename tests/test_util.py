"""
Test per _util.py — data loader condiviso per Observable Framework.

Contratto:
  - _parquet_exists(): verifica esistenza parquet su GCS via gcs_manifest.json
    con fallback a object_exists() (HEAD) se manifest non disponibile
  - load_dataset(): produce JSON valido su stdout con aggregazioni corrette,
    salta anni senza parquet, gestisce where clause

Prova del fuoco: se cancello questi test, un refactor di _util.py
può rompere tutti i data loader senza preavviso.
"""
import io
import json
import sys
from unittest.mock import MagicMock, patch

import pytest

from lab_connectors.gcs.paths import CLEAN_BUCKET

# ── _parquet_exists ──────────────────────────────────────────────────────────


def _make_manifest(paths: list[str]) -> dict:
    """Crea un manifest finto con i path indicati."""
    return {
        "files": [
            {"bucket": CLEAN_BUCKET, "path": p}
            for p in paths
        ]
    }


class TestParquetExists:
    """Contratto: _parquet_exists usa gcs_manifest.json o fallback object_exists."""

    def _patch_manifest(self, manifest: dict):
        """Patch _load_manifest per restituire un manifest controllato."""
        return patch("src.data._util._load_manifest", return_value=manifest)

    def test_exists_returns_true_when_in_manifest(self):
        """Path presente nel manifest → esiste."""
        manifest = _make_manifest(["test-slug/2023/test-slug_2023_clean.parquet"])
        with self._patch_manifest(manifest):
            from src.data._util import _parquet_exists

            assert _parquet_exists("test-slug", 2023) is True

    def test_missing_returns_false_when_not_in_manifest_and_not_on_gcs(self):
        """Path assente dal manifest E assente su GCS → non esiste."""
        manifest = _make_manifest(["altro-slug/2023/altro-slug_2023_clean.parquet"])
        with patch("lab_connectors.gcs.object_exists", return_value=False):
            with self._patch_manifest(manifest):
                from src.data._util import _parquet_exists

                assert _parquet_exists("test-slug", 2023) is False

    def test_fallback_to_object_exists_when_manifest_empty(self):
        """Manifest senza files → fallback a object_exists()."""
        with patch("lab_connectors.gcs.object_exists", return_value=True):
            with self._patch_manifest({"files": []}):
                from src.data._util import _parquet_exists

                assert _parquet_exists("test-slug", 2023) is True

    def test_missing_in_manifest_falls_back_to_gcs(self):
        """Path non nel manifest ma presente su GCS → esiste (evita falso negativo).

        Un parquet appena pubblicato (dopo l'ultimo refresh del manifest)
        non deve risultare assente.
        """
        manifest = _make_manifest(["altro-slug/2023/altro-slug_2023_clean.parquet"])
        with patch("lab_connectors.gcs.object_exists", return_value=True):
            with self._patch_manifest(manifest):
                from src.data._util import _parquet_exists

                assert _parquet_exists("test-slug", 2023) is True

    def test_fallback_passes_correct_params(self):
        """Fallback chiama object_exists con bucket e key corretti."""
        with patch("lab_connectors.gcs.object_exists") as mock_exists:
            mock_exists.return_value = True
            with self._patch_manifest({}):
                from src.data._util import _parquet_exists

                _parquet_exists("test-slug", 2023)
                called_bucket, called_key = mock_exists.call_args[0]
                assert called_bucket == CLEAN_BUCKET
                assert called_key == "test-slug/2023/test-slug_2023_clean.parquet"


# ── location / _parquet_refs ────────────────────────────────────────────────


class TestLocationHttpsPrefix:
    """Contratto: _location_https_prefix deriva il prefix HTTPS dal location registry."""

    def _prefix(self, location):
        from src.data._util import _location_https_prefix

        return _location_https_prefix(location, "test-slug")

    def test_no_location_returns_none(self):
        assert self._prefix(None) is None
        assert self._prefix({}) is None

    def test_non_gs_path_returns_none(self):
        assert self._prefix({"path": "https://example.com/x"}) is None

    def test_simple_slug(self):
        loc = {"path": f"gs://{CLEAN_BUCKET}/test-slug/2023/test-slug_2023_clean.parquet"}
        assert self._prefix(loc) == (
            f"https://storage.googleapis.com/{CLEAN_BUCKET}/test-slug"
        )

    def test_prefixed_repo(self):
        loc = {"path": f"gs://{CLEAN_BUCKET}/conto-annuale/anzianita/2023/anzianita_2023_clean.parquet"}
        assert self._prefix(loc) == (
            f"https://storage.googleapis.com/{CLEAN_BUCKET}/conto-annuale/anzianita"
        )

    def test_year_in_middle(self):
        loc = {"path": f"gs://{CLEAN_BUCKET}/a/b/2020/c/d.parquet"}
        assert self._prefix(loc) == (
            f"https://storage.googleapis.com/{CLEAN_BUCKET}/a/b"
        )


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


class TestTargetPath:
    """Contratto: _target_path deriva la key GCS dal location (prefix e multi_file)."""

    def _path(self, slug, year, location=None):
        from src.data._util import _target_path

        return _target_path(slug, year, location)

    def test_canonical_fallback(self):
        assert self._path("test-slug", 2023) == "test-slug/2023/test-slug_2023_clean.parquet"

    def test_prefixed(self):
        loc = {"path": f"gs://{CLEAN_BUCKET}/siope/siope_x/2026/siope_x_2026_clean.parquet"}
        assert self._path("siope_x", 2026, loc) == "siope/siope_x/2026/siope_x_2026_clean.parquet"

    def test_multi_file(self):
        loc = {
            "path": f"gs://{CLEAN_BUCKET}/conto-annuale/anzianita/*/anzianita_*_clean.parquet",
            "multi_file": True,
        }
        assert self._path("anzianita", 2024, loc) == (
            "conto-annuale/anzianita/2024/anzianita_2024_clean.parquet"
        )


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

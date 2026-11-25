"""Test per scripts/prefetch.py — loader in parallelo nella cache del build.

Contratto: l'output scritto in cache è esattamente lo stdout del loader, e un
loader rotto ferma il prefetch (meglio deploy rosso che dati di ieri).
"""

import json

import pytest

from scripts import prefetch as pf


@pytest.fixture
def repo(tmp_path):
    data = tmp_path / "data"
    cache = tmp_path / "cache"
    data.mkdir()
    cache.mkdir()
    return data, cache


def _loader(data_dir, name, body):
    (data_dir / f"{name}.json.py").write_text(body, encoding="utf-8")


def _print_json(payload):
    return f"import json\nprint(json.dumps({payload!r}))\n"


class TestRunLoader:
    def test_scrive_la_cache_con_l_output(self, repo):
        data, cache = repo
        _loader(data, "ok", _print_json([{"anno": 2024, "n": 3}]))

        result = pf.run_loader("ok", data_dir=data, cache_dir=cache)

        assert result["name"] == "ok"
        assert json.loads(pf.cache_file("ok", cache).read_text(encoding="utf-8")) == [
            {"anno": 2024, "n": 3}
        ]

    def test_loader_inesistente(self, repo):
        data, cache = repo
        with pytest.raises(RuntimeError, match="non trovato"):
            pf.run_loader("manca", data_dir=data, cache_dir=cache)

    def test_loader_che_fallisce(self, repo):
        data, cache = repo
        _loader(data, "rotto", 'raise SystemExit("boom")\n')

        with pytest.raises(RuntimeError, match="exit"):
            pf.run_loader("rotto", data_dir=data, cache_dir=cache)
        assert not pf.cache_file("rotto", cache).exists()

    def test_output_non_json(self, repo):
        data, cache = repo
        _loader(data, "testo", 'print("non json")\n')

        with pytest.raises(RuntimeError, match="non JSON"):
            pf.run_loader("testo", data_dir=data, cache_dir=cache)


class TestPrefetch:
    def test_esegue_tutti_e_riporta_la_somma(self, repo):
        data, cache = repo
        for name in ("a", "b", "c"):
            _loader(data, name, _print_json([{"x": name}]))

        results, errors = pf.prefetch(["a", "b", "c"], workers=3, data_dir=data, cache_dir=cache)

        assert errors == []
        assert {item["name"] for item in results} == {"a", "b", "c"}
        for name in ("a", "b", "c"):
            assert json.loads(pf.cache_file(name, cache).read_text(encoding="utf-8")) == [{"x": name}]

    def test_un_fallito_non_ferma_gli_altri_ma_viene_riportato(self, repo):
        data, cache = repo
        _loader(data, "ok", _print_json([{"x": 1}]))
        _loader(data, "rotto", 'raise SystemExit(1)\n')

        _results, errors = pf.prefetch(
            ["ok", "rotto"], workers=2, data_dir=data, cache_dir=cache
        )

        assert len(errors) == 1 and "rotto" in errors[0]
        assert pf.cache_file("ok", cache).exists()

    def test_lista_vuota(self, repo):
        data, cache = repo
        assert pf.prefetch([], workers=2, data_dir=data, cache_dir=cache) == ([], [])

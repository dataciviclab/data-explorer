"""Test per scripts/invalidate_cache.py — invalidazione mirata della cache OF.

Il contratto: toccare un dataset invalida i suoi loader (tutti quelli che ne
leggono i mart), non i 58; un dataset senza pagina non è un errore; il report
contiene esattamente i loader che il workflow deve ritrovare nel build.
"""

import pytest
from scripts import invalidate_cache as ic


@pytest.fixture
def repo(tmp_path, monkeypatch):
    loaders = tmp_path / "src" / "data"
    loaders.mkdir(parents=True)
    cache = tmp_path / "cache"
    (cache / "data").mkdir(parents=True)
    monkeypatch.setattr(ic, "LOADERS_DIR", loaders)
    monkeypatch.setattr(ic, "CACHE_DIR", cache)
    return loaders, cache


def _loader(loaders, name, text=""):
    (loaders / f"{name}.json.py").write_text(text, encoding="utf-8")


def _cached(cache, stem):
    path = cache / "data" / f"{stem}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}", encoding="utf-8")
    return path


class TestResolveDatasets:
    def test_trova_tutti_i_loader_che_leggono_i_mart(self, repo):
        loaders, _ = repo
        _loader(loaders, "bdap-entrate", "mart_rows('bdap_entrate_stato__mart_entrate_anno')")
        _loader(loaders, "entrate-vs-spese", "mart_rows('bdap_entrate_stato__mart_x')")
        _loader(loaders, "altro", "mart_rows('altro__m')")

        resolved = ic.resolve_datasets(["bdap_entrate_stato"])

        assert resolved["bdap_entrate_stato"] == ["bdap-entrate", "entrate-vs-spese"]

    def test_risolve_anche_lo_url_slug_dal_nome_file(self, repo):
        loaders, _ = repo
        _loader(loaders, "anac-bandi-gara", "print('x')")
        assert ic.resolve_datasets(["anac-bandi-gara"])["anac-bandi-gara"] == ["anac-bandi-gara"]

    def test_dataset_senza_loader_non_esplode(self, repo):
        loaders, _ = repo
        _loader(loaders, "altro", "")
        assert ic.resolve_datasets(["nessuno"])["nessuno"] == []

    def test_non_confonde_slug_con_prefisso_comune(self, repo):
        loaders, _ = repo
        _loader(loaders, "a", "mart_rows('anac_bandi_gara_extra__m')")
        _loader(loaders, "b", "mart_rows('anac_bandi_gara__m')")
        assert ic.resolve_datasets(["anac_bandi_gara"])["anac_bandi_gara"] == ["b"]


class TestInvalidate:
    def test_rimuove_solo_gli_output_indicati(self, repo):
        _, cache = repo
        keep = _cached(cache, "altro")
        target = _cached(cache, "anac-bandi-gara")

        removed = ic.invalidate(["anac-bandi-gara"], cache_dir=cache)

        assert removed == ["anac-bandi-gara"]
        assert not target.exists()
        assert keep.exists()

    def test_ignora_output_gia_assenti(self, repo):
        _, cache = repo
        assert ic.invalidate(["mai-generato"], cache_dir=cache) == []

    def test_purge_svuota_tutta_la_cache(self, repo):
        _, cache = repo
        _cached(cache, "a")
        _cached(cache, "b")
        ic.purge_cache(cache_dir=cache)
        assert not cache.exists()


class TestCli:
    def test_datasets_invalida_e_scrive_il_report(self, repo, tmp_path):
        loaders, cache = repo
        _loader(loaders, "anac-bandi-gara", "mart_rows('anac_bandi_gara__m')")
        _loader(loaders, "altro", "mart_rows('altro__m')")
        _cached(cache, "anac-bandi-gara")
        keep = _cached(cache, "altro")
        report = tmp_path / "report.txt"

        code = ic.main(["--datasets", "anac_bandi_gara", "--report", str(report)])

        assert code == 0
        assert report.read_text(encoding="utf-8").split() == ["anac-bandi-gara"]
        assert keep.exists()
        assert not (cache / "data" / "anac-bandi-gara.json").exists()

    def test_full_vuole_tutti_i_loader_nel_report(self, repo, tmp_path):
        loaders, cache = repo
        _loader(loaders, "a", "")
        _loader(loaders, "b", "")
        _cached(cache, "a")
        report = tmp_path / "report.txt"

        assert ic.main(["--full", "--report", str(report)]) == 0

        assert report.read_text(encoding="utf-8").split() == ["a", "b"]
        assert not cache.exists()

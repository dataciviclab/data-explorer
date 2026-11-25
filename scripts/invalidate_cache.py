#!/usr/bin/env python3
"""Invalida la cache dei loader Observable **solo** per ciò che è cambiato.

`observable build` chiama i loader con `useStale: true` (`framework/dist/
build.js`): un output in cache viene servito anche se il sorgente è cambiato.
Questo script toglie dalla cache esattamente ciò che non è più valido:

- `--full`: tutto (cambio contrattuale o refresh manuale);
- diff `base..HEAD`: i loader modificati; se cambia un file condiviso
  (`_util`, `_registry`, `_views`, `requirements.txt`) si invalida tutto.
  Il PR check passa `--on-shared reuse`: il full resta al deploy;
- `--datasets a,b`: i loader che leggono i mart di quei dataset.

Il matching dei dataset è sul **sorgente** del loader: un loader può servire
più dataset (`bdap_entrate_stato` compare in `bdap-entrate` e
`entrate-vs-spese`), e il nome del file non è sempre lo `url_slug`. Così non
esiste una tabella di mapping da tenere aggiornata.

`--report PATH` scrive i loader invalidati: il workflow verifica dopo il build
che i loro output siano stati riscritti (cioè che i loader siano girati
davvero, senza fallback silenzioso allo stale).
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "src" / ".observablehq" / "cache"
LOADERS_DIR = ROOT / "src" / "data"

# File condivisi: se cambiano, la cache dei loader non è più affidabile.
SHARED = (
    "src/data/_util.py",
    "src/data/_registry.py",
    "src/data/_views.py",
    "requirements.txt",
)

# Un ref è "menzionato" se non è preceduto da caratteri di parola e, dopo, o
# inizia il separatore dei mart (`<slug>__<tabella>`) o non è un altro slug
# (`anac_bandi_gara_extra` non deve matchare `anac_bandi_gara`).
_REF_TEMPLATE = r"(?<![0-9A-Za-z-]){ref}(?:(?=__)|(?![0-9A-Za-z_-]))"


def loaders(loaders_dir: Path | None = None) -> list[Path]:
    """Loader dichiarati nel repo (`src/data/*.json.py`)."""
    return sorted((loaders_dir or LOADERS_DIR).glob("*.json.py"))


def loader_name(path: str | Path) -> str:
    """`src/data/anac-bandi-gara.json.py` → `anac-bandi-gara`."""
    return Path(path).name[: -len(".json.py")]


def _mentions(text: str, ref: str) -> bool:
    return re.search(_REF_TEMPLATE.format(ref=re.escape(ref)), text) is not None


def resolve_datasets(
    datasets: list[str], loaders_dir: Path | None = None
) -> dict[str, list[str]]:
    """dataset (slug DI o url_slug) → nomi dei loader che lo leggono."""
    files = loaders(loaders_dir)
    texts = {path: path.read_text(encoding="utf-8") for path in files}
    resolved: dict[str, list[str]] = {}
    for ref in datasets:
        names = [
            loader_name(path)
            for path, text in texts.items()
            if path.name == f"{ref}.json.py" or _mentions(text, ref)
        ]
        resolved[ref] = sorted(set(names))
    return resolved


def changed_files(base: str, root: Path | None = None) -> list[str]:
    """File cambiati tra `base` e `HEAD` (git diff, path relativi alla root)."""
    result = subprocess.run(
        ["git", "-C", str(root or ROOT), "diff", "--name-only", base, "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git diff {base}..HEAD fallito: {result.stderr.strip()}")
    return [line for line in result.stdout.splitlines() if line.strip()]


def changed_loaders(files: list[str]) -> list[str]:
    """Nomi dei loader tra i file cambiati."""
    return [
        loader_name(path)
        for path in files
        if path.startswith("src/data/") and path.endswith(".json.py")
    ]


def invalidate(names: list[str], cache_dir: Path | None = None) -> list[str]:
    """Rimuove gli output in cache dei loader indicati; ritorna quelli rimossi."""
    data_dir = (cache_dir or CACHE_DIR) / "data"
    removed = []
    for name in names:
        path = data_dir / f"{name}.json"
        if path.exists():
            path.unlink()
            removed.append(name)
    return removed


def purge_cache(cache_dir: Path | None = None) -> None:
    """Svuota la cache OF (full refresh)."""
    target = cache_dir or CACHE_DIR
    if target.exists():
        shutil.rmtree(target)


def _all_loader_names(loaders_dir: Path | None = None) -> list[str]:
    return [loader_name(path) for path in loaders(loaders_dir)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="", help="commit base del diff (vuoto: salta il diff)")
    parser.add_argument("--datasets", default="", help="slug DI o url_slug separati da virgola")
    parser.add_argument("--full", action="store_true", help="invalida tutta la cache")
    parser.add_argument(
        "--on-shared",
        choices=("full", "reuse"),
        default="full",
        help="contratto condiviso cambiato: full (deploy) o reuse (PR check)",
    )
    parser.add_argument("--report", default="", help="file con i loader invalidati")
    args = parser.parse_args(argv)

    names: set[str] = set()
    purged = False

    if args.full:
        purge_cache()
        names = set(_all_loader_names())
        purged = True
        print(f"full: cache svuotata ({len(names)} loader da rieseguire)")
    else:
        base = args.base.strip()
        if base and set(base) == {"0"}:
            base = ""  # branch nuova: niente diff affidabile
        if base:
            files = changed_files(base)
            shared = sorted(set(files) & set(SHARED))
            if shared and args.on_shared == "full":
                purge_cache()
                names = set(_all_loader_names())
                purged = True
                print(f"contratto condiviso cambiato ({', '.join(shared)}): cache svuotata")
            elif shared:
                print(
                    "contratto condiviso cambiato: uso la cache "
                    "(full validato dal deploy)"
                )
            if not purged:
                loaders_changed = changed_loaders(files)
                if loaders_changed:
                    names.update(loaders_changed)
                    print(f"loader cambiati: {', '.join(sorted(loaders_changed))}")
        elif not args.datasets.strip():
            print("nessun base né dataset: solo metadati (nessuna invalidazione)")

        refs = [ref.strip() for ref in args.datasets.split(",") if ref.strip()]
        if refs:
            for ref, ref_names in resolve_datasets(refs).items():
                if ref_names:
                    names.update(ref_names)
                    print(f"{ref}: {', '.join(ref_names)}")
                else:
                    print(
                        f"! {ref}: nessun loader lo legge (dataset senza pagina?)",
                        file=sys.stderr,
                    )

    if names and not purged:
        removed = invalidate(sorted(names))
        print(f"{len(removed)}/{len(names)} output rimossi dalla cache")

    if args.report:
        report = Path(args.report)
        report.write_text("\n".join(sorted(names)) + ("\n" if names else ""), encoding="utf-8")
        print(f"report: {report} ({len(names)} loader)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

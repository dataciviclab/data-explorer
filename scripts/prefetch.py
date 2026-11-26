#!/usr/bin/env python3
"""Esegue in parallelo i data loader invalidati e prepara la cache del build.

`observable build` esegue i data loader **uno alla volta**: 58 loader sono
694 s misurati in CI (un deploy da 12,5 minuti quasi tutto qui). I loader non
dipendono l'uno dall'altro: qui girano in N processi e il loro output viene
scritto in ``src/.observablehq/cache/data/<loader>.json``, il file che il
build riusa subito dopo (comportamento `useStale` di Framework).

Il conto è semplice: 694 s / 4 worker ≈ 175 s, più il render delle pagine.

Input: il report di ``invalidate_cache.py`` (un nome di loader per riga).
Un loader che esce con errore o non produce JSON valido ferma tutto: meglio
un deploy rosso che una pagina con i numeri di ieri.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "src" / "data"
CACHE_DIR = ROOT / "src" / ".observablehq" / "cache" / "data"


def read_names(report: str | Path) -> list[str]:
    """Nomi dei loader dal report di invalidazione."""
    path = Path(report)
    if not path.exists():
        raise SystemExit(f"prefetch: report non trovato: {path}")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def cache_file(name: str, cache_dir: Path | None = None) -> Path:
    return (cache_dir or CACHE_DIR) / f"{name}.json"


def run_loader(
    name: str,
    *,
    data_dir: Path | None = None,
    cache_dir: Path | None = None,
    timeout: int = 900,
) -> dict:
    """Esegue un loader e scrive il suo output nella cache. Solleva se fallisce."""
    script = (data_dir or DATA_DIR) / f"{name}.json.py"
    if not script.exists():
        raise RuntimeError(f"{name}: loader {script} non trovato")

    started = time.monotonic()
    process = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    elapsed = time.monotonic() - started

    if process.returncode != 0:
        detail = (process.stderr or process.stdout).strip().splitlines()
        tail = " | ".join(detail[-3:]) if detail else "nessun output"
        raise RuntimeError(f"{name}: exit {process.returncode} — {tail}")

    try:
        json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{name}: output non JSON ({exc})") from exc

    target = cache_file(name, cache_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text(process.stdout, encoding="utf-8")
    temporary.replace(target)  # scrittura atomica: il build non legge un file a metà
    return {"name": name, "seconds": elapsed}


def prefetch(
    names: list[str],
    *,
    workers: int = 4,
    data_dir: Path | None = None,
    cache_dir: Path | None = None,
) -> tuple[list[dict], list[str]]:
    """Esegue i loader in parallelo. Ritorna (risultati, errori)."""
    results: list[dict] = []
    errors: list[str] = []
    if not names:
        return results, errors

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {
            pool.submit(run_loader, name, data_dir=data_dir, cache_dir=cache_dir): name
            for name in names
        }
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as exc:  # noqa: BLE001 — l'errore va riportato tutto
                errors.append(str(exc))
    return results, errors


def warm_registry() -> None:
    """Precarica il topic_index una volta: evita N fetch identici in parallelo."""
    code = (
        "import sys; sys.path.insert(0, 'src/data');"
        "from _registry import load_registry; load_registry()"
    )
    subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), capture_output=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Esegue i loader in parallelo nella cache del build.")
    parser.add_argument("--report", required=True, help="file con un loader per riga")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--cache-dir", default="")
    args = parser.parse_args(argv)

    names = read_names(args.report)
    if not names:
        print("prefetch: nessun loader da eseguire")
        return 0

    cache_dir = Path(args.cache_dir) if args.cache_dir else None
    warm_registry()

    started = time.monotonic()
    results, errors = prefetch(names, workers=args.workers, cache_dir=cache_dir)
    wall = time.monotonic() - started

    for error in errors:
        print(f"✗ {error}", file=sys.stderr)

    total = sum(item["seconds"] for item in results)
    if errors:
        print(f"✗ prefetch: {len(errors)}/{len(names)} loader falliti", file=sys.stderr)
        return 1

    speedup = total / wall if wall else 0
    print(
        f"✓ prefetch: {len(results)} loader in {wall:.0f}s con {args.workers} worker "
        f"(sequenziale: {total:.0f}s, ×{speedup:.1f})"
    )
    for item in sorted(results, key=lambda item: -item["seconds"])[:5]:
        print(f"  · {item['name']}: {item['seconds']:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Data loader: ISPRA emissioni GHG dalle fonti energetiche — per anno.

Legge i mart della pipeline: nessun anno hardcoded e nessun path GCS. Il
perimetro lo decide il mart (1990 → ultimo anno completo).

Output: una riga per anno con i quattro settori e il totale
(``[{anno, industrie_energetiche, ..., totale}]``), la forma attesa dalla
pagina. Un anno con settori mancanti è un errore, non uno zero.
"""

import sys

sys.path.insert(0, "src/data")
from _views import mart_rows, write

SETTORI = (
    "industrie_energetiche",
    "industrie_manifatturiere",
    "residenziale_e_servizi",
    "trasporti",
)

rows = mart_rows(
    "ispra_emissioni_ghg__mart_settori_anno",
    select={"anno": "anno", "settore": "settore", "emissioni": "emissioni_mt"},
    until="last_complete",
)

per_anno: dict[int, dict] = {}
for row in rows:
    if row["anno"] is None or row["settore"] not in SETTORI:
        continue
    anno = int(row["anno"])
    bucket = per_anno.setdefault(anno, {"anno": anno, **{s: None for s in SETTORI}})
    bucket[row["settore"]] = row["emissioni"]

incompleti = sorted(anno for anno, bucket in per_anno.items() if any(bucket[s] is None for s in SETTORI))
if incompleti:
    raise RuntimeError(
        f"ispra-emissioni-ghg: anni con settori mancanti {incompleti} "
        f"(attesi {list(SETTORI)})"
    )

write(
    [
        {**bucket, "totale": sum(bucket[s] for s in SETTORI)}
        for _, bucket in sorted(per_anno.items())
    ]
)

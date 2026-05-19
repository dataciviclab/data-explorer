#!/usr/bin/env python3
"""Data loader: Flussi giustizia civile — aggregazione per distretto e anno.

Nota: il parquet ha tutti gli anni in un unico file (2025).
Usiamo solo quell'anno come riferimento, il GROUP BY gestisce il resto."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="civile_flussi",
    years=[2025],  # unico file multi-anno
    group_cols=["anno", "distretto"],
    metric_cols=["sopravvenuti", "definiti_totale", "pendenti_finali"],
)

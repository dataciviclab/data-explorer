#!/usr/bin/env python3
"""Data loader: ISPRA rifiuti urbani — aggregazione per regione."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="ispra_ru_base",
    years=list(range(2020, 2025)),
    group_cols=["anno", "regione"],
    metric_cols=["totale_ru_tonnellate", "totale_rd_tonnellate"],
)

#!/usr/bin/env python3
"""Data loader: Popolazione ISTAT — per anno e fascia d'età."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="popolazione_istat_comunale_2019_2025",
    years=list(range(2019, 2026)),
    group_cols=["anno", "fascia_eta"],
    metric_cols=["popolazione_residente", "totale_maschi", "totale_femmine"],
)

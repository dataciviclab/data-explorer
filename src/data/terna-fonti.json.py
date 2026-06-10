#!/usr/bin/env python3
"""Data loader: Terna capacità rinnovabile — potenza netta per fonte e regione."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="terna_capacita_rinnovabile",
    years=list(range(2015, 2025)),
    group_cols=["anno", "fonti", "regione"],
    metric_cols=["potenza_mw"],
    where="tipo_capacita = 'Netta'",
)

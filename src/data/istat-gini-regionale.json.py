#!/usr/bin/env python3
"""Data loader: ISTAT Gini regionale — indice per regione e anno.

Il parquet è un unico file multi-anno (2003-2024): nessun anno hardcoded.
``pres_aff_imp`` è pubblicato come stringa e la pagina lo confronta con 1/2,
quindi esce come intero.
"""

import sys; sys.path.insert(0, "src/data")
from _util import load_dataset, get_location

load_dataset(
    slug="istat_gini_regionale",
    years=None,  # anni dalla location (file multi-anno)
    group_cols=["anno", "regione", "pres_aff_imp"],
    metric_cols=["gini"],
    location=get_location("istat_gini_regionale"),
    ints=["pres_aff_imp"],
)

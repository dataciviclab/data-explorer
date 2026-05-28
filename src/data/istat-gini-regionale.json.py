#!/usr/bin/env python3
"""Data loader: ISTAT Gini regionale — indice per regione e anno."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="istat_gini_regionale",
    years=[2023],  # unico file multi-anno
    group_cols=["anno", "regione", "pres_aff_imp"],
    metric_cols=["gini"],
)

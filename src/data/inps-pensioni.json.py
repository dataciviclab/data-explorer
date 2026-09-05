#!/usr/bin/env python3
"""Data loader: INPS pensioni trimestrali — per gestione, area, anno."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset, get_location

load_dataset(
    slug="inps_pensioni_trimestrale",
    years=[2024],  # unico file 2020-2024
    group_cols=["anno", "gestione", "area_geografica"],
    metric_cols=["numero_pensioni"],
    location=get_location("inps_pensioni_trimestrale"),
)

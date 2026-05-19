#!/usr/bin/env python3
"""Data loader: AIFA spesa farmaceutica — per regione e classe ATC1."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="aifa_spesa_consumo",
    years=list(range(2018, 2025)),
    group_cols=["anno", "regione", "descrizione_atc1"],
    metric_cols=["numero_confezioni_convenzionata", "spesa_convenzionata"],
)

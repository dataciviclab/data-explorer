#!/usr/bin/env python3
"""Data loader: BDAP LEA — totale spesa per regione."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="bdap_lea",
    years=[2024],
    group_cols=["descrizione_regione"],
    metric_cols=["importo_totale"],
    where="codice_voce_contabile = '49999'",
)

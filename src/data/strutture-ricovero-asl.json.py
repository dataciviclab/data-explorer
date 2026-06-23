#!/usr/bin/env python3
"""Data loader: strutture di ricovero per ASL — personale, posti letto, ricoveri."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="strutture_ricovero_asl",
    years=[2022],
    group_cols=[
        "regione", "denominazione_struttura", "comune",
        "sigla_provincia_struttura", "tipo_struttura", "asl",
    ],
    metric_cols=[
        "posti_letto_previsti",
        "posti_letto_utilizzati",
        "totale_personale",
        "medici",
        "infermieri",
        "ricoveri",
    ],
)

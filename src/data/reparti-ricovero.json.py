#!/usr/bin/env python3
"""Data loader: reparti di ricovero — posti letto per disciplina e regione."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="reparti_ricovero",
    years=[2022],
    group_cols=["regione", "disciplina", "tipo_struttura"],
    metric_cols=[
        "posti_letto_degenza_ordinaria",
        "posti_letto_day_hospital",
        "posti_letto_day_surgery",
        "posti_letto_utilizzati",
        "tasso_utilizzo",
        "degenza_media_ordinaria",
    ],
)

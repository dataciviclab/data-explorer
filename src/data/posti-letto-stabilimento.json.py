#!/usr/bin/env python3
"""Data loader: posti letto per stabilimento ospedaliero — serie 2020-2023."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="posti_letto_stabilimento",
    years=[2020, 2021, 2022, 2023],
    group_cols=[
        "anno", "descrizione_regione", "descrizione_tipo_struttura",
        "descrizione_disciplina",
    ],
    metric_cols=[
        "totale_posti_letto",
        "posti_letto_degenza_ordinaria",
        "posti_letto_day_hospital",
        "posti_letto_day_surgery",
    ],
)

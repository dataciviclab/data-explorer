#!/usr/bin/env python3
"""Data loader: BDAP entrate dello Stato — per titolo e anno."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="bdap_entrate_stato",
    years=[2024],  # unico file multi-anno
    group_cols=["esercizio_finanziario", "titolo"],
    metric_cols=["previsioni_definitive_cp", "previsioni_definitive_cs"],
)

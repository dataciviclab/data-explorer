#!/usr/bin/env python3
"""Data loader: BDAP entrate dello Stato — per titolo e anno."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset, get_location

load_dataset(
    slug="bdap_entrate_stato",
    years=[2025],  # unico file multi-anno (contiene 2008-2025)
    group_cols=["esercizio_finanziario", "titolo"],
    metric_cols=["previsioni_definitive_cp", "previsioni_definitive_cs"],
    location=get_location("bdap_entrate_stato"),
)

#!/usr/bin/env python3
"""Data loader: MIT incidentalità stradale — mensile nazionale."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="mit_incidentalita_mensile",
    years=[2001],  # unico file multi-anno
    group_cols=["anno", "mese", "mese_numero"],
    metric_cols=["incidenti", "morti", "feriti", "incidenti_mortali",
                 "indice_mortalita", "indice_gravita", "indice_lesivita"],
)

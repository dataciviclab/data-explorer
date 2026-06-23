#!/usr/bin/env python3
"""Data loader: strutture e attività ASL — medici, pediatri, residenti, ricette."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="strutture_asl",
    years=[2022],
    group_cols=["regione", "denominazione_asl", "comune_asl", "sigla_provincia_asl"],
    metric_cols=[
        "totale_residenti",
        "totale_medici",
        "totale_pediatri",
        "euro_importo_ricette",
        "num_ricette_specialita_medicinali",
    ],
)

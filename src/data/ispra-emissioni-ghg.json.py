#!/usr/bin/env python3
"""Data loader: ISPRA emissioni GHG da processi energetici — per settore e anno."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="ispra_emissioni_ghg",
    years=[2023],  # unico file multi-anno (1990-2023)
    group_cols=["anno"],
    metric_cols=["industrie_energetiche", "industrie_manifatturiere", "residenziale_e_servizi", "trasporti", "totale"],
)

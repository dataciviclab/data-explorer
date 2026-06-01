#!/usr/bin/env python3
"""Data loader: MIM Alunni corso/età — aggregati per anno, regione, ordine."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="mim_alunni_corso_eta",
    years=list(range(2016, 2026)),
    group_cols=["anno_scolastico", "regione", "ordine_scuola", "area_geografica"],
    metric_cols=["alunni"],
)

#!/usr/bin/env python3
"""Data loader: Pensioni PA — per microqualifica, regione e anno.

Singolo file parquet multi-anno (2017-2022)."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="pensioni_pa_dag",
    years=[2024],  # unico file multi-anno
    group_cols=["anno", "regione", "descrizione_microqualifica"],
    metric_cols=["numero_partite", "importi_mensili_pagati_eur"],
)

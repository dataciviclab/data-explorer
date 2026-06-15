#!/usr/bin/env python3
"""Data loader: OpenCoesione — progetti delle politiche di coesione.
Aggregato per ciclo di programmazione, macroarea, tema sintetico e stato.
"""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="opencoesione_progetti",
    years=[2026],  # unico snapshot multi-ciclo
    group_cols=["OC_DESCR_CICLO", "OC_MACROAREA", "OC_TEMA_SINTETICO", "OC_STATO_PROGETTO"],
    metric_cols=["FINANZ_TOTALE_PUBBLICO", "TOT_PAGAMENTI", "OC_COSTO_COESIONE"],
)

#!/usr/bin/env python3
"""Data loader: Consip Consumi Convenzione — spesa per regione PA."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="consip_consumi_convenzione",
    years=list(range(2023, 2026)),
    group_cols=["anno_riferimento", "regione_pa"],
    metric_cols=["valore_economico_consumi", "numero_ordini_con_consumi", "n_pa_con_consumi", "n_po_con_consumi"],
)

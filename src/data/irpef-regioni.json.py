#!/usr/bin/env python3
"""Data loader: IRPEF — aggregazione per regione (per i chart della pagina irpef-comunale)."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="irpef_comunale",
    years=list(range(2019, 2024)),
    group_cols=["anno_di_imposta", "regione"],
    metric_cols=["numero_contribuenti", "reddito_imponibile_eur", "imposta_netta_eur"],
)

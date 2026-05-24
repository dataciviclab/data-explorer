#!/usr/bin/env python3
"""Data loader: BDAP LEA — spesa per regione e macro-area (prevenzione, distrettuale, ospedaliera, ricerca)."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="bdap_lea",
    years=[2024],
    group_cols=["descrizione_regione", "descrizione_voce_contabile"],
    metric_cols=["importo_totale"],
    where="codice_voce_contabile IN ('19999', '29999', '39999', '48888')",
)

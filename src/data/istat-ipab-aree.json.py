#!/usr/bin/env python3
"""Data loader: ISTAT IPAB Aree — indice prezzi per area e trimestre."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="istat_ipab_aree",
    years=list(range(2010, 2026)),
    group_cols=["area", "trimestre"],
    metric_cols=["indice_prezzi"],
    where="tipo_abitazione = 'EXST_DW'",
)

#!/usr/bin/env python3
"""Data loader: Terna produzione elettrica — per fonte, regione e anno."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="terna_electricity_by_source",
    years=list(range(2023, 2025)),
    group_cols=["anno", "fonte", "regione"],
    metric_cols=["produzione_gwh"],
    where="tipo_produzione = 'Netta'",
)

#!/usr/bin/env python3
"""Data loader: OpenCivitas FSC 2025 — fondo solidarietà comunale per comune."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset

load_dataset(
    slug="opencivitas_fsc_2025_rso",
    years=[2025],
    group_cols=["regione", "comune", "provincia", "popolazione"],
    metric_cols=["capacita_fiscale", "fondo_perequativo", "dotazione_finale_fsc",
                 "imu_tasi_standard", "totale_risorse_storiche"],
    where="regione != 'ITALIA' AND provincia IS NOT NULL AND provincia != ''",
)

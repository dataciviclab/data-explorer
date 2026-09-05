#!/usr/bin/env python3
"""Data loader: RNA — Aiuti di Stato (MIMIT).

Analisi del Registro Nazionale Aiuti: trend, distribuzione regionale,
strumenti e beneficiari degli aiuti pubblici alle imprese italiane.
"""
import sys
sys.path.insert(0, "src/data")
from _util import load_dataset, get_location

load_dataset(
    slug="rna_aiuti_stato",
    years=[y for y in range(2017, 2027)],
    group_cols=["anno", "regione_beneficiario", "tipo_beneficiario", "strumento", "procedimento", "soggetto_concedente"],
    metric_cols=["elemento_aiuto", "importo_nominale"],
    location=get_location("rna_aiuti_stato"),
)

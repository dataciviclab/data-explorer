#!/usr/bin/env python3
"""Data loader: IRPEF — aggregazione per regione (per i chart della pagina irpef-comunale)."""
import sys; sys.path.insert(0, "src/data")
from _util import load_dataset, get_location

load_dataset(
    slug="irpef_comunale",
    years=list(range(2019, 2024)),
    group_cols=["anno_di_imposta", "regione"],
    metric_cols=["numero_contribuenti", "reddito_imponibile_eur", "imposta_netta_eur"],
    # La riga aggregata dei comuni non riconosciuti ha codice ISTAT '0' e
    # cambia etichetta negli anni ('Non indicato' / 'Mancante/errata'):
    # si esclude per codice, non per nome.
    where="codice_istat_comune <> '0'",
    location=get_location("irpef_comunale"),
)

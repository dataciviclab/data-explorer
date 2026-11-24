#!/usr/bin/env python3
"""Data loader: ANAC Bandi di Gara (CIG) — viste dai mart della pipeline.

Nessuna SQL locale: legge i mart dichiarati in ``appalti-pubblici``
(``mart_annuale``, ``mart_esiti_per_procedura``, ``mart_top_stazioni``) e
proietta le colonne attese dalla pagina.

Output:
- trend:    [{anno, n_lotti, importo_totale}]
- per_tipo: [{anno, tipo, n_lotti, importo}]   (tipo_scelta_contraente)
- top_sa:   [{anno, denominazione, n_lotti, importo}]
- anni:     [2016, ...]

Perimetro: dal 2016 (CIG confrontabile) all'ultimo anno completo.
L'anno in corso è escluso perché la partizione è parziale.
"""

import sys

sys.path.insert(0, "src/data")
from _views import group_rows, mart_rows, write

ANNO_MIN = 2016

trend = mart_rows(
    "anac_bandi_gara__mart_annuale",
    select={"anno": "anno", "n_lotti": "n_lotti", "importo_totale": "importo_totale"},
    since=ANNO_MIN,
    until="last_complete",
)

per_tipo = group_rows(
    mart_rows(
        "anac_bandi_gara__mart_esiti_per_procedura",
        select={
            "anno": "anno",
            "tipo": "tipo_scelta_contraente",
            "n_lotti": "n_lotti",
            "importo": "importo_totale",
        },
        since=ANNO_MIN,
        until="last_complete",
    ),
    by=["anno", "tipo"],
    metrics={"n_lotti": "sum", "importo": "sum"},
    sort_by="anno",
)

top_sa = mart_rows(
    "anac_bandi_gara__mart_top_stazioni",
    select={
        "anno": "anno",
        "denominazione": "denominazione_amministrazione_appaltante",
        "n_lotti": "n_lotti",
        "importo": "importo_totale",
    },
    since=ANNO_MIN,
    until="last_complete",
)

write(
    {
        "trend": trend,
        "per_tipo": per_tipo,
        "top_sa": top_sa,
        "anni": [row["anno"] for row in trend],
    }
)

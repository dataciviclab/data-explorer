#!/usr/bin/env python3
"""Data loader: OpenCoesione — progetti delle politiche di coesione.

Legge `mart_tema_ciclo` (tema × macroarea × ciclo): una riga per combinazione,
con finanziamento e pagamenti. Prima il loader leggeva il clean (18,5 MB di
colonne, 2,3 M righe) per produrre lo stesso aggregato.

Verificato: i totali per ciclo coincidono con `mart_ciclo` e
`mart_macroarea_ciclo` (±0 €).
"""

import sys

sys.path.insert(0, "src/data")
from _views import mart_rows, write

write(
    mart_rows(
        "opencoesione_progetti__mart_tema_ciclo",
        select={
            "ciclo": "ciclo",
            "macroarea": "macroarea",
            "tema": "tema",
            "finanziato": "finanz_tot_pub",
            "pagato": "pagamenti_tot",
        },
    )
)

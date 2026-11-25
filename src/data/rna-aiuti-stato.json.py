#!/usr/bin/env python3
"""Data loader: RNA — Aiuti di Stato (MIMIT).

Legge i mart della pipeline e restituisce **le aggregazioni che la pagina usa**,
non il cubo a 6 dimensioni: prima il loader spediva 18 MB di righe e la pagina
le raggruppava in JS.

Misura: `totale_esl` è la somma di `elemento_aiuto` (verificato sull'intero
dataset, 493,87 G€ su entrambi), `aiuti` è il numero di elementi di aiuto.

Delta noti rispetto al cubo: la categoria `tipo_beneficiario = '-'` non è nei
mart (0,38 G€ nel 2023) e `soggetto_concedente = ''` (7 righe) è escluso.
La pagina già scarta `-` dal grafico dei tipi.
"""

import sys

sys.path.insert(0, "src/data")
from _views import group_rows, mart_rows, write


def per_categoria(ref: str, campo: str, chiave: str) -> list[dict]:
    """Somma importo e numero aiuti per una dimensione, ordinata per importo."""
    rows = mart_rows(ref, select={campo: campo, "esl": "totale_esl", "n": "aiuti"})
    grouped = group_rows(
        rows,
        by=[campo],
        metrics={"importo": ("esl", "sum"), "n": ("n", "sum")},
        sort_by="importo",
        descending=True,
    )
    return [
        {chiave: row[campo], "importo": row["importo"], "n": row["n"]}
        for row in grouped
        if row[campo] is not None
    ]


trend = group_rows(
    mart_rows("rna_aiuti_stato__mart_aiuti_temporale", select={"anno": "anno", "esl": "totale_esl"}),
    by=["anno"],
    metrics={"importo": ("esl", "sum")},
    sort_by="anno",
)

tipi = [
    {"anno": row["anno"], "tipo": row["tipo_beneficiario"], "importo": row["importo"]}
    for row in group_rows(
        mart_rows(
            "rna_aiuti_stato__mart_aiuti_tipo_beneficiario",
            select={"anno": "anno", "tipo_beneficiario": "tipo_beneficiario", "esl": "totale_esl"},
        ),
        by=["anno", "tipo_beneficiario"],
        metrics={"importo": ("esl", "sum")},
        sort_by=["anno"],
    )
    if row["tipo_beneficiario"] is not None
]

write(
    {
        "trend": trend,
        "regioni": per_categoria(
            "rna_aiuti_stato__mart_aiuti_per_regione", "regione_beneficiario", "regione"
        ),
        "strumenti": per_categoria(
            "rna_aiuti_stato__mart_aiuti_per_strumento", "strumento", "strumento"
        ),
        "procedimenti": per_categoria(
            "rna_aiuti_stato__mart_aiuti_per_procedimento", "procedimento", "procedimento"
        ),
        "concedenti": per_categoria(
            "rna_aiuti_stato__mart_aiuti_concedenti", "soggetto_concedente", "concedente"
        ),
        "tipi": tipi,
    }
)

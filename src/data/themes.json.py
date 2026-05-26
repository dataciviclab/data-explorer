#!/usr/bin/env python3
"""Data loader: temi editoriali. Mappa slug tema → slug dataset."""
import json, sys

themes = [
    {
        "slug": "territorio-ambiente",
        "name": "Territorio e ambiente",
        "description": "Trasformazioni territoriali, ambiente, energia e rifiuti",
        "datasets": ["rifiuti-urbani", "capacita-rinnovabile"],
    },
    {
        "slug": "finanza-pubblica",
        "name": "Finanza pubblica",
        "description": "Entrate dello Stato, capacità fiscale e tributi locali",
        "datasets": ["irpef-comunale", "entrate-stato", "consip-consumi-convenzione"],
    },
    {
        "slug": "sanita",
        "name": "Sanità",
        "description": "Spesa farmaceutica, consumi sanitari e prevenzione",
        "datasets": ["spesa-farmaceutica", "bdap-lea"],
    },
    {
        "slug": "welfare-lavoro",
        "name": "Welfare e lavoro",
        "description": "Pubblico impiego, pensioni e previdenza",
        "datasets": ["dipendenti-pubblici", "pensioni-inps"],
    },
    {
        "slug": "giustizia",
        "name": "Giustizia",
        "description": "Flussi civili, tempi e carichi dei tribunali",
        "datasets": ["flussi-giustizia-civile"],
    },
]

json.dump(themes, sys.stdout, ensure_ascii=False)

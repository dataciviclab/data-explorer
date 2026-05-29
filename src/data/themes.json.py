#!/usr/bin/env python3
"""Data loader: temi editoriali. Mappa slug tema → slug dataset."""
import json, sys

themes = [
    {
        "slug": "territorio-ambiente",
        "name": "Territorio e ambiente",
        "description": "Trasformazioni territoriali, ambiente, energia e rifiuti",
        "datasets": ["rifiuti-urbani", "capacita-rinnovabile", "produzione-elettrica-fonti"],
    },
    {
        "slug": "finanza-pubblica",
        "name": "Finanza pubblica",
        "description": "Entrate dello Stato, capacità fiscale, tributi locali, FSC e disuguaglianza del reddito",
        "datasets": ["irpef-comunale", "entrate-stato", "consip-consumi-convenzione", "istat-gini-regionale", "opencivitas-fsc-2025"],
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
        "description": "Pubblico impiego, pensioni, previdenza e prezzi delle abitazioni",
        "datasets": ["dipendenti-pubblici", "pensioni-inps", "istat-ipab-aree"],
    },
    {
        "slug": "giustizia",
        "name": "Giustizia",
        "description": "Flussi civili, tempi e carichi dei tribunali",
        "datasets": ["flussi-giustizia-civile"],
    },
]

json.dump(themes, sys.stdout, ensure_ascii=False)

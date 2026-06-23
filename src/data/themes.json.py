#!/usr/bin/env python3
"""Data loader: temi editoriali. Mappa slug tema → slug dataset."""
import json, sys

themes = [
    {
        "slug": "territorio-ambiente",
        "name": "Territorio e ambiente",
        "description": "Trasformazioni territoriali, ambiente, energia, rifiuti e sicurezza stradale",
        "datasets": ["rifiuti-urbani", "capacita-rinnovabile", "produzione-elettrica-fonti", "mit-incidentalita"],
    },
    {
        "slug": "finanza-pubblica",
        "name": "Finanza pubblica",
        "description": "Entrate dello Stato, capacità fiscale, tributi locali, FSC, politiche di coesione, partecipazioni PA e disuguaglianza del reddito",
        "datasets": ["irpef-comunale", "entrate-stato", "consip-consumi-convenzione", "istat-gini-regionale", "opencivitas-fsc-2025", "opencoesione-progetti", "mef-partecipazioni", "bdap-spese-stato"],
    },
    {
        "slug": "sanita",
        "name": "Sanità",
        "description": "Spesa farmaceutica, strutture sanitarie e posti letto ospedalieri",
        "datasets": [
            "spesa-farmaceutica", "bdap-lea",
            "strutture-asl", "strutture-ricovero-asl",
            "reparti-ricovero", "posti-letto-stabilimento",
            "farmacie",
        ],
    },
    {
        "slug": "welfare-lavoro",
        "name": "Welfare e lavoro",
        "description": "Pubblico impiego, pensioni, istruzione e prezzi delle abitazioni",
        "datasets": ["dipendenti-pubblici", "pensioni-inps", "pensioni-pa-dag", "istat-ipab-aree", "mim-alunni-corso-eta", "popolazione-istat", "housing-crowding"],
    },
    {
        "slug": "giustizia",
        "name": "Giustizia",
        "description": "Flussi civili, tempi e carichi dei tribunali",
        "datasets": ["flussi-giustizia-civile"],
    },
    {
        "slug": "terzo-settore",
        "name": "Terzo settore",
        "description": "5x1000, enti non profit, flussi finanziari al terzo settore",
        "datasets": ["cinque-per-mille"],
    },
]

json.dump(themes, sys.stdout, ensure_ascii=False)

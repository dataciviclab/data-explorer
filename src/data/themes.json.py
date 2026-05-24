#!/usr/bin/env python3
"""Data loader: temi editoriali. Mappa slug tema → slug dataset."""
import json, sys

themes = [
    {
        "slug": "territorio-ambiente",
        "name": "Territorio e ambiente",
        "description": "Trasformazioni territoriali, ambiente, energia e rifiuti",
        "datasets": ["rifiuti-urbani", "capacita-rinnovabile"],
        "questions": ["Come varia la raccolta differenziata tra territori?", "Come cambia il mix elettrico regionale tra fonti fossili e rinnovabili?"],
    },
    {
        "slug": "finanza-pubblica",
        "name": "Finanza pubblica",
        "description": "Entrate dello Stato, capacità fiscale e tributi locali",
        "datasets": ["irpef-comunale", "entrate-stato"],
        "questions": ["Come si distribuisce la capacità fiscale tra regioni?", "Quali sono le principali voci di entrata dello Stato?"],
    },
    {
        "slug": "sanita",
        "name": "Sanità",
        "description": "Spesa farmaceutica, consumi sanitari e prevenzione",
        "datasets": ["spesa-farmaceutica", "bdap-lea"],
        "questions": ["Come cambia tra regioni la spesa farmaceutica per classi terapeutiche?", "Quanto spendono le regioni per i Livelli Essenziali di Assistenza?"],
    },
    {
        "slug": "welfare-lavoro",
        "name": "Welfare e lavoro",
        "description": "Pubblico impiego, pensioni e previdenza",
        "datasets": ["dipendenti-pubblici", "pensioni-inps"],
        "questions": ["La crescita del pubblico impiego è diffusa o concentrata in pochi comparti?", "Come sono distribuite le pensioni tra gestioni previdenziali?"],
    },
    {
        "slug": "giustizia",
        "name": "Giustizia",
        "description": "Flussi civili, tempi e carichi dei tribunali",
        "datasets": ["flussi-giustizia-civile"],
        "questions": ["Come si distribuisce il carico civile tra i distretti italiani?"],
    },
]

json.dump(themes, sys.stdout, ensure_ascii=False)

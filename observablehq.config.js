export default {
  root: "src",
  output: "dist/observable",
  title: "DataCivicLab Explorer",
  theme: ["air", "ocean-floor"],
  interpreters: {
    ".py": ["python3"]
  },
  pages: [
  {
    "name": "Territorio e ambiente",
    "collapsible": true,
    "pages": [
      {
        "name": "Emissioni GHG da processi energetici",
        "path": "/dataset/ispra-emissioni-ghg"
      },
      {
        "name": "Rifiuti urbani nei comuni",
        "path": "/dataset/rifiuti-urbani"
      },
      {
        "name": "Incidenti stradali",
        "path": "/dataset/mit-incidentalita"
      },
      {
        "name": "Infrastrutture strategiche SILOS",
        "path": "/dataset/silos-infrastrutture"
      },
      {
        "name": "Capacità rinnovabile per regione",
        "path": "/dataset/capacita-rinnovabile"
      },
      {
        "name": "Produzione elettrica per fonte",
        "path": "/dataset/produzione-elettrica-fonti"
      }
    ]
  },
  {
    "name": "Finanza pubblica",
    "collapsible": true,
    "pages": [
      {
        "name": "Entrate dello Stato",
        "path": "/dataset/entrate-stato"
      },
      {
        "name": "Spese dello Stato",
        "path": "/dataset/bdap-spese-stato"
      },
      {
        "name": "Consumi in convenzione Consip",
        "path": "/dataset/consip-consumi-convenzione"
      },
      {
        "name": "FTS EU Grants — Finanziamenti UE in Italia",
        "path": "/dataset/fts-eu-grants"
      },
      {
        "name": "IRPEF — quanto reddito si dichiara in ogni territorio",
        "path": "/dataset/irpef-comunale"
      },
      {
        "name": "Indice di Gini regionale",
        "path": "/dataset/istat-gini-regionale"
      },
      {
        "name": "Partecipazioni pubbliche",
        "path": "/dataset/mef-partecipazioni"
      },
      {
        "name": "Fondo di Solidarietà Comunale",
        "path": "/dataset/opencivitas-fsc-2025"
      },
      {
        "name": "OpenCoesione — Progetti delle politiche di coesione",
        "path": "/dataset/opencoesione-progetti"
      },
      {
        "name": "PNRR Gare — Italia Domani",
        "path": "/dataset/pnrr-gare"
      },
      {
        "name": "PNRR Pagamenti — Italia Domani",
        "path": "/dataset/pnrr-pagamenti"
      },
      {
        "name": "PNRR Progetti — Italia Domani",
        "path": "/dataset/pnrr-progetti"
      },
      {
        "name": "Bandi di gara pubblici ANAC",
        "path": "/dataset/anac-bandi-gara"
      }
    ]
  },
  {
    "name": "Sanità",
    "collapsible": true,
    "pages": [
      {
        "name": "Spesa farmaceutica convenzionata",
        "path": "/dataset/spesa-farmaceutica"
      },
      {
        "name": "Spesa sanitaria regionale LEA",
        "path": "/dataset/bdap-lea"
      },
      {
        "name": "Farmacie italiane",
        "path": "/dataset/farmacie"
      },
      {
        "name": "Posti letto ospedalieri",
        "path": "/dataset/posti-letto-stabilimento"
      },
      {
        "name": "Posti letto per disciplina ospedaliera",
        "path": "/dataset/reparti-ricovero"
      },
      {
        "name": "Strutture e attività delle ASL",
        "path": "/dataset/strutture-asl"
      },
      {
        "name": "Strutture di ricovero del SSN",
        "path": "/dataset/strutture-ricovero-asl"
      }
    ]
  },
  {
    "name": "Welfare e lavoro",
    "collapsible": true,
    "pages": [
      {
        "name": "Dipendenti pubblici per comparto",
        "path": "/dataset/dipendenti-pubblici"
      },
      {
        "name": "Pensioni INPS — da quali gestioni arrivano?",
        "path": "/dataset/pensioni-inps"
      },
      {
        "name": "Densità abitativa",
        "path": "/dataset/housing-crowding"
      },
      {
        "name": "Indice prezzi abitazioni (IPAB) per area",
        "path": "/dataset/istat-ipab-aree"
      },
      {
        "name": "Pensioni Pubblica Amministrazione — DAG",
        "path": "/dataset/pensioni-pa-dag"
      },
      {
        "name": "Popolazione italiana per età",
        "path": "/dataset/popolazione-istat"
      },
      {
        "name": "Alunni per corso ed età",
        "path": "/dataset/mim-alunni-corso-eta"
      }
    ]
  },
  {
    "name": "Giustizia",
    "collapsible": true,
    "pages": [
      {
        "name": "Flussi della giustizia civile",
        "path": "/dataset/flussi-giustizia-civile"
      }
    ]
  },
  {
    "name": "Terzo settore",
    "collapsible": true,
    "pages": [
      {
        "name": "5x1000 — beneficiari e importi per ente",
        "path": "/dataset/cinque-per-mille"
      }
    ]
  },
  {
    "name": "Altri dataset",
    "collapsible": true,
    "pages": [
      {
        "name": "Votazioni Camera dei Deputati",
        "path": "/dataset/votazioni-camera"
      },
      {
        "name": "Elezioni Comunali",
        "path": "/dataset/elezioni-comunali"
      },
      {
        "name": "Elezioni Europee",
        "path": "/dataset/elezioni-europee"
      },
      {
        "name": "Elezioni Politiche Italiane",
        "path": "/dataset/elezioni-politiche"
      },
      {
        "name": "Elezioni Referendum",
        "path": "/dataset/elezioni-referendum"
      },
      {
        "name": "Elezioni Regionali",
        "path": "/dataset/elezioni-regionali"
      },
      {
        "name": "Aiuti di Stato — Registro Nazionale Aiuti (RNA)",
        "path": "/dataset/rna-aiuti-stato"
      }
    ]
  },
  {
    "name": "Visioni incrociate",
    "collapsible": true,
    "pages": [
      {
        "name": "Entrate vs Spese — Il Bilancio dello Stato",
        "path": "/cross-views/entrate-vs-spese"
      },
      {
        "name": "Previsione vs Consuntivo per Missione",
        "path": "/cross-views/previsione-vs-consuntivo"
      }
    ]
  }
],
};

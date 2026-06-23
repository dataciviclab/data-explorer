export default {
  root: "src",
  output: "dist/observable",
  title: "DataCivicLab Explorer",
  theme: ["air", "ocean-floor"],
  pages: [
  {
    "name": "Territorio e ambiente",
    "collapsible": true,
    "pages": [
      {
        "name": "Rifiuti urbani nei comuni",
        "path": "/dataset/rifiuti-urbani"
      },
      {
        "name": "Capacità rinnovabile per regione",
        "path": "/dataset/capacita-rinnovabile"
      },
      {
        "name": "Produzione elettrica per fonte",
        "path": "/dataset/produzione-elettrica-fonti"
      },
      {
        "name": "Incidenti stradali",
        "path": "/dataset/mit-incidentalita"
      }
    ]
  },
  {
    "name": "Finanza pubblica",
    "collapsible": true,
    "pages": [
      {
        "name": "IRPEF comunale",
        "path": "/dataset/irpef-comunale"
      },
      {
        "name": "Entrate dello Stato",
        "path": "/dataset/entrate-stato"
      },
      {
        "name": "Consumi in convenzione Consip",
        "path": "/dataset/consip-consumi-convenzione"
      },
      {
        "name": "Indice di Gini regionale",
        "path": "/dataset/istat-gini-regionale"
      },
      {
        "name": "Fondo di Solidarietà Comunale 2025",
        "path": "/dataset/opencivitas-fsc-2025"
      },
      {
        "name": "OpenCoesione — Progetti delle politiche di coesione",
        "path": "/dataset/opencoesione-progetti"
      },
      {
        "name": "Partecipazioni pubbliche",
        "path": "/dataset/mef-partecipazioni"
      },
      {
        "name": "Spese dello Stato",
        "path": "/dataset/bdap-spese-stato"
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
        "name": "Pensioni INPS",
        "path": "/dataset/pensioni-inps"
      },
      {
        "name": "Pensioni Pubblica Amministrazione — DAG",
        "path": "/dataset/pensioni-pa-dag"
      },
      {
        "name": "Indice prezzi abitazioni (IPAB) per area",
        "path": "/dataset/istat-ipab-aree"
      },
      {
        "name": "Alunni per corso ed età",
        "path": "/dataset/mim-alunni-corso-eta"
      },
      {
        "name": "Popolazione italiana per età",
        "path": "/dataset/popolazione-istat"
      },
      {
        "name": "Densità abitativa",
        "path": "/dataset/housing-crowding"
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
    "name": "Altri dataset",
    "collapsible": true,
    "pages": [
      {
        "name": "Votazioni Camera dei Deputati",
        "path": "/dataset/votazioni-camera"
      }
    ]
  }
],
};

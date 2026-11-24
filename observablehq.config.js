export default {
  root: "src",
  output: "dist/observable",
  title: "DataCivicLab Explorer",
  theme: ["air", "ocean-floor"],
  interpreters: {
    ".py": ["python3"]
  },
  // Schede dataset: una route dinamica, N path calcolati dal file statico
  // prodotto da scripts/build-cards.py. Nessun path hardcoded qui.
  dynamicPaths: async function* () {
    try {
      const { readFileSync } = await import("node:fs");
      const cards = JSON.parse(readFileSync(new URL("./src/data/cards.json", import.meta.url), "utf-8"));
      for (const slug of Object.keys(cards)) yield `/schede/${slug}`;
    } catch {
      // Nessuna scheda generata: il sito resta valido, solo senza /schede/*
    }
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
        "name": "Incidenti stradali",
        "path": "/dataset/mit-incidentalita"
      },
      {
        "name": "Rifiuti urbani nei comuni",
        "path": "/dataset/rifiuti-urbani"
      },
      {
        "name": "Capacità rinnovabile per regione",
        "path": "/dataset/capacita-rinnovabile"
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
        "name": "FTS EU Grants — Finanziamenti UE in Italia",
        "path": "/dataset/fts-eu-grants"
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
        "name": "IRPEF — quanto reddito si dichiara in ogni territorio",
        "path": "/dataset/irpef-comunale"
      },
      {
        "name": "OpenCoesione — Progetti delle politiche di coesione",
        "path": "/dataset/opencoesione-progetti"
      },
      {
        "name": "Consumi in convenzione Consip",
        "path": "/dataset/consip-consumi-convenzione"
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
        "name": "Fondo di Solidarietà Comunale",
        "path": "/dataset/opencivitas-fsc-2025"
      },
      {
        "name": "Aiuti di Stato — Registro Nazionale Aiuti (RNA)",
        "path": "/dataset/rna-aiuti-stato"
      },
      {
        "name": "Bandi di gara pubblici ANAC",
        "path": "/dataset/anac-bandi-gara"
      },
      {
        "name": "Infrastrutture strategiche SILOS",
        "path": "/dataset/silos-infrastrutture"
      }
    ]
  },
  {
    "name": "Sanità",
    "collapsible": true,
    "pages": [
      {
        "name": "Spesa sanitaria regionale LEA",
        "path": "/dataset/bdap-lea"
      },
      {
        "name": "Spesa farmaceutica convenzionata",
        "path": "/dataset/spesa-farmaceutica"
      },
      {
        "name": "Farmacie italiane",
        "path": "/dataset/farmacie"
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
      },
      {
        "name": "Posti letto ospedalieri",
        "path": "/dataset/posti-letto-stabilimento"
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
        "name": "Pensioni Pubblica Amministrazione — DAG",
        "path": "/dataset/pensioni-pa-dag"
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
    "name": "Politica",
    "collapsible": true,
    "pages": [
      {
        "name": "Camera dei Deputati — Legislature e composizione",
        "path": "/dataset/camera-deputati"
      },
      {
        "name": "Attività in Aula — Camera dei Deputati",
        "path": "/dataset/attivita-aula"
      },
      {
        "name": "Votazioni Camera dei Deputati",
        "path": "/dataset/votazioni-camera"
      },
      {
        "name": "Voti dei Deputati — accountability parlamentare",
        "path": "/dataset/voti-deputati"
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
        "name": "Elezioni Referendum",
        "path": "/dataset/elezioni-referendum"
      },
      {
        "name": "Elezioni Regionali",
        "path": "/dataset/elezioni-regionali"
      },
      {
        "name": "Elezioni Politiche Italiane",
        "path": "/dataset/elezioni-politiche"
      }
    ]
  },
  {
    "name": "Schede dataset",
    "path": "/schede/"
  },
  {
    "name": "Altri dataset",
    "collapsible": true,
    "pages": [
      {
        "name": "Produzione elettrica per fonte",
        "path": "/dataset/produzione-elettrica-fonti"
      }
    ]
  },
  {
    "name": "Visioni incrociate",
    "collapsible": true,
    "pages": [
      {
        "name": "Chi cattura la crescita? Produttività, salari e imprese",
        "path": "/cross-views/chi-cattura-la-crescita"
      },
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

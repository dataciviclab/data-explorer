export default {
  root: "src",
  output: "dist/observable",
  title: "DataCivicLab Explorer",
  // Ricerca: OF non la attiva da solo (default null). Con true costruisce
  // l'indice delle pagine e mette il campo nella sidebar.
  search: true,
  theme: ["air", "ocean-floor"],
  interpreters: {
    ".py": ["python3"]
  },
  // Temi e schede: route dinamiche. I path dei temi vengono da themes.json
  // (generato qui), quelli delle schede dal file statico di build_cards.py.
  dynamicPaths: async function* () {
    for (const slug of ["territorio-ambiente","finanza-pubblica","sanita","welfare-lavoro","giustizia","terzo-settore","politica"]) {
      yield `/temi/${slug}`;
    }
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
    "path": "/temi/territorio-ambiente",
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
        "name": "Produzione elettrica per fonte",
        "path": "/dataset/terna-elettricita-per-fonte"
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
    "path": "/temi/finanza-pubblica",
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
        "name": "PIL territoriale",
        "path": "/schede/istat-pil-territoriale"
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
    "path": "/temi/sanita",
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
    "path": "/temi/welfare-lavoro",
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
    "path": "/temi/giustizia",
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
    "path": "/temi/terzo-settore",
    "pages": [
      {
        "name": "5x1000 — beneficiari e importi",
        "path": "/dataset/cinque-per-mille"
      }
    ]
  },
  {
    "name": "Politica",
    "collapsible": true,
    "path": "/temi/politica",
    "pages": [
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
      }
    ]
  },
  {
    "name": "Schede dataset",
    "path": "/schede/"
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

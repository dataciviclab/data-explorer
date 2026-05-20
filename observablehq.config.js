export default {
  root: "src",
  output: "dist/observable",
  title: "DataCivicLab Explorer",
  pages: [
    {
      name: "Dataset",
      collapsible: false,
      pages: [
        { name: "IRPEF comunale", path: "/dataset/irpef-comunale" },
        { name: "Rifiuti urbani", path: "/dataset/rifiuti-urbani" },
        { name: "Flussi giustizia", path: "/dataset/flussi-giustizia-civile" },
        { name: "Dipendenti pubblici", path: "/dataset/dipendenti-pubblici" },
        { name: "Capacità rinnovabile", path: "/dataset/capacita-rinnovabile" },
        { name: "Spesa farmaceutica", path: "/dataset/spesa-farmaceutica" },
        { name: "Entrate dello Stato", path: "/dataset/entrate-stato" },
        { name: "Pensioni INPS", path: "/dataset/pensioni-inps" },
      ],
    },
    {
      name: "Temi",
      collapsible: false,
      pages: [
        { name: "Territorio e ambiente", path: "/temi/territorio-ambiente" },
        { name: "Finanza pubblica", path: "/temi/finanza-pubblica" },
        { name: "Sanità", path: "/temi/sanita" },
        { name: "Welfare e lavoro", path: "/temi/welfare-lavoro" },
        { name: "Giustizia", path: "/temi/giustizia" },
      ],
    },
  ],
};

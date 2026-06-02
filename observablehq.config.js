export default {
  root: "src",
  output: "dist/observable",
  title: "DataCivicLab Explorer",
  theme: ["air", "ocean-floor"],
  pages: [
    {
      name: "Territorio e ambiente",
      collapsible: true,
      pages: [
        { name: "Rifiuti urbani", path: "/dataset/rifiuti-urbani" },
        { name: "Capacità rinnovabile", path: "/dataset/capacita-rinnovabile" },
        { name: "Produzione elettrica", path: "/dataset/produzione-elettrica-fonti" },
      ],
    },
    {
      name: "Finanza pubblica",
      collapsible: true,
      pages: [
        { name: "IRPEF comunale", path: "/dataset/irpef-comunale" },
        { name: "Entrate dello Stato", path: "/dataset/entrate-stato" },
        { name: "Consumi Consip", path: "/dataset/consip-consumi-convenzione" },
        { name: "Fondo Solidarietà Comunale", path: "/dataset/opencivitas-fsc-2025" },
        { name: "Indice di Gini regionale", path: "/dataset/istat-gini-regionale" },
      ],
    },
    {
      name: "Sanità",
      collapsible: true,
      pages: [
        { name: "Spesa farmaceutica", path: "/dataset/spesa-farmaceutica" },
        { name: "Spesa sanitaria LEA", path: "/dataset/bdap-lea" },
      ],
    },
    {
      name: "Welfare e lavoro",
      collapsible: true,
      pages: [
        { name: "Dipendenti pubblici", path: "/dataset/dipendenti-pubblici" },
        { name: "Pensioni INPS", path: "/dataset/pensioni-inps" },
        { name: "Indice prezzi IPAB", path: "/dataset/istat-ipab-aree" },
        { name: "Alunni corso/età", path: "/dataset/mim-alunni-corso-eta" },
      ],
    },
    {
      name: "Giustizia",
      collapsible: true,
      pages: [
        { name: "Flussi giustizia", path: "/dataset/flussi-giustizia-civile" },
      ],
    },
    {
      name: "Altri dataset",
      collapsible: true,
      pages: [
        { name: "Votazioni Camera", path: "/dataset/votazioni-camera" },
        { name: "Popolazione per età", path: "/dataset/popolazione-istat" },
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

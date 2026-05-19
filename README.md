# data-explorer

Frontend pubblico dati del Lab, basato su **Observable Framework**, DuckDB e clean parquet pubblici su GCS.

**Live**: [explorer.dataciviclab.org](https://explorer.dataciviclab.org)

## Setup

```bash
npm install --legacy-peer-deps
pip install -r requirements.txt
npm run dev
```

Apri http://localhost:3000

## Pagine

| Pagina | Dataset |
|---|---|
| Home | Catalogo completo dei dataset |
| IRPEF comunale | Capacità fiscale per comune e regione |
| Rifiuti urbani | Produzione e raccolta differenziata |
| Flussi giustizia civile | Sopravvenuti, definiti e pendenti |
| Dipendenti pubblici | Pubblico impiego per comparto |
| Capacità rinnovabile | Potenza installata Terna |
| Spesa farmaceutica | AIFA spesa e consumo SSN |
| Entrate dello Stato | Previsioni BDAP RGS |
| Pensioni INPS | Numero pensioni per gestione |

## Data loader

Gli script Python in `src/data/` leggono i parquet da GCS via DuckDB a build time e producono JSON aggregato. La utility `_util.py` gestisce GROUP BY, WHERE e skip anni mancanti.

## Deploy

Su **GitHub Pages** via workflow CI: `npm run build` → `observable build` → deploy su `explorer.dataciviclab.org`.

## Stack

- **Observable Framework** — static site generator
- **Observable Plot** — chart
- **DuckDB** — query engine per parquet su GCS
- **Python** — data loader

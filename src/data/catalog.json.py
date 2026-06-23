#!/usr/bin/env python3
import json, sys, requests
url = "https://raw.githubusercontent.com/dataciviclab/dataset-incubator/main/registry/clean_catalog.json"
r = requests.get(url, timeout=15)
cat = r.json()

# URL_SLUG_OVERRIDES: mapping eccezioni per slug URL pubblici.
#
# La regola di default converte meccanicamente lo slug DI (underscore)
# in URL slug (hyphen):  "aifa_spesa_consumo" → "aifa-spesa-consumo".
#
# Per i dataset ereditati dalla fase Evidence, gli slug URL sono stati
# scelti editorialmente e NON seguono lo slug DI. Ogni entry qui sotto
# documenta questa divergenza.
#
# Per i NUOVI dataset: se l'URL slug meccanico va bene, non serve aggiungere
# nulla qui. Se serve un nome URL diverso, aggiungi l'override con commento.
URL_SLUG_OVERRIDES = {
    "aifa_spesa_consumo": "spesa-farmaceutica",             # editoriale: nome tema
    "ispra_ru_base": "rifiuti-urbani",                      # editoriale: nome tema
    "civile_flussi": "flussi-giustizia-civile",             # editoriale: specifica tema
    "terna_capacita_rinnovabile": "capacita-rinnovabile",   # editoriale: nome tema
    "terna_electricity_by_source": "produzione-elettrica-fonti",  # editoriale: nome tema
    "camera_votazioni_sparql": "votazioni-camera",          # editoriale: nome tema
    "bdap_entrate_stato": "entrate-stato",                  # editoriale: nome tema
    "inps_pensioni_trimestrale": "pensioni-inps",           # editoriale: nome tema
}

def resolve_url_slug(di_slug: str) -> str:
    """Risolve lo slug DI (underscore) in URL slug (hyphen).

    Default: sostituzione meccanica _ → -.
    Override: se presente in URL_SLUG_OVERRIDES.
    """
    return URL_SLUG_OVERRIDES.get(di_slug, di_slug.replace("_", "-"))

datasets = []
for ds in cat.get("datasets", []):
    period = ds.get("period", {})
    slug = ds["slug"]
    url_slug = resolve_url_slug(slug)
    datasets.append({
        "slug": slug,
        "url_slug": url_slug,
        "name": ds.get("name", ""),
        "description": ds.get("description", "")[:150],
        "stage": ds.get("stage", ""),
        "years": f"{period.get('start','?')}–{period.get('end','?')}" if period else "?",
        "source": ds.get("source", ""),
    })
output = {
    "updated_at": cat.get("updated_at", ""),
    "total": len(datasets),
    "published": sum(1 for d in datasets if d["stage"] == "published"),
    "incubating": sum(1 for d in datasets if d["stage"] == "incubating"),
    "datasets": datasets,
}
json.dump(output, sys.stdout, ensure_ascii=False)

#!/usr/bin/env python3
import json, sys, requests
url = "https://raw.githubusercontent.com/dataciviclab/dataset-incubator/main/registry/clean_catalog.json"
r = requests.get(url, timeout=15)
cat = r.json()

# Mapping DI slug (underscore) → URL slug (hyphen) per pagine Explorer.
# Fallback: sostituisce _ con - meccanicamente.
SLUG_MAP = {
    "aifa_spesa_consumo": "spesa-farmaceutica",
    "ispra_ru_base": "rifiuti-urbani",
    "civile_flussi": "flussi-giustizia-civile",
    "terna_capacita_rinnovabile": "capacita-rinnovabile",
    "terna_electricity_by_source": "produzione-elettrica-fonti",
    "camera_votazioni_sparql": "votazioni-camera",
    "bdap_entrate_stato": "entrate-stato",
    "inps_pensioni_trimestrale": "pensioni-inps",
}

datasets = []
for ds in cat.get("datasets", []):
    period = ds.get("period", {})
    slug = ds["slug"]
    url_slug = SLUG_MAP.get(slug, slug.replace("_", "-"))
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

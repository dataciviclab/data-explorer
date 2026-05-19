#!/usr/bin/env python3
import json, sys, requests
url = "https://raw.githubusercontent.com/dataciviclab/dataset-incubator/main/registry/clean_catalog.json"
r = requests.get(url, timeout=15)
cat = r.json()
datasets = []
for ds in cat.get("datasets", []):
    period = ds.get("period", {})
    datasets.append({"slug": ds["slug"], "name": ds.get("name", ""), "description": ds.get("description", "")[:150], "stage": ds.get("stage", ""), "years": f"{period.get('start','?')}–{period.get('end','?')}" if period else "?", "source": ds.get("source", "")})
output = {"updated_at": cat.get("updated_at", ""), "total": len(datasets), "published": sum(1 for d in datasets if d["stage"] == "published"), "incubating": sum(1 for d in datasets if d["stage"] == "incubating"), "datasets": datasets}
json.dump(output, sys.stdout, ensure_ascii=False)

#!/usr/bin/env python3
"""Data loader: Terna produzione elettrica — per fonte, regione e anno.

Legge la location dichiarata in ACB (`energia_italia/terna_elettricita_per_fonte`),
non il path canonico con lo slug vecchio `terna_electricity_by_source`: quella
copia legacy aveva numeri diversi (totale 2.864.678 GWh contro 2.747.283).

Perimetro: dal 2015 (inizio editoriale della pagina) all'ultimo anno completo,
ricavati dai file pubblicati — nessun anno scritto a mano.
"""

import sys

sys.path.insert(0, "src/data")
from _util import get_location, load_dataset
from _views import last_complete_year, years_in
from lab_connectors.gcs.paths import location_urls

SLUG = "terna_elettricita_per_fonte"
ANNO_MIN = 2015  # inizio del perimetro editoriale della pagina

location = get_location(SLUG)
anni = [
    anno
    for anno in years_in(location_urls(location))
    if ANNO_MIN <= anno <= last_complete_year()
]

load_dataset(
    slug=SLUG,
    years=anni,
    group_cols=["anno", "fonte", "regione"],
    metric_cols=["produzione_gwh"],
    where="tipo_produzione = 'Netta'",
    location=location,
)

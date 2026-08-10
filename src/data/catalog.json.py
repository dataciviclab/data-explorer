#!/usr/bin/env python3
"""Data loader: catalogo explorer derivato dal registry dataset-incubator.

Legge registry/registry.json (fusion registry) e produce il catalogo
esposto al frontend (index, temi page, sidebar build). La logica di
costruzione è in _registry.build_catalog() (testabile e condivisa).
"""
import json
import sys

sys.path.insert(0, "src/data")
from _registry import build_catalog, load_registry

json.dump(build_catalog(load_registry()), sys.stdout, ensure_ascii=False)

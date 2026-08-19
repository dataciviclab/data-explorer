#!/usr/bin/env python3
"""Data loader: catalogo explorer dai registry multi-repo (fusion).

Legge i registry.json di TUTTI i repo del Lab (fusion ADR) e produce il
catalogo esposto al frontend (index, temi page, sidebar build). La logica
di costruzione è in _registry.fuse_registries()/build_catalog() (testabile
e condivisa).
"""
import json
import sys

sys.path.insert(0, "src/data")
from _registry import build_catalog, load_registry

json.dump(build_catalog(load_registry()), sys.stdout, ensure_ascii=False)

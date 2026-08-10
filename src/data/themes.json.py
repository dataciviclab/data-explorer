#!/usr/bin/env python3
"""Data loader: temi dinamici dal registry (category) + config editoriale.

La mappatura category → tema è in catalog/themes.json (single source).
I dataset entrano in un tema se hanno una pagina explorer e category
mappata (lo stage registry è irrilevante).
"""
import json
import sys

sys.path.insert(0, "src/data")
from _registry import build_themes

json.dump(build_themes(), sys.stdout, ensure_ascii=False)

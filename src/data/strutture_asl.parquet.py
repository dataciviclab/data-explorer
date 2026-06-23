#!/usr/bin/env python3
"""Data loader binario: copia parquet pulito da GCS (nessuna aggregazione)."""
import sys
import urllib.request

URL = "https://storage.googleapis.com/dataciviclab-clean/strutture_asl/2022/strutture_asl_2022_clean.parquet"
sys.stdout.buffer.write(urllib.request.urlopen(URL).read())

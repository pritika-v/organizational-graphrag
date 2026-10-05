import json
from pathlib import Path
from .config import DATA_DIR

def load_data():
    with open(DATA_DIR / 'organization.json', encoding='utf-8') as f:
        org = json.load(f)
    with open(DATA_DIR / 'benchmark.json', encoding='utf-8') as f:
        benchmark = json.load(f)
    return org, benchmark

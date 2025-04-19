# === File: data_utils.py ===
# Helper functions for saving/loading and normalization

import os
from models import School
import json


DATA_FILE = "schools_data.json"

def normalize_name(name):
    if " - " in name:
        base_name = name.split(" - ")[0]
    else:
        base_name = name
    return base_name.strip().lower()

def load_schools():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        raw_data = json.load(f)
    schools = [School.from_dict(item) for item in raw_data]
    return schools

def save_schools(schools):
    with open(DATA_FILE, 'w') as f:
        json.dump([s.to_dict() for s in schools], f, indent=2)
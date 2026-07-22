#!/usr/bin/env python
"""Fetch Brecke Conflict Catalog."""
from pathlib import Path
from mahan_vs_attrition.ingest import brecke

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")

if __name__ == "__main__":
    brecke.run(RAW_DIR / "brecke", OUTPUT_DIR)

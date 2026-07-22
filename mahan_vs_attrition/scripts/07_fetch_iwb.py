#!/usr/bin/env python
"""Import Interstate War Battle Dataset."""
from pathlib import Path
from mahan_vs_attrition.ingest import iwb

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")

if __name__ == "__main__":
    iwb.run(RAW_DIR / "iwb", OUTPUT_DIR)

#!/usr/bin/env python
"""Fetch UCDP Battle-Related Deaths data."""
from pathlib import Path
from mahan_vs_attrition.ingest import ucdp

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")

if __name__ == "__main__":
    ucdp.run(RAW_DIR / "ucdp", OUTPUT_DIR)

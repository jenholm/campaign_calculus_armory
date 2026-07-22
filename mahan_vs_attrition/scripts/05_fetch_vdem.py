#!/usr/bin/env python
"""Fetch V-Dem dataset."""
from pathlib import Path
from mahan_vs_attrition.ingest import vdem

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")

if __name__ == "__main__":
    vdem.run(RAW_DIR / "vdem", OUTPUT_DIR)

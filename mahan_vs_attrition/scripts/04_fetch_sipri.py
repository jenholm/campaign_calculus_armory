#!/usr/bin/env python
"""Fetch SIPRI Military Expenditure data."""
from pathlib import Path
from mahan_vs_attrition.ingest import sipri

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")

if __name__ == "__main__":
    sipri.run(RAW_DIR / "sipri", OUTPUT_DIR)

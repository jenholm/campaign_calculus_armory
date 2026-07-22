#!/usr/bin/env python
"""Fetch COW War and NMC data."""
from pathlib import Path
from mahan_vs_attrition.ingest import cow_nmc, cow_war

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")

if __name__ == "__main__":
    cow_nmc.run(RAW_DIR / "cow_nmc", OUTPUT_DIR)
    cow_war.run(RAW_DIR / "cow_war", OUTPUT_DIR)

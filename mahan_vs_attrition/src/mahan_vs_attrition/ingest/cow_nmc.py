"""COW National Material Capabilities (NMC v7.0) ingestion.

Downloads and processes the NMC dataset providing annual state-level
capability indicators from 1816-2022.
"""

import io
import logging
import zipfile
from pathlib import Path

import pandas as pd
import requests
import urllib3

from mahan_vs_attrition.ingest.base import sha256_hash, write_source_log

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

NMC_URL = "https://correlatesofwar.org/wp-content/uploads/NMCv7.zip"


def download_nmc(raw_dir: Path, force: bool = False) -> Path:
    """Download NMC dataset, handling nested zip structure."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    csv_path = raw_dir / "NMC-70-abridged.csv"

    if csv_path.exists() and not force:
        logger.info(f"NMC already exists at {csv_path}, skipping download")
        return csv_path

    outer_zip_path = raw_dir / "NMCv7.zip"
    logger.info(f"Downloading NMC from {NMC_URL}...")
    resp = requests.get(NMC_URL, timeout=300, verify=False)
    resp.raise_for_status()
    outer_zip_path.write_bytes(resp.content)

    # Nested zip: NMCv7.zip -> NMCv7/NMC-v7-abridged.zip -> NMC-70-abridged.csv
    with zipfile.ZipFile(outer_zip_path) as outer_zf:
        inner_name = [n for n in outer_zf.namelist() if "abridged.zip" in n]
        if inner_name:
            inner_data = outer_zf.read(inner_name[0])
            with zipfile.ZipFile(io.BytesIO(inner_data)) as inner_zf:
                csv_name = [n for n in inner_zf.namelist() if n.endswith(".csv")][0]
                csv_data = inner_zf.read(csv_name)
                csv_path.write_bytes(csv_data)
                logger.info(f"NMC extracted: {csv_name} -> {csv_path}")
        else:
            logger.error("Could not find NMC-v7-abridged.zip inside NMCv7.zip")
            return csv_path

    return csv_path


def ingest_nmc(csv_path: Path, output_dir: Path) -> pd.DataFrame:
    """Parse NMC CSV into a clean parquet file."""
    df = pd.read_csv(csv_path, encoding="latin1")

    col_map = {
        "ccode": "cow_code",
        "state": "state_name",
        "year": "year",
        "milex": "military_expenditure",
        "milper": "military_personnel",
        "irst": "iron_steel",
        "pec": "energy_consumption",
        "tpop": "population",
        "upop": "urban_population",
        "cinc": "cinc",
    }
    df = df.rename(columns=col_map)
    df = df[[c for c in col_map.values() if c in df.columns]]

    numeric_cols = [
        "military_expenditure", "military_personnel", "iron_steel",
        "energy_consumption", "population", "urban_population", "cinc",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "cow_nmc.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"NMC written to {out_path} ({len(df)} rows)")

    return df


def run(raw_dir: Path, output_dir: Path, force_download: bool = False) -> None:
    """Full NMC ingestion pipeline."""
    csv_path = download_nmc(raw_dir, force=force_download)
    if not csv_path.exists():
        logger.error("NMC CSV not found after download")
        return
    df = ingest_nmc(csv_path, output_dir)

    h = sha256_hash(csv_path)
    write_source_log(
        db_path=output_dir / "source_log.duckdb",
        source_id="cow_nmc",
        source_name="COW National Material Capabilities v7.0",
        local_path=csv_path,
        hash_sha256=h,
        source_url=NMC_URL,
        license_notes="Check COW terms of use",
        citation=(
            "Singer, J. David (1987). 'Reconstructing the Correlates of War "
            "Dataset on Material Capabilities of States, 1816-1985.'"
        ),
        notes=f"{len(df)} rows, {df['year'].min()}-{df['year'].max()}",
    )

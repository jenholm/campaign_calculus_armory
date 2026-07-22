"""V-Dem dataset ingestion."""

import logging
from pathlib import Path

import pandas as pd
import requests

from mahan_vs_attrition.ingest.base import sha256_hash, write_source_log

logger = logging.getLogger(__name__)

VDEM_URL = "https://www.v-dem.net/vdemds/V-Dem-CY-full+others-v14.rds"


def download_vdem(raw_dir: Path, force: bool = False) -> Path:
    """Download V-Dem dataset."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_path = raw_dir / "vdem_cy.rds"

    if out_path.exists() and not force:
        logger.info(f"V-Dem data exists at {out_path}, skipping")
        return out_path

    logger.info(f"Downloading V-Dem from {VDEM_URL}...")
    resp = requests.get(VDEM_URL, timeout=600)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    logger.info(f"V-Dem saved to {out_path}")
    return out_path


def ingest_vdem(rds_path: Path, output_dir: Path) -> pd.DataFrame:
    """Parse V-Dem RDS into parquet (requires pyreadr or similar)."""
    try:
        import pyreadr

        result = pyreadr.read_r(rds_path)
        df = result[None] if None in result else list(result.values())[0]
    except ImportError:
        logger.warning("pyreadr not installed. Install with: uv add pyreadr")
        df = pd.DataFrame()

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "vdem.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"V-Dem written to {out_path} ({len(df)} rows)")
    return df


def run(raw_dir: Path, output_dir: Path, force_download: bool = False) -> None:
    rds_path = download_vdem(raw_dir, force=force_download)
    df = ingest_vdem(rds_path, output_dir)
    if len(df) > 0:
        h = sha256_hash(rds_path)
        write_source_log(
            db_path=output_dir / "source_log.duckdb",
            source_id="vdem",
            source_name="V-Dem Dataset v14",
            local_path=rds_path,
            hash_sha256=h,
            source_url=VDEM_URL,
            license_notes="V-Dem data is publicly available with registration",
            citation="Coppedge, Michael, et al. 'V-Dem [Country-Year/Country-Date] Dataset v14'",
            notes=f"{len(df)} rows",
        )

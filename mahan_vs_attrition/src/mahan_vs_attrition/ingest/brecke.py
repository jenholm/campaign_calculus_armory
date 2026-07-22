"""Brecke Conflict Catalog ingestion stub."""

import logging
from pathlib import Path

import pandas as pd
import requests

from mahan_vs_attrition.ingest.base import sha256_hash, write_source_log

logger = logging.getLogger(__name__)

BRECKE_URL = (
    "https://bpb-us-e1.wpmucdn.com/sites.gatech.edu/dist/1/19/files/2018/09/"
    "Conflict-Catalog-18-vars.xlsx"
)
# Redirects to a CDN via BunnyCDN; requests handles 302 by default


def download_brecke(raw_dir: Path, force: bool = False) -> Path:
    """Download Brecke Conflict Catalog."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_path = raw_dir / "brecke_conflict_catalog.xlsx"

    if out_path.exists() and not force:
        logger.info(f"Brecke data exists at {out_path}, skipping")
        return out_path

    logger.info(f"Downloading Brecke from {BRECKE_URL}...")
    resp = requests.get(BRECKE_URL, timeout=300)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    logger.info(f"Brecke saved to {out_path}")
    return out_path


def ingest_brecke(xlsx_path: Path, output_dir: Path) -> pd.DataFrame:
    """Parse Brecke Excel into parquet."""
    df = pd.read_excel(xlsx_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "brecke_conflicts.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"Brecke written to {out_path} ({len(df)} rows)")
    return df


def run(raw_dir: Path, output_dir: Path, force_download: bool = False) -> None:
    xlsx_path = download_brecke(raw_dir, force=force_download)
    df = ingest_brecke(xlsx_path, output_dir)
    h = sha256_hash(xlsx_path)
    write_source_log(
        db_path=output_dir / "source_log.duckdb",
        source_id="brecke",
        source_name="Brecke Conflict Catalog v1 (2019)",
        local_path=xlsx_path,
        hash_sha256=h,
        source_url=BRECKE_URL,
        license_notes="Publicly available for research use",
        citation="Brecke, P. (2019). Conflict Catalog v1.",
        notes=f"{len(df)} rows",
    )

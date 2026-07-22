"""UCDP Battle-Related Deaths ingestion."""

import logging
from pathlib import Path

import pandas as pd
import requests

from mahan_vs_attrition.ingest.base import sha256_hash, write_source_log

logger = logging.getLogger(__name__)

UCDP_BRD_URL = "https://ucdp.uu.se/downloads/brd/ucdp-brd-conf-261-csv.zip"


def download_ucdp(raw_dir: Path, force: bool = False) -> Path:
    """Download UCDP BRD dataset."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    zip_path = raw_dir / "ucdp-brd-conf-261-csv.zip"
    csv_path = raw_dir / "ucdp_brd.csv"

    if csv_path.exists() and not force:
        logger.info(f"UCDP data exists at {csv_path}, skipping")
        return csv_path

    logger.info(f"Downloading UCDP BRD from {UCDP_BRD_URL}...")
    resp = requests.get(UCDP_BRD_URL, timeout=300)
    resp.raise_for_status()
    zip_path.write_bytes(resp.content)

    import zipfile
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(raw_dir)

    extracted = list(raw_dir.glob("**/*.csv"))
    if extracted:
        csv_path = extracted[0]

    logger.info(f"UCDP saved to {csv_path}")
    return csv_path


def ingest_ucdp(csv_path: Path, output_dir: Path) -> pd.DataFrame:
    """Parse UCDP CSV into parquet."""
    df = pd.read_csv(csv_path, encoding="utf-8", low_memory=False)
    col_map = {
        "conflict_id": "conflict_id",
        "year": "year",
        "side_a": "side_a",
        "side_b": "side_b",
        "bd_best": "deaths_best",
        "bd_low": "deaths_low",
        "bd_high": "deaths_high",
    }
    available = {k: v for k, v in col_map.items() if k in df.columns}
    df = df.rename(columns=available)
    for c in ["deaths_best", "deaths_low", "deaths_high"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "ucdp_battle_deaths.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"UCDP written to {out_path} ({len(df)} rows)")
    return df


def run(raw_dir: Path, output_dir: Path, force_download: bool = False) -> None:
    csv_path = download_ucdp(raw_dir, force=force_download)
    df = ingest_ucdp(csv_path, output_dir)
    h = sha256_hash(csv_path)
    write_source_log(
        db_path=output_dir / "source_log.duckdb",
        source_id="ucdp_battle_deaths",
        source_name="UCDP Battle-Related Deaths v25.1",
        local_path=csv_path,
        hash_sha256=h,
        source_url=UCDP_BRD_URL,
        license_notes="UCDP data is publicly available",
        citation="UCDP Battle-Related Deaths Dataset v25.1",
        notes=f"{len(df)} rows, {df['year'].min()}-{df['year'].max()}",
    )

"""COW War Data ingestion (Dyadic Interstate War, Intra-State v5.1)."""

import logging
from pathlib import Path

import pandas as pd
import requests
import urllib3

from mahan_vs_attrition.ingest.base import sha256_hash, write_source_log

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

COW_WAR_URL_INTERSTATE = (
    "https://correlatesofwar.org/wp-content/uploads/Dyadic-Interstate-War-Dataset.zip"
)
COW_WAR_URL_INTRASTATE = (
    "https://correlatesofwar.org/wp-content/uploads/Intra-State-Wars-v5.1.zip"
)


def download_cow_war(raw_dir: Path, force: bool = False) -> list[Path]:
    """Download COW war datasets."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    csv_files = list(raw_dir.glob("**/*.csv"))
    if csv_files and not force:
        logger.info(f"COW war data exists in {raw_dir}, skipping")
        return csv_files

    for label, url in [
        ("interstate", COW_WAR_URL_INTERSTATE),
        ("intrastate", COW_WAR_URL_INTRASTATE),
    ]:
        zip_path = raw_dir / f"cow_war_{label}.zip"
        logger.info(f"Downloading {label} war data from {url}...")
        try:
            resp = requests.get(url, timeout=300, verify=False)
            resp.raise_for_status()
            zip_path.write_bytes(resp.content)
            import zipfile
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(raw_dir)
        except Exception as e:
            logger.warning(f"Failed to download {label} war data: {e}")

    csv_files = list(raw_dir.glob("**/*.csv"))
    logger.info(f"Found {len(csv_files)} CSV files in {raw_dir}")
    return csv_files


def ingest_cow_war(raw_dir: Path, output_dir: Path) -> pd.DataFrame:
    """Parse COW war CSVs into parquet."""
    csv_files = download_cow_war(raw_dir)

    if not csv_files:
        logger.warning("No COW war CSV files found")
        df = pd.DataFrame()
        df.to_parquet(output_dir / "cow_war.parquet", index=False)
        return df

    dfs = []
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding="latin1", low_memory=False)
            dfs.append(df)
        except Exception as e:
            logger.warning(f"Skipping {csv_file.name}: {e}")

    df = pd.concat(dfs, ignore_index=True, sort=False) if dfs else pd.DataFrame()

    # Convert object columns to string to avoid mixed-type issues with parquet
    for col in df.select_dtypes(include=["object", "str"]).columns:
        df[col] = df[col].astype(str)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "cow_war.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"COW war data written to {out_path} ({len(df)} rows)")
    return df


def run(raw_dir: Path, output_dir: Path) -> None:
    df = ingest_cow_war(raw_dir, output_dir)
    csv_files = list(raw_dir.glob("**/*.csv"))
    if csv_files:
        h = sha256_hash(csv_files[0])
        write_source_log(
            db_path=output_dir / "source_log.duckdb",
            source_id="cow_war",
            source_name="COW War Data",
            local_path=csv_files[0],
            hash_sha256=h,
            source_url=COW_WAR_URL_INTERSTATE,
            license_notes="Check COW terms of use",
            citation="Sarkees, M. R., & Wayman, F. (2010). Resort to War: 1816-2007.",
            notes=f"{len(df)} rows",
        )

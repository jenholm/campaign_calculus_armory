"""Autocracies of the World (AoW) dataset ingestion.

Regime type, leadership, and instability indicators, 1950-2012.
"""

import logging
from pathlib import Path

import pandas as pd

from mahan_vs_attrition.ingest.base import sha256_hash, write_source_log

logger = logging.getLogger(__name__)


def ingest_aow(raw_dir: Path, output_dir: Path) -> pd.DataFrame:
    """Ingest AoW dataset."""
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = raw_dir / "aow_v1.csv"

    if not csv_path.exists():
        logger.warning(f"AoW CSV not found at {csv_path}")
        pd.DataFrame().to_parquet(output_dir / "aow.parquet", index=False)
        return pd.DataFrame()

    df = pd.read_csv(csv_path, encoding="ISO-8859-1")

    for col in df.select_dtypes(include=["object", "str"]).columns:
        df[col] = df[col].astype(str)

    out_path = output_dir / "aow.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"AoW written to {out_path} ({len(df)} rows, {df['ccode'].nunique()} countries)")
    return df


def run(raw_dir: Path, output_dir: Path) -> None:
    df = ingest_aow(raw_dir, output_dir)
    csv_path = raw_dir / "aow_v1.csv"
    if csv_path.exists():
        h = sha256_hash(csv_path)
        write_source_log(
            db_path=output_dir / "source_log.duckdb",
            source_id="aow",
            source_name="Autocracies of the World",
            local_path=csv_path,
            hash_sha256=h,
            source_url="https://www.ericmin.com/s/aow_v1.csv",
            license_notes="CC attribution (Magaloni, Chu, Min 2013)",
            citation="Magaloni, Chu & Min (2013). Autocracies of the World, 1950-2012.",
            notes=f"{len(df)} rows",
        )

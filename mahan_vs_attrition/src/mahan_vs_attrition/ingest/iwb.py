"""Interstate War Battle (IWB) Dataset ingestion.

Sources: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/KLQFAP
"""

import logging
from pathlib import Path

import pandas as pd

from mahan_vs_attrition.ingest.base import sha256_hash, write_source_log

logger = logging.getLogger(__name__)

IWB_URL = "https://dataverse.harvard.edu/api/access/datafile/4435240"


def download_iwb(raw_dir: Path, force: bool = False) -> Path | None:
    """Download IWB dataset from Harvard Dataverse."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    out = raw_dir / "iwbd1.0.tab"
    if out.exists() and not force:
        logger.info(f"IWB data exists at {out}, skipping")
        return out
    import requests
    logger.info(f"Downloading IWB from {IWB_URL}...")
    resp = requests.get(IWB_URL, timeout=120)
    resp.raise_for_status()
    out.write_bytes(resp.content)
    logger.info(f"Downloaded IWB to {out} ({len(resp.content)} bytes)")
    return out


def ingest_iwb(raw_dir: Path, output_dir: Path) -> pd.DataFrame:
    """Ingest Interstate War Battle dataset."""
    output_dir.mkdir(parents=True, exist_ok=True)

    tab_file = raw_dir / "iwbd1.0.tab"
    if not tab_file.exists():
        tab_file = download_iwb(raw_dir)

    if not tab_file.exists():
        logger.warning(f"IWB data not found at {tab_file}")
        df = pd.DataFrame()
        df.to_parquet(output_dir / "iwb_battles.parquet", index=False)
        return df

    df = pd.read_csv(tab_file, sep="\t", encoding="ISO-8859-1")

    for col in df.select_dtypes(include=["object", "str"]).columns:
        df[col] = df[col].astype(str)

    out_path = output_dir / "iwb_battles.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"IWB written to {out_path} ({len(df)} rows, {df['cowNum'].nunique()} wars)")
    return df


def run(raw_dir: Path, output_dir: Path) -> None:
    df = ingest_iwb(raw_dir, output_dir)
    tab_file = raw_dir / "iwbd1.0.tab"
    if tab_file.exists():
        h = sha256_hash(tab_file)
        write_source_log(
            db_path=output_dir / "source_log.duckdb",
            source_id="iwb",
            source_name="Interstate War Battle Dataset",
            local_path=tab_file,
            hash_sha256=h,
            source_url="https://doi.org/10.7910/DVN/KLQFAP",
            license_notes="CC0 1.0",
            citation=(
                "Min, E. (2021). Interstate War Battle dataset (1823-2003). "
                "Journal of Peace Research 58(2): 294-303."
            ),
            notes=f"{len(df)} rows, {df['cowNum'].nunique() if len(df) > 0 else 0} wars",
        )

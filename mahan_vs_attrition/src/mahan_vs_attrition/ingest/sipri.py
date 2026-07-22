"""SIPRI Military Expenditure Database ingestion.

The SIPRI Excel file has a complex layout:
- Header rows (0-4) with metadata
- Row 5: column headers (Country, empty, Notes, 1949, 1950, ...)
- Row 6: empty separator
- Row 7+: data, with regional groupings and country-level rows
"""

import logging
from pathlib import Path

import pandas as pd
import requests

from mahan_vs_attrition.ingest.base import sha256_hash, write_source_log

logger = logging.getLogger(__name__)

SIPRI_MILEX_URL = (
    "https://www.sipri.org/sites/default/files/SIPRI-Milex-data-1949-2024.xlsx"
)


def download_sipri(raw_dir: Path, force: bool = False) -> Path:
    """Download SIPRI military expenditure data."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_path = raw_dir / "sipri_milex.xlsx"

    if out_path.exists() and not force:
        logger.info(f"SIPRI data exists at {out_path}, skipping")
        return out_path

    logger.info(f"Downloading SIPRI from {SIPRI_MILEX_URL}...")
    resp = requests.get(SIPRI_MILEX_URL, timeout=300)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    logger.info(f"SIPRI saved to {out_path}")
    return out_path


def _parse_sipri_sheet(xlsx_path: Path, sheet_name: str) -> pd.DataFrame:
    """Parse a SIPRI sheet into a country-year DataFrame.

    The sheet has header info in rows 0-4, column headers in row 5,
    then data from row 7 onwards with region groupings mixed in.
    """
    raw = pd.read_excel(
        xlsx_path, sheet_name=sheet_name, header=None, skiprows=5
    )
    raw.columns = raw.iloc[0]
    raw = raw.iloc[2:]  # skip empty row and repeated header

    years_cols = [c for c in raw.columns if isinstance(c, (int, float)) and 1900 <= c <= 2100]
    if not years_cols:
        return pd.DataFrame()

    id_cols = [c for c in raw.columns if c not in years_cols]
    # Use first column as country name, extract notes if present
    country_col = id_cols[0] if id_cols else None
    if country_col is None:
        return pd.DataFrame()

    records = []
    for _, row in raw.iterrows():
        country = str(row[country_col]).strip()
        if not country or country in ("nan", ""):
            continue
        # skip region headers (all-caps rows like "AFRICA")
        if country.isupper() and len(country) < 30:
            continue
        if country in ("Country", "", ". ."):
            continue

        for year in years_cols:
            val = row.get(year)
            if pd.notna(val) and val not in ("...", "xxx", ""):
                try:
                    records.append({
                        "country": country,
                        "year": int(year),
                        "value": float(val),
                        "sheet": sheet_name,
                    })
                except (ValueError, TypeError):
                    pass

    return pd.DataFrame(records)


def ingest_sipri(xlsx_path: Path, output_dir: Path) -> pd.DataFrame:
    """Parse SIPRI Excel into a tidy parquet file."""
    sheet_names = pd.ExcelFile(xlsx_path).sheet_names

    # Parse the most useful sheets
    target_sheets = [
        "Constant (2023) US$",
        "Current US$",
        "Share of GDP",
    ]

    all_dfs = []
    available = [s for s in target_sheets if s in sheet_names]
    if not available:
        available = [s for s in sheet_names if s not in ("Front page", "Footnotes")]

    for sheet in available:
        df = _parse_sipri_sheet(xlsx_path, sheet)
        if len(df) > 0:
            all_dfs.append(df)
            logger.info(f"Parsed {sheet}: {len(df)} rows")

    result = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "sipri_milex.parquet"
    result.to_parquet(out_path, index=False)
    logger.info(f"SIPRI written to {out_path} ({len(result)} rows)")
    return result


def run(raw_dir: Path, output_dir: Path, force_download: bool = False) -> None:
    xlsx_path = download_sipri(raw_dir, force=force_download)
    df = ingest_sipri(xlsx_path, output_dir)
    h = sha256_hash(xlsx_path)
    write_source_log(
        db_path=output_dir / "source_log.duckdb",
        source_id="sipri_milex",
        source_name="SIPRI Military Expenditure Database",
        local_path=xlsx_path,
        hash_sha256=h,
        source_url=SIPRI_MILEX_URL,
        license_notes="SIPRI data is publicly available with attribution",
        citation="SIPRI Military Expenditure Database, 1949-2024",
        notes=f"{len(df)} rows",
    )

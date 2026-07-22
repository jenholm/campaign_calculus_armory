"""ACLED ingestion stub (requires API key in .env)."""

import logging
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

ACLED_API_URL = "https://api.acleddata.com/acled/v2"


def fetch_acled(
    raw_dir: Path,
    api_key: str = None,
    email: str = None,
    limit: int = 5000,
) -> pd.DataFrame:
    """Fetch ACLED data via API pagination."""
    api_key = api_key or os.getenv("ACLED_API_KEY")
    email = email or os.getenv("ACLED_EMAIL")

    if not api_key or not email:
        logger.warning("ACLED API key or email not set. Set ACLED_API_KEY and ACLED_EMAIL in .env")
        return pd.DataFrame()

    raw_dir.mkdir(parents=True, exist_ok=True)
    all_events = []
    page = 1

    while True:
        params = {
            "key": api_key,
            "email": email,
            "limit": limit,
            "page": page,
        }
        resp = requests.get(f"{ACLED_API_URL}/acled/read", params=params, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        events = data.get("data", [])
        if not events:
            break
        all_events.extend(events)
        page += 1
        if page > 100:
            break

    df = pd.DataFrame(all_events) if all_events else pd.DataFrame()
    out_path = raw_dir / "acled_events.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"ACLED saved: {len(df)} events to {out_path}")
    return df


def run(raw_dir: Path, output_dir: Path) -> None:
    df = fetch_acled(raw_dir)
    if len(df) > 0:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / "acled.parquet"
        df.to_parquet(out_path, index=False)

"""Base ingestion utilities: hashing, logging, download helpers."""

import hashlib
import logging
from datetime import date
from pathlib import Path

import duckdb

logger = logging.getLogger(__name__)

SOURCE_LOG_SCHEMA = {
    "source_id": str,
    "source_name": str,
    "source_url": str,
    "download_date": str,
    "local_path": str,
    "hash_sha256": str,
    "license_notes": str,
    "citation": str,
    "notes": str,
}


def sha256_hash(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_source_log(
    db_path: Path,
    source_id: str,
    source_name: str,
    local_path: Path,
    hash_sha256: str,
    source_url: str = "",
    license_notes: str = "",
    citation: str = "",
    notes: str = "",
) -> None:
    """Append a row to the source log table."""
    con = duckdb.connect(str(db_path))
    try:
        con.execute(
            "CREATE TABLE IF NOT EXISTS source_log ("
            "source_id VARCHAR, source_name VARCHAR, source_url VARCHAR, "
            "download_date VARCHAR, local_path VARCHAR, hash_sha256 VARCHAR, "
            "license_notes VARCHAR, citation VARCHAR, notes VARCHAR)"
        )
        con.execute(
            "INSERT INTO source_log VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                source_id,
                source_name,
                source_url,
                date.today().isoformat(),
                str(local_path),
                hash_sha256,
                license_notes,
                citation,
                notes,
            ],
        )
    finally:
        con.close()


def connect_duckdb(db_path: Path, read_only: bool = False) -> duckdb.DuckDBPyConnection:
    """Get a DuckDB connection to the processed data store."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(db_path), read_only=read_only)

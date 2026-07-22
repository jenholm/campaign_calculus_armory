"""Human-readable labels for paper tables and figures."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from mahan_vs_attrition.conflict_names import CONFLICT_NAME_MAP


STATIC_WAR_NAME_BY_ID: dict[str, str] = {
    "cow_iw_1": "Franco-Spanish War (1823)",
    "cow_iw_4": "First Russo-Turkish War (1828-1829)",
    "cow_iw_7": "Mexican-American War (1846-1847)",
    "cow_iw_10": "Austro-Sardinian War (1848-1849)",
    "cow_iw_13": "First Schleswig-Holstein War (1848-1849)",
    "cow_iw_49": "Lopez War / Paraguayan War (1864-1870)",
    "cow_iw_58": "Franco-Prussian War (1870-1871)",
    "cow_iw_85": "Russo-Japanese War (1904-1905)",
    "cow_iw_106": "World War I (1914-1918)",
    "cow_iw_130": "Third Sino-Japanese War (1937-1941)",
    "cow_iw_139": "World War II (1939-1945)",
    "cow_iw_163": "Vietnam War (1965-1975)",
    "cow_iw_199": "Iran-Iraq War (1980-1988)",
    "cow_iw_211": "Gulf War (1990-1991)",
}

PRESET_DISPLAY_NAME: dict[str, str] = {
    "gulf_war_1991": "Gulf War (1991)",
    "vietnam_war": "Vietnam War",
    "wwi": "World War I",
    "wwii": "World War II",
    "franco_prussian": "Franco-Prussian War",
    "korean_war": "Korean War",
    "iran_iraq": "Iran-Iraq War",
}


@lru_cache(maxsize=1)
def _load_wars_lookup() -> dict[str, str]:
    """Load war_id -> war_name from processed data when available."""
    path = Path("data/processed/wars.parquet")
    if not path.exists():
        return {}

    df = pd.read_parquet(path)
    if "war_id" not in df.columns or "war_name" not in df.columns:
        return {}

    out: dict[str, str] = {}
    for _, row in df[["war_id", "war_name"]].dropna().iterrows():
        out[str(row["war_id"])] = str(row["war_name"])
    return out


def display_war_name(value: object) -> str:
    """Return a paper-safe human-readable war name."""
    raw = str(value)

    if raw in PRESET_DISPLAY_NAME:
        return PRESET_DISPLAY_NAME[raw]

    if raw in STATIC_WAR_NAME_BY_ID:
        return STATIC_WAR_NAME_BY_ID[raw]

    if raw in CONFLICT_NAME_MAP:
        return CONFLICT_NAME_MAP[raw]

    lookup = _load_wars_lookup()
    if raw in lookup:
        return lookup[raw]

    # Last resort: make internal keys readable, but never leave cow_iw in output.
    if raw.startswith("cow_iw_"):
        return f"COW war {raw.removeprefix('cow_iw_')}"

    return raw.replace("_", " ").title()


def display_war_name_strict(value: object) -> str:
    """Return a paper-safe name and fail if a raw COW ID would leak."""
    name = display_war_name(value)
    if "cow_iw" in name.lower():
        raise ValueError(f"Missing display name for paper output: {value}")
    return name

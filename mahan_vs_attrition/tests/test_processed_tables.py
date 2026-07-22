"""Tests for processed table integrity, ID uniqueness, and audit invariants."""

from pathlib import Path

import pandas as pd

DATA_DIR = Path("data/processed")


class TestProcessedTables:
    """Invariants that must hold after a successful normalize + score run."""

    def test_wars_have_no_duplicate_war_id(self):
        wars = pd.read_parquet(DATA_DIR / "wars.parquet")
        assert wars["war_id"].duplicated().sum() == 0, (
            f"wars.parquet has {wars['war_id'].duplicated().sum()} duplicate war_id values. "
            "COW WarNum is not unique per sub-war; use a per-row sequence."
        )

    def test_battles_have_no_duplicate_battle_id(self):
        battles = pd.read_parquet(DATA_DIR / "battles.parquet")
        assert battles["battle_id"].duplicated().sum() == 0, (
            f"battles.parquet has {battles['battle_id'].duplicated().sum()} duplicate battle_id values. "
            "IWB iwdNum is the dyad number, not a unique per-battle id; "
            "include a per-war sequence number."
        )

    def test_dss_score_count_matches_interstate(self):
        wars = pd.read_parquet(DATA_DIR / "wars.parquet")
        dss = pd.read_parquet(DATA_DIR / "dss_scores.parquet")
        # DSS only valid for interstate wars with IWB battles
        interstate = wars[wars["war_type"] == "interstate"]
        # Allow DSS up to 91 (interstate) plus manual cases with cow_iw_* ids
        assert len(dss) <= len(interstate) + 10

    def test_ses_score_count_within_range(self):
        ses = pd.read_parquet(DATA_DIR / "ses_scores.parquet")
        # SES is computed for any war with capability data
        assert 2000 <= len(ses) <= 10000

    def test_classification_keys_present(self):
        tc = pd.read_parquet(DATA_DIR / "termination_classification.parquet")
        assert "war_id" in tc.columns
        assert "termination_type_model" in tc.columns
        assert "dss_score" in tc.columns
        assert "ses_score" in tc.columns

    def test_wars_known_columns(self):
        wars = pd.read_parquet(DATA_DIR / "wars.parquet")
        for col in ("war_id", "war_name", "start_date", "end_date", "war_type", "era", "confidence"):
            assert col in wars.columns, f"wars.parquet missing {col}"

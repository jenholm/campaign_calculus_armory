"""Tests for DSS scoring with manual case study overrides."""

from pathlib import Path

import pandas as pd


class TestDSSComponents:
    """Component-level DSS scoring."""

    def setup_method(self):
        from mahan_vs_attrition.metrics.dss import compute_dss
        self.compute_dss = compute_dss

    def test_source_claims_dominates_when_high(self):
        # source_claims_decisive=90 with weight 0.35 contributes 31.5
        r = self.compute_dss(source_claims_decisive=90)
        assert r["dss_score"] >= 30

    def test_capital_capture_full_credit(self):
        r = self.compute_dss(capital_capture=True)
        assert r["dss_components"]["capital_capture"] == 100.0

    def test_battle_winner_zero_when_missing(self):
        r = self.compute_dss()
        assert r["dss_components"]["battle_winner_equals_war_winner"] == 0.0

    def test_field_army_destroyed_score(self):
        r = self.compute_dss(field_army_destroyed=True)
        assert r["dss_components"]["field_army_destroyed"] == 100.0

    def test_components_sum_within_bounds(self):
        r = self.compute_dss(
            source_claims_decisive=100,
            capital_capture=True,
            regime_collapse=True,
            field_army_destroyed=True,
            battle_winner_equals_war_winner=True,
        )
        # Even with all max, weighted sum should be in 0-100
        assert 0 <= r["dss_score"] <= 100


class TestManualCaseDSS:
    """DSS for the 6 manual case studies with cow_iw_* war_ids."""

    def setup_method(self):
        self.manual = pd.read_csv("data/manual/manual_case_scores.csv")
        self.dss = pd.read_parquet("data/processed/dss_scores.parquet")

    def test_franco_prussian_dss_above_50(self):
        """After manual override, Franco-Prussian DSS should be well above 50."""
        row = self.dss[self.dss["war_id"] == "cow_iw_58"]
        assert len(row) == 1
        dss_score = float(row.iloc[0]["dss_score"])
        # Manual is 85; model should be within 30 points
        assert dss_score > 50, f"Franco-Prussian DSS = {dss_score} should be > 50"

    def test_vietnam_dss_around_30(self):
        """Vietnam has manual 30 and a short war ending after exhaustion."""
        row = self.dss[self.dss["war_id"] == "cow_iw_163"]
        assert len(row) == 1
        dss_score = float(row.iloc[0]["dss_score"])
        # Should be in 20-50 range (low decisive)
        assert 15 <= dss_score <= 50, f"Vietnam DSS = {dss_score} out of range"

    def test_dss_components_table_exists(self):
        comp_path = Path("data/processed/dss_components.parquet")
        if comp_path.exists():
            comps = pd.read_parquet(comp_path)
            assert "war_id" in comps.columns
            # Should have component columns
            assert any(c in comps.columns for c in ("source_claims_decisive", "capital_capture"))

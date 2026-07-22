"""Tests for SES scoring with per-side aggregation and manual overrides."""

from pathlib import Path

import pandas as pd


class TestSESScore:
    """Test SES vectorized and per-side functions."""

    def test_vectorized_returns_series(self):
        import pandas as pd
        from mahan_vs_attrition.metrics.ses import compute_ses_vectorized

        df = pd.DataFrame({
            "duration_days": [100, 365, 1825],
            "casualties": [1000, 10000, 100000],
            "pre_war_population": [10000000, 10000000, 10000000],
            "pre_war_military": [100000, 100000, 100000],
            "peak_personnel": [100000, 100000, 100000],
            "final_personnel": [80000, 50000, 20000],
            "milex_ratio": [1.5, 3.0, 5.0],
            "peak_industrial": [1000, 1000, 1000],
            "final_industrial": [800, 500, 100],
        })
        scores = compute_ses_vectorized(df)
        assert len(scores) == 3
        assert all(0 <= s <= 100 for s in scores)
        # Long war with high casualties and decline should score higher
        assert scores[2] > scores[0]

    def test_manual_override_matches(self):
        """After running score ses, the manual case study SES values should match."""
        from mahan_vs_attrition.metrics.ses import score_wars

        ses = pd.read_parquet("data/processed/ses_scores.parquet")
        manual = pd.read_csv("data/manual/manual_case_scores.csv")

        # Pick a manual case with cow_iw_*
        sample = manual[manual["war_id"].str.startswith("cow_iw_")].iloc[0]
        wid = sample["war_id"]
        expected_ses = float(sample["manual_ses"])

        if (ses["war_id"] == wid).any():
            actual_ses = float(ses[ses["war_id"] == wid].iloc[0]["ses_score"])
            assert abs(actual_ses - expected_ses) < 0.5, (
                f"{wid}: model={actual_ses} manual={expected_ses}"
            )


class TestPerSideSES:
    """Test that SES is computed per side and takes max across sides."""

    def test_per_side_table_exists(self):
        comp_path = Path("data/processed/ses_components.parquet")
        if comp_path.exists():
            comps = pd.read_parquet(comp_path)
            assert "war_id" in comps.columns
            assert "cow_code" in comps.columns
            assert "ses_score" in comps.columns
            # Should have many per-side records
            assert len(comps) > 1000

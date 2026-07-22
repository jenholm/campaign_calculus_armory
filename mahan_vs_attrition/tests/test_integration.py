"""Integration tests for the ingestion and metrics pipeline."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def sample_nmc_data():
    return pd.DataFrame(
        {
            "ccode": [2, 2, 200, 200],
            "state": ["USA", "USA", "UK", "UK"],
            "year": [1917, 1918, 1917, 1918],
            "milex": [1000, 5000, 800, 3000],
            "milper": [200, 500, 150, 400],
            "irst": [100, 200, 80, 150],
            "pec": [500, 600, 400, 450],
            "tpop": [100000, 101000, 45000, 45500],
            "upop": [50000, 51000, 25000, 26000],
            "cinc": [0.2, 0.25, 0.15, 0.18],
        }
    )


@pytest.fixture
def sample_war_data():
    return pd.DataFrame(
        {
            "war_id": ["ww1"],
            "war_name": ["World War I"],
            "start_date": pd.to_datetime(["1914-07-28"]),
            "end_date": pd.to_datetime(["1918-11-11"]),
            "war_type": ["interstate"],
            "outcome": ["win_coalition"],
        }
    )


class TestIngestionPipeline:
    def test_nmc_ingest(self, sample_nmc_data):
        """Test that NMC data can be written and read as parquet."""
        from mahan_vs_attrition.ingest.cow_nmc import ingest_nmc

        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.csv"
            sample_nmc_data.to_csv(input_path, index=False)
            output = Path(tmp) / "output"
            df = ingest_nmc(input_path, output)
            assert len(df) == 4
            assert "cow_code" in df.columns
            assert "population" in df.columns

    def test_ingest_nmc_from_df(self, sample_nmc_data):
        """Simulate NMC ingestion with a CSV file."""
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "nmc_test.csv"
            sample_nmc_data.to_csv(csv_path, index=False)

            from mahan_vs_attrition.ingest.cow_nmc import ingest_nmc

            df = ingest_nmc(csv_path, Path(tmp))
            assert "cow_code" in df.columns
            assert "cinc" in df.columns
            assert "year" in df.columns

    def test_sha256_hash_utility(self):
        from mahan_vs_attrition.ingest.base import sha256_hash

        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
            f.write("col1,col2\n1,2\n")
            tmp = Path(f.name)
        try:
            h = sha256_hash(tmp)
            assert len(h) == 64
        finally:
            tmp.unlink(missing_ok=True)


class TestMetricsPipeline:
    def test_dss_ses_classification_roundtrip(self):
        """Verify that DSS + SES → classification works end-to-end."""
        from mahan_vs_attrition.metrics.classify import classify_termination
        from mahan_vs_attrition.metrics.dss import compute_dss
        from mahan_vs_attrition.metrics.ses import compute_ses

        dss = compute_dss(final_battle_proximity=3, rapid_surrender=True)
        ses = compute_ses(duration_days=500, casualties=50000)
        cls = classify_termination(dss_score=dss["dss_score"], ses_score=ses["ses_score"])

        assert "termination_type_model" in cls
        assert cls["dss_score"] > cls["ses_score"]

    def test_dss_component_breakdown(self):
        """Verify DSS exposes component values."""
        from mahan_vs_attrition.metrics.dss import compute_dss

        result = compute_dss(final_battle_proximity=3, rapid_surrender=True)
        assert "dss_components" in result
        components = result["dss_components"]
        assert "final_battle_proximity" in components
        assert components["final_battle_proximity"] == 100.0

    def test_ses_component_breakdown(self):
        """Verify SES exposes component values."""
        from mahan_vs_attrition.metrics.ses import compute_ses

        result = compute_ses(duration_days=365, casualties=100000)
        assert "ses_components" in result
        components = result["ses_components"]
        assert "duration_pressure" in components
        assert "casualty_burden" in components


class TestAllThresholdToggles:
    """Verify classification works at boundary conditions."""

    def test_boundary_decisive(self):
        from mahan_vs_attrition.metrics.classify import classify_termination

        r = classify_termination(dss_score=70, ses_score=49)
        assert r["termination_type_model"] == "decisive_battle_or_campaign"

    def test_boundary_exhaustion(self):
        from mahan_vs_attrition.metrics.classify import classify_termination

        r = classify_termination(dss_score=49, ses_score=70)
        assert r["termination_type_model"] == "strategic_exhaustion"

    def test_boundary_mixed(self):
        from mahan_vs_attrition.metrics.classify import classify_termination

        # With hybrid rule, DSS=60 SES=60 falls in mixed_or_uncertain
        # (both below 65, difference below margin)
        r = classify_termination(dss_score=60, ses_score=60)
        assert r["termination_type_model"] == "mixed_or_uncertain"

    def test_strong_mixed(self):
        from mahan_vs_attrition.metrics.classify import classify_termination

        # Both >= 65 -> mixed
        r = classify_termination(dss_score=70, ses_score=70)
        assert r["termination_type_model"] == "mixed"

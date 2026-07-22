"""Verify package imports and basic function calls."""

import tempfile
from pathlib import Path


class TestImports:
    def test_package_import(self):
        import mahan_vs_attrition

        assert mahan_vs_attrition.__version__ == "0.1.0"

    def test_cli_import(self):
        from mahan_vs_attrition.cli import app

        assert app is not None

    def test_ingest_base_import(self):
        from mahan_vs_attrition.ingest.base import sha256_hash

        assert sha256_hash is not None

    def test_ingest_cow_nmc_import(self):
        from mahan_vs_attrition.ingest.cow_nmc import ingest_nmc

        assert ingest_nmc is not None

    def test_metrics_dss_import(self):
        from mahan_vs_attrition.metrics.dss import compute_dss

        assert compute_dss is not None

    def test_metrics_ses_import(self):
        from mahan_vs_attrition.metrics.ses import compute_ses

        assert compute_ses is not None

    def test_metrics_lss_import(self):
        from mahan_vs_attrition.metrics.lss import compute_lss

        assert compute_lss is not None

    def test_metrics_classify_import(self):
        from mahan_vs_attrition.metrics.classify import classify_termination

        assert classify_termination is not None

    def test_normalize_import(self):
        from mahan_vs_attrition.normalize.actor_crosswalk import build_actor_crosswalk

        assert build_actor_crosswalk is not None

    def test_models_import(self):
        from mahan_vs_attrition.models.analysis import analyze_duration

        assert analyze_duration is not None

    def test_viz_import(self):
        from mahan_vs_attrition.viz.plots import plot_war_duration_by_era

        assert plot_war_duration_by_era is not None


class TestSha256:
    def test_sha256_hash(self):
        from mahan_vs_attrition.ingest.base import sha256_hash

        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
            f.write("a,b,c\n1,2,3\n")
            tmp = Path(f.name)
        try:
            h = sha256_hash(tmp)
            assert isinstance(h, str)
            assert len(h) == 64
            assert all(c in "0123456789abcdef" for c in h)
        finally:
            tmp.unlink(missing_ok=True)


class TestDSS:
    def test_final_battle_proximity(self):
        from mahan_vs_attrition.metrics.dss import compute_final_battle_proximity

        assert compute_final_battle_proximity(3) == 100.0
        assert compute_final_battle_proximity(15) == 80.0
        assert compute_final_battle_proximity(60) == 60.0
        assert compute_final_battle_proximity(100) == 30.0
        assert compute_final_battle_proximity(365) == 0.0
        assert compute_final_battle_proximity(None) == 0.0

    def test_compute_dss(self):
        from mahan_vs_attrition.metrics.dss import compute_dss

        result = compute_dss(
            final_battle_proximity=3,
            rapid_surrender=True,
        )
        assert "dss_score" in result
        assert isinstance(result["dss_score"], float)
        assert result["dss_score"] > 0


class TestSES:
    def test_duration_pressure(self):
        from mahan_vs_attrition.metrics.ses import compute_duration_pressure

        assert compute_duration_pressure(1) == 0.0
        assert compute_duration_pressure(None) == 0.0
        val = compute_duration_pressure(365)
        assert 0 < val < 100

    def test_casualty_burden(self):
        from mahan_vs_attrition.metrics.ses import compute_casualty_burden

        val = compute_casualty_burden(100000, 10000000, 500000)
        assert 0 <= val <= 100

    def test_compute_ses(self):
        from mahan_vs_attrition.metrics.ses import compute_ses

        result = compute_ses(duration_days=365, casualties=50000)
        assert "ses_score" in result
        assert isinstance(result["ses_score"], float)


class TestClassification:
    def test_classify_decisive_battle(self):
        from mahan_vs_attrition.metrics.classify import classify_termination

        result = classify_termination(dss_score=85, ses_score=20)
        assert result["termination_type_model"] == "decisive_battle_or_campaign"

    def test_classify_exhaustion(self):
        from mahan_vs_attrition.metrics.classify import classify_termination

        result = classify_termination(dss_score=20, ses_score=85)
        assert result["termination_type_model"] == "strategic_exhaustion"

    def test_classify_mixed(self):
        from mahan_vs_attrition.metrics.classify import classify_termination

        result = classify_termination(dss_score=70, ses_score=70)
        assert result["termination_type_model"] == "mixed"

    def test_classify_uncertain(self):
        from mahan_vs_attrition.metrics.classify import classify_termination

        result = classify_termination(dss_score=40, ses_score=40)
        assert result["termination_type_model"] == "uncertain_or_negotiated"


class TestActorCrosswalk:
    def test_build_crosswalk(self):
        from mahan_vs_attrition.normalize.actor_crosswalk import build_actor_crosswalk

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            df = build_actor_crosswalk(output)
            assert len(df) > 0
            assert "actor_id" in df.columns
            assert "actor_name_standard" in df.columns

    def test_resolve_actor(self):
        from mahan_vs_attrition.normalize.actor_crosswalk import (
            build_actor_crosswalk,
            resolve_actor,
        )

        with tempfile.TemporaryDirectory() as tmp:
            crosswalk = build_actor_crosswalk(Path(tmp))
            aid = resolve_actor(crosswalk, cow_code=2)
            assert aid == "USA"
            aid = resolve_actor(crosswalk, cow_code=999)
            assert "UNKNOWN" in aid

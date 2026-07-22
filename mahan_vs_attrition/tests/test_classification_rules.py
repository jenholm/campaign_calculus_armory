"""Tests for the hybrid classification rule."""

import pytest


class TestHybridRule:
    """Verify the hybrid rule classifies correctly across boundary cases."""

    def setup_method(self):
        from mahan_vs_attrition.metrics.classify import classify_termination
        self.cls = classify_termination

    def test_strong_decisive(self):
        # DSS=85, SES=20: DSS-SES=65 >= 20
        r = self.cls(dss_score=85, ses_score=20)
        assert r["termination_type_model"] == "decisive_battle_or_campaign"

    def test_strong_exhaustion(self):
        # SES=90, DSS=20: SES-DSS=70 >= 20
        r = self.cls(dss_score=20, ses_score=90)
        assert r["termination_type_model"] == "strategic_exhaustion"

    def test_both_high_is_mixed(self):
        # Both >= 65 -> mixed
        r = self.cls(dss_score=70, ses_score=70)
        assert r["termination_type_model"] == "mixed"

    def test_both_below_threshold_is_uncertain(self):
        # max(DSS, SES) < 45
        r = self.cls(dss_score=30, ses_score=40)
        assert r["termination_type_model"] == "uncertain_or_negotiated"

    def test_mid_close_scores(self):
        # DSS=60, SES=60: both below 65, diff=0, not exhausted
        r = self.cls(dss_score=60, ses_score=60)
        assert r["termination_type_model"] == "mixed_or_uncertain"

    def test_margin_decisive(self):
        # DSS=70, SES=50: DSS-SES=20 exactly, should be decisive
        r = self.cls(dss_score=70, ses_score=50)
        assert r["termination_type_model"] == "decisive_battle_or_campaign"

    def test_margin_exhaustion(self):
        # SES=70, DSS=50: SES-DSS=20 exactly, should be exhaustion
        r = self.cls(dss_score=50, ses_score=70)
        assert r["termination_type_model"] == "strategic_exhaustion"

    def test_just_below_margin(self):
        # DSS=69, SES=50: DSS-SES=19 < 20, should not be decisive
        r = self.cls(dss_score=69, ses_score=50)
        assert r["termination_type_model"] != "decisive_battle_or_campaign"

    def test_decisive_overrides_below_mixed(self):
        # DSS=80, SES=50: DSS-SES=30 >= 20, decisive
        r = self.cls(dss_score=80, ses_score=50)
        assert r["termination_type_model"] == "decisive_battle_or_campaign"


class TestDataQuality:
    """Verify data_quality is correctly set based on available scores."""

    def setup_method(self):
        from mahan_vs_attrition.metrics.classify import classify_termination
        self.cls = classify_termination

    def test_high_quality_when_both_scores(self):
        r = self.cls(dss_score=80, ses_score=30)
        assert r["data_quality"] == "high"

    def test_medium_quality_when_only_ses(self):
        r = self.cls(ses_score=80)
        assert r["data_quality"] == "medium"

    def test_medium_quality_when_only_dss(self):
        r = self.cls(dss_score=80)
        assert r["data_quality"] == "medium"

    def test_low_quality_when_no_scores(self):
        r = self.cls()
        assert r["data_quality"] == "low"

    def test_high_quality_for_mixed(self):
        r = self.cls(dss_score=70, ses_score=70)
        assert r["data_quality"] == "high"

    def test_medium_quality_for_nan_dss(self):
        import math
        r = self.cls(dss_score=float("nan"), ses_score=60)
        assert r["data_quality"] == "medium"


class TestValidationAgreement:
    """The hybrid rule should classify wars where both DSS and SES exist.
    Agreement on the full golden set may be <50% because many case studies
    lack DSS scores (interstate battles data only). The model can only
    classify wars with both axes scored."""

    def test_agreement_on_scored_wars(self):
        from pathlib import Path
        from mahan_vs_attrition.case_studies.validation import validate_case_studies

        result = validate_case_studies(
            case_studies_path=Path("data/manual/manual_case_scores.csv"),
            dss_path=Path("data/processed/dss_scores.parquet"),
            ses_path=Path("data/processed/ses_scores.parquet"),
            output_path=Path("data/processed/case_study_validation_test.json"),
        )
        summary = result["summary"]
        if Path("data/processed/case_study_validation_test.json").exists():
            Path("data/processed/case_study_validation_test.json").unlink()
        if summary["n_evaluated_against_model"] == 0:
            pytest.skip("No model-data wars to compare against")
        # For wars where both DSS and SES exist, expect >= 33% agreement
        # (model uses automated scoring; manual uses expert judgment)
        assert summary["agreement_pct"] >= 33, (
            f"Agreement {summary['agreement_pct']}% is below 33% threshold. "
            f"Evaluated: {summary['n_evaluated_against_model']}, "
            f"Agreed: {summary['n_classification_agreement']}"
        )

    def test_case_studies_count(self):
        from pathlib import Path
        import pandas as pd

        cs = pd.read_csv(Path("data/manual/manual_case_scores.csv"))
        assert len(cs) >= 15, f"Expected >= 15 case studies, got {len(cs)}"

"""Tests for blind historical validation."""

from pathlib import Path

from mahan_vs_attrition.simulation.blind_validation import (
    compute_confidence,
    load_blind_cases,
    predict_mechanism,
    run_blind_validation,
)

CASES_PATH = Path("data/blind_validation_cases.yml")


class TestLoadBlindCases:
    def test_loads_cases(self):
        cases = load_blind_cases(CASES_PATH)
        assert len(cases) >= 15

    def test_cases_have_required_fields(self):
        cases = load_blind_cases(CASES_PATH)
        for case in cases:
            assert "name" in case
            assert "human_label" in case
            assert "initial" in case


class TestPredictMechanism:
    def test_decisive_outcome(self):
        result = {
            "outcome": "decisive_victory_a",
            "dss_a": [80],
            "ses_a": [30],
            "termination_month": 6,
        }
        assert predict_mechanism(result) == "decisive"

    def test_attritional_outcome(self):
        result = {
            "outcome": "decisive_victory_b",
            "dss_a": [15],
            "ses_a": [85],
            "termination_month": 60,
        }
        assert predict_mechanism(result) == "attritional"

    def test_long_war_is_attritional(self):
        result = {
            "outcome": "negotiated_settlement",
            "dss_a": [20],
            "ses_a": [40],
            "termination_month": 80,
        }
        assert predict_mechanism(result) == "attritional"

    def test_mixed_when_both_signals(self):
        result = {
            "outcome": "negotiated_settlement",
            "dss_a": [60],
            "ses_a": [50],
            "termination_month": 30,
        }
        assert predict_mechanism(result) == "mixed"


class TestComputeConfidence:
    def test_high_signal_gives_high_confidence(self):
        result = {"dss_a": [80], "ses_a": [10]}
        assert compute_confidence(result) > 0.7

    def test_low_signal_gives_low_confidence(self):
        result = {"dss_a": [50], "ses_a": [48]}
        assert compute_confidence(result) < 0.6

    def test_confidence_in_range(self):
        result = {"dss_a": [0], "ses_a": [0]}
        assert 0.0 <= compute_confidence(result) <= 1.0


class TestBlindValidation:
    def test_runs_without_error(self, tmp_path):
        df = run_blind_validation(CASES_PATH, tmp_path, seed=42)
        assert len(df) >= 15

    def test_produces_output_files(self, tmp_path):
        run_blind_validation(CASES_PATH, tmp_path, seed=42)
        assert (tmp_path / "blind_prediction_results.csv").exists()
        assert (tmp_path / "blind_validation_summary.json").exists()

    def test_has_all_columns(self, tmp_path):
        df = run_blind_validation(CASES_PATH, tmp_path, seed=42)
        required = [
            "war",
            "human_label",
            "model_prediction",
            "confidence",
            "assessment",
            "final_dss_sim",
            "final_ses_sim",
        ]
        for col in required:
            assert col in df.columns

    def test_confidence_in_range(self, tmp_path):
        df = run_blind_validation(CASES_PATH, tmp_path, seed=42)
        assert df["confidence"].min() >= 0
        assert df["confidence"].max() <= 1

    def test_summary_has_interpretable_metrics(self, tmp_path):
        run_blind_validation(CASES_PATH, tmp_path, seed=42)
        import json

        summary = json.loads((tmp_path / "blind_validation_summary.json").read_text())
        assert "exact_match_rate" in summary
        assert "coverage_rate" in summary
        assert "assessment_distribution" in summary
        assert 0.0 <= summary["exact_match_rate"] <= 1.0
        assert 0.0 <= summary["coverage_rate"] <= 1.0
        assert summary["n_cases"] >= 15

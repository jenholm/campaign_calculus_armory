"""Tests for baseline comparison."""

import pytest
import pandas as pd
from pathlib import Path
from mahan_vs_attrition.models.baseline_comparison import (
    baseline_duration_only,
    baseline_majority_class,
    compute_metrics,
    run_baseline_comparison,
)


class TestBaselineDuration:
    def test_short_war_decisive(self):
        df = pd.DataFrame({"duration_days": [100]})
        result = baseline_duration_only(df)
        assert result["predictions"][0] == "decisive"

    def test_long_war_attritional(self):
        df = pd.DataFrame({"duration_days": [2000]})
        result = baseline_duration_only(df)
        assert result["predictions"][0] == "attritional"

    def test_medium_war_mixed(self):
        df = pd.DataFrame({"duration_days": [500]})
        result = baseline_duration_only(df)
        assert result["predictions"][0] == "mixed"

    def test_missing_duration_uncertain(self):
        df = pd.DataFrame({"duration_days": [None]})
        result = baseline_duration_only(df)
        assert result["predictions"][0] == "uncertain"

    def test_negative_duration_uncertain(self):
        df = pd.DataFrame({"duration_days": [-10]})
        result = baseline_duration_only(df)
        assert result["predictions"][0] == "uncertain"


class TestBaselineMajorityClass:
    def test_majority_prediction(self):
        df = pd.DataFrame({"primary_mechanism": ["decisive", "decisive", "attritional"]})
        result = baseline_majority_class(df)
        assert all(p == "decisive" for p in result["predictions"])

    def test_missing_column(self):
        df = pd.DataFrame({"other_col": [1, 2]})
        result = baseline_majority_class(df)
        assert "error" in result


class TestComputeMetrics:
    def test_perfect_prediction(self):
        y_true = ["decisive", "attritional", "decisive"]
        y_pred = ["decisive", "attritional", "decisive"]
        m = compute_metrics(y_true, y_pred, "test")
        assert m["accuracy"] == 1.0

    def test_worst_prediction(self):
        y_true = ["decisive", "decisive"]
        y_pred = ["attritional", "attritional"]
        m = compute_metrics(y_true, y_pred, "test")
        assert m["accuracy"] == 0.0

    def test_filters_insufficient(self):
        y_true = ["decisive", "data_insufficient", "attritional"]
        y_pred = ["decisive", "decisive", "attritional"]
        m = compute_metrics(y_true, y_pred, "test")
        assert m["n"] == 2

    def test_empty_input(self):
        m = compute_metrics([], [], "test")
        assert m["n"] == 0
        assert m["accuracy"] == 0

    def test_has_model_name(self):
        m = compute_metrics(["a"], ["a"], "my_model")
        assert m["model"] == "my_model"

    def test_all_filtered_out(self):
        y_true = ["data_insufficient", "ses_only_insufficient"]
        y_pred = ["data_insufficient", "ses_only_insufficient"]
        m = compute_metrics(y_true, y_pred, "test")
        assert m["n"] == 0


class TestRunBaselineComparison:
    def test_runs_without_error(self, tmp_path):
        wars = pd.DataFrame({"war_id": ["w1", "w2"], "duration_days": [100, 2000]})
        war_years = pd.DataFrame({
            "war_id": ["w1", "w1", "w2", "w2"],
            "year": [2000, 2001, 2000, 2001],
            "battle_deaths": [50000, 100000, 600000, 700000],
            "cinc": [0.1, 0.12, 0.08, 0.09],
        })
        classifications = pd.DataFrame({
            "war_id": ["w1", "w2"],
            "primary_mechanism": ["decisive", "attritional"],
        })
        result = run_baseline_comparison(wars, war_years, classifications, tmp_path)
        assert "baselines" in result
        assert len(result["baselines"]) > 0

    def test_saves_json_and_csv(self, tmp_path):
        wars = pd.DataFrame({"war_id": ["w1"], "duration_days": [100]})
        war_years = pd.DataFrame({
            "war_id": ["w1"],
            "year": [2000],
            "battle_deaths": [50000],
        })
        classifications = pd.DataFrame({
            "war_id": ["w1"],
            "primary_mechanism": ["decisive"],
        })
        run_baseline_comparison(wars, war_years, classifications, tmp_path)
        assert (tmp_path / "baseline_comparison.json").exists()
        assert (tmp_path / "baseline_comparison.csv").exists()

    def test_missing_mechanism_column(self, tmp_path):
        wars = pd.DataFrame({"war_id": ["w1"]})
        war_years = pd.DataFrame()
        classifications = pd.DataFrame({"war_id": ["w1"]})
        result = run_baseline_comparison(wars, war_years, classifications, tmp_path)
        assert "error" in result

    def test_dss_ses_model_in_results(self, tmp_path):
        wars = pd.DataFrame({"war_id": ["w1", "w2", "w3"], "duration_days": [100, 500, 2000]})
        war_years = pd.DataFrame({
            "war_id": ["w1", "w2", "w3"],
            "year": [2000, 2000, 2000],
            "battle_deaths": [50000, 200000, 700000],
        })
        classifications = pd.DataFrame({
            "war_id": ["w1", "w2", "w3"],
            "primary_mechanism": ["decisive", "mixed", "attritional"],
        })
        result = run_baseline_comparison(wars, war_years, classifications, tmp_path)
        model_names = [b["model"] for b in result["baselines"]]
        assert "dss_ses_model" in model_names

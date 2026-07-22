"""Tests for hypothesis testing module."""

import json

import pandas as pd
import pytest

from mahan_vs_attrition.models.hypothesis_testing import (
    ablation_study,
    compute_dss_slope,
    compute_ses_slope,
    logistic_regression_hypothesis,
    survival_analysis_hypothesis,
    validate_simulation_against_history,
)
from mahan_vs_attrition.simulation.war_dynamics import HISTORICAL_PRESETS

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_classifications_df():
    """Minimal classifications DataFrame."""
    return pd.DataFrame(
        {
            "war_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "termination_type_model": [
                "decisive_battle_or_campaign",
                "strategic_exhaustion",
                "mixed",
                "decisive_battle_or_campaign",
                "strategic_exhaustion",
                "mixed_or_uncertain",
                "decisive_battle_or_campaign",
                "strategic_exhaustion",
                "mixed",
                "uncertain_or_negotiated",
                "decisive_battle_or_campaign",
                "strategic_exhaustion",
            ],
            "dss_score": [75, 30, 60, 80, 25, 50, 70, 35, 55, 40, 85, 20],
            "ses_score": [25, 70, 55, 20, 75, 48, 30, 65, 50, 42, 15, 80],
        }
    )


@pytest.fixture
def sample_wars_df():
    """Minimal wars DataFrame."""
    return pd.DataFrame(
        {
            "war_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "duration_days": [60, 1200, 600, 45, 1500, 900, 90, 1000, 750, 500, 30, 1400],
            "start_date": pd.to_datetime(
                ["2020-01-01"] * 12
            ),
            "end_date": pd.to_datetime(
                ["2020-03-01", "2021-01-01", "2020-08-01", "2020-02-15",
                 "2021-06-01", "2020-11-01", "2020-04-01", "2020-12-01",
                 "2020-10-01", "2020-06-01", "2020-02-01", "2021-03-01"]
            ),
        }
    )


@pytest.fixture
def sample_war_years_df():
    """Minimal war_years DataFrame with DSS/SES columns."""
    records = []
    for wid in range(1, 13):
        for year_offset in range(3):
            records.append(
                {
                    "war_id": wid,
                    "year": 2020 + year_offset,
                    "cinc": 0.1 + year_offset * 0.01,
                    "economic_a": 50 - year_offset * 5,
                }
            )
    return pd.DataFrame(records)


@pytest.fixture
def sample_war_years_with_dss_ses():
    """War years DataFrame with explicit DSS/SES columns."""
    records = []
    for wid in range(1, 13):
        for year_offset in range(4):
            dss = 20 + year_offset * 10 if wid % 2 == 0 else 60 - year_offset * 5
            ses = 30 + year_offset * 8 if wid % 2 != 0 else 15 + year_offset * 3
            records.append(
                {
                    "war_id": wid,
                    "year": 2020 + year_offset,
                    "cinc": 0.1,
                    "economic_a": 50,
                    "dss_score": dss,
                    "ses_score": ses,
                }
            )
    return pd.DataFrame(records)


@pytest.fixture
def output_dir(tmp_path):
    return tmp_path / "output"


# ---------------------------------------------------------------------------
# Test compute_dss_slope
# ---------------------------------------------------------------------------


class TestComputeDssSlope:
    def test_returns_dataframe(self, sample_classifications_df, sample_war_years_df):
        result = compute_dss_slope(sample_classifications_df, sample_war_years_df)
        assert isinstance(result, pd.DataFrame)
        assert "war_id" in result.columns
        assert "early_dss_slope" in result.columns
        assert len(result) == len(sample_classifications_df)

    def test_empty_classifications(self, sample_war_years_df):
        empty = pd.DataFrame(columns=["war_id", "dss_score"])
        result = compute_dss_slope(empty, sample_war_years_df)
        assert len(result) == 0

    def test_with_dss_columns(self, sample_classifications_df, sample_war_years_with_dss_ses):
        result = compute_dss_slope(sample_classifications_df, sample_war_years_with_dss_ses)
        assert len(result) == len(sample_classifications_df)
        assert all("early_dss_slope" in row for _, row in result.iterrows())


# ---------------------------------------------------------------------------
# Test compute_ses_slope
# ---------------------------------------------------------------------------


class TestComputeSesSlope:
    def test_returns_dataframe(self, sample_classifications_df, sample_war_years_df):
        result = compute_ses_slope(sample_classifications_df, sample_war_years_df)
        assert isinstance(result, pd.DataFrame)
        assert "war_id" in result.columns
        assert "ses_slope" in result.columns
        assert len(result) == len(sample_classifications_df)

    def test_empty_classifications(self, sample_war_years_df):
        empty = pd.DataFrame(columns=["war_id", "ses_score"])
        result = compute_ses_slope(empty, sample_war_years_df)
        assert len(result) == 0


# ---------------------------------------------------------------------------
# Test logistic_regression_hypothesis
# ---------------------------------------------------------------------------


class TestLogisticRegressionHypothesis:
    def test_basic_run(
        self, sample_war_years_df, sample_classifications_df, sample_wars_df, output_dir
    ):
        result = logistic_regression_hypothesis(
            sample_war_years_df, sample_classifications_df, output_dir, wars_df=sample_wars_df
        )
        assert "mean_accuracy" in result or "error" in result
        if "error" not in result:
            assert 0 <= result["mean_accuracy"] <= 1
            assert "coefficients" in result
            assert "feature_names" in result

    def test_output_file_written(
        self, sample_war_years_df, sample_classifications_df, output_dir
    ):
        logistic_regression_hypothesis(
            sample_war_years_df, sample_classifications_df, output_dir
        )
        expected = output_dir / "hypothesis_logistic_regression.json"
        assert expected.exists()
        data = json.loads(expected.read_text())
        assert isinstance(data, dict)

    def test_empty_input(self, output_dir):
        result = logistic_regression_hypothesis(
            pd.DataFrame(), pd.DataFrame(), output_dir
        )
        assert "error" in result


# ---------------------------------------------------------------------------
# Test survival_analysis_hypothesis
# ---------------------------------------------------------------------------


class TestSurvivalAnalysisHypothesis:
    def test_basic_run(self, sample_wars_df, sample_classifications_df, output_dir):
        result = survival_analysis_hypothesis(
            sample_wars_df, sample_classifications_df, output_dir
        )
        assert isinstance(result, dict)
        assert "kaplan_meier" in result or "error" in result

    def test_output_file_written(self, sample_wars_df, sample_classifications_df, output_dir):
        survival_analysis_hypothesis(sample_wars_df, sample_classifications_df, output_dir)
        expected = output_dir / "hypothesis_survival_analysis.json"
        assert expected.exists()

    def test_empty_input(self, output_dir):
        result = survival_analysis_hypothesis(pd.DataFrame(), pd.DataFrame(), output_dir)
        assert "error" in result

    def test_km_results_have_structure(self, sample_wars_df, sample_classifications_df, output_dir):
        result = survival_analysis_hypothesis(
            sample_wars_df, sample_classifications_df, output_dir
        )
        km = result.get("kaplan_meier", {})
        for term_type, info in km.items():
            assert "n_wars" in info
            assert "median_duration_months" in info


# ---------------------------------------------------------------------------
# Test ablation_study
# ---------------------------------------------------------------------------


class TestAblationStudy:
    def test_basic_run(
        self, sample_war_years_df, sample_classifications_df, output_dir
    ):
        result = ablation_study(
            sample_war_years_df, sample_classifications_df, output_dir
        )
        assert isinstance(result, dict)
        assert "error" in result or "full" in result
        if "error" not in result:
            assert "full" in result
            assert "dss_loss" in result
            assert "ses_loss" in result
            assert "interpretation" in result

    def test_output_file_written(
        self, sample_war_years_df, sample_classifications_df, output_dir
    ):
        ablation_study(sample_war_years_df, sample_classifications_df, output_dir)
        expected = output_dir / "hypothesis_ablation_study.json"
        assert expected.exists()

    def test_interpretation_structure(
        self, sample_war_years_df, sample_classifications_df, output_dir
    ):
        result = ablation_study(
            sample_war_years_df, sample_classifications_df, output_dir
        )
        if "interpretation" in result:
            interp = result["interpretation"]
            assert "dss_more_predictive" in interp
            assert "ses_more_predictive" in interp
            assert "both_contribute" in interp

    def test_empty_input(self, output_dir):
        result = ablation_study(pd.DataFrame(), pd.DataFrame(), output_dir)
        assert "error" in result


# ---------------------------------------------------------------------------
# Test validate_simulation_against_history
# ---------------------------------------------------------------------------


class TestValidateSimulation:
    def test_all_presets_validate(self, output_dir):
        result = validate_simulation_against_history(output_dir=output_dir)
        assert "summary" in result
        assert result["summary"]["total_validated"] > 0

    def test_gulf_war_pattern(self, output_dir):
        result = validate_simulation_against_history(
            presets={"gulf_war_1991": HISTORICAL_PRESETS["gulf_war_1991"]},
            output_dir=output_dir,
        )
        assert "gulf_war_1991" in result
        gw = result["gulf_war_1991"]
        assert "passes" in gw
        assert "expected_pattern" in gw
        assert gw["expected_pattern"] == "decisive"

    def test_vietnam_war_pattern(self, output_dir):
        result = validate_simulation_against_history(
            presets={"vietnam_war": HISTORICAL_PRESETS["vietnam_war"]},
            output_dir=output_dir,
        )
        assert "vietnam_war" in result
        vw = result["vietnam_war"]
        assert vw["expected_pattern"] == "attritional"

    def test_output_file_written(self, output_dir):
        validate_simulation_against_history(output_dir=output_dir)
        expected = output_dir / "hypothesis_simulation_validation.json"
        assert expected.exists()
        data = json.loads(expected.read_text())
        assert "summary" in data

    def test_simulation_runs_correctly(self, output_dir):
        result = validate_simulation_against_history(
            presets={"wwi": HISTORICAL_PRESETS["wwi"]},
            output_dir=output_dir,
        )
        wwi = result["wwi"]
        assert wwi["duration_months"] > 0
        assert wwi["max_ses_a"] > 0

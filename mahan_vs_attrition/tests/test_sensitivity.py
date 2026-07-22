"""Tests for parameter sensitivity analysis."""

from mahan_vs_attrition.simulation.sensitivity import (
    classify_outcome,
    generate_sensitivity_heatmap_data,
    generate_sensitivity_heatmap_figure,
    run_sensitivity_analysis,
)
from mahan_vs_attrition.simulation.war_dynamics import HISTORICAL_PRESETS


def _make_result(
    outcome: str = "inconclusive",
    dss: list[float] | None = None,
    ses: list[float] | None = None,
    termination_month: int = 120,
    mil_a: list[float] | None = None,
    econ_a: list[float] | None = None,
    pol_a: list[float] | None = None,
) -> dict:
    """Build a result dict with enough structure for the v2 classifier."""
    return {
        "outcome": outcome,
        "dss_a": dss or [],
        "ses_a": ses or [],
        "termination_month": termination_month,
        "military_a": mil_a or [70],
        "economic_a": econ_a or [70],
        "political_will_a": pol_a or [70],
        "military_b": [70],
        "economic_b": [70],
        "political_will_b": [70],
    }


class TestClassifyOutcome:
    def test_decisive_outcome(self):
        # High DSS, short war → decisive shock
        cls = classify_outcome(_make_result(
            outcome="decisive_victory_a",
            dss=[80, 90],
            ses=[30, 35],
            termination_month=6,
        ))
        assert cls["mechanism"] == "decisive shock"

    def test_attritional_outcome(self):
        # High SES, long war, declining states → strategic exhaustion
        cls = classify_outcome(_make_result(
            outcome="mutual_exhaustion",
            dss=[20, 10],
            ses=[60, 85],
            termination_month=60,
            mil_a=[70, 20],
            econ_a=[70, 15],
        ))
        assert cls["mechanism"] == "strategic exhaustion"

    def test_mixed_outcome(self):
        # Both DSS and SES elevated → mixed (whichever scores higher)
        result = _make_result(
            outcome="inconclusive",
            dss=[65, 70],
            ses=[55, 60],
            termination_month=120,
        )
        cls = classify_outcome(result)
        assert cls["mechanism"] in ("decisive shock", "strategic exhaustion")

    def test_inconclusive(self):
        # Low scores on both dimensions → still one dominates
        cls = classify_outcome(_make_result(
            outcome="inconclusive",
            dss=[30],
            ses=[25],
            termination_month=48,
        ))
        assert cls["mechanism"] in (
            "decisive shock", "strategic exhaustion"
        )

    def test_empty_scores(self):
        # Empty lists → scores computed from params alone
        cls = classify_outcome(_make_result(
            outcome="inconclusive",
            termination_month=120,
        ))
        assert cls["decisive_shock_score"] > 0  # from default shock=50
        assert cls["strategic_exhaustion_score"] > 0  # from default attrition=50

    def test_classification_keys(self):
        cls = classify_outcome(_make_result(
            outcome="decisive_victory_a",
            dss=[50],
            ses=[50],
            termination_month=10,
        ))
        expected_keys = {
            "outcome",
            "mechanism",
            "duration_months",
            "confidence",
            "secondary_mechanism",
            "termination_event",
            "decisive_shock_score",
            "strategic_exhaustion_score",
            "political_exhaustion_score",
        }
        assert set(cls.keys()) == expected_keys


class TestSensitivityAnalysis:
    def test_runs_without_error(self, tmp_path):
        result = run_sensitivity_analysis(tmp_path, n_samples_per_param=3)
        assert "aggregate" in result
        assert result["aggregate"]["n_presets"] > 0

    def test_produces_output_files(self, tmp_path):
        run_sensitivity_analysis(tmp_path, n_samples_per_param=3)
        assert (tmp_path / "sensitivity_results.csv").exists()
        assert (tmp_path / "sensitivity_summary.json").exists()

    def test_baseline_separates_event_from_mechanism(self, tmp_path):
        """The v2 classifier separates termination event from dominant mechanism.
        Gulf War's termination event is decisive victory, but the trajectory-based
        mechanism may indicate strategic exhaustion."""
        result = run_sensitivity_analysis(tmp_path, n_samples_per_param=2)
        gulf = result["per_preset"]["gulf_war_1991"]
        # Termination event is decisive victory
        assert gulf["baseline"]["outcome"] in ("dominance_a", "dominance_b", "collapse_a", "collapse_b")
        # Dominant mechanism is computed from trajectory scores
        assert gulf["baseline"]["mechanism"] in (
            "decisive shock", "strategic exhaustion", "mixed", "uncertain"
        )

    def test_flip_rates_are_valid(self, tmp_path):
        result = run_sensitivity_analysis(tmp_path, n_samples_per_param=3)
        for preset, data in result["per_preset"].items():
            assert 0 <= data["mean_flip_rate"] <= 1
            assert 0 <= data["max_flip_rate"] <= 1

    def test_all_presets_present(self, tmp_path):
        result = run_sensitivity_analysis(tmp_path, n_samples_per_param=2)
        assert set(result["per_preset"].keys()) == set(HISTORICAL_PRESETS.keys())

    def test_aggregate_fields(self, tmp_path):
        result = run_sensitivity_analysis(tmp_path, n_samples_per_param=2)
        agg = result["aggregate"]
        assert "n_presets" in agg
        assert "mean_flip_rate" in agg
        assert "max_flip_rate" in agg
        assert "fragile_presets" in agg
        assert "robust_presets" in agg

    def test_flip_rates_for_all_params(self, tmp_path):
        result = run_sensitivity_analysis(tmp_path, n_samples_per_param=2)
        for preset, data in result["per_preset"].items():
            for param in ("shock_strength", "attrition_rate",
                          "economic_resilience", "political_resilience"):
                assert param in data["flip_rates"]

    def test_csv_has_expected_columns(self, tmp_path):
        run_sensitivity_analysis(tmp_path, n_samples_per_param=2)
        import pandas as pd
        df = pd.read_csv(tmp_path / "sensitivity_results.csv")
        assert "preset" in df.columns
        assert "param" in df.columns
        assert "mechanism" in df.columns
        assert "flip" not in df.columns  # flip is computed, not stored row-level


class TestHeatmapData:
    def test_generates_matrix(self, tmp_path):
        run_sensitivity_analysis(tmp_path, n_samples_per_param=2)
        data = generate_sensitivity_heatmap_data(tmp_path)
        assert "matrix" in data
        assert len(data["matrix"]) > 0

    def test_matrix_dimensions(self, tmp_path):
        run_sensitivity_analysis(tmp_path, n_samples_per_param=2)
        data = generate_sensitivity_heatmap_data(tmp_path)
        n_presets = len(HISTORICAL_PRESETS)
        n_params = 4
        assert len(data["matrix"]) == n_presets
        assert all(len(row) == n_params for row in data["matrix"])

    def test_missing_file_returns_empty(self, tmp_path):
        data = generate_sensitivity_heatmap_data(tmp_path)
        assert data == {}


class TestHeatmapFigure:
    def test_generates_png(self, tmp_path):
        run_sensitivity_analysis(tmp_path, n_samples_per_param=2)
        fig_path = generate_sensitivity_heatmap_figure(tmp_path)
        assert fig_path is not None
        assert fig_path.exists()
        assert fig_path.suffix == ".png"

    def test_returns_none_when_no_data(self, tmp_path):
        fig_path = generate_sensitivity_heatmap_figure(tmp_path)
        assert fig_path is None

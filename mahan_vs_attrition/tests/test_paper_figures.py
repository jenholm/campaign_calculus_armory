"""Figure validation tests: ensure all figures exist and contain data."""

from pathlib import Path

import pytest

FIGURES_DIR = Path("paper/figures")


class TestFiguresExist:
    """All expected figures must exist and be non-empty."""

    REQUIRED_FIGURES = [
        "fig_01_conceptual_model.png",
        "fig_02_observed_vs_predictive_dss.png",
        "fig_03_baseline_comparison.png",
        "fig_04_blind_validation.png",
        "fig_05_dss_vs_ses_scatter.png",
        "fig_06_trajectory_examples.png",
        "fig_07_case_study_scorecards.png",
        "fig_08_sensitivity_heatmap.png",
        "fig_09_internal_coefficient_sensitivity.png",
    ]

    def test_figures_directory_exists(self):
        assert FIGURES_DIR.exists(), f"Figures directory not found: {FIGURES_DIR}"

    @pytest.mark.parametrize("figure", REQUIRED_FIGURES)
    def test_figure_exists_and_nonempty(self, figure):
        path = FIGURES_DIR / figure
        assert path.exists(), f"Missing figure: {figure}"
        assert path.stat().st_size > 1000, f"Figure too small (< 1KB): {figure}"


class TestFiguresValid:
    """Figures should be valid PNG files."""

    @pytest.mark.parametrize("figure", TestFiguresExist.REQUIRED_FIGURES)
    def test_figure_is_valid_png(self, figure):
        path = FIGURES_DIR / figure
        if not path.exists():
            pytest.skip(f"Figure not found: {figure}")

        # Check PNG magic bytes
        with open(path, "rb") as f:
            header = f.read(8)
        assert header[:4] == b"\x89PNG", f"Invalid PNG header: {figure}"


class TestReportsExist:
    """Report files must exist."""

    def test_html_report_exists(self):
        html = Path("reports/mahan_vs_attrition_report.html")
        assert html.exists(), "HTML report not found"
        assert html.stat().st_size > 10000, "HTML report too small"

    def test_md_report_exists(self):
        md = Path("reports/mahan_vs_attrition_report.md")
        assert md.exists(), "Markdown report not found"

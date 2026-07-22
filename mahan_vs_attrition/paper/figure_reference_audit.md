# Figure Reference Audit

## Figure Reference Table

| Figure Filename | Section Reference | File Exists | Has Caption |
|---|---|---|---|
| fig_01_conceptual_model.png | *Unreferenced* | Yes | N/A |
| fig_02_observed_vs_predictive_dss.png | *Unreferenced* | Yes | N/A |
| fig_03_baseline_comparison.png | *Unreferenced* | Yes | N/A |
| fig_04_blind_validation.png | *Unreferenced* | Yes | N/A |
| fig_05_dss_vs_ses_scatter.png | *Unreferenced* | Yes | N/A |
| fig_06_trajectory_examples.png | *Unreferenced* | Yes | N/A |
| fig_07_case_study_scorecards.png | *Unreferenced* | Yes | N/A |
| fig_08_sensitivity_heatmap.png | results.tex (line 86) | Yes | Yes (line 87) |
| fig_09_internal_coefficient_sensitivity.png | results.tex (line 93) | Yes | Yes (line 94) |

## Text-Only Figure References (no `\includegraphics`)

The following figure labels are referenced in prose but have no corresponding `\includegraphics` command in any section file:

| Label | Section Reference | Note |
|---|---|---|
| fig:scatter | results.tex (line 7) | Referenced as `Figure~\ref{fig:scatter}` but no figure environment or `\includegraphics` found |

## Summary

| Metric | Count |
|---|---|
| Total figures on disk in `paper/figures/` | 9 |
| Total figures referenced via `\includegraphics` | 2 |
| Total figures missing from disk (referenced but not on disk) | 0 |
| Total figures on disk but unreferenced in any `.tex` file | 7 |
| All `\includegraphics` references have `\caption` | Yes (2/2) |
| Text-only figure references (no image) | 1 (`fig:scatter`) |

# Figure Cleanup Report

## Figure Inventory

| Filename | Purpose | Included via \includegraphics | Referenced via \ref | Recommendation |
|----------|---------|-------------------------------|---------------------|----------------|
| fig_01_conceptual_model.png | Conceptual model diagram | No | No | Add to introduction.tex (after line 7, alongside the framework description) |
| fig_02_observed_vs_predictive_dss.png | Observed vs predictive DSS comparison | No | No | Add to methods.tex (section "Observed versus Predictive Decision Scores", ~line 122) |
| fig_03_baseline_comparison.png | Logistic regression and random forest baseline comparison | No | No | Add to results.tex (section "Baseline Comparison Results", ~line 108) |
| fig_04_blind_validation.png | Blind validation results across 24 case studies | No | No | Add to results.tex (section "Blind Validation Results", ~line 101) |
| fig_05_dss_vs_ses_scatter.png | DSS vs SES scatter plot (91 wars) | No | Yes (\ref{fig:scatter} in results.tex:7) | Add \includegraphics to results.tex at the \ref{fig:scatter} location (~line 7) |
| fig_06_trajectory_examples.png | Example simulation trajectories | No | No | Move to supplementary materials (not directly referenced in text) |
| fig_07_case_study_scorecards.png | Case study simulation scorecards | No | No | Move to supplementary materials (detailed per-case data; Table~\ref{tab:simulation} covers this in main text) |
| fig_08_sensitivity_heatmap.png | Parameter sensitivity heatmap (6 presets × 4 parameters) | Yes (results.tex:89) | Yes (\ref{fig:sensitivity_heatmap} in results.tex:83) | Keep |
| fig_09_internal_coefficient_sensitivity.png | Internal coefficient sensitivity heatmap (23 coefficients × 3 presets) | Yes (results.tex:96) | Yes (\ref{fig:internal_sensitivity} in results.tex:83) | Keep |

## Summary

- Total figures: 9
- Referenced in manuscript: 2 (fig_08, fig_09)
- Referenced via \ref but missing \includegraphics: 1 (fig_05)
- Completely unreferenced: 6 (fig_01, fig_02, fig_03, fig_04, fig_06, fig_07)

## Recommendations

### Figures to add to manuscript (4)

1. **fig_01_conceptual_model.png** — Insert into `introduction.tex` after line 7 ("...enabling large-n quantitative analysis of war termination mechanisms."). The conceptual model diagram would visually support the three-component framework (DSS, SES, simulation) described in the introduction.

2. **fig_02_observed_vs_predictive_dss.png** — Insert into `methods.tex` in the "Observed versus Predictive Decision Scores" subsection (around line 122). This is the natural location for comparing the two DSS variants.

3. **fig_03_baseline_comparison.png** — Insert into `results.tex` in the "Baseline Comparison Results" subsection (around line 108). This subsection already discusses logistic regression vs. random forest but has no figure.

4. **fig_04_blind_validation.png** — Insert into `results.tex` in the "Blind Validation Results" subsection (around line 101). The text discusses 24 case studies but has no accompanying figure.

### Figure to complete reference (1)

5. **fig_05_dss_vs_ses_scatter.png** — `results.tex:7` already references `Figure~\ref{fig:scatter}` but no `\includegraphics` command exists. Add a `\begin{figure}...\end{figure}` block with `\includegraphics` and a matching `\label{fig:scatter}` near the text reference.

### Figures to move to supplementary (2)

6. **fig_06_trajectory_examples.png** — Example trajectories are illustrative but not referenced. Move to supplementary as a supporting visualization for the simulation methodology.

7. **fig_07_case_study_scorecards.png** — Detailed per-case scorecards duplicate information already in Table~\ref{tab:simulation}. Move to supplementary for readers wanting per-case detail.

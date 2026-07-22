# Final Figure Integrity Audit

**Date:** 2025-07-20
**Scope:** Figures fig_01 through fig_09 in `paper/figures/`

## Summary Table

| Figure | File Exists | Included in LaTeX | Caption Verified | Data Verified | Refs Exist |
|--------|-------------|-------------------|------------------|---------------|------------|
| fig_01_conceptual_model.png | ✅ 219,979 bytes | ✅ introduction.tex:9 | ✅ | N/A (conceptual) | ❌ No `\ref{fig:conceptual}` in text |
| fig_02_observed_vs_predictive_dss.png | ✅ 264,530 bytes | ✅ methods.tex:170 | ✅ | ✅ | ✅ methods.tex:166 |
| fig_03_baseline_comparison.png | ✅ 126,691 bytes | ✅ results.tex:51 | ❌ Caption mismatch | ❌ Values not from data | ✅ results.tex:47 |
| fig_04_blind_validation.png | ✅ 467,274 bytes | ✅ results.tex:155 | ✅ | ✅ | ✅ results.tex:151 |
| fig_05_dss_vs_ses_scatter.png | ✅ 77,291 bytes | ✅ results.tex:13 | ✅ | ✅ | ✅ results.tex:7 |
| fig_06_trajectory_examples.png | ✅ 57,291 bytes | ✅ supplementary.tex:9 | ⚠️ Caption overstates | N/A (trajectory) | ✅ supplementary.tex:5 |
| fig_07_case_study_scorecards.png | ✅ 121,118 bytes | ✅ supplementary.tex:20 | ✅ | ✅ | ✅ supplementary.tex:16 |
| fig_08_sensitivity_heatmap.png | ✅ 93,602 bytes | ✅ results.tex:135 | ✅ | ✅ | ✅ results.tex:129 |
| fig_09_internal_coefficient_sensitivity.png | ✅ 145,247 bytes | ✅ results.tex:142 | ✅ | ✅ | ✅ results.tex:129 |

## Detailed Findings

### fig_01_conceptual_model.png

**Caption:** "Conceptual model of the attritional iceberg. The visible decisive shock operates atop a larger attritional substrate that has already shifted the strategic balance."

**Script:** `scripts/generate_paper_figures.py:fig_01_conceptual_model()` draws four labeled boxes (Attrition Process, Strategic Vulnerability, Decisive Shock, War Termination) with connecting arrows and an annotation about "the historical mistake." Caption accurately summarizes the conceptual diagram.

**Refs issue:** The `\label{fig:conceptual}` is defined at `introduction.tex:11`, but no `\ref{fig:conceptual}` appears anywhere in the manuscript text. The figure is only implicitly present via its `\includegraphics` and surrounding prose. The label is orphaned.

---

### fig_02_observed_vs_predictive_dss.png

**Caption:** "Observed versus predictive DSS for eight historical cases..."

**Script:** `scripts/generate_paper_figures.py:fig_02_observed_vs_predictive_dss()` plots 8 cases with hardcoded observed and predictive DSS values.

**Data verification:**
- Script data: Gulf War (80.0/64.4), Six Day War (95.0/55.0), Franco-Prussian (85.0/53.0), WWI (60.0/52.4), WWII (50.0/54.6), Korea (45.0/62.7), Vietnam (30.0/69.9), Iran-Iraq (35.0/49.5)
- These match the outcome information delta table at `results.tex:107-114` exactly.
- Caption claim "Six Day War shows the highest positive delta" is correct (delta = +40.0).
- `methods.tex:166` states delta range "-39.9 to +40.0 (mean +2.3)" — computed from script values: mean = +2.31 ≈ +2.3. ✅
- Note: The table at `results.tex:116` states the mean as −0.6, which is incorrect (should be +2.3). This is a table error, not a figure error.

---

### fig_03_baseline_comparison.png

**Caption:** "Baseline comparison: logistic regression versus random forest feature importances and performance."

**Script:** `scripts/generate_paper_figures.py:fig_03_baseline_comparison()` plots five bar categories: "Duration Only" (0.45), "Casualties Only" (0.38), "Power Ratio" (0.42), "Majority Class" (0.35), "DSS+SES" (0.52). Title: "Baseline Comparison: Does DSS+SES Add Information?"

**Issues found:**
1. **Caption-image mismatch.** The caption claims the figure compares "logistic regression versus random forest," but the figure actually shows five model/feature-set variants with their classification accuracies. The logistic regression (54.8% test accuracy) and random forest (73.2% test accuracy) cited in the text at `results.tex:47` are not represented in the figure. The surrounding text says "Figure~\ref{fig:baseline} compares the two models" but the figure shows a different comparison.
2. **Values are hardcoded, not derived from data.** The accuracy values (0.45, 0.38, 0.42, 0.35, 0.52) are hardcoded in the Python script and do not correspond to any CSV data file or to the 54.8%/73.2% accuracy values cited in the manuscript text.

---

### fig_04_blind_validation.png

**Caption:** "Blind validation results: confusion matrix for 24 historical case studies with neutral default parameters."

**Script:** `scripts/generate_paper_figures.py:fig_04_blind_validation()` loads 24 cases from `data/blind_validation_cases.yml`, runs simulation with default parameters, classifies, and plots per-case results plus error analysis.

**Data verification:**
- YAML file contains exactly 24 cases. ✅
- `data/processed/blind_prediction_results.csv` confirms: 24 rows, 0 correct matches, 3 false_decisive (Soviet-Afghan, Boer, Chechen), 21 other_mismatch. Accuracy = 0/24 = 0%. ✅
- Text at `results.tex:151`: "predicts 'uncertain' for 21 of 24 cases, correctly identifies 0 cases as decisive, and misclassifies 3 attritional cases as decisive" — matches CSV. ✅

---

### fig_05_dss_vs_ses_scatter.png

**Caption:** "DSS versus SES scatter for 91 wars with complete battle-level data. Points are jittered to reveal overlapping observations."

**Source:** Copied from `reports/figures/fig_03_dss_vs_ses_scatter.png` via `copy_existing_figures()` in the generation script. The source function `src/mahan_vs_attrition/viz/plots.py:plot_dss_vs_ses_scatter()` creates a jittered scatter with density contours and quadrant labels (Decisive Shock, Strategic Exhaustion, Uncertain, Mixed).

**Data verification:**
- "91 wars" claim is consistent with text at `results.tex:7` and `results.tex:3` ("full DSS computation requires battle-level data from the Interstate War Battle Dataset, which covers only 91 of the 4,812 wars"). ✅
- Caption caveat about metric construction matches `results.tex:9` discussion. ✅

---

### fig_06_trajectory_examples.png

**Caption:** "Simulation trajectories for four historical presets. Military, economic, and political state variables evolve over time, showing the interaction between shock events and attritional decay."

**Source:** Copied from `reports/figures/fig_04_attrition_trajectories_selected_wars.png`. The generating function `src/mahan_vs_attrition/viz/plots.py:plot_attrition_trajectories()` plots only `year` vs `cinc` (one metric), with title "Capability Trajectories During War."

**Issue:** The caption claims "Military, economic, and political state variables evolve over time," but the source generating function only plots CINC scores (a composite capability index), not the three individual state variables. The actual PNG file (copied from a prior generation run) may have been produced by a different code path. The caption may overstate what the figure shows, depending on which version of the code produced the source file.

---

### fig_07_case_study_scorecards.png

**Caption:** "Case study scorecards for seven historical conflicts. Each scorecard compares the model's mechanism classification with the historical interpretation."

**Source:** Copied from `reports/figures/fig_07_case_study_scorecards.png`. The generating function `src/mahan_vs_attrition/viz/plots.py:plot_case_study_scorecards()` plots manual DSS/SES bars overlaid with model scores, with dominant mechanism annotations.

**Data verification:**
- "Seven historical conflicts" is consistent with the 7 case studies in Table 2 (`results.tex:74-86`): Gulf War, Franco-Prussian, Vietnam, WWI, WWII, Korea, Iran-Iraq. ✅
- `data/manual/manual_case_scores.csv` contains 30 total case studies, but only 7 primary ones are used in the mechanism classification table. ✅

---

### fig_08_sensitivity_heatmap.png

**Caption:** "Parameter sensitivity heatmap showing classification flip rates across six historical presets and four control parameters. Darker cells indicate higher flip rates. All presets are classified as robust (mean flip rate < 20%)."

**Script:** `src/mahan_vs_attrition/simulation/sensitivity.py:generate_sensitivity_heatmap_figure()` reads from `sensitivity_summary.json` and plots a heatmap using RdYlGn_r colormap.

**Data verification:**
- "Six historical presets" matches `data/processed/sensitivity_results.csv`: gulf_war_1991, vietnam_war, wwi, franco_prussian, korean_war, iran_iraq (WWII absent from CSV). ✅
- "Four control parameters" matches `VARY_PARAMS`: shock_strength, attrition_rate, economic_resilience, political_resilience. ✅
- Flip rate robustness verified from CSV: Gulf War (0%), Vietnam (0%), WWI (0%), Franco-Prussian (~5%), Korean War (~5%), Iran-Iraq (0%). All < 20%. ✅
- Note: `HISTORICAL_PRESETS` in `war_dynamics.py` has 7 presets (includes wwii), but sensitivity_results.csv only contains 6 (wwii missing). The figure matches the generated CSV data.

---

### fig_09_internal_coefficient_sensitivity.png

**Caption:** "Internal coefficient sensitivity heatmap showing flip rates across 23 model coefficients and three representative presets. The battle loss rate is the only coefficient with non-zero flip rates (6.7% mean, 20% for Vietnam). All other coefficients are fully robust."

**Script:** `src/mahan_vs_attrition/simulation/sensitivity.py:generate_internal_coefficient_heatmap_figure()` reads from `internal_coefficient_sensitivity.json`.

**Data verification:**
- "23 model coefficients" matches `INTERNAL_COEFFICIENTS` dict in `sensitivity.py` (23 entries). ✅
- "Three representative presets" matches `test_presets = ["gulf_war_1991", "vietnam_war", "wwi"]`. ✅
- Battle loss rate flip rates from CSV:
  - Gulf War: 0 flips (all decisive) → 0%
  - Vietnam: 1 flip at value 0.08 (mechanism changes from decisive to uncertain) → 20%
  - WWI: 0 flips (all uncertain) → 0%
  - Mean: (0 + 0.20 + 0) / 3 = 6.7%. ✅
- All other 22 coefficients show 0 flips across all presets. ✅

---

## Issues Requiring Attention

| Priority | Figure | Issue |
|----------|--------|-------|
| High | fig_03 | Caption claims "logistic regression versus random forest" comparison but figure shows five feature-set variants; 73.2% RF accuracy not depicted |
| High | fig_03 | Accuracy values (0.45, 0.38, 0.42, 0.35, 0.52) are hardcoded in script, not derived from data files |
| Medium | fig_01 | `\label{fig:conceptual}` is orphaned — no `\ref{fig:conceptual}` text reference exists anywhere in the manuscript |
| Medium | fig_06 | Caption claims "Military, economic, and political state variables" but the generating function `plot_attrition_trajectories()` only plots CINC scores |
| Low | results.tex:116 | Outcome information delta table mean states −0.6 but should be +2.3 (same data referenced by fig_02) |

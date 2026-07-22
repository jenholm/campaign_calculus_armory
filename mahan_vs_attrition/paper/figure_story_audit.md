# Figure Story Audit

## Purpose
Ensure figures tell a coherent scientific story. Each figure should
advance the paper's argument, not just display data.

## Required Figures for the Paper

### Figure 1: Conceptual Model (NEW - needs to be created)
**Story:** Shows the attrition → vulnerability → shock → termination pathway.
**Components:**
- Box: "Attrition Process" (with arrows showing time progression)
- Box: "Strategic Vulnerability" (result of attrition)
- Box: "Shock Event" (decisive battle/campaign)
- Box: "War Termination"
- Arrows: Attrition → Vulnerability → (enables) Shock → Termination
- Annotation: "The historical mistake is treating the visible collapse event as the entire cause"

**File:** paper/figures/fig_01_conceptual_model.png (TO BE GENERATED)

**Status:** Does not exist. Needs to be drawn. This is the most important missing figure—it communicates the paper's core theoretical contribution at a glance.

### Figure 2: DSS vs SES Scatter (EXISTS: fig_03_dss_vs_ses_scatter.png)
**Story:** Shows that most wars fall along both axes, not just one.
**Text reference:** Section "Decomposing War Termination" (results.tex:7–9)
**Existing file:** `reports/figures/fig_03_dss_vs_ses_scatter.png`
**Status:** EXISTS in `reports/figures/` but NOT in `paper/figures/`. Needs to be copied/symlinked. The manuscript references this as `\ref{fig:scatter}` but the label is never defined—needs `\label{fig:scatter}` added to the LaTeX.

**Caption should state:** "Relationship between Decisive Shock Score (DSS) and Strategic Exhaustion Score (SES) across 4,220 wars. Negative correlation (r = -0.34, p < 0.001) confirms tendency toward specialization, but substantial scatter indicates mixed dynamics are common. Cluster in upper-right quadrant represents wars with both decisive battles and prolonged exhaustion (e.g., WWII, Thirty Years' War, Napoleonic Wars)."

### Figure 3: Three Historical Trajectories (EXISTS: fig_04_attrition_trajectories_selected_wars.png)
**Story:** Gulf War (decisive), WWI (attritional), Vietnam (attritional) show different patterns.
**Text reference:** Section "Historical Case Studies" (referenced in discussion.tex implicitly)
**Existing file:** `reports/figures/fig_04_attrition_trajectories_selected_wars.png`
**Status:** EXISTS in `reports/figures/` but NOT in `paper/figures/`. Needs to be copied/symlinked.

**Caption should state:** "Simulated war trajectories for three historical cases: Gulf War 1991 (decisive shock), World War I (strategic exhaustion), and Vietnam War (strategic exhaustion). State variables (military, economic, political will) shown over simulated time. The Gulf War shows rapid military collapse of Iraq; WWI shows gradual parallel decline of both sides; Vietnam shows US political will erosion despite military advantage."

### Figure 4: Baseline Comparison (NEEDS GENERATION from baseline_comparison.csv)
**Story:** DSS+SES vs simpler heuristics — shows interpretive value.
**Components:** Bar chart of accuracy for each baseline model.
**File:** paper/figures/fig_04_baseline_comparison.png (TO BE GENERATED)

**Status:** DOES NOT EXIST. No `baseline_comparison.csv` file exists in the repo. The data for this figure is presented only in Table 6 (results.tex:132–147). Can be hand-constructed from the table:
- Majority class: 0.44
- Duration only: 0.51
- Casualties only: 0.49
- Power ratio only: 0.47
- DSS + SES: 0.62

**Caption should state:** "Classification accuracy of the DSS/SES framework compared to four baseline heuristics. The DSS/SES framework achieves 62% accuracy, an 11-percentage-point improvement over the best simple heuristic (duration-only, 51%) and 18 points above the majority class baseline (44%)."

### Figure 5: Sensitivity Heatmap (NEEDS GENERATION — sensitivity data in Table 5)
**Story:** Most presets are robust; some parameters are fragile.
**Text reference:** Section "Parameter Sensitivity" (results.tex:92–118)
**File:** paper/figures/fig_05_sensitivity_heatmap.png (TO BE GENERATED)

**Status:** DOES NOT EXIST. No `sensitivity_heatmap.png` exists anywhere in the repo. Data is available in Table 5 (results.tex:98–116). Can be generated from the six presets × four parameters matrix.

**Caption should state:** "Parameter sensitivity heatmap showing flip rates (proportion of ±50% parameter variations that change mechanism classification) for six historical presets across four parameters. Mean flip rate of 0.30 indicates that ~70% of parameter variations do not change classification. No preset exceeds 0.50, confirming general robustness."

### Figure 6: Blind Validation Results (NEEDS GENERATION — needs data from blind_prediction_results.csv)
**Story:** Model predicts mechanism from structure alone (no historical labels).
**Components:** Confusion matrix or accuracy bar chart.
**File:** paper/figures/fig_06_blind_validation.png (TO BE GENERATED)

**Status:** DOES NOT EXIST. No `blind_prediction_results.csv` exists in the repo. The results are described only in text (results.tex:120–124): 6/10 correct (60%), with error analysis showing "over-mixed" tendency. If the CSV is created, this figure can be generated. Alternatively, a simple bar chart can be constructed from the text:
- Correct: 6
- Incorrect: 4
- By type: attritional 75%, decisive 50%, mixed (not reported)

**Caption should state:** "Blind validation results: simulation predictions of termination mechanism using only initial conditions (no historical outcome labels). Model correctly classified 6 of 10 cases (60%), with higher accuracy on attritional cases (75%) than decisive cases (50%). The most common error type was over-classification as 'mixed.'"

### Figure 7: Case Study Scorecards (EXISTS: fig_07_case_study_scorecards.png)
**Story:** Manual vs model comparison for key cases.
**Text reference:** Section "Validation" (referenced implicitly in results.tex:66–90)
**Existing file:** `reports/figures/fig_07_case_study_scorecards.png`
**Status:** EXISTS in `reports/figures/` but NOT in `paper/figures/`. Needs to be copied/symlinked.

**Caption should state:** "Manual expert assessment versus model classification for six historical case studies. Checkmarks indicate agreement, X indicates disagreement, tilde indicates partial agreement. Model achieves 5/6 agreement on termination type, 4/6 on duration, 2/6 on trajectory shape."

---

## Narrative Flow

The figures should tell this story:

1. **Conceptual model** → "Here's our framework" — attrition creates vulnerability, shock exploits it
2. **DSS vs SES scatter** → "Wars vary on both axes" — most wars aren't purely one type
3. **Historical trajectories** → "Here's what the patterns look like" — three exemplars
4. **Baseline comparison** → "Our framework adds interpretive value" — outperforms simple heuristics
5. **Sensitivity** → "The framework is robust to parameter changes" — classifications hold under perturbation
6. **Blind validation** → "It works even without knowing the answer" — generalization evidence
7. **Case study scorecards** → "It matches expert judgment on key cases" — face validity

**Current narrative gap:** The conceptual model (Figure 1) is the most important figure because it communicates the core theoretical contribution. Without it, the reader must infer the framework from text alone. The scatter (Figure 2) and trajectories (Figure 3) are the most important empirical figures. The baseline comparison (Figure 4) is important for justifying the framework's value. The sensitivity (Figure 5), blind validation (Figure 6), and scorecards (Figure 7) are supporting evidence.

## Missing Figures

1. **Conceptual model** (Figure 1): Needs to be drawn. Shows attrition → vulnerability → shock → termination. This is the paper's core theoretical contribution visualized. Can be created with TikZ, draw.io, or matplotlib with annotations.

2. **Baseline comparison bar chart** (Figure 4): Can be generated from the data in Table 6 (results.tex:132–147). No CSV exists; data must be extracted from the table.

3. **Sensitivity heatmap** (Figure 5): Can be generated from the data in Table 5 (results.tex:98–116). No CSV or existing heatmap exists.

4. **Blind validation confusion matrix** (Figure 6): Can be generated from text description (results.tex:120–124). No CSV exists. If a proper confusion matrix is desired, the 10 case predictions need to be documented in a CSV.

## Figure Quality Checklist

For each figure:
- [ ] Resolution ≥ 300 DPI for print
- [ ] Font size readable (≥ 8pt)
- [ ] Color-blind friendly palette
- [ ] Caption is self-contained
- [ ] No unnecessary chart junk
- [ ] Axis labels clear
- [ ] Legend present if multiple series

### Per-figure status:

| Figure | Exists | In paper/figures/ | Caption written | Label defined | Quality check |
|--------|--------|-------------------|----------------|---------------|---------------|
| Fig 1 (Conceptual) | NO | NO | NO | NO | N/A |
| Fig 2 (Scatter) | YES (reports/) | NO | NO | NO | Needs copy + caption |
| Fig 3 (Trajectories) | YES (reports/) | NO | NO | NO | Needs copy + caption |
| Fig 4 (Baseline) | NO | NO | NO | NO | Needs generation |
| Fig 5 (Sensitivity) | NO | NO | NO | NO | Needs generation |
| Fig 6 (Blind val.) | NO | NO | NO | NO | Needs generation |
| Fig 7 (Scorecards) | YES (reports/) | NO | NO | NO | Needs copy + caption |

## Additional Observations

### Figure numbering mismatch
The manuscript uses `\ref{fig:scatter}` (results.tex:9) as the only figure reference, but no `\label{fig:scatter}` is defined anywhere. The `reports/figures/` directory uses sequential numbering (fig_01 through fig_07) that doesn't match the paper's narrative order. The paper should use its own figure numbering (1–7) independent of the reports directory.

### Missing figure references
Only one figure is explicitly referenced in the text (`fig:scatter` in results.tex:9). The other figures (trajectories, scorecards) are discussed in the text but never cross-referenced by figure number. Each figure should be explicitly referenced at least once.

### Data availability for figure generation
- Figure 2 (scatter): Data presumably in simulation output or DSS/SES computation pipeline. Not available as a standalone CSV.
- Figure 3 (trajectories): Data presumably from simulation runs. Not available as a standalone CSV.
- Figure 4 (baseline): Data available in Table 6 (results.tex:132–147). Can be hard-coded.
- Figure 5 (sensitivity): Data available in Table 5 (results.tex:98–116). Can be hard-coded.
- Figure 6 (blind validation): Data described in text (results.tex:120–124) but not in any file. Needs to be created.
- Figure 7 (scorecards): Data presumably in the scorecards figure generation script. Not available as a standalone CSV.

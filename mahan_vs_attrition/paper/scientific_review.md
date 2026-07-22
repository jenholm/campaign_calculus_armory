# Scientific Review: Manuscript Assessment

## Executive Summary

Overall assessment: **Adequate with Critical Issues**

The manuscript presents an ambitious framework for distinguishing "decisive shock" and "strategic exhaustion" as war termination mechanisms. The core contribution—moving beyond a binary classification to treat both as interacting mechanisms—is well-motivated and intellectually honest. However, the paper has serious internal contradictions: the `model_assumptions_audit.md` identifies critical circularity and encoding problems that the manuscript itself does not adequately address. The manuscript's claims often overstate what the methodology can support.

### Key strengths
1. Clear research question with genuine intellectual contribution (moving beyond binary classification)
2. Comprehensive dataset (4,220+ wars, seven sources)
3. Honest treatment of ambiguity (58% blind validation accuracy framed as evidence of genuine ambiguity, not failure)
4. Good literature review covering both Mahan and Clausewitz traditions
5. Well-structured ablation study design comparing DSS-only, SES-only, and combined models
6. Transparent limitations section (circularity, sensitivity, validation sample size)

### Key weaknesses
1. **Circularity problem**: The `model_assumptions_audit.md` (line 389–419) identifies that DSS and SES are computed from the same simulation functions that produce the dynamics—a mathematical tautology. The manuscript acknowledges this in limitations (line 3–5) but the Results section still presents simulation-derived DSS/SES as meaningful empirical findings without adequate qualification.
2. **Historical presets encode known outcomes**: The presets are parameterized to produce the answer they "find" (see `model_assumptions_audit.md` lines 389–419). This is not testing a hypothesis—it is demonstrating an assumption.
3. **No figures in paper/figures/**: The `paper/figures/` directory contains only `.gitkeep`. The manuscript references figures (`\ref{fig:scatter}`, `\ref{fig:trajectories}`, etc.) but no figure files exist in the paper directory. The figures in `reports/figures/` use different numbering and are not linked.
4. **Baseline comparison and blind validation CSVs don't exist**: The task references `baseline_comparison.csv` and `blind_prediction_results.csv` for figure generation, but neither file exists in the repo.
5. **Coefficient justification absent**: All simulation coefficients (0.04, 0.004, 1.5, 5.0, 4.0, 0.8, 0.2, etc.) are "magic numbers" with no historical calibration, as noted in `model_assumptions_audit.md` lines 21–36.
6. **Overclaiming in results**: The Results section presents findings as if the simulation is testing the hypothesis rather than encoding it.

---

## Section-by-Section Review

### Abstract

| Claim | Supported? | Notes |
|-------|-----------|-------|
| "4,220+ wars from antiquity to the present" | Partial | Dataset includes pre-modern wars, but DSS requires battle-level data only available for modern interstate wars. The "antiquity" claim is overstated. |
| "Both DSS and SES contribute independently" | Partial | Supported by ablation table (Table 2), but the independence claim is undermined by the circularity identified in the assumptions audit. |
| "Exhaustion features have higher independent predictive power" | Partial | ΔAIC = -289 vs -235 supports this numerically, but again depends on SES being computed independently of attrition dynamics—which it is not. |
| "Majority of wars exhibit substantial attritional dynamics" | Partial | 44.2% Strategic Exhaustion + 24.4% Mixed. But the classification threshold is arbitrary (see limitations line 21). |
| "58% accuracy—above chance but below expert consensus" | Partial | Abstract says 58%, introduction says 58%, but results.tex:124 says "60% accuracy" (6 of 10). Internal inconsistency. |
| "Robust to ±50% weight perturbations, mean flip rate 38%" | Y | But this is only for the historical presets, not the full dataset. The 38% flip rate is stated in the introduction but 0.30 in the results—internal inconsistency. |

- **Overclaiming**: "From antiquity to the present" overstates coverage. DSS primarily works for 1600+ with battle data.
- **Missing**: No mention that the simulation-derived DSS/SES metrics are circular. The abstract presents them as empirical findings.

### Introduction

- **Research question clear**: Y
- **Contribution stated**: Y (lines 5–7)
- **Literature review adequate**: Y (references Mahan, Clausewitz, Luttwak, Biddle, COW, UCDP, etc.)
- **Internal inconsistency**: Line 9 states "mean flip rates of 38%" but the Results section (line 118) reports mean flip rate of 0.30. The 38% figure appears to be from a different analysis or is an error.
- **Missing**: No acknowledgment that the simulation approach faces the circularity risk identified in the assumptions audit.

### Background (Mahan vs Attrition)

- **Historical accuracy**: Good. Mahan, Clausewitz, Luttwak, Biddle are correctly characterized.
- **Balance between hypotheses**: Good. Presents both traditions fairly before arguing for integration.
- **Gap identification**: Clear and well-motivated (lines 17–23). The argument that no large-n study has systematically quantified both mechanisms is plausible.
- **Missing citation**: No citation for the "attritional iceberg" metaphor—it appears to be an original contribution, which should be stated explicitly.

### Data

- **Sources documented**: Y (Table 1, line 3)
- **Coverage described**: Y (seven sources with wars, participant-years, battles)
- **Limitations stated**: Partial. Line 44 notes IWB geographic/temporal limitations. But no discussion of how the 4,220 number was derived from merging (possible double-counting across sources).
- **Overclaiming**: "Largest and most diverse dataset yet assembled for computational analysis of war termination mechanisms" (line 56)—needs citation or qualification.
- **Missing**: No description of how missing data was handled beyond "multiple imputation" (line 55). No report of missing data rates.

### Methods

- **DSS computation clear**: Y (Equation 1, lines 9–26). Nine components with weights documented.
- **SES computation clear**: Y (Equation 2, lines 34–52). Ten components with weights documented.
- **Classification rule justified**: Partially (Equation 3, lines 60–67). The threshold of 0.5 is arbitrary; the limitations section acknowledges this (line 21) but the methods section does not justify it.
- **Simulation model documented**: Y (lines 71–138). State variables, update equations, shock mechanics, termination conditions all specified.
- **Statistical methods appropriate**: Y. Logistic regression, ablation, survival analysis are standard.
- **Circularity not addressed**: The methods section does not acknowledge that DSS and SES computed from simulation outputs (Equations 5–6) are tautological with the simulation dynamics. This is only raised in the limitations.
- **Coefficient justification missing**: All magic numbers (0.04, 0.004, 1.5, 5.0, 4.0, 0.8, 0.2, 0.3, etc.) are stated without historical or empirical justification. The `model_assumptions_audit.md` (lines 21–36) correctly identifies this as a critical issue.

### Results

- **Every claim has evidence**: Partial.
  - Termination type distribution (31.4%/44.2%/24.4%): Evidence via classification rule, but the classification itself is method-dependent.
  - DSS vs SES scatter r = -0.34: Referenced but figure doesn't exist in paper/figures/.
  - Logistic regression (Table 2): Evidence provided. OR and CI reported.
  - Ablation (Table 3): Evidence provided. ΔAIC values reported.
  - Survival analysis: Evidence provided (HR = 1.34 and 0.72).
  - Simulation validation (Table 4): Evidence provided, but 5/6 termination agreement on n=6 cases is not statistically meaningful.
  - Sensitivity (Table 5): Evidence provided.
  - Blind validation (60% on n=10): Evidence provided, with honest caveats.
  - Baseline comparison (Table 6): Evidence provided. 0.62 accuracy vs baselines.
- **Figures referenced**: `fig:scatter` (line 9) — no figure file exists.
- **Tables referenced**: Tables 1–6 all referenced. Y.
- **Statistical significance reported**: Y for all statistical tests.
- **Overclaiming**: Line 118 states "no preset exhibits a mean flip rate above 0.50, confirming that classifications are generally robust"—this is a weak claim given the small preset count (n=6) and the fact that 0.50 is already quite high.

### Discussion

- **Interpretation appropriate**: Mostly. The "attritional iceberg" interpretation is compelling.
- **Limitations acknowledged**: Y in the limitations section, but the discussion itself does not revisit the circularity issue.
- **Comparison with literature**: Y (Bennett & Stam, Huth, Freedman, Stevenson).
- **Overclaiming**: Line 3: "the majority of wars—including those traditionally classified as 'decisive battles'—exhibit substantial attritional dynamics." The 38% figure (wars with SES > 0.5 among "decisive" wars) is based on a classification threshold, not independent historical evidence.

### Limitations

- **Comprehensiveness**: Good. Six subsections covering circularity, sensitivity, validation, data quality, subjectivity, and simplifications.
- **Honesty**: Excellent. The circularity admission (lines 3–5) is unusually transparent. The small validation sample concern (lines 11–13) is well-stated with exact binomial CI.
- **Framing**: The final paragraph (lines 25–27) is too dismissive of the limitations: "Despite these limitations, we believe that the overall pattern...is robust." This comes too quickly after acknowledging serious methodological concerns. Should spend more time on what would change the conclusion.

### Conclusion

- **Findings restated accurately**: Y
- **Future directions appropriate**: Y (extend to non-Western conflicts, more sophisticated simulation, contemporary conflicts)
- **Overclaiming**: Line 5: "the decisive battle is best understood not as an alternative to attrition but as a mechanism that operates within an attritional context." This is a strong claim that the simulation-based evidence cannot fully support given the circularity issues.

---

## Figure-Text Consistency

| Figure | Referenced in text | Caption matches content | Data matches claims | Status |
|--------|-------------------|------------------------|--------------------|--------|
| DSS vs SES scatter (`fig:scatter`) | results.tex:9 | N/A (no figure) | N/A | **MISSING** from paper/figures/. Exists as `reports/figures/fig_03_dss_vs_ses_scatter.png` |
| Attrition trajectories | Not explicitly referenced by label | N/A (no figure) | N/A | Exists as `reports/figures/fig_04_attrition_trajectories_selected_wars.png` |
| Case study scorecards | Not explicitly referenced by label | N/A (no figure) | N/A | Exists as `reports/figures/fig_07_case_study_scorecards.png` |
| Baseline comparison | results.tex:130 ("Table 6") | N/A (no figure) | N/A | **MISSING** — no CSV or figure |
| Sensitivity heatmap | Not referenced | N/A (no figure) | N/A | **MISSING** — not generated |
| Blind validation | Not referenced as figure | N/A (no figure) | N/A | **MISSING** — no CSV or figure |
| Conceptual model | Not referenced | N/A (no figure) | N/A | **MISSING** — needs creation |

**Critical issue**: The manuscript references figures via `\ref{}` but the `paper/figures/` directory is empty. No figures exist in the paper directory. The figures in `reports/figures/` use different numbering and are not referenced by the manuscript.

---

## Table-Text Consistency

| Table | Referenced in text | Data matches claims |
|-------|-------------------|---------------------|
| Table 1 (Data sources) | data.tex:3 | Y — numbers match text |
| Table 2 (Logistic regression) | results.tex:13 | Y — OR values match text interpretation |
| Table 3 (Ablation) | results.tex:42 | Y — ΔAIC values match text |
| Table 4 (Simulation validation) | results.tex:68 | Y — checkmarks match text summary |
| Table 5 (Sensitivity) | results.tex:96 | Y — mean flip rate matches |
| Table 6 (Baseline comparison) | results.tex:130 | Y — accuracy values match text |

All tables are properly referenced and data matches claims.

---

## Citation Audit

| Claim type | Supported? | Notes |
|-----------|-----------|-------|
| Historical claims (Mahan, Clausewitz, battles) | Y | mahan1890, clausewitz1832, wawro2003, howard1979, friedman1998 all cited |
| Methodological claims (Lanchester, COW, UCDP) | Y | lanchester1916, singer1972, gleditsch2002, rester2019, brecke1999 all cited |
| Statistical claims (logistic regression, Cox) | N | No citation for the statistical methodology itself. Standard methods, but should cite a textbook (e.g., Hosmer-Lemeshow for logistic regression, Collett for survival analysis). |
| "Attritional iceberg" metaphor | N | Original contribution not attributed as such. |
| "Delphi process with five domain experts" (methods.tex:28) | N | No citation or appendix documenting this process. |
| IWB dataset limitations | Y | rester2019 cited |
| Comparison with literature (Bennett/Stam, Huth) | Y | bennett2000, huth1996 cited |
| Case study literature (Freedman, Stevenson) | Y | freedman1982, stevenson2003 cited |

---

## Recommendations

### Must fix before submission:
1. **Create or copy all figures into `paper/figures/`**: The manuscript references figures but the directory is empty. At minimum: DSS vs SES scatter, attrition trajectories, and case study scorecards need to be placed in `paper/figures/` with consistent naming.
2. **Address circularity prominently**: The limitations section admits circularity, but the Results section still presents simulation-derived DSS/SES as findings. Either (a) add a prominent caveat to every results subsection that uses simulation-derived metrics, or (b) separate the empirical DSS/SES (from IWB/COW data) from simulation-derived DSS/SES and present them as distinct analyses.
3. **Resolve numerical inconsistencies**: (a) Introduction line 9 says "mean flip rates of 38%" but results.tex:118 says "mean flip rate of 0.30." (b) Abstract says "58% accuracy" but results.tex:124 says "60% accuracy (6 of 10)." (c) Results.tex:118 claims "Gulf War and Franco-Prussian presets show the highest robustness (mean flip rates of 0.25)" but the table shows both at 0.20—lower than Korea/Iran-Iraq at 0.30 and WWI at 0.25. These contradictions undermine credibility.
4. **Generate or locate baseline_comparison.csv and blind_prediction_results.csv**: These are needed for Figure 4 (baseline comparison bar chart) and Figure 6 (blind validation confusion matrix). Without them, two figures cannot be created.
5. **Justify or acknowledge all simulation coefficients**: The magic numbers (0.04, 0.004, 1.5, 5.0, 4.0, 0.8, 0.2, 0.3) need either historical grounding or explicit treatment as free parameters with documented sensitivity.

### Should fix:
1. **Add figure labels and captions to all `\ref{}` commands**: Ensure every `\ref{fig:...}` has a corresponding `\label{fig:...}` and exists as a file.
2. **Qualify "from antiquity to the present"**: DSS requires battle-level data only available from ~1600. The abstract should say "from the early modern period to the present" or qualify which metrics apply to which time periods.
3. **Add citation for statistical methods**: Cite a standard reference for logistic regression and Cox proportional hazards.
4. **Document the Delphi process**: Either cite a supplement/appendix or remove the claim about expert-validated weights.
5. **Discuss double-counting risk**: When merging seven datasets, some wars appear in multiple sources. The methods should address how this was handled.
6. **Add missing data rates**: The data section mentions imputation but doesn't report how much data was missing.
7. **Strengthen the limitations conclusion**: The final paragraph of limitations.tex is too quick to dismiss concerns. Spend more time on what would change the conclusion.

### Nice to have:
1. **Create the conceptual model figure** (Figure 1 in the task spec): The attrition → vulnerability → shock → termination pathway would strengthen the introduction.
2. **Add a sensitivity heatmap figure**: The sensitivity data in Table 5 would be more impactful as a visualization.
3. **Add a blind validation confusion matrix figure**: Would make the 60% accuracy result more interpretable.
4. **Add a table summarizing all simulation coefficients with their stated or assumed justification**.
5. **Consider adding a "threats to validity" subsection** to the limitations, organized as internal/external/construction validity.

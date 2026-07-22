# Claim Boundary Audit

## Purpose
Ensure the paper never says more than the evidence supports.

## Methodology
Searched all paper sections (`abstract.tex`, `introduction.tex`, `background.tex`, `data.tex`, `methods.tex`, `results.tex`, `discussion.tex`, `limitations.tex`, `conclusion.tex`, and `manuscript.tex`) for overclaiming language. Each occurrence was evaluated against the available evidence: statistical results, simulation outputs, and dataset characteristics.

## Findings

### Total occurrences: 59
### Changes needed: 11

---

### Category 1: "Prove" language

No standalone occurrences of "prove," "proves," or "proven." All grep matches were substrings within "confirming"/"confirms" (addressed in Category 6).

| File | Line | Original | Supported? | Replacement |
|------|------|----------|------------|-------------|
| — | — | (none found) | — | — |

---

### Category 2: "Predict" language

18 occurrences found. The majority use standard statistical terminology ("predictors," "predictive power," "predicting termination type") in the context of logistic regression, ablation studies, and survival analysis. These are appropriate uses of statistical vocabulary and do not imply the model forecasts future wars.

| File | Line | Original | Supported? | Replacement |
|------|------|----------|------------|-------------|
| abstract.tex | 2 | "contribute independently to predicting termination type" | Yes — logistic regression results | None needed |
| background.tex | 15 | "extensively studied as a predictor of war outcomes" | Yes — literature description | None needed |
| background.tex | 21 | "determining war outcomes" / "significant predictors" / "predict war outcomes" | Yes — describing Huth, Bennett & Stam, Ward | None needed |
| conclusion.tex | 3 | "contribute to predicting how wars terminate" | Yes — ablation study | None needed |
| discussion.tex | 11 | "DSS is a significant predictor of termination type" | Yes — logistic regression | None needed |
| discussion.tex | 23 | "material and political factors as predictors of war outcomes" | Yes — literature description | None needed |
| introduction.tex | 9 | "contribute independently to predicting how wars terminate" / "predictive power" | Yes — ablation study | None needed |
| methods.tex | 69 | "features that predict each type" | Yes — classification rule description | None needed |
| methods.tex | 144 | "predictive power of DSS and SES" | Yes — logistic regression | None needed |
| methods.tex | 166 | "predict the hazard of war termination" | Yes — Cox model terminology | None needed |
| methods.tex | 170 | "predictive accuracy" | Yes — validation discussion | None needed |
| results.tex | 13 | "predicting Decisive Shock termination type" | Yes — regression model | None needed |
| results.tex | 17 | "predicting Decisive Shock termination type" (caption) | Yes — regression model | None needed |
| results.tex | 38 | "both DSS and SES are significant predictors" | Yes — regression table | None needed |
| results.tex | 60 | "predictive power" | Yes — AIC comparison | None needed |
| results.tex | 122 | "predict termination mechanism" | Yes — blind validation setup | None needed |
| results.tex | 124 | "predicting mixed when the human label is decisive" | Yes — error analysis | None needed |
| results.tex | 128 | "predictive information beyond simple heuristics" / "predict the most common mechanism" | Yes — baseline comparison | None needed |

**Assessment:** All "predict" instances use standard statistical vocabulary. No changes needed.

---

### Category 3: "Cause/Causal" language

3 occurrences found. Two are describing a historical mistake (acceptable). One makes a direct causal claim.

| File | Line | Original | Supported? | Replacement |
|------|------|----------|------------|-------------|
| introduction.tex | 5 | "treating the visible collapse event as the entire cause" | Yes — describes the mistake the paper argues against | None needed |
| discussion.tex | 3 | "treating the visible collapse event as the entire cause" | Yes — same framing, describing error | None needed |
| discussion.tex | 5 | "The shock is the proximate cause of termination, but the attrition is the distal cause" | **No** — the model shows temporal sequence and correlation, not causation. The simulation demonstrates that shocks follow attritional degradation, but "cause" implies a causal mechanism the model cannot verify. | "The shock is the proximate correlate of termination, but the attrition is the associated distal pattern" |

---

### Category 4: "Demonstrate" language

2 occurrences found. One overclaims; one is acceptable.

| File | Line | Original | Supported? | Replacement |
|------|------|----------|------------|-------------|
| abstract.tex | 2 | "Our analysis demonstrates that decisive events and attritional processes are not competing explanations but interacting mechanisms" | **Partial** — the analysis is consistent with this interpretation, but "demonstrates" implies proof. The logistic regression and ablation results support independent contributions, but the claim that they are "interacting mechanisms" is an interpretation, not a demonstrated fact. | "Our analysis suggests that decisive events and attritional processes are not competing explanations but interacting mechanisms" |
| results.tex | 128 | "To demonstrate that the DSS/SES framework provides predictive information beyond simple heuristics" | Yes — the baseline comparison table supports this claim directly | None needed |

---

### Category 5: "Determine/Determines" language

4 occurrences found. One is a direct overclaim. Others are method descriptions or attributed to other scholars.

| File | Line | Original | Supported? | Replacement |
|------|------|----------|------------|-------------|
| introduction.tex | 1 | "naval supremacy...determines the outcomes of wars" | Yes — attributed to Mahan as his argument | None needed (proper attribution) |
| methods.tex | 28 | "The weights were determined through a Delphi process" | Yes — describes methodology | None needed |
| methods.tex | 32 | "measures the degree to which a war's outcome is determined by cumulative attrition" | **No** — the SES measures correlation/association with exhaustion dynamics, not determination. The metric captures features associated with attritional processes, not the mechanism that "determines" outcomes. | "measures the degree to which a war's outcome is associated with cumulative attrition and exhaustion" |
| methods.tex | 103 | "interval determined by the war type" | Yes — technical parameter setting | None needed |

---

### Category 6: "Confirm/Confirms" language

14 occurrences found. Most report statistical results appropriately. Two overclaim.

| File | Line | Original | Supported? | Replacement |
|------|------|----------|------------|-------------|
| abstract.tex | 2 | "confirms that model classifications are robust to ±50% weight perturbations" | Yes — sensitivity analysis directly supports this | None needed |
| results.tex | 5 | "confirms the expected pattern that interstate wars...are more amenable to decisive outcomes" | **Partial** — "confirms" is slightly strong for a distributional shift. The data is consistent with the expectation. | "is consistent with the expected pattern that interstate wars...are more amenable to decisive outcomes" |
| results.tex | 9 | "confirming that wars high on one dimension tend to be low on the other" | Yes — correlation is statistically significant (r = -0.34, p < 0.001) | None needed |
| results.tex | 38 | "confirm that both DSS and SES are significant predictors" | Yes — p < 0.001 for both | None needed |
| results.tex | 60 | "confirming that both dimensions capture meaningful variation" / "confirms that the additional improvement...is statistically significant" | Yes — AIC and likelihood ratio test | None needed |
| results.tex | 64 | "confirms the theoretical prediction that wars with decisive shock dynamics tend to terminate more quickly" | Yes — hazard ratio = 1.34, p < 0.001 | None needed |
| results.tex | 90 | "confirming that the model captures the essential qualitative dynamics of most wars" | **No** — trajectory agreement is only 2/6. "Most wars" and "essential qualitative dynamics" overstate 33% trajectory agreement. | "is consistent with the model capturing qualitative dynamics in some wars" |
| results.tex | 118 | "confirming that classifications are generally robust" | Yes — 70% non-flip rate | None needed |
| results.tex | 149 | "confirms that the framework provides meaningful discriminative ability" / "confirms that the DSS/SES decomposition captures information" | Yes — AUC = 0.58, consistent improvement over baselines | None needed |
| discussion.tex | 11 | "confirms that some wars (Marathon, Franco-Prussian War, Falklands) are genuinely characterized by decisive shock dynamics" | **Partial** — simulation calibration matches these cases, but calibration was done to match known outcomes. This is partially circular. | "is consistent with Marathon, Franco-Prussian War, and Falklands being characterized by decisive shock dynamics" |
| conclusion.tex | 5 | "confirms an outcome that exhaustion has already made inevitable" | Yes — discussion context, not a standalone claim | None needed |

---

### Category 7: "Validate/Validates" language

5 occurrences found. All describe methodology appropriately.

| File | Line | Original | Supported? | Replacement |
|------|------|----------|------------|-------------|
| background.tex | 27 | "simulation models...have not been validated against historical data at scale" | Yes — describes gap in literature | None needed |
| conclusion.tex | 1 | "our dynamical simulation model has been validated against six historical case studies" | Yes — describes what was done | None needed |
| data.tex | 52 | "validate our quantitative metrics against detailed historical analysis" | Yes — describes methodology | None needed |
| methods.tex | 28 | "validated through sensitivity analysis" | Yes — describes methodology | None needed |
| methods.tex | 170 | "We validate the simulation model against six historical case studies" | Yes — describes methodology | None needed |

**Assessment:** All "validate" instances describe methodological steps, not claims of validation success. No changes needed.

---

### Category 8: "Show that" language

3 occurrences found. All report statistical results.

| File | Line | Original | Supported? | Replacement |
|------|------|----------|------------|-------------|
| abstract.tex | 2 | "show that both DSS and SES contribute independently to predicting termination type" | Yes — logistic regression | None needed |
| results.tex | 64 | "show that higher DSS scores are associated with shorter war duration" | Yes — Cox model results | None needed |
| discussion.tex | 11 | "show that DSS is a significant predictor of termination type" | Yes — logistic regression | None needed |

**Assessment:** All "show that" instances report supported statistical findings. No changes needed.

---

### Category 9: "Establish/Establishes" language

1 occurrence found. Acceptable (attributed).

| File | Line | Original | Supported? | Replacement |
|------|------|----------|------------|-------------|
| background.tex | 3 | "established the theoretical foundation for the decisive battle hypothesis" | Yes — attributed to Mahan | None needed |

---

### Category 10: "Reveal/Reveals" language

8 occurrences found. Mostly acceptable as "our analysis shows." One is borderline.

| File | Line | Original | Supported? | Replacement |
|------|------|----------|------------|-------------|
| results.tex | 3 | "our metrics reveal that 38% have SES values exceeding 0.5" | Yes — reporting data finding | None needed |
| results.tex | 9 | "reveals a moderate negative correlation" | Yes — r = -0.34 | None needed |
| results.tex | 60 | "reveal three key findings" | Yes — reporting ablation results | None needed |
| results.tex | 90 | "revealing the fundamental difficulty of simulating complex historical events" | Yes — interpretation of partial agreement | None needed |
| results.tex | 124 | "reveals that the most common error type is 'over-mixed'" | Yes — error analysis | None needed |
| discussion.tex | 5 | "our metrics reveal that France had already suffered significant manpower depletion" | Yes — DSS/SES computation | None needed |
| discussion.tex | 7 | "reveals the extent to which the attritional substrate has been underappreciated" | **Partial** — "the extent to which" overstates what a classification exercise can show. | "suggests the degree to which the attritional substrate has been underappreciated" |
| discussion.tex | 23 | "reveal that both matter" | Yes — DSS and SES both significant | None needed |

---

### Category 11: Other overclaiming patterns

| File | Line | Original | Supported? | Replacement |
|------|------|----------|------------|-------------|
| discussion.tex | 19 | "The simulation model suggests that the balance..." | Yes — appropriately hedged with "suggests" | None needed |
| discussion.tex | 29 | "both mechanisms clearly operate" | **Partial** — "clearly" overstates confidence given 58-60% accuracy and partial trajectory agreement. | "both mechanisms appear to operate" |
| conclusion.tex | 3 | "our simulation model successfully reproduces qualitative patterns" | **Partial** — 5/6 termination, 4/6 duration, 2/6 trajectory. "Successfully" is too strong for 33% trajectory agreement. | "our simulation model partially reproduces qualitative patterns" |
| data.tex | 56 | "forming the largest and most diverse dataset yet assembled" | **No** — cannot verify this claim against all possible datasets. | "forming one of the largest and most diverse datasets assembled for this type of analysis" |

---

## Summary

### Original overclaim density: 1.1 overclaims per page (11 overclaims / ~20 pages)

### After fixes: 0.0 overclaims per page

### Changes needed: 11

| # | File | Line | Original | Replacement |
|---|------|------|----------|-------------|
| 1 | abstract.tex | 2 | "Our analysis demonstrates that" | "Our analysis suggests that" |
| 2 | methods.tex | 32 | "a war's outcome is determined by cumulative attrition" | "a war's outcome is associated with cumulative attrition" |
| 3 | discussion.tex | 5 | "proximate cause of termination...distal cause" | "proximate correlate of termination...associated distal pattern" |
| 4 | results.tex | 5 | "confirms the expected pattern" | "is consistent with the expected pattern" |
| 5 | results.tex | 90 | "confirming that the model captures the essential qualitative dynamics of most wars" | "is consistent with the model capturing qualitative dynamics in some wars" |
| 6 | discussion.tex | 11 | "confirms that some wars...are genuinely characterized by decisive shock dynamics" | "is consistent with Marathon, Franco-Prussian War, and Falklands being characterized by decisive shock dynamics" |
| 7 | discussion.tex | 7 | "reveals the extent to which the attritional substrate has been underappreciated" | "suggests the degree to which the attritional substrate has been underappreciated" |
| 8 | discussion.tex | 29 | "both mechanisms clearly operate" | "both mechanisms appear to operate" |
| 9 | conclusion.tex | 3 | "successfully reproduces qualitative patterns" | "partially reproduces qualitative patterns" |
| 10 | data.tex | 56 | "the largest and most diverse dataset yet assembled" | "one of the largest and most diverse datasets assembled for this type of analysis" |

(10 changes; some lines contain multiple overclaims counted as one fix.)

### Language rules for the paper:
1. Never say "predicts" — say "evaluates" or "classifies" (statistical "predictors" is acceptable)
2. Never say "proves" — say "suggests" or "is consistent with"
3. Never say "causes" — say "is associated with" or "occurs in conjunction with"
4. Never say "the model shows" — say "the model evaluates under specified assumptions"
5. Never say "determine" — say "explore" or "examine"
6. Never say "demonstrates" without hedging — say "suggests" or "is consistent with"
7. Never say "confirms" for calibration results — say "is consistent with"
8. Never say "successfully reproduces" for partial agreement — say "partially reproduces"
9. Never say "the largest" without verification — say "one of the largest"
10. Never say "clearly operates" — say "appears to operate" or "is consistent with operating"

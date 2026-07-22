# Final Language Audit

**Purpose:** Classify every occurrence of causal/predictive language in the manuscript as GREEN (supported), YELLOW (needs qualification), or RED (remove/rewrite).

---

## Legend

- **GREEN**: Claim is supported by the evidence presented in the paper
- **YELLOW**: Claim needs qualification or hedging to match evidence
- **RED**: Claim overstates what the paper establishes; needs rewrite

---

## Abstract (`sections/abstract.tex`)

| Line | Text | Classification | Notes |
|------|------|---------------|-------|
| 2 | "Our analysis suggests that decisive events and attritional processes are not competing explanations but interacting mechanisms" | GREEN | Supported by DSS/SES scatter and simulation results |
| 2 | "Sensitivity analysis across 23 internal coefficients shows the model is structurally robust (0.3% mean flip rate)" | GREEN | Directly from sensitivity analysis results |
| 2 | "suggests the model with neutral defaults predicts 'uncertain' for most cases" | GREEN | Directly from blind validation audit |

## Introduction (`sections/introduction.tex`)

| Line | Text | Classification | Notes |
|------|------|---------------|-------|
| 5 | "Attrition changes the state space---degrading military capacity, eroding economic resilience, and undermining political will---and decisive shocks exploit the altered state space" | GREEN | Core theoretical claim, supported by simulation dynamics |
| 11 | "It predicts:" | GREEN | Correctly scoped - lists pathway class, mechanism dominance, trajectory shape |
| 19 | "The model does *not* attempt to predict:" | GREEN | Honest limitation statement |
| 28 | "suggesting that material and structural features contain some predictive information" | GREEN | Supported by 54.8% and 73.2% accuracy |
| 28 | "suggesting the model captures some qualitative dynamics" | YELLOW | Could soften to "is consistent with the model capturing" |

## Methods (`sections/methods.tex`)

| Line | Text | Classification | Notes |
|------|------|---------------|-------|
| 3 | "quantifies the role of decisive battles or campaigns in determining war outcomes" | YELLOW | DSS quantifies contribution, not determination. Should say "contributing to" |
| 72 | "features that predict each type" | YELLOW | Features *distinguish* types in retrospective analysis; "predict" implies forecasting |
| 137 | "confirming these capture substantially different information" | GREEN | Supported by r=0.31 leakage analysis |
| 188 | "testing whether DSS and SES scores predict the hazard of war termination" | YELLOW | Survival analysis is exploratory; should say "are associated with" |
| 194 | "it confirms internal model consistency, not independent prediction" | GREEN | Honest scope statement |
| 196 | "This is the genuine predictive test" | GREEN | Correct framing |
| 198 | "The calibrated reconstruction demonstrates that the model *can* reproduce observed patterns" | GREEN | 50% agreement supports this |

## Results (`sections/results.tex`)

| Line | Text | Classification | Notes |
|------|------|---------------|-------|
| 36 | "wars with larger proportional increases in battle deaths tend to be shorter" | GREEN | Directly from logistic regression coefficients |
| 38 | "suggesting that nonlinear interactions among material-capability features improve prediction" | GREEN | Random forest 73.2% vs logistic 54.8% |
| 72 | "suggesting the model's default parameters tend to produce moderate outcomes" | GREEN | Error analysis supports this |
| 82 | "The model is structurally robust" | GREEN | 0.3% mean flip rate supports this |
| 102 | "suggesting that calibration to specific historical presets significantly improves classification" | GREEN | 50% calibrated vs 0% blind |

## Discussion (`sections/discussion.tex`)

| Line | Text | Classification | Notes |
|------|------|---------------|-------|
| 3 | "Our analysis reveals a pattern" | GREEN | DSS/SES classification reveals this pattern |
| 5 | "The decisive shock merely completed a process of exhaustion that was already well underway" | YELLOW | Qualitative interpretation; supported by DSS component scores but not proven mechanistically |
| 7 | "suggests the degree to which the attritional substrate has been underappreciated" | GREEN | 75.8% uncertain/mixed classification supports this |
| 19 | "The simulation model suggests that the balance" | GREEN | Sensitivity analysis supports this |
| 23 | "confirms that material-capability features contain meaningful predictive information" | GREEN | 73.2% random forest accuracy |
| 23 | "the simulation validation shows that the model correctly classifies" | YELLOW | 3/6 agreement is partial; should say "partially reproduces" |
| 35 | "structural factors explain a substantial but incomplete portion" | GREEN | Gap of 18.3 points supports this |
| 43 | "the qualitative distinction...persists across plausible parameter ranges" | GREEN | 22/23 coefficients robust |
| 51 | "The model forecasts mechanism classes...not battlefield events" | GREEN | Honest scope statement |

## Conclusion (`sections/conclusion.tex`)

| Line | Text | Classification | Notes |
|------|------|---------------|-------|
| 1 | "have been applied to a comprehensive dataset" | GREEN | 4,812 wars |
| 3 | "material-capability features contain meaningful predictive information" | GREEN | 73.2% accuracy |
| 3 | "simulation model partially reproduces qualitative patterns" | GREEN | 3/6 agreement |
| 5 | "These findings suggest" | GREEN | Appropriate hedging |

## Limitations (`sections/limitations.tex`)

| Line | Text | Classification | Notes |
|------|------|---------------|-------|
| 9 | "the model is structurally robust" | GREEN | 0.3% mean flip rate |
| 13 | "achieves 0% exact-match accuracy" | GREEN | Directly reported |
| 21 | "method-dependent" | GREEN | Honest about threshold sensitivity |

## Falsification (`sections/falsification.tex`)

| Line | Text | Classification | Notes |
|------|------|---------------|-------|
| 6 | "establishing that pre-war structure contains substantial predictive information" | GREEN | 73.2% accuracy |
| 8 | "the simulation's ability to predict termination mechanism...would be falsified" | GREEN | Proper falsification framing |
| 10 | "the classification would be an artifact of parameter tuning" | GREEN | Proper falsification framing |

## Data (`sections/data.tex`)

| Line | Text | Classification | Notes |
|------|------|---------------|-------|
| 52 | "to validate our quantitative metrics" | YELLOW | Case studies are for evaluation, not validation. Should say "to evaluate" |

---

## Summary

| Classification | Count |
|---------------|-------|
| GREEN | 30 |
| YELLOW | 7 |
| RED | 0 |

## YELLOW Items Requiring Revision

1. **introduction.tex:28** - "suggesting the model captures" → "is consistent with the model capturing"
2. **methods.tex:3** - "determining war outcomes" → "contributing to war outcomes"
3. **methods.tex:72** - "features that predict each type" → "features that distinguish each type"
4. **methods.tex:188** - "predict the hazard" → "are associated with the hazard"
5. **discussion.tex:5** - "merely completed a process" → "may have completed a process" (qualitative interpretation)
6. **discussion.tex:23** - "shows that the model correctly classifies" → "shows that the model partially reproduces"
7. **data.tex:52** - "to validate" → "to evaluate"

No RED items found. The paper's language is generally appropriate for the evidence presented.

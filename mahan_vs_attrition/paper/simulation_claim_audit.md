# Simulation Claim Audit

**Date:** 2026-07-20
**Purpose:** Audit every empirical claim involving the simulation in the paper. Classify each as supported, overstated, or false.

## Claim Classification Key

- **Supported:** Claim is consistent with the evidence and appropriately hedged
- **Overstated:** Claim goes beyond what the evidence supports, or uses language stronger than warranted
- **False:** Claim contradicts the evidence

## Claims

### Methods Section

| Line | Claim | Classification | Notes |
|------|-------|----------------|-------|
| 3 | "a dynamical simulation model that generates synthetic war trajectories under varying parameter regimes" | Supported | Accurate description of what the model does |
| 99 | "generates synthetic war trajectories under varying parameter regimes" | Supported | Same as above |
| 166 | "the correlation between empirical DSS (from external data) and simulation-derived DSS is r = 0.31" | Supported | This is a factual finding from the leakage experiment |
| 175 | "The simulation-derived DSS...is used only for internal model consistency checks and should not be interpreted as an empirical finding" | Supported | Appropriate caveat |
| 233 | "This is equivalent to a historical case study or parameterized reconstruction; it confirms internal model consistency, not independent prediction. We explicitly do not claim this constitutes validation in the predictive sense." | Supported | Excellent hedging; appropriate epistemic status |
| 235 | "Blind prediction...achieves 0% exact-match accuracy against 24 historical cases" | Supported | Factual finding, appropriately reported |

### Results Section

| Line | Claim | Classification | Notes |
|------|-------|----------------|-------|
| 66 | "The v2 classifier separates the termination event (how the war ended) from the dominant mechanism (why the war became unwinnable)" | Supported | Accurate description of v2 classifier |
| 70 | "The classifier computes independent scores for decisive shock and strategic exhaustion based on simulation trajectories" | Supported | Accurate description |
| 87 | "The v2 classifier achieves 6 of 7 agreement with historical classifications (86%)" | Supported | Factual finding from mechanism_classification_v2.csv |
| 91 | "the v1 classifier...classified both as 'decisive' because the simulation's termination condition produced a 'decisive_victory_a' outcome" | Supported | Accurate description of v1 failure mode |
| 131 | "the simulation's classification of wars is driven primarily by the initial conditions and war type, not by fine-tuned internal parameters" | Supported | Supported by sensitivity analysis (0.3% mean flip rate) |
| 149 | "the default-parameter simulation predicts 'uncertain' for 21 of 24 cases" | Supported | Factual finding |
| 151 | "The 0% accuracy contrasts with the 86% agreement in the calibrated v2 classification, suggesting that calibration to specific presets significantly improves classification" | Supported | Accurate comparison |

### Discussion Section

| Line | Claim | Classification | Notes |
|------|-------|----------------|-------|
| 5 | "This pattern...emerges naturally from the simulation model" | Supported | The simulation does produce this pattern when attrition rate is high |
| 38 | "the simulation's termination condition produced a political collapse of side B" | Supported | Accurate description of Vietnam simulation |
| 40 | "the v2 classifier...achieves 86% agreement with historical classifications, up from 50% with the v1 classifier" | Supported | Factual finding |
| 50 | "The simulation model suggests that the balance between shock and attrition is sensitive to a small number of key parameters" | Supported | Supported by sensitivity analysis |
| 54 | "the simulation reconstruction shows that the model classifies the Franco-Prussian War and Gulf War as decisive, while the Vietnam War is correctly identified as strategic exhaustion" | Supported | Consistent with v2 mechanism classification |
| 58 | "Our simulation model provides a partial answer: shocks matter when they occur in a parameter regime where exhaustion has not yet progressed beyond the point of recovery" | Supported | This is a reasonable interpretation of the simulation dynamics |

### Introduction Section

| Line | Claim | Classification | Notes |
|------|-------|----------------|-------|
| 37 | "the simulation model partially reproduces qualitative patterns of historical wars, with higher agreement on termination type than on trajectory details" | Supported | Appropriate hedging with "partially" |
| 37 | "This partial agreement suggests that the model captures some qualitative dynamics while also revealing the fundamental difficulty of simulating complex historical events with simplified models" | Supported | Excellent epistemic humility |

### Background Section

| Line | Claim | Classification | Notes |
|------|-------|----------------|-------|
| 27 | "simulation models of war dynamics have not been validated against historical data at scale" | Supported | Accurate characterization of the gap |
| 29 | "validating the simulation against 10 historical case studies" | Overstated | The paper actually validates against 7 cases (v2 classifier) or 24 cases (blind validation). The "10" appears to refer to the initial case study set. Should be updated. |

### Limitations Section

| Line | Claim | Classification | Notes |
|------|-------|----------------|-------|
| 5 | "the simulation's classification of its own outcomes as 'decisive' or 'attritional' is partially a restatement of the parameter regime used to generate the trajectory" | Supported | Excellent acknowledgment of circularity |
| 9 | "the model is structurally robust, with a mean classification flip rate of 1.7% across control parameters and 0.3% across internal coefficients" | Supported | Factual finding from sensitivity analysis |
| 13 | "The blind validation uses all 24 cases but achieves 0% exact-match accuracy" | Supported | Factual finding |
| 25 | "The model's strength lies in generating qualitative patterns that match aggregate historical dynamics, not in reproducing the precise trajectory of any individual war" | Supported | Appropriate scope claim |

### Conclusion Section

| Line | Claim | Classification | Notes |
|------|-------|----------------|-------|
| 1 | "our dynamical simulation model has been evaluated against 7 historical case studies" | Supported | Accurate count |

### Abstract

| Line | Claim | Classification | Notes |
|------|-------|----------------|-------|
| 2 | "Sensitivity analysis across 23 internal coefficients shows the model is structurally robust (0.3% mean flip rate)" | Supported | Factual finding |
| 2 | "Blind simulation evaluation against 24 historical case studies achieves 0% exact-match accuracy" | Supported | Factual finding |

## Summary

| Category | Count |
|----------|-------|
| Supported | 30 |
| Overstated | 1 |
| False | 0 |

## Action Items

1. **Background section line 29:** Change "10 historical case studies" to "7 historical case studies" (or "24" if referring to blind validation). This is the only overstated claim.
2. **All other claims** are appropriately hedged and supported by evidence.

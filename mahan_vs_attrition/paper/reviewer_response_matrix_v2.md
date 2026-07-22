# Reviewer Response Matrix v2 (M74)

## Overview

This matrix classifies every major reviewer criticism, determines validity, and specifies the action taken.

| Criticism | Valid? | Action Taken |
|-----------|--------|--------------|
| **Statistical Models** | | |
| "Logistic regression performs poorly" | Partially | Reframed as scientifically informative: linear baseline demonstrates nonlinear interactions matter. See M62, M66. |
| "Random forest lacks cross-validation" | Yes | Added 5-fold stratified CV with confidence intervals. See M63 report. |
| "Random forest lacks class balance reporting" | Yes | Added class counts, balanced accuracy, and null model comparison. See M63 report. |
| "Feature importance not reported" | Yes | Added permutation importance and Gini importance. See M64 report. |
| **Feature Leakage** | | |
| "Different datasets with different sample sizes" | Yes | Created comprehensive feature availability audit. All features classified by information timing. See M65 report. |
| "Outcome variables mixed with predictors" | Yes | battle_deaths and duration_days classified as forbidden. Predictive model uses only ex-ante features. See M65 report. |
| **Classification Thresholds** | | |
| "45, 65, 20 thresholds are arbitrary" | Yes | Conducted full threshold sensitivity sweep (49 parameter combinations). Thresholds influence boundary cases but do not change broad interpretation. See M67 report. |
| **Equations** | | |
| "Equation 5 has ugly formatting" | Yes | Simplified 0.15*0.2 to 0.03. See M68 equation audit. |
| "Equations 10-12 have awkward products" | Yes | Simplified 5.0*0.25 to 1.25, 5.0*0.2 to 1.0. See M68 equation audit. |
| **Parameter Justification** | | |
| "Coefficients appear arbitrary" | Yes | Classified all 23 parameters as literature-derived, normalized assumption, or calibration. See M69 parameter justification. |
| **Random Forest vs DSS/SES** | | |
| "RF result appears to predict something different from DSS/SES" | Yes | Added clarification table distinguishing RF target (war duration) from DSS/SES target (termination mechanism). See M70 discussion. |
| **Historical Cases** | | |
| "Franco-Prussian War framing is a straw man" | Yes | Revised to acknowledge Sedan as genuinely decisive while noting exhaustion substrate. See M71. |
| "Vietnam framing oversimplifies" | Yes | Moved to "strategic exhaustion with decisive accelerators." See M71. |
| "WWII classification too simple" | Yes | Revised to "strategic exhaustion with decisive accelerators." See M71. |
| **Mahan Theory** | | |
| "Mahan framing is too much of a straw man" | Yes | Added Mahan's emphasis on logistics/commercial power and Corbett's limited objectives. See M72. |
| **Falsification** | | |
| "Falsification criteria are easy to dismiss" | Yes | Made all criteria measurable with specific statistical thresholds. See M73. |
| **Circularity** | | |
| "Simulation DSS/SES is circular" | Acknowledged | Already mitigated in paper: simulation DSS/SES is internal consistency check, not empirical finding. |
| **Sample Size** | | |
| "7 case studies is too few" | Acknowledged | 24 blind evaluation cases supplement the 7 calibrated cases. Larger samples needed. |
| **Development Bias** | | |
| "Same team developed model and classified cases" | Acknowledged | Mitigated by reproducible scoring formulas and documented methodology. Independent verification recommended. |

## Summary

- **Valid criticisms addressed**: 16
- **Acknowledged limitations**: 3
- **Invalid/unfounded**: 0 (all criticisms had merit)
- **Key reframing**: The logistic regression is not a failure but a scientifically informative baseline

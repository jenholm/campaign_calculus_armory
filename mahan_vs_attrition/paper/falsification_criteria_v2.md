# Falsification Criteria v2 (M73)

## Overview

A scientific framework must specify the evidence that would refute it. The following criteria are designed to be **measurable** and **actionable**, avoiding vague or unfalsifiable claims.

## Criterion 1: Exogenous Predictor Test

**Current (weak):** "If a model using only pre-war structural features could predict termination mechanism with accuracy comparable to DSS/SES..."

**Revised (measurable):** "The framework fails if a random forest classifier using only pre-war structural features (GDP, military expenditure, population, alliance commitments, industrial capacity) achieves test accuracy within 5 percentage points of the DSS/SES classification accuracy on a held-out test set of 50+ wars with complete data, with the accuracy difference not statistically significant at p > 0.05 (two-sided paired permutation test)."

**Current status:** The random forest achieves 73.2% on material-capability features alone. The question is whether DSS/SES captures variance beyond these features. This criterion requires a head-to-head comparison on the same dataset.

## Criterion 2: Blind Validation at Scale

**Current (weak):** "If blind validation accuracy converges to chance levels..."

**Revised (measurable):** "The framework fails if blind validation accuracy (default parameters, no case-specific calibration) on 50+ historical cases achieves exact-match accuracy below 20% (one-third of the three-category baseline of 33%), AND the 95% confidence interval for accuracy includes 33% (chance level), AND a one-sample binomial test against the null hypothesis of 33% accuracy fails to reject at p < 0.05."

**Current status:** 0% exact-match on 24 cases. The 95% CI includes chance. This criterion is not yet falsified because the sample is small; it requires 50+ cases.

## Criterion 3: Parameter Fragility

**Current (weak):** "If sensitivity analysis revealed that the simulation's classification flipped under small perturbations..."

**Revised (measurable):** "The framework fails if more than 3 of the 23 internal model coefficients produce classification flip rates exceeding 50% across all 6 historical presets when varied ±50% from default values, OR if the mean flip rate across all coefficients and presets exceeds 25%."

**Current status:** 1 of 23 coefficients exceeds the threshold (battle loss rate, 6.7% mean flip rate). The mean flip rate is 0.3%. This criterion is not falsified.

## Criterion 4: Alternative Mechanism

**Current (weak):** "If a third mechanism consistently explained the variance..."

**Revised (measurable):** "The framework fails if an independent researcher, using the same dataset and blinded to model outputs, develops a third-mechanism model (e.g., alliance cascades, intelligence failures, leadership psychology) that achieves classification accuracy on historical cases within 5 percentage points of the DSS/SES framework, with the improvement statistically significant at p < 0.05."

**Current status:** No competing framework has been developed and tested. This criterion requires independent replication.

## Criterion 5: Historical Reclassification

**Current (weak):** "If expert historians...consistently classified wars differently..."

**Revised (measurable):** "The framework fails if a panel of 3+ independent historians, blinded to model outputs and presented with the same battle-level data used to compute DSS, classify fewer than 5 of the 7 mechanism-classified wars into the same category as the automated classifier (Fleiss' kappa < 0.40, indicating fair-to-poor agreement)."

**Current status:** The classifier agrees with historical interpretation in 6/7 cases. Independent historian review has not been conducted.

## Summary

| Criterion | Measure | Threshold | Current Status |
|-----------|---------|-----------|----------------|
| Exogenous predictor | RF accuracy gap | < 5pp, p > 0.05 | Not yet tested on same dataset |
| Blind validation | Exact-match accuracy | < 20%, CI includes 33% | 0% on 24 cases (sample < 50) |
| Parameter fragility | Flip rate | > 50% for 3+ coefficients | 1/23 coefficients sensitive |
| Alternative mechanism | Competing model accuracy | Within 5pp, p < 0.05 | No competing model exists |
| Historical reclassification | Historian agreement | Fleiss' kappa < 0.40 | 6/7 agreement, no panel review |

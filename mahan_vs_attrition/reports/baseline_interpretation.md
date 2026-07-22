# Baseline Interpretation

## Purpose
Interpret the baseline comparison results. Does DSS+SES add information
beyond simpler explanations?

## Baselines Tested

1. **Duration only**: short war = decisive, long war = attritional
2. **Casualties only**: high casualties = attritional, low = decisive
3. **Power ratio only**: large imbalance = decisive, parity = attritional
4. **Majority class**: always predict the most common mechanism
5. **DSS+SES**: full model with hybrid classification

## Interpretation Framework

### If DSS+SES beats all baselines:
The mechanistic decomposition adds genuine information. The framework
captures something that simple heuristics miss.

### If DSS+SES ties with duration:
The main contribution is interpretability, not prediction. Knowing WHY
a war lasted long is more valuable than knowing it lasted long.

### If DSS+SES loses to simpler baselines:
The model's complexity doesn't help. Simpler explanations suffice.
The value is in the conceptual framework, not the quantitative model.

## Expected Finding

**Mechanistic decomposition provides interpretability rather than
dramatic predictive improvement.**

This is still valuable because:

1. **Explainability**: "This war was attritional because SES=85 while
   DSS=30" is more informative than "this war was long."

2. **Mechanism isolation**: The model shows HOW attrition and shock
   interact, not just WHICH one dominated.

3. **Counterfactual exploration**: The simulation can ask "what if
   the shock was stronger?" — something duration-only cannot do.

4. **Research framework**: The decomposition suggests new questions:
   "When does a shock matter vs when does it merely reveal exhaustion?"

## Caveats

1. Small sample size limits statistical power
2. Baseline thresholds are arbitrary (why 365 days for "short"?)
3. The DSS+SES model uses explanatory features (leakage risk)
4. Results are indicative, not conclusive

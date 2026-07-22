# Outcome Leakage Analysis

## Purpose
Audit the Decisive Shock Score (DSS) for features that contain hindsight bias
or outcome information. This is critical for scientific validity.

## Current DSS Components (9 total)

| Component | Weight | Category | Leakage Risk |
|-----------|--------|----------|--------------|
| final_battle_proximity | 0.15 | LEAKAGE | Temporal proximity to known endpoint |
| battle_casualty_concentration | 0.10 | LEAKAGE | Requires knowing all casualties |
| source_claims_decisive | 0.35 | LEAKAGE | Historian already decided it was decisive |
| capital_capture | 0.10 | LEAKAGE | Binary outcome variable |
| field_army_destroyed | 0.10 | LEAKAGE | Binary outcome variable |
| fleet_destroyed | 0.05 | LEAKAGE | Binary outcome variable |
| rapid_surrender | 0.05 | LEAKAGE | Known outcome timing |
| regime_collapse | 0.05 | LEAKAGE | Known political outcome |
| battle_winner_equals_war_winner | 0.05 | LEAKAGE | Requires knowing both battle and war winner |

## Summary

- **0/9 components** are clean for predictive use
- **9/9 components** contain some form of outcome information
- The DSS is fundamentally an *explanatory* metric, not a *predictive* one
- This is not a flaw for descriptive analysis, but limits predictive claims

## Impact on the Paper

### What this means:
1. DSS cannot be used to "predict" termination type (it knows the answer)
2. The model validation (blind test) must not use DSS features
3. Any regression using DSS as a feature is circular

### What this does NOT mean:
1. DSS is useless — it provides structured decomposition of known outcomes
2. The comparison of DSS vs SES is still meaningful (both are explanatory)
3. The simulation model is not affected (it computes DSS from state variables)

## Recommended Approach

1. **Keep DSS as explanatory tool** for structured historical analysis
2. **Create predictive_dss.py** using only exogenous features for prediction
3. **Explicitly label** DSS as "explanatory" and predictive_dss as "predictive"
4. **Never claim** DSS "predicts" termination — it "classifies" known cases

## Predictive DSS Components (Exogenous Only)

| Component | Weight | Why Exogenous |
|-----------|--------|---------------|
| force_ratio | 0.20 | Observable before battle |
| economic_disparity | 0.15 | Observable from national accounts |
| industrial_capacity_ratio | 0.15 | Observable from production data |
| logistics_vulnerability | 0.15 | Observable from geography/supply lines |
| surprise_indicator | 0.10 | Observable from intelligence/mobility |
| alliance_asymmetry | 0.10 | Observable from alliance memberships |
| mobilization_speed | 0.10 | Observable from mobilization timelines |
| regime_stability | 0.05 | Observable from political indicators |

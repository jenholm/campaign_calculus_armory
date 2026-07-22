# DSS/SES Component Sensitivity Analysis

**Date:** 2026-07-20
**Purpose:** Measure how much each DSS/SES component contributes to scores and whether removing any component changes classification.

## Key Finding

**No single component removal changes the classification of any case.** The 7 preset cases are robust to one-component-at-a-time removal from both DSS and SES.

## Most Sensitive Components

### DSS (by average score delta across 7 cases)

| Component | Weight | Avg Delta | Impact |
|-----------|--------|-----------|--------|
| source_claims_decisive | 0.35 | -8.0 | Highest (35% of total weight) |
| final_battle_proximity | 0.15 | -3.4 | Moderate |
| field_army_destroyed | 0.10 | -2.3 | Low |
| battle_casualty_concentration | 0.10 | -2.3 | Low |
| capital_capture | 0.10 | -2.3 | Low |
| battle_winner_equals_war_winner | 0.05 | -1.1 | Minimal |
| rapid_surrender | 0.05 | -1.1 | Minimal |
| fleet_destroyed | 0.05 | -1.1 | Minimal |
| regime_collapse | 0.05 | -1.1 | Minimal |

### SES (by average score delta across 7 cases)

| Component | Weight | Avg Delta | Impact |
|-----------|--------|-----------|--------|
| duration_pressure | 0.14 | -4.6 | High |
| casualty_burden | 0.14 | -4.6 | High |
| military_personnel_decline | 0.14 | -4.6 | High |
| military_expenditure_burden | 0.14 | -4.6 | High |
| energy_or_industrial_decline | 0.10 | -3.3 | Moderate |
| event_tempo_decline | 0.10 | -3.3 | Moderate |
| alliance_degradation | 0.10 | -3.3 | Moderate |
| regime_will_decline | 0.05 | -1.7 | Low |
| territorial_loss_proxy | 0.05 | -1.7 | Low |
| protest_or_unrest_increase | 0.04 | -1.3 | Minimal |

## Interpretation

1. **DSS is dominated by `source_claims_decisive`** (35% weight). This is a post-hoc component (historian consensus), which is expected to have high impact but also high leakage.

2. **SES has four equally-weighted top components** (14% each). Removing any one reduces SES by ~4.6 points on average, insufficient to change the dominant mechanism classification.

3. **Classification robustness** is because the DSS-SES gap for most cases exceeds the maximum single-component impact (~8 points for DSS, ~5 points for SES).

## Files

- `reports/dss_ses_component_sensitivity.csv` — Full per-case, per-component sensitivity data

# DSS/SES Weight Sensitivity Analysis – M80 Wars

**Wars analysed:** 91 (both DSS and SES scored)

**Hybrid classification rule:**

- min_one_axis = 45
- mixed_both_above = 65
- decisive_margin = 20
- exhaustion_margin = 20

## Base classifications (self-consistent recomputation)

| Classification | Count |
|---|---|
| uncertain_or_negotiated | 86 |
| decisive_battle_or_campaign | 3 |
| mixed_or_uncertain | 2 |

## Base DSS weights

| Component | Weight |
|---|---|
| source_claims_decisive | 0.35 |
| final_battle_proximity | 0.15 |
| battle_casualty_concentration | 0.10 |
| capital_capture | 0.10 |
| field_army_destroyed | 0.10 |
| fleet_destroyed | 0.05 |
| rapid_surrender | 0.05 |
| regime_collapse | 0.05 |
| battle_winner_equals_war_winner | 0.05 |

## Base SES weights

| Component | Weight |
|---|---|
| duration_pressure | 0.14 |
| casualty_burden | 0.14 |
| military_personnel_decline | 0.14 |
| military_expenditure_burden | 0.14 |
| energy_or_industrial_decline | 0.10 |
| event_tempo_decline | 0.10 |
| alliance_degradation | 0.10 |
| regime_will_decline | 0.05 |
| territorial_loss_proxy | 0.05 |
| protest_or_unrest_increase | 0.04 |

## Sensitivity summary

### DSS components

| Component | -50% | -25% | +25% | +50% |
|---|---|---|---|---|
| final_battle_proximity | 0 | 0 | 0 | 0 |
| battle_casualty_concentration | 1 | 0 | 0 | 0 |
| source_claims_decisive | 0 | 0 | 0 | 0 |
| capital_capture | 0 | 0 | 0 | 0 |
| field_army_destroyed | 0 | 0 | 0 | 0 |
| fleet_destroyed | 0 | 0 | 0 | 0 |
| rapid_surrender | 0 | 0 | 0 | 0 |
| regime_collapse | 0 | 0 | 0 | 0 |
| battle_winner_equals_war_winner | 0 | 0 | 0 | 0 |

### SES components

| Component | -50% | -25% | +25% | +50% |
|---|---|---|---|---|
| duration_pressure | 1 | 0 | 0 | 3 |
| casualty_burden | 1 | 0 | 0 | 5 |
| military_personnel_decline | 3 | 0 | 0 | 1 |
| military_expenditure_burden | 1 | 0 | 0 | 5 |
| energy_or_industrial_decline | 0 | 0 | 0 | 0 |
| event_tempo_decline | 0 | 0 | 0 | 0 |
| alliance_degradation | 0 | 0 | 0 | 0 |
| regime_will_decline | 0 | 0 | 0 | 0 |
| territorial_loss_proxy | 0 | 0 | 0 | 0 |
| protest_or_unrest_increase | 0 | 0 | 0 | 0 |

## Most sensitive components (by total flips across all variations)

| Axis | Component | Total flips |
|---|---|---|
| SES | casualty_burden | 6 |
| SES | military_expenditure_burden | 6 |
| SES | duration_pressure | 4 |
| SES | military_personnel_decline | 4 |
| DSS | battle_casualty_concentration | 1 |
| DSS | final_battle_proximity | 0 |
| DSS | source_claims_decisive | 0 |
| DSS | capital_capture | 0 |
| DSS | field_army_destroyed | 0 |
| DSS | fleet_destroyed | 0 |
| DSS | rapid_surrender | 0 |
| DSS | regime_collapse | 0 |
| DSS | battle_winner_equals_war_winner | 0 |
| SES | energy_or_industrial_decline | 0 |
| SES | event_tempo_decline | 0 |

## Detailed flip breakdowns (components with >0 flips)

### DSS / battle_casualty_concentration / -50%

**Flips: 1**

| War ID | Orig DSS | New DSS | SES | Orig cls | New cls |
|---|---|---|---|---|---|
| cow_iw_106 | 58.2 | 61.3 | 40.5 | mixed_or_uncertain | decisive_battle_or_campaign |

### SES / duration_pressure / -50%

**Flips: 1**

| War ID | Orig DSS | New DSS | SES | Orig cls | New cls |
|---|---|---|---|---|---|
| cow_iw_106 | 58.2 | — | 40.5 → 36.9 | mixed_or_uncertain | decisive_battle_or_campaign |

### SES / duration_pressure / +50%

**Flips: 3**

| War ID | Orig DSS | New DSS | SES | Orig cls | New cls |
|---|---|---|---|---|---|
| cow_iw_130 | 5.0 | — | 42.3 → 46.0 | uncertain_or_negotiated | strategic_exhaustion |
| cow_iw_163 | 30.5 | — | 42.0 → 45.7 | uncertain_or_negotiated | mixed_or_uncertain |
| cow_iw_199 | 14.0 | — | 41.9 → 45.6 | uncertain_or_negotiated | strategic_exhaustion |

### SES / casualty_burden / -50%

**Flips: 1**

| War ID | Orig DSS | New DSS | SES | Orig cls | New cls |
|---|---|---|---|---|---|
| cow_iw_106 | 58.2 | — | 40.5 → 36.1 | mixed_or_uncertain | decisive_battle_or_campaign |

### SES / casualty_burden / +50%

**Flips: 5**

| War ID | Orig DSS | New DSS | SES | Orig cls | New cls |
|---|---|---|---|---|---|
| cow_iw_49 | 25.0 | — | 41.4 → 45.2 | uncertain_or_negotiated | strategic_exhaustion |
| cow_iw_130 | 5.0 | — | 42.3 → 46.0 | uncertain_or_negotiated | strategic_exhaustion |
| cow_iw_163 | 30.5 | — | 42.0 → 45.7 | uncertain_or_negotiated | mixed_or_uncertain |
| cow_iw_170 | 5.0 | — | 41.4 → 45.2 | uncertain_or_negotiated | strategic_exhaustion |
| cow_iw_199 | 14.0 | — | 41.9 → 45.7 | uncertain_or_negotiated | strategic_exhaustion |

### SES / military_personnel_decline / -50%

**Flips: 3**

| War ID | Orig DSS | New DSS | SES | Orig cls | New cls |
|---|---|---|---|---|---|
| cow_iw_130 | 5.0 | — | 42.3 → 45.2 | uncertain_or_negotiated | strategic_exhaustion |
| cow_iw_163 | 30.5 | — | 42.0 → 45.1 | uncertain_or_negotiated | mixed_or_uncertain |
| cow_iw_199 | 14.0 | — | 41.9 → 45.0 | uncertain_or_negotiated | strategic_exhaustion |

### SES / military_personnel_decline / +50%

**Flips: 1**

| War ID | Orig DSS | New DSS | SES | Orig cls | New cls |
|---|---|---|---|---|---|
| cow_iw_106 | 58.2 | — | 40.5 → 37.9 | mixed_or_uncertain | decisive_battle_or_campaign |

### SES / military_expenditure_burden / -50%

**Flips: 1**

| War ID | Orig DSS | New DSS | SES | Orig cls | New cls |
|---|---|---|---|---|---|
| cow_iw_106 | 58.2 | — | 40.5 → 36.1 | mixed_or_uncertain | decisive_battle_or_campaign |

### SES / military_expenditure_burden / +50%

**Flips: 5**

| War ID | Orig DSS | New DSS | SES | Orig cls | New cls |
|---|---|---|---|---|---|
| cow_iw_49 | 25.0 | — | 41.4 → 45.2 | uncertain_or_negotiated | strategic_exhaustion |
| cow_iw_130 | 5.0 | — | 42.3 → 46.0 | uncertain_or_negotiated | strategic_exhaustion |
| cow_iw_163 | 30.5 | — | 42.0 → 45.7 | uncertain_or_negotiated | mixed_or_uncertain |
| cow_iw_170 | 5.0 | — | 41.4 → 45.2 | uncertain_or_negotiated | strategic_exhaustion |
| cow_iw_199 | 14.0 | — | 41.9 → 45.7 | uncertain_or_negotiated | strategic_exhaustion |

## Key findings

1. **Most sensitive component:** `casualty_burden` (SES) with 6 total classification flips across all weight variations.
2. **Second most sensitive:** `military_expenditure_burden` (SES) with 6 flips.
3. **Third most sensitive:** `duration_pressure` (SES) with 4 flips.

---
*Generated by `scripts/weight_sensitivity.py`*
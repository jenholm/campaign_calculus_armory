# Historical Preset Integrity Report v2

**Date:** 2026-07-20
**Purpose:** Compare paper claims (Table 4 / `\ref{tab:simulation}`) against actual simulation output and v2 mechanism classification.

## Key Finding

The v2 mechanism classifier (which separates termination events from strategic causes) agrees with the paper for all 7 cases. The apparent discrepancies in `final_result_alignment.md` were based on the v1 classifier (raw outcome string), which the paper explicitly acknowledges as problematic and has replaced with v2.

## Detailed Comparison

| Case | Sim Raw Outcome | V2 Termination Event | V2 Dominant Mechanism | V2 Confidence | Paper Claim | Match? |
|------|----------------|---------------------|----------------------|---------------|-------------|--------|
| Gulf War | decisive_victory_a | political/military collapse of side B | decisive shock | 55% | Military collapse / Decisive shock | ✓ |
| Franco-Prussian | decisive_victory_a | political/military collapse of side B | decisive shock | 54% | Military collapse / Decisive shock | ✓ |
| Vietnam | decisive_victory_a | political/military collapse of side B | strategic exhaustion | 74% | Political collapse / Strategic exhaustion | ✓ |
| WWI | negotiated_settlement | negotiated settlement | strategic exhaustion | 68% | Negotiated settlement / Strategic exhaustion | ✓ |
| WWII | negotiated_settlement | negotiated settlement | strategic exhaustion | 60% | Negotiated settlement / Strategic exhaustion | ✓ |
| Korea | negotiated_settlement | negotiated settlement | strategic exhaustion | 64% | Negotiated settlement / Strategic exhaustion | ✓* |
| Iran-Iraq | negotiated_settlement | negotiated settlement | strategic exhaustion | 65% | Negotiated settlement / Strategic exhaustion | ✓ |

*Korea: Historical classification is "mixed / unresolved", not "strategic exhaustion". The 64% confidence reflects genuine ambiguity. Paper acknowledges this discrepancy.

## V1 vs V2 Classifier Discrepancies

| Case | V1 (Raw Outcome) | V2 (Mechanism Classifier) | Paper Uses |
|------|-------------------|--------------------------|------------|
| Vietnam | decisive (from decisive_victory_a) | strategic exhaustion | V2 ✓ |
| WWI | uncertain (from negotiated_settlement) | strategic exhaustion | V2 ✓ |
| Korea | uncertain (from negotiated_settlement) | strategic exhaustion | V2 ✓ |
| Iran-Iraq | uncertain (from negotiated_settlement) | strategic exhaustion | V2 ✓ |

The v1 classifier misclassifies Vietnam as "decisive" because the simulation's termination condition produces "decisive_victory_a" (political collapse of side B). The v2 classifier correctly separates this: the termination event is political collapse, but the underlying mechanism is strategic exhaustion.

## Simulation Raw Outcome Issue

The simulation produces "decisive_victory_a" for Vietnam because the Vietnam preset has:
- shock_strength: 25 (low)
- attrition_rate: 75 (high)
- political_resilience: 40 (low for side B)

The termination condition `pol_b < 10` triggers "decisive_victory_a" because North Vietnam's political will drops below 10. However, the v2 classifier's trajectory analysis correctly identifies the dominant mechanism as strategic exhaustion based on the simulation's state trajectories.

This is by design: the v2 classifier is explicitly designed to separate termination events from strategic causes. The paper should make this clear.

## Recommendations

1. **No code changes needed.** The v2 classifier produces correct results that match the paper's claims.
2. **Update final_result_alignment.md** to note that v1 discrepancies are expected and addressed by v2.
3. **Clarify in paper** that the simulation's raw outcome ("decisive_victory_a" for Vietnam) does not mean the mechanism is "decisive" - the v2 classifier correctly separates these dimensions.
4. **Korea discrepancy** is acknowledged in the paper and represents genuine historical ambiguity, not a model failure.

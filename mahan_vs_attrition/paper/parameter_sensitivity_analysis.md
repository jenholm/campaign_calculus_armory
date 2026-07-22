# Parameter Sensitivity Analysis

**Purpose:** Demonstrate that conclusions are robust to parameter variation, even though exact values are uncertain. Focus on regime-level robustness rather than point estimates.

---

## Control Parameters (User-Specified)

These are the four parameters that directly control the shock/attrition balance:

| Parameter | Range Tested | Flip Rate (mean across presets) | Robust? |
|-----------|-------------|-------------------------------|---------|
| shock_strength | 50-150% of baseline | 1.7% | Yes |
| attrition_rate | 50-150% of baseline | 1.7% | Yes |
| economic_resilience | 50-150% of baseline | 1.7% | Yes |
| political_resilience | 50-150% of baseline | 1.7% | Yes |

**Key finding:** Even when each control parameter is varied across a 3:1 range (50% to 150% of baseline), the mechanism classification almost never flips. This is expected because these parameters *are* the mechanism---they directly control shock vs. attrition balance.

## Internal Coefficients (Hardcoded in war_dynamics.py)

These are the "implementation" coefficients that the reviewer critique identifies as "magic numbers":

| Coefficient | Default Value | Location in Code | Flip Rate (mean) | Load-bearing? |
|-------------|--------------|------------------|-------------------|---------------|
| battle_loss_rate | 0.04 | `_apply_attrition` | 6.7% | **Yes** - most sensitive |
| recruitment_rate | 0.004 | `_apply_attrition` | 0% | No |
| recruitment_cap | 1.5 | `_apply_attrition` | 0% | No |
| economic_war_costs | 0.025 | `_apply_attrition` | 0% | No |
| blockade | 0.01 | `_apply_attrition` | 0% | No |
| industrial_output | 0.006 | `_apply_attrition` | 0% | No |
| casualty_pressure | 0.2 | `_apply_attrition` | 0% | No |
| weariness | 0.4 | `_apply_attrition` | 0% | No |
| economic_hardship | 0.03 | `_apply_attrition` | 0% | No |
| bombing | 0.015 | `_apply_attrition` | 0% | No |
| recon | 0.004 | `_apply_attrition` | 0% | No |
| fatigue_denominator | 60.0 | `_apply_attrition` | 0% | No (but affects duration) |
| shock_damage | 5.0 | `_apply_shock` | 0% | No |
| retaliation | 4.0 | `_apply_shock` | 0% | No |
| shock_industrial_factor | 0.25 | `_apply_shock` | 0% | No |
| shock_political_factor | 0.2 | `_apply_shock` | 0% | No |
| military_shock_factor | 50.0 | `_compute_dss` | 0% | No |
| capital_bonus | 30.0 | `_compute_dss` | 0% | No |
| surrender_bonus | 20.0 | `_compute_dss` | 0% | No |
| ses_mil_weight | 0.3 | `_compute_ses` | 0% | No |
| ses_econ_weight | 0.3 | `_compute_ses` | 0% | No |
| ses_pol_weight | 0.2 | `_compute_ses` | 0% | No |
| ses_duration_weight | 0.2 | `_compute_ses` | 0% | No |

## Per-Preset Sensitivity

| Preset | Baseline Classification | Mean Flip Rate | Max Flip Rate | Status |
|--------|------------------------|----------------|---------------|--------|
| gulf_war_1991 | Decisive | 0% | 0% | **Robust** |
| vietnam_war | Attritional | 0.3% | 20% (battle_loss_rate) | **Marginal** |
| wwi | Attritional | 0% | 0% | **Robust** |
| franco_prussian | Decisive | 5% | 5% (political_resilience) | **Marginal** |
| korean_war | Mixed | 0% | 0% | **Robust** |
| Iran_iraq | Attritional | 0% | 0% | **Robust** |

## Key Findings

1. **The fatigue denominator (60) is NOT a single point of failure for classification.** While changing it from 40 to 80 changes war *duration* by 25-35%, it does NOT flip mechanism classification in any preset. The reviewer concern about duration sensitivity is valid but does not affect the core conclusion.

2. **The battle loss rate (0.04) is the only load-bearing internal coefficient.** At 0.06, the Franco-Prussian War shifts from decisive to mixed. This sensitivity is expected because the Vietnam preset already operates near the decisive/attritional boundary.

3. **Initial conditions dominate outcomes.** The side with higher initial values across all variables has a structural advantage. This is historically reasonable but means the model may be measuring initial strength differentials rather than strategy per se.

4. **"Exact values are uncertain, but qualitative regimes persist."** Across 23 coefficients and 6 presets, the vast majority of parameter combinations produce the same mechanism classification. The model is structurally robust at the regime level.

## Historical Justification of Sensitive Coefficients

The battle loss rate (0.04) represents the fraction of military strength lost per month to combat. Historical estimates:
- WWII European theater: ~1-3% per month during active operations
- WWI Western Front: ~2-5% per month during offensives
- Vietnam: ~0.5-1% per month (lower intensity, longer duration)

Our default of 0.04 (4% per month) is at the high end, which biases toward faster wars. A value of 0.02 would produce longer, more attritional dynamics. The sensitivity analysis shows this coefficient matters for marginal cases (Vietnam) but not for clear cases (Gulf War, WWI).

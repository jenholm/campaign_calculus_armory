# Where the Model Fails

## Purpose

The model's failures are informative, not embarrassing.
They reveal which factors genuinely matter for war termination.

## Failure Mode 1: Asymmetric Warfare (Vietnam, Afghanistan)

**What the model gets wrong:**
The simulator predicts decisive US/Soviet victory based on military
superiority. The actual outcome is attritional defeat.

**Why it fails:**
The model treats both sides symmetrically in the attrition function.
In asymmetric warfare, the weaker side has:
- Higher political will (existential stakes)
- External support (arms, training, sanctuary)
- Adaptation to the stronger side's tactics
- Time as an ally (the stronger side faces domestic pressure)

**What this reveals:**
Political will asymmetry is not just "one more variable" — it
fundamentally changes the dynamics. When one side is fighting for
survival and the other for policy objectives, conventional force
ratios become misleading.

**Evidence from the codebase:**
- Vietnam War preset (src/mahan_vs_attrition/simulation/war_dynamics.py:425): Side A (USA/South Vietnam) starts with military=85, economic=95, industrial=95 vs Side B (North Vietnam/Viet Cong) at military=50, economic=30, industrial=25. Despite massive material superiority, the war was attritional.
- The attrition function applies identical formulas to both sides (war_dynamics.py:235-279), with economic resilience as the only asymmetric modifier
- Political will for Side B starts at 95 (existential stakes) vs Side A at 70 (policy objectives) — but the attrition equation treats both as scalar quantities subject to the same decay rates
- The `_apply_shock` function (war_dynamics.py:180-218) scales retaliation proportionally to military ratio, but does not account for guerrilla adaptation or sanctuary effects

**Model improvement needed:**
Asymmetric attrition rates based on regime type and war aims.
External support as a state variable.

## Failure Mode 2: Long-Duration Attrition (WWI)

**What the model gets wrong:**
The model may underestimate how long attrition can sustain itself
when both sides have high initial capacity.

**Why it fails:**
The fatigue function (1.0 + month/60) assumes linear increase.
Real wars show nonlinear dynamics:
- Innovation (new weapons, tactics)
- Adaptation (learning curves)
- External shocks (new entrants, regime changes)
- Random events (assassination, weather)

**What this reveals:**
The model's clean curves are a simplification. Real wars have
discontinuities, feedback loops, and emergent phenomena that
linear update equations cannot capture.

**Evidence from the codebase:**
- WWI preset (war_dynamics.py:444): Both sides start with comparable military (80 vs 75) and economic (85 vs 70) capacity
- The fatigue factor increases from 1.0 to ~3.0 over 10 years (war_dynamics.py:233: `fatigue = 1.0 + month / 60.0`)
- This is strictly linear — no representation of the innovation cycle (gas warfare, tanks, stormtrooper tactics) that characterised WWI's middle period
- The shock interval for total_war is 6 months (war_dynamics.py:191), creating regular but uniform shock events rather than the clustered, escalating offensives of the actual war
- Economic resilience is applied as a constant damping factor (war_dynamics.py:243-246), not an adaptive variable that changes with wartime learning

**Model improvement needed:**
Nonlinear fatigue functions. Innovation as a state variable.
Random shock events.

## Failure Mode 3: Coexisting Mechanisms (WWII Eastern Front)

**What the model gets wrong:**
The model may classify WWII Eastern Front as purely attritional,
missing the decisive role of Stalingrad.

**Why it fails:**
The shock and attrition functions are independent. In reality,
they interact:
- Attrition creates conditions for decisive moments
- Decisive moments accelerate attrition
- The relationship is bidirectional and dynamic

**What this reveals:**
The model's mechanism isolation (treating shock and attrition
separately) is a strength for understanding but a weakness for
reproduction. Real wars have mechanisms that are entangled, not
separable.

**Evidence from the codebase:**
- `_apply_shock` (war_dynamics.py:180) and `_apply_attrition` (war_dynamics.py:220) are called sequentially with no coupling — shock does not modify attrition parameters and vice versa
- Shock damage is computed from current military ratio (war_dynamics.py:207: `mil_ratio = state["military_b"] / max(state["military_a"], 1)`), but attrition-induced depletion does not amplify subsequent shock damage
- DSS is computed from military delta relative to initial strength (war_dynamics.py:299-300), not from the combined attrition-shock trajectory
- The logistic regression shows DSS and SES are complementary predictors (ΔAIC = -424 for full model vs -289 for SES-only), confirming both dimensions carry independent information — but the simulation does not model their interaction

**Model improvement needed:**
Coupled dynamics where attrition enables shock and shock
accelerates attrition.

## Failure Mode 4: Political and Ideological Factors

**What the model gets wrong:**
Wars driven by ideology (WWII, Civil Wars) may have dynamics
the model cannot capture.

**Why it fails:**
The model's political will variable is a scalar (0-100).
Real political will is multidimensional:
- Elite cohesion
- Public legitimacy
- International recognition
- Ideological commitment
- Leadership quality

**What this reveals:**
Reducing political will to a single number loses essential
information. The model captures the DIMENSION of political
pressure but not its STRUCTURE.

**Evidence from the codebase:**
- Political will updates (war_dynamics.py:260-267): `state[pol_key] = state[pol_key] - casualty_pressure - weariness + victory_bonus`
- The victory bonus is binary: 0.8 if military领先, 0.0 otherwise (war_dynamics.py:266) — no distinction between morale-boosting victories and pyrrhic ones
- Political resilience is a single scalar per side (war_dynamics.py:57), applied uniformly — it does not differentiate between regime types (democratic vs authoritarian), which face fundamentally different domestic pressures
- The termination conditions (war_dynamics.py:346-398) check political will against absolute thresholds (< 10, < 15), but real political collapse is relational and contextual
- Population support (war_dynamics.py:270-271) depends only on economic hardship and casualty pressure — no representation of propaganda, media, or information effects

**Model improvement needed:**
Multi-dimensional political state (elite, public, international).

## Failure Mode 5: Trajectory Shape Prediction

**What the model gets wrong:**
The simulation correctly predicts termination type for 5/6 cases
but only captures trajectory shape for 2/6 cases.

**Why it fails:**
The model produces smooth, monotonic state trajectories. Real wars
have reversals, stalemates, and sudden shifts. The model captures
the destination but not the journey.

**Evidence from the codebase:**
- Simulation validation (paper/sections/results.tex:78-88): trajectory agreement is partial ($\sim$) for 3 cases, full ($\checkmark$) for only 2, and absent ($\times$) for 1
- The Korean War case is particularly instructive: the simulation captures attritional dynamics but misses the sudden Chinese intervention — an external shock not modeled in the state variables
- State updates are deterministic monthly steps with small Gaussian noise (war_dynamics.py:120-122: `state[key] += rng.normal(0, 0.5)`) — no representation of cascading failures, routs, or morale collapses
- The termination check (war_dynamics.py:346-398) is evaluated monthly, but real wars can transform in days (e.g., the fall of France, 1940)

**Model improvement needed:**
Event-driven shocks overlaid on continuous attrition.
External intervention as a state variable.
Regime collapse as a phase transition, not a threshold.

## Summary

The model fails in predictable ways:
1. When asymmetry dominates (Vietnam, Afghanistan)
2. When duration is extreme (WWI)
3. When mechanisms are coupled (WWII Eastern Front)
4. When ideology matters (Civil Wars, WWII)
5. When trajectory matters as much as outcome (Korean War)

These failures are INFORMATIVE. They tell us exactly which
factors the model excludes — and why those factors matter.

The model's explanatory power (62% accuracy, 5/6 termination type agreement)
exceeds its predictive power (60% blind validation, 2/6 trajectory agreement).
This gap is itself a finding: knowing what happened helps us understand why
it happened, but understanding why does not help us predict what will happen.
The mechanisms of war termination are more legible in retrospect than in
prospect.

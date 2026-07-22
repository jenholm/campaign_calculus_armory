# Model Assumptions Audit

## Purpose
This document audits every assumption in the `WarSimulator` to determine whether
the simulator is actually testing Mahan vs Attrition, or merely encoding it.

**Verdict: The model has significant circularity and assumption risks that could
invalidate conclusions about Mahan vs Attrition.** Detailed findings below.

---

## State Variables

### Military Strength (0–100)
- **What it represents:** Offensive/defensive combat capability of a belligerent.
- **Update equation:**
  - Attrition phase: `M(t+1) = M(t) - battle_losses + recruitment`
  - `battle_losses = M * base * 0.04 * resist * fatigue` (line 249)
  - `recruitment = min(1.5, industrial * 0.004)` (line 250)
  - Shock phase: `M -= damage` where damage comes from `_apply_shock` (lines 202, 209)
- **Coefficients:** `0.04` (battle loss rate), `0.004` (recruitment per industrial unit),
  `1.5` (recruitment cap), `5.0` (shock damage to B), `4.0` (retaliation damage to A).
- **Historical justification:** Partially grounded. Military strength does degrade from
  combat losses and can be replenished from industrial capacity. However, the fixed
  coefficients have no historical calibration — they are magic numbers. The recruitment
  cap of 1.5/month is never justified. Real recruitment depends on demographics,
  training pipeline length, equipment availability, and political decisions, none of
  which are modeled.
- **Assumption:** Military strength is a single scalar. In reality, offense and defense
  are asymmetric (Mahan's own point), air/naval/land are different domains, and
  quality degrades differently from quantity. A single number cannot capture this.
- **Sensitivity:** HIGH. The recruitment cap of 1.5 is a hard ceiling — once military
  drops below ~375 (at 0.004 rate), recruitment cannot offset even moderate attrition.
  The 0.04 coefficient determines whether wars end in 20 months or 80 months. Changing
  it by ±50% would likely flip outcomes for marginal cases. **No sensitivity analysis
  has been performed.**

### Economic Strength (0–100)
- **What it represents:** Economic capacity to sustain war effort.
- **Update equation:**
  - `E(t+1) = E(t) - war_costs - blockade + industrial_output` (line 257)
  - `war_costs = E * base * 0.025 * fatigue` (line 254)
  - `blockade = E * base * 0.01 * resist` (line 255)
  - `industrial_output = industrial * 0.006` (line 256)
- **Historical justification:** The war costs model is reasonable in principle — wars
  consume economic resources proportionally to existing capacity. The blockade effect
  is a nod to Mahan's emphasis on sea control. However, `industrial_output = industrial * 0.006`
  means economic recovery is trivially small (0.6% of industrial per month). The
  blockade coefficient is fixed regardless of naval balance, which undermines the
  Mahan-vs-attrition test (Mahan would say blockade is decisive; this model makes it minor).
- **Assumption:** Economic damage is proportional to current economic strength (a
  Lanchester-like attrition). Real economic damage is often targeted at specific
  infrastructure (bombing campaigns, sanctions) and doesn't scale linearly with
  GDP. The blockade is symmetric in formula but only differentiated by resilience,
  not by naval power.
- **Sensitivity:** MODERATE. The 0.006 industrial output coefficient determines economic
  recovery. If doubled to 0.012, economies recover faster and wars last longer, potentially
  changing whether attrition or shock determines outcomes.

### Political Will (0–100)
- **What it represents:** Government willingness to continue fighting.
- **Update equation:**
  - `P(t+1) = P(t) - casualty_pressure - weariness + victory_bonus` (line 267)
  - `casualty_pressure = battle_losses * 0.2` (line 260)
  - `weariness = base * 0.4 * fatigue * (1.0 - pol_resist / 200.0)` (line 264)
  - `victory_bonus = 0.8 if military > opponent's military else 0.0` (line 266)
- **Historical justification:** The casualty-pressure mechanism is supported by
  historical evidence (US in Vietnam, Russia in Afghanistan). The weariness function
  is reasonable but the victory_bonus is problematic: it's a binary step function
  (0.8 if winning, 0.0 if losing). Real political will is influenced by public
  opinion, media, elections, diplomatic context, and narrative — none modeled here.
- **Assumption:** Political will is a single linear variable. In reality, it's
  discontinuous — governments can hold firm for years then collapse suddenly
  (France 1940, Russia 1917). The model captures none of this nonlinearity.
- **Sensitivity:** MODERATE. The 0.2 casualty-pressure coefficient and the 0.8
  victory bonus interact: if victory_bonus is 0.4 instead of 0.8, the side that
  temporarily leads in military strength loses its political advantage, making
  attrition (which slowly erodes both sides) more likely to determine outcomes.

### Population Support (0–100)
- **What it represents:** Public willingness to sustain the war effort.
- **Update equation:**
  - `Pop(t+1) = Pop(t) - econ_hardship - casualty_pressure * 0.15` (line 271)
  - `econ_hardship = max(0, (50 - E)) * base * 0.03 * fatigue` (line 270)
- **Historical justification:** The mechanism that population support declines with
  economic hardship and casualties is well-supported. However, population support
  has no recovery mechanism — it can only decline or stay constant. This is
  historically wrong: wartime propaganda, national unity, and shared sacrifice
  can increase population support (UK in 1940, Ukraine in 2022).
- **Assumption:** Population support is purely a function of economic hardship and
  casualties. It ignores propaganda, nationalism, external threats, leadership,
  and media — factors that were decisive in many wars.
- **Sensitivity:** LOW in isolation (population support only affects termination
  conditions at thresholds < 20), but combined with political will, it can trigger
  termination.

### Industrial Capacity (0–100)
- **What it represents:** Ability to produce weapons, equipment, and war materiel.
- **Update equation:**
  - `I(t+1) = I(t) - bombing + recon` (line 276)
  - `bombing = I * base * 0.015 * resist * fatigue` (line 274)
  - `recon = E * 0.004` (line 275)
- **Historical justification:** Industrial capacity does degrade from bombing and
  can be rebuilt from economic resources. The bombing coefficient (0.015) is
  unrealistically low — the Combined Bomber Offensive in WWII reduced German
  industrial output by ~30-50% in targeted sectors. Here it takes decades.
- **Assumption:** Industrial capacity is a passive target. Real industrial capacity
  involves labor, raw materials, supply chains, technological sophistication, and
  management — none of which are modeled.
- **Sensitivity:** MODERATE. Industrial capacity feeds into recruitment (military)
  and recovery (economic), creating a positive feedback loop. If bombing damage
  were doubled, industrial decline would cascade into military and economic collapse
  faster, potentially making shock-based strategies more effective.

---

## Dynamics

### Shock Application (`_apply_shock`)
- **Trigger:** Every `shock_interval` months (5 for `limited_war`, 6 for `total_war`,
  7 for `coalition`). Lines 190–196.
- **Mechanism:** Side A always shocks first. `damage_b = mag * 5.0` (line 201).
  Side B retaliates proportional to relative military strength:
  `damage_a = mag * mil_ratio * 4.0` (line 208) where `mil_ratio = mil_b / mil_a`.
- **Historical justification:** Decisive battles (Trafalgar, Midway, Cannae) do
  exist and do cause sudden military drops. However, modeling them as periodic
  clockwork events is deeply problematic. Real decisive battles emerge from
  strategic context, intelligence failures, terrain, leadership decisions, and
  chance — they are not scheduled.
- **Key assumptions:**
  1. **Shocks happen at regular intervals.** This is the most consequential
     assumption. It means the simulator cannot model wars where timing of
     decisive moments matters (which is all wars).
  2. **Side A always shocks first.** This gives the initiator a structural
     advantage. In reality, defensive shocks (Tannenberg, Midway) are common.
  3. **Retaliation is proportional to military ratio.** A weaker side
     retaliates less, which is sometimes true but often not (Guerrilla forces
     with inferior military strength can inflict disproportionate damage).
  4. **Shocks affect military, industrial, and political will** — but not
     population support or economy directly. This is arbitrary.
- **Problem:** The shock interval is deterministic. A war with `shock_interval=5`
  has exactly the same number of shocks over 100 months regardless of what happens
  in between. This makes shock timing irrelevant — the model cannot test whether
  *timing* of decisive operations matters.
- **Fix needed:**
  1. Make shock timing stochastic or endogenous (triggered by state conditions,
     not fixed intervals).
  2. Allow both sides to initiate shocks (not just side A).
  3. Model shock magnitude as a function of preparation, intelligence, terrain —
     not just a fixed parameter.

### Attrition Application (`_apply_attrition`)
- **Continuous monthly degradation of all five state variables.**
- **Fatigue factor:** `1.0 + month / 60.0` — linearly increasing from 1.0 to ~3.0
  over 10 years (line 233). This means wars get progressively harder to sustain.
- **Resilience:** Reduces damage via `resist = 1.0 - resilience / 200.0` (line 246).
  Resilience of 50 gives `resist = 0.75`; resilience of 100 gives `resist = 0.5`.
- **Historical justification:** The attrition mechanism is broadly reasonable —
  wars do drain resources progressively. The fatigue factor captures war-weariness
  and is supported by historical evidence (wars tend to become less sustainable
  over time). However, the linear fatigue function is a simplification: real
  fatigue is often nonlinear (slow onset, then rapid collapse — "the last straw"
  effect).
- **Key assumptions:**
  1. **Linear fatigue increase.** Real fatigue has threshold effects and
     nonlinear acceleration.
  2. **Symmetric degradation structure.** Both sides use identical formulas,
     differing only in parameters. In reality, the side being bombed suffers
     differently from the side doing the bombing.
  3. **All variables degrade simultaneously.** In reality, economic collapse
     precedes military collapse which precedes political collapse (or sometimes
     the reverse). The model doesn't capture causal ordering.
- **Sensitivity:** HIGH. The fatigue function determines war duration. If the
  denominator changes from 60 to 40, wars end 33% faster. Combined with the
  attrition_rate parameter, this determines whether the model produces attrition
  victories or negotiated settlements.

### Stochastic Noise
- **Gaussian noise:** N(0, 0.5) added to all state variables each month (line 121).
- **Historical justification:** War is inherently uncertain. Some noise is
  appropriate.
- **Assumption:** Noise magnitude is fixed and independent of state. In reality,
  uncertainty increases as information degrades (fog of war). The 0.5 standard
  deviation is arbitrary.
- **Sensitivity:** LOW in isolation, but noise can push variables across
  termination thresholds, affecting outcomes. Over 100 months, cumulative
  noise can shift values by ±5.

---

## Derived Metrics

### DSS (Decisive Shock Score)
- **Formula:** `min(100, military_shock * 50 + capital_bonus * 30 + surrender_bonus * 20)`
  (line 306)
- **Components:**
  - `military_shock = max(0, -delta_military) / max(initial_mil, 1.0)` where
    `delta_military = curr_mil - prev_mil` (lines 299–300)
  - `capital_bonus = 1.0 if curr_mil < initial_mil * 0.3 else 0.0` (line 303)
  - `surrender_bonus = 1.0 if pol_will < 20 else 0.0` (line 304)
- **Historical justification:** The idea that decisive outcomes involve sudden
  military drops, capital capture, or political collapse is historically grounded.
- **Problem: CIRCULARITY.** This is the most critical finding. The shock function
  (`_apply_shock`) causes military drops. DSS measures military drops. Therefore
  DSS is not an independent measure of decisiveness — it is a direct readout of
  the shock function's output. The model creates the very phenomenon it claims to
  measure. Specifically:
  - `_apply_shock` reduces `state["military_b"]` by `mag * 5.0` every 5–7 months
  - `_compute_dss` looks at `delta_military` between consecutive months
  - If a shock month happens to be a consecutive month checked, DSS captures it
  - The `capital_bonus` and `surrender_bonus` are triggered by thresholds that
    the shock function can push state variables toward
  - **Net effect:** DSS will always be high for the side receiving shocks, and
    low for the side inflicting them. This doesn't test whether decisive strategy
    works — it measures whether shocks happen.
- **Fix needed:** DSS should be computed from observable historical analogues, not
  from the simulation's own shock outputs. Or it should be defined in terms of
  *strategic* outcomes (territory, fleet destruction, government change) rather than
  single-month military drops.

### SES (Strategic Exhaustion Score)
- **Formula:** `(military_ex * 0.3 + economic_ex * 0.3 + political_ex * 0.2 +
  duration * 0.2) * 100.0` (lines 334–339)
- **Components:**
  - `military_exhaustion = 1.0 - (military_current / military_initial)` (line 329)
  - `economic_exhaustion = 1.0 - (economic_current / economic_initial)` (line 330)
  - `political_exhaustion = 1.0 - (political_current / political_initial)` (line 331)
  - `duration_factor = min(1.0, month / 60.0)` (line 332)
- **Historical justification:** Exhaustion metrics based on cumulative decline from
  initial values are reasonable. The weighting (military 30%, economic 30%, political
  20%, duration 20%) is a judgment call — there's no historical basis for these
  specific weights.
- **Key assumptions:**
  1. **Linear weights with fixed proportions.** Why is military exhaustion equal to
     economic exhaustion? For some wars (WWII), economic exhaustion was decisive;
     for others (WWI), political exhaustion was.
  2. **Duration is penalized.** The duration factor means that even if a side is
     winning militarily and economically, prolonged war increases its SES. This
     bakes in an assumption that long wars favor attrition outcomes — which is
     exactly what the model is supposed to test, not assume.
  3. **Initial values are the baseline.** If a side starts strong but declines
     slowly, it gets high SES. If a side starts weak and stays weak, it gets
     low SES. This penalizes the side that was initially stronger.
- **Sensitivity:** MODERATE. The weights (0.3, 0.3, 0.2, 0.2) determine which
  component dominates. If duration weight is 0 instead of 0.2, attrition victories
  through prolonged war become less decisive in the model.

---

## Termination Conditions

### 1. Political Will Collapse (pol < 10) → Decisive Victory
- **Assumption:** Political will of 10 or below means the government capitulates.
  This is a threshold model for a phenomenon that is historically variable.
  France in 1940 had political will collapse with military still partially
  functional. The USSR in 1991 dissolved with military largely intact.
- **Problem:** Threshold at 10 is arbitrary. At what political will level does
  a government actually surrender? This varies enormously by regime type.

### 2. Military Collapse (mil < 10) → Decisive Victory
- **Assumption:** Military strength below 10 means total defeat.
- **Problem:** Reasonable in principle, but the 0–100 scale makes this a
  relative measure. Military at 10 could mean 10% of peak strength or
  10 absolute units — the model doesn't distinguish.

### 3. Military Dominance (2x ratio, opponent < 30) → Decisive Victory
- **Assumption:** Having 2x military and opponent below 30 is decisive.
- **Problem:** The 2x ratio is arbitrary. Historical decisive advantages vary
  (Cannae was ~2:1, Kursk was more complex). The < 30 threshold is also arbitrary.

### 4. Mutual Exhaustion (both SES > 80) → Mutual Exhaustion
- **Assumption:** Both sides reaching 80% exhaustion means mutual exhaustion.
- **Problem:** The SES > 80 threshold for mutual exhaustion may trigger before
  other termination conditions, cutting short scenarios where one side would
  have collapsed. This could mask attrition outcomes.

### 5. Economic Collapse (SES > 80 or econ < 15) → Decisive Victory
- **Assumption:** Economic collapse at 15 or SES > 80 means the side loses.
- **Problem:** Economic collapse doesn't always mean military defeat. Germany
  in 1918 was economically exhausted but militarily still in the field. The
  model conflates economic and military outcomes.

### 6. Negotiated Settlement (both mil < 50)
- **Assumption:** When both sides are below 50 military strength, they negotiate.
- **Problem:** This is a strong assumption. Many wars with both sides weakened
  ended in decisive outcomes (WWII) not negotiations. The threshold of 50 is
  arbitrary and may be too high.

### 7. Combined Political-Population Collapse (pol < 15, pop < 20)
- **Assumption:** Both political will AND population support must be low.
- **Problem:** This is redundant with condition 1 (pol < 10 already triggers).
  The only scenarios where this matters are pol in [15, 10) — a narrow band.

### Overall Termination Assessment
The termination conditions are a collection of threshold rules with no historical
calibration. They create a complex interaction where the first condition to trigger
determines the outcome, but the conditions are not mutually exclusive and may
contradict each other. **The ordering matters and is not justified.**

---

## Historical Presets

### Gulf War 1991
| Parameter | Value | Historically Grounded? | Sensitivity |
|-----------|-------|----------------------|-------------|
| `war_type` | `limited_war` | Yes — limited objective | Low |
| `military_a` | 95 | Reasonable for coalition | Low |
| `military_b` | 70 | Inflated — Iraqi army was demoralized | Moderate |
| `economic_a` | 95 | Yes — US-led coalition economy | Low |
| `economic_b` | 40 | Yes — sanctions already hurting | Low |
| `political_will_a` | 85 | Yes — broad coalition support | Low |
| `political_will_b` | 60 | Possibly high — Saddam held firm | Moderate |
| `industrial_a` | 95 | Yes — massive industrial base | Low |
| `industrial_b` | 35 | Yes — degraded by sanctions | Low |
| `shock_strength` | 90 | Yes — 100-hour ground war | Low |
| `attrition_rate` | 30 | Yes — short war | Low |
| `economic_resilience` | 80 | Yes — coalition had strong economy | Low |
| `political_resilience` | 70 | Yes — coalition held together | Low |

**What would flip the conclusion?** If `shock_strength` drops below 50 or
`attrition_rate` rises above 60, the model might show a negotiated settlement
instead of decisive victory — which contradicts the historical outcome.

### Vietnam War
| Parameter | Value | Historically Grounded? | Sensitivity |
|-----------|-------|----------------------|-------------|
| `war_type` | `limited_war` | Yes — limited objectives | Low |
| `military_a` | 85 | Reasonable for US+ARVN | Low |
| `military_b` | 50 | Low — NVA/VC had less conventional strength | Moderate |
| `political_will_a` | 70 | Debatable — US will eroded over time | HIGH |
| `political_will_b` | 95 | Yes — North Vietnam had high will | Low |
| `shock_strength` | 25 | Debatable — Tet Offensive was a shock | Moderate |
| `attrition_rate` | 75 | Yes — protracted war | Low |

**Critical question:** The `political_will_a` of 70 means US will starts high and
declines. But historically, US will was the decisive factor. If it starts at 60
instead of 70, the model might terminate earlier, changing the narrative. **The
political will initial value is doing most of the work in this preset.**

### WWI
| Parameter | Value | Historically Grounded? | Sensitivity |
|-----------|-------|----------------------|-------------|
| `war_type` | `total_war` | Yes | Low |
| `military_a` | 80 | Reasonable | Low |
| `military_b` | 75 | Yes — Central Powers were competitive early | Low |
| `shock_strength` | 40 | Debatable — battles were massive but not decisive | HIGH |
| `attrition_rate` | 80 | Yes — war of attrition | Low |

**Critical question:** WWI is the canonical example of attrition winning over
shock (Mahan's decisive battle doctrine failed at the Marne, Jutland, etc.).
But the model gives `shock_strength=40` and `attrition_rate=80`, which essentially
pre-determines an attrition outcome. **Is the model testing attrition vs shock,
or is it parameterized to produce the known answer?**

### Franco-Prussian War
| Parameter | Value | Historically Grounded? | Sensitivity |
|-----------|-------|----------------------|-------------|
| `shock_strength` | 90 | Yes — Prussian decisive operations | Low |
| `attrition_rate` | 35 | Yes — short war | Low |

**Critical question:** This is the canonical Mahan example. High shock, low
attrition. But the parameters are set to produce this outcome. **The preset
encodes the hypothesis rather than testing it.**

### Korean War
| Parameter | Value | Historically Grounded? | Sensitivity |
|-----------|-------|----------------------|-------------|
| `war_type` | `coalition` | Debatable — UN was coalition but US-dominated | Low |
| `political_will_a` | 70 | Debatable — MacArthur fired, UN limits | HIGH |
| `political_will_b` | 85 | Yes — Chinese/NK commitment | Low |

### Iran-Iraq War
| Parameter | Value | Historically Grounded? | Sensitivity |
|-----------|-------|----------------------|-------------|
| `attrition_rate` | 85 | Yes — 8 years of attrition | Low |
| `shock_strength` | 30 | Yes — limited decisive operations | Low |
| `political_will_a` | 90 | Yes — revolutionary zeal | Low |

**This preset is the most internally consistent** — it models a war of attrition
and produces an attrition outcome.

---

## Critical Assessment

### Is the model testing the hypothesis or encoding it?

**Finding: The model is largely encoding the hypothesis, not testing it.**

The fundamental problem is that the model has two mechanisms (shock and attrition)
that are *added together* in each time step (lines 116–117). The relative strength
of each is controlled by two parameters (`shock_strength` and `attrition_rate`)
that are set per preset. The model then asks: "which metric (DSS or SES) better
predicts the outcome?" But since DSS is computed from shock outputs and SES is
computed from cumulative state decline, **the model will always find that DSS
predicts shock outcomes and SES predicts attrition outcomes** — this is tautological.

### Circularity Risks

1. **DSS ← shock function → DSS:** The shock function creates military drops.
   DSS measures military drops. DSS will always correlate with shock parameters
   because it is literally measuring the shock function's output. This is not
   evidence that decisive strategy works — it's evidence that the model implements
   decisive strategy.

2. **SES ← attrition function → SES:** Similarly, the attrition function creates
   cumulative decline. SES measures cumulative decline. SES will always correlate
   with attrition parameters.

3. **Termination conditions use thresholds that are reachable primarily through
   one mechanism or the other.** Military collapse (mil < 10) is more likely from
   repeated shocks. Economic collapse (econ < 15) is more likely from attrition.
   The model's termination conditions are not mechanism-neutral.

4. **Historical presets are parameterized to produce known outcomes.** The Gulf War
   preset has high shock / low attrition → produces decisive victory. WWI has low
   shock / high attrition → produces attrition outcome. The model "validates" by
   reproducing what was already assumed.

### Parameter Sensitivity Risks

1. **No sensitivity analysis has been performed.** All coefficients (0.04, 0.025,
   0.015, 0.004, 0.006, 5.0, 4.0, 0.8, 0.2, 0.3) are fixed without justification.
   Changing any one of them could flip conclusions for marginal cases.

2. **The fatigue function denominator (60) is a single point of failure.** If changed
   to 40, wars end 33% faster. If changed to 80, wars last 33% longer. This parameter
   alone could determine whether attrition or shock appears to dominate.

3. **Initial conditions dominate outcomes.** The side with higher initial values
   across all variables has a structural advantage. This is historically reasonable
   but means the model may be measuring initial strength, not strategy.

4. **The 0–100 clamping creates artificial floors and ceilings.** Variables cannot
   go below 0 or above 100, which means extreme scenarios are truncated. A military
   of 0.5 and a military of 0.0 are treated identically.

### What would break the model?

1. **Swap initial conditions between sides.** If the historically weaker side is
   given stronger initial conditions but lower shock / higher attrition parameters,
   does the model still produce the correct outcome? If yes, the model is measuring
   initial strength not strategy.

2. **Make shocks endogenous.** If shocks are triggered by state conditions (e.g.,
   when one side achieves local superiority) rather than fixed intervals, the model
   might produce different outcomes.

3. **Remove one mechanism entirely.** Set `shock_strength = 0` for all presets.
   Does the model still produce historically correct outcomes? If yes, attrition
   alone explains the outcomes and the Mahan component is unnecessary.

4. **Randomize shock timing.** If shock events happen at random months instead of
   fixed intervals, does the model still produce the same DSS values? If DSS
   depends on *when* shocks happen, the fixed-interval assumption is doing the work.

5. **Add a third strategy.** If a "hybrid" strategy (moderate shock + moderate
   attrition) produces the best outcomes across all presets, the model doesn't
   actually test Mahan vs Attrition — it tests extreme vs moderate.

### What would strengthen the paper?

1. **Compute DSS from exogenous data, not simulation outputs.** Use historical
   battle data, territory changes, or fleet losses to define DSS independently
   of the simulation's own dynamics.

2. **Perform systematic sensitivity analysis.** Vary each coefficient ±25%, ±50%
   and report which conclusions are robust and which flip. If more than 2 coefficients
   can flip conclusions, the results are not reliable.

3. **Test against out-of-sample wars.** Train on 4 historical presets, predict on 2
   held-out wars. If the model can't predict unseen wars, it's overfit to the
   training data.

4. **Make shock timing stochastic.** Replace fixed intervals with probabilistic
   triggers to test whether *timing* of decisive operations matters.

5. **Add mechanism-neutral termination conditions.** Use outcomes that don't
   depend on which mechanism caused the state change (e.g., territory held,
   government survival, armistice terms).

6. **Compare against a null model.** Show that the model performs better than
   random assignment of outcomes. If random outcomes are equally predictive,
   the model adds no information.

7. **Justify all coefficients historically.** Every magic number should reference
   historical data or be treated as a free parameter with documented uncertainty.

8. **Address the encoding problem directly.** Acknowledge that the model has two
   mechanisms with two knobs, and that "finding" one mechanism works for one metric
   is expected, not informative.

---

## Summary of Key Findings

| Finding | Severity | Fix Effort |
|---------|----------|------------|
| DSS measures shock function output (circularity) | **CRITICAL** | Medium |
| Historical presets encode known outcomes | **CRITICAL** | Low |
| No sensitivity analysis on any coefficient | **HIGH** | Medium |
| Shock timing is fixed, not endogenous | **HIGH** | High |
| Side A always shocks first (structural bias) | **HIGH** | Low |
| SES penalizes duration (bakes in attrition bias) | **HIGH** | Low |
| Linear fatigue function (no threshold effects) | **MEDIUM** | Low |
| Population support has no recovery mechanism | **MEDIUM** | Low |
| Termination thresholds are arbitrary | **MEDIUM** | Medium |
| Noise magnitude is fixed and small | **LOW** | Low |
| Binary victory bonus in political will | **LOW** | Low |

**Bottom line:** The model as currently implemented will tend to find that DSS
predicts decisive outcomes and SES predicts attrition outcomes, regardless of
the historical preset, because these metrics are computed from the same functions
that drive the dynamics. This is not evidence that Mahan's doctrine works — it is
a mathematical tautology. To produce credible results, the model needs either
exogenous outcome measures, sensitivity analysis, or a fundamentally different
approach to computing DSS and SES.

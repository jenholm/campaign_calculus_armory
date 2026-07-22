# Adversarial Case Analysis

## Purpose
Test the model framework against cases where it is expected to struggle.
These are not cherry-picked successes — they probe model limitations.

## Cases

### Case 1: Vietnam War
**Challenge:** Tactical success fails strategically
**Expected:** attritional

The model must capture the fundamental asymmetry: the US wins every battle
but loses the war. This requires political will degradation to dominate
military effectiveness.

**Key test:** Does the model produce attritional outcome despite US military
superiority (85 vs 50)?

### Case 2: Soviet-Afghan War
**Challenge:** Military superiority fails against insurgency
**Expected:** attritional

Soviet military advantage (90 vs 30) is overwhelming. The model must show
how 10 years of political will degradation overcomes this advantage.

**Key test:** Can the model sustain conflict long enough for political
exhaustion to manifest?

### Case 3: World War I
**Challenge:** Exhaustion dominates despite major battles
**Expected:** mixed

Both sides have strong shock potential and strong attrition. The model must
show that shocks (Verdun, Somme) didn't terminate the war while attrition
gradually exhausted both sides.

**Key test:** Do high shock values coexist with attritional termination?

### Case 4: WWII Eastern Front
**Challenge:** Attrition and decisive campaigns coexist
**Expected:** mixed

Stalingrad (decisive) + Soviet industrial attrition (attritional) = mixed.
The model must show both mechanisms operating simultaneously.

**Key test:** Can the model produce mixed outcomes?

### Case 5: American Civil War
**Challenge:** Strategic exhaustion plus decisive campaigns
**Expected:** mixed

Grant (attritional) + Sherman (decisive) = Union victory through both.
The model must show complementary mechanisms.

**Key test:** Does the model capture mechanism complementarity?

## Expected Results

If the model correctly classifies these adversarial cases, it suggests
the framework captures genuine structural dynamics. If it fails, the
failures reveal model limitations.

## Limitations Revealed

1. The model may struggle with asymmetric warfare (Vietnam, Afghanistan)
   because it treats both sides symmetrically in the attrition function.

2. The model may overestimate shock effectiveness because shocks
   happen at fixed intervals regardless of state conditions.

3. The model may not capture the complementarity of attrition + shock
   because these are separate functions rather than interacting dynamics.

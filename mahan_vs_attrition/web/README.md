# War Dynamics Simulator v2

## What This Is

An interactive browser-based simulation exploring how strategic exhaustion
and decisive shocks interact in war termination. Aligned with paper v2
mechanism classifier.

## What This Is NOT

This is **not** a war prediction engine. It does not predict who will win
any real conflict. It is a conceptual model for exploring mechanism dynamics.

## How to Use

Open `index.html` in any modern browser. No server needed - presets are
embedded directly in the JavaScript.

1. Select a historical preset or configure custom parameters
2. Click "Run Simulation" to see the trajectory
3. Toggle "History Mode" for annotated historical replay
4. Toggle "Full 5-Variable Model" to see all state variables

## Controls

### War Type
- Total War: high attrition, frequent shocks
- Limited War: moderate attrition, focused shocks
- Colonial War: asymmetric dynamics
- Coalition War: alliance effects

### Parameters
- **Shock Strength**: Mahan parameter — decisive battle potential (0-100)
- **Attrition Rate**: Exhaustion parameter — cumulative wear (0-100)
- **Economic Resilience**: Ability to sustain war costs (0-100)
- **Political Resilience**: Willingness to continue fighting (0-100)

### Historical Presets
Pre-configured parameters for 7 historical wars:
- Gulf War 1991 (decisive shock)
- Vietnam War (strategic exhaustion)
- World War I (strategic exhaustion)
- World War II (strategic exhaustion with decisive accelerators)
- Franco-Prussian War (decisive shock)
- Korean War (mixed / unresolved)
- Iran-Iraq War (strategic exhaustion)

## What the Model Shows

### v2 Mechanism Classification

The simulator separates two distinct questions:

1. **Termination Event**: How the war ended (military collapse, political
   collapse, negotiated settlement, etc.)
2. **Dominant Mechanism**: Why the war became unwinnable (decisive shock
   or strategic exhaustion)

These are different questions. The v1 classifier confused them. The v2
classifier computes independent scores for each mechanism.

### Trajectories
Military strength, political will, and economic capacity for both sides
over time. Toggle "Full 5-Variable Model" to also see population support
and industrial capacity.

### Mechanism Dominance
DSS (Decisive Shock Score) and SES (Strategic Exhaustion Score) over time.
Shows which mechanism dominates at each phase.

### History Mode
Annotated historical events overlaid on the simulation trajectory.
Shows the model's interpretation of when each mechanism was active.

### Mechanism Breakdown
Percentage breakdown of exhaustion-driven vs shock-driven vs mixed months.

## Scientific Context

This simulator accompanies the paper:
"Decisive Shock or Strategic Exhaustion? A Dynamical Model of War
Termination Mechanisms"

The paper's key finding: wars often contain both mechanisms. Attrition
changes the state space; decisive shocks exploit the changed state space.
The historical mistake is treating the visible collapse event as the
entire cause.

## Limitations

- The simulation is deterministic (same inputs → same outputs)
- Parameters are calibrated to historical examples (circularity risk)
- The model excludes ideology, leadership, diplomacy, and culture
- Results are conceptual, not predictive

## Technical Details

- Pure HTML/CSS/JS (no frameworks, no CDN)
- Canvas-based charting (no external libraries)
- Seeded PRNG for reproducibility
- Self-contained (~60KB total)
- Presets generated from Python HISTORICAL_PRESETS
- v2 mechanism classifier ported from Python source

## Regenerating Presets

Presets are embedded in `js/presets.js` and generated from the Python
source `src/mahan_vs_attrition/simulation/war_dynamics.py`.

To regenerate:

```bash
python3 scripts/export_web_presets.py
```

## Tests

```bash
# Static checks
bash web/tests/static_check.sh

# Node.js simulation smoke test
node web/tests/simulation_smoke.mjs
```

# Model Scope and Limitations

## Framing

This model intentionally prioritizes mechanism isolation over complete
historical reconstruction. Like all models, it is wrong. The question
is whether it is usefully wrong.

## What the Model Captures

### Military Dynamics
- Force strength degradation from combat
- Recruitment and replacement
- Battle losses as function of attrition rate
- Shock events as discrete military blows

### Economic Dynamics
- War cost accumulation
- Industrial production capacity
- Economic resilience to sustained conflict
- Blockade and supply disruption effects

### Political Dynamics
- Political will degradation from casualties
- Victory bonus effect on morale
- Population support erosion from hardship
- War weariness accumulation

### Termination Mechanisms
- Military collapse threshold
- Political will collapse
- Economic exhaustion
- Negotiated settlement conditions
- Regime collapse dynamics

### Mechanism Decomposition
- DSS (explanatory): measures decisive shock potential from state history
- DSS (predictive): estimates shock potential from exogenous features only
- SES: measures cumulative exhaustion across all dimensions
- Classification: hybrid rule combining both axes

## What the Model Does Not Capture

### Individual-Level Factors
- Leadership quality and decision-making
- Generalship and tactical brilliance
- Individual courage and morale events
- Assassination and leadership decapitation

### Ideological Factors
- Religious motivation
- Nationalist fervor
- Political ideology
- War aims and objectives

### Diplomatic Factors
- Alliance formation and dissolution
- Diplomatic negotiations during war
- Third-party mediation
- Arms races and pre-war dynamics

### Cultural Factors
- Military culture and doctrine
- Civil-military relations
- Social cohesion
- Propaganda and information warfare

### Environmental Factors
- Weather and seasons
- Terrain (modeled only as logistics difficulty)
- Disease and epidemic
- Natural disasters

### Technological Factors
- Weapons technology differences
- Innovation during war
- Intelligence and surveillance
- Communication technology

### Stochastic Factors
- Random battle outcomes
- Fog of war
- Luck and chance events
- Individual incidents escalating

## Why These Exclusions Are Intentional

The model is a **mechanism isolation tool**, not a war simulator.

By excluding ideology, leadership, and diplomacy, we can ask:
"What happens to the structural dynamics of war when we vary only
shock strength and attrition rate?"

This is a valid scientific question even though the answer is incomplete.

The model tells us: "Given these structural conditions, the
attrition-shock decomposition produces this trajectory."

It does NOT tell us: "This is what actually happened."

## Calibration Strategy

Historical presets are calibrated to match known outcomes. This is
intentional for demonstration purposes. The blind validation test
removes this calibration to test predictive validity.

## Known Limitations

1. **Circularity in observed DSS**: The explanatory DSS contains
   outcome information. We quantify this gap using predictive DSS.

2. **Parameter sensitivity**: Some presets may be fragile under
   parameter variation. We report sensitivity analysis results.

3. **Small validation set**: 15 blind validation cases is insufficient
   for strong statistical claims. Results are indicative, not conclusive.

4. **Simulation simplicity**: The model uses linear update equations.
   Real war dynamics are nonlinear and chaotic.

5. **Selection bias**: Case studies are not randomly selected.
   They represent the authors' judgment of prototypical cases.

## What Would Strengthen the Claims

1. Larger blind validation set (50+ wars)
2. Independent parameter estimation (not hand-tuned)
3. Nonlinear dynamics (coupled ODEs or agent-based model)
4. Stochastic simulation (Monte Carlo)
5. Out-of-sample prediction on newly coded wars

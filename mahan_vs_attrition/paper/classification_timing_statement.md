# Classification Timing Statement

**Date:** 2026-07-20
**Purpose:** Document when historical mechanism labels were assigned relative to simulation development.

## Timeline

1. **Simulation model developed** — The WarSimulator class and HISTORICAL_PRESETS were implemented
2. **V2 classifier designed** — The mechanism_classifier.py was written to separate termination events from strategic mechanisms
3. **Historical classifications assigned** — The HISTORICAL_CASES_V2 dict was populated with ground-truth labels based on historical knowledge
4. **Simulation run** — The model was run against presets and compared to historical classifications
5. **Results analyzed** — Agreement metrics (86%) were computed

## Key Point

Historical mechanism classifications were assigned independently of individual simulation trajectories but were not blinded from the development team. They should therefore be interpreted as structured comparisons rather than independent validation labels.

## What This Means

- The labels are based on historical knowledge, not simulation output
- But the same team developed both the model and the labels
- This is standard practice in computational social science
- Independent verification by historians blind to simulation results would strengthen the analysis

## Added to Paper

This statement was added to `methods.tex` in the "Historical Reconstruction versus Blind Prediction" subsection.

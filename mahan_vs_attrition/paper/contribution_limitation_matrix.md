# Contribution and Limitation Map

**Purpose:** Systematic mapping of reviewer concerns to valid criticisms and response strategies. This document does not remove criticisms — it converts them into discussion material.

---

| Issue | Reviewer Concern | Valid? | Response Strategy |
|-------|-----------------|--------|-------------------|
| **DSS hindsight bias** | The simulation-derived DSS measures output of the shock function it contains. This is tautological, not empirical. | **Yes.** The simulation-derived DSS (Equation 5) does measure shock output. However, the paper's primary statistical results (logistic regression, ablation, survival analysis) use the *empirical* DSS computed from external IWB/COW data via Equation 1. These are distinct metrics. | Explain and separate observed vs. predictive DSS. Add leakage analysis showing empirical and simulation-derived DSS have r=0.31 (different information). Restructure Methods to make this distinction visible. |
| **Historical presets encode the answer** | Gulf War has shock=90/attrition=30 → decisive. WWI has shock=40/attrition=80 → attrition. Validation merely reproduces assumed outcomes. | **Yes.** The calibrated validation (Table 4) is a consistency check, not an independent test. The authors' own audit states: "The preset encodes the hypothesis rather than testing it." | Reframe presets as mechanism demonstrations, not validation experiments. Change wording from "validated against" to "tested whether mechanism combinations can reproduce historically observed trajectory classes." Add explicit separation of calibrated validation (consistency check) from blind validation (predictive test). |
| **Limited wars / sample scope** | The 30 case studies are hand-picked. Where are anomalous cases? | **Partially.** Case study selection is standard qualitative practice but was not random. | Explain data availability and scope. Add coverage analysis table. Add explicit discussion of anomalous cases. Frame 4,220 wars as "wars with varying completeness" not "fully characterized wars." |
| **Parameter selection / magic numbers** | 15+ free coefficients with no historical calibration. Sensitivity analysis tests only 4 parameters. Fatigue denominator of 60 is a single point of failure. | **Yes.** This is the most technically valid criticism. The sensitivity analysis tests only "control" parameters, not "implementation" coefficients. | Conduct and present full internal coefficient sensitivity analysis (Table 5b). Add discussion of which coefficients are "load-bearing" vs. robust. Add historical justification or uncertainty ranges. Focus on "Exact values are uncertain, but qualitative regimes persist." |
| **Prediction claims** | Paper uses "demonstrates," "shows," "confirms" — implying it predicts war outcomes. | **Yes.** Causal language throughout overstates what the methodology can establish. | Refine terminology. The model predicts: termination pathway class, dominance of mechanism, trajectory shape. It does not predict: exact winner, date of surrender, battlefield outcome. Replace "demonstrates" with "evaluates," "shows" with "suggests within the model." |
| **Missing variables** | Model ignores leadership, intelligence, geography, technology, alliances, domestic politics, weather, C2. | **Partially.** Valid as statement about scope. Misses the paper's intent as a conceptual model. | Explain intentional abstraction. The simulation isolates the interaction between two specific mechanisms. Add explicit list of omitted variables and their potential impact in specific case studies. |
| **Unfalsifiability of attritional iceberg** | No possible evidence could refute the thesis. Decisive battles → enabled by attrition. Attrition → confirms attrition. Mixed → confirms interaction. | **No — falsifiable.** The blind validation provides the falsification test. If the iceberg were narrative, the simulator (default neutral parameters) would not distinguish decisive from attritional cases above chance. It achieves 58% vs. 33% chance. | Add dedicated falsification section (Section 5.8). Frame blind validation accuracy as the falsification threshold. Explicitly state what would refute the attritional iceberg. |
| **Statistical methodology** | Logistic regression may overfit. Ablation uses no cross-validation. Survival R²=0.12. Blind validation CI includes chance. | **Partially.** Several sub-issues: (a) overfitting is modest (CV accuracy 0.59 vs. training 0.62), (b) survival analysis is exploratory, (c) blind validation CI is wide. | Add 5-fold cross-validation. Revise survival language to "exploratory." Expand blind validation to 20+ cases. Do not delete — verify and reinterpret. |
| **Reproducibility incomplete** | No random seeds, Python version, convergence criteria, or expert identification in paper. | **Partially.** Seeds (42) and Python version are specified in pyproject.toml. Delphi experts confidential per IRB. | Add reproducibility section with seeds, versions, environment. Add Delphi protocol description (expert selection criteria, 3-round protocol, 70% agreement threshold). |
| **Simulation produces clean results** | Smooth deterministic curves with trivial noise. Attritional iceberg is artifact of continuous attrition function. | **Partially.** Simulation is deterministic by design — conceptual model. The iceberg is primarily supported by empirical DSS/SES analysis, not simulation. | Add scope documentation. Distinguish empirical findings from simulation illustrations. Note that smooth trajectories are a modeling artifact. |

---

## Summary

Of 10 major criticisms:
- **4 fully valid** (parameters, causal claims, statistics partially, reproducibility partially) → changes made
- **4 partially valid** (circularity, presets, selection, simulation, missing variables) → addressed with caveats and clarifications
- **1 not valid as stated** (unfalsifiable) → defended with explicit falsification test
- **1 partially valid but defending core contribution** (unfalsifiable, reframed) → falsification section added

## Quantitative Changes Made
- Added 5-fold cross-validation for logistic regression
- Expanded blind validation from 10 to 20+ cases
- Added full internal parameter sensitivity analysis (15+ coefficients x 3 presets)
- Added leakage analysis (empirical vs. simulation DSS: r=0.31)
- Revised 23 instances of causal language
- Added coverage statistics table for dataset
- Added reproducibility documentation (seeds, versions, environment)
- Added dedicated falsification section

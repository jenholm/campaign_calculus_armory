# DSS/SES Metric Artifact Analysis

**Date:** 2026-07-20
**Purpose:** Audit whether clustering in the DSS/SES scatter plot reflects natural discontinuities in historical conflict mechanisms or artifacts of the scoring system.

## Concern

The DSS/SES scatter plot (Figure 5) shows clustering along horizontal and vertical axes. A reviewer will ask: "Are we seeing war mechanisms, or the geometry of the scoring system?"

## Analysis

### DSS Construction

DSS is a composite score from 9 weighted components, each scored 0-100:
- Components are binary (0 or 100) for 5 of 9 variables (capital_capture, field_army_destroyed, fleet_destroyed, rapid_surrender, regime_collapse)
- Source_claims_decisive is manually coded (typically 0, 50, or 100)
- Final_battle_proximity uses binned values (0, 30, 60, 80, 100)
- Battle_casualty_concentration is a continuous ratio

**Implication:** The binary nature of 5/9 components creates artificial clustering at specific score values. Wars with the same combination of binary outcomes will cluster at identical DSS values.

### SES Construction

SES is a composite score from 10 weighted components, each scored 0-100:
- Components use continuous ratios and log-transformed values
- More continuous than DSS, but still bounded [0, 100]
- Imputation models used for missing data introduce additional smoothing

**Implication:** SES is more continuous than DSS, but still subject to boundary effects at 0 and 100.

### Clustering Sources

1. **Binary component clustering (DSS):** 5/9 DSS components are binary. This creates artificial clusters at specific DSS values. For example, wars with capital_capture=100, field_army_destroyed=100, rapid_surrender=100, regime_collapse=100, fleet_destroyed=0 will cluster at specific DSS values regardless of other components.

2. **Weight concentration (DSS):** source_claims_decisive has weight 0.35. If this component is 0 or 100, it creates a large jump in DSS. This binary high-weight component creates two clusters.

3. **Boundary effects:** Both DSS and SES are bounded [0, 100]. Wars near the boundaries cluster at the edges.

4. **Data sparsity:** Only 91 wars have complete DSS data. With 91 points, apparent clusters may reflect sparse sampling rather than natural mechanisms.

### Recommendations

1. **Add jitter** to scatter points to reveal overlapping observations
2. **Add density contours** to show the actual distribution shape
3. **Acknowledge in the paper** that DSS and SES are composite indices, and clustering along score boundaries may partially reflect metric construction rather than natural discontinuities
4. **Show component distributions** in supplementary material to help readers assess the scoring architecture

### Paper Language Addition

Add to the DSS/SES scatter section:

"Because DSS and SES are composite indices constructed from weighted component scores, clustering along score boundaries may partially reflect metric construction rather than natural discontinuities in historical conflict mechanisms. The binary nature of five DSS components (capital capture, field army destroyed, fleet destroyed, rapid surrender, regime collapse) creates artificial clustering at specific score values. We add jitter to overlapping points and show density contours to reveal the underlying distribution shape."

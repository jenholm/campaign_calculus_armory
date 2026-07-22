# Final Numerical Traceability Audit

Date: 2026-07-20
Scope: Paper at `paper/`, CSV at `reports/outcome_information_delta_v2.csv`, figure code at `scripts/generate_paper_figures.py`, config at `config/metric_weights.yml`

---

## 1. Table 2 (OID Table) vs CSV — results.tex lines 107–114

| Conflict | CSV obs | Table obs | CSV pred | Table pred | CSV Δ | Table Δ | Match? |
|---|---|---|---|---|---|---|---|
| Gulf War (1991) | 80.0 | 80.0 | 64.4 | 64.4 | +15.6 | +15.6 | ✅ |
| Six Day War (1967) | 95.0 | 95.0 | 55.0 | 55.0 | +40.0 | +40.0 | ✅ |
| Franco-Prussian (1870) | 85.0 | 85.0 | 53.0 | 53.0 | +32.0 | +32.0 | ✅ |
| World War I (1914–19) | 60.0 | 60.0 | 52.4 | 52.4 | +7.6 | +7.6 | ✅ |
| World War II | 50.0 | 50.0 | 54.6 | 54.6 | −4.6 | −4.6 | ✅ |
| Korean War (1950–53) | 45.0 | 45.0 | 62.7 | 62.7 | −17.7 | −17.7 | ✅ |
| Vietnam War (1965–75) | 30.0 | 30.0 | 69.9 | 69.9 | −39.9 | −39.9 | ✅ |
| Iran–Iraq (1980–88) | 35.0 | 35.0 | 49.5 | 49.5 | −14.5 | −14.5 | ✅ |

**All 8 rows match.** ✅

### Mean OID

Correct computation: (15.6 + 40.0 + 32.0 + 7.6 − 4.6 − 17.7 − 39.9 − 14.5) / 8 = 18.5 / 8 = **+2.3**

| Location | Value | Correct? |
|---|---|---|
| `results.tex:116` (table footer) | **−$0.6** | ❌ **ERROR** |
| `methods.tex:166` (prose) | **+2.3** | ✅ |

**FINDING: The table footer in results.tex:116 reports the mean as −$0.6. The correct value is +2.3. This is a clear error that contradicts both the CSV data and the prose in methods.tex:166.**

---

## 2. Figure 2 (OID Bar Chart) vs CSV

Source: `scripts/generate_paper_figures.py`, function `fig_02_observed_vs_predictive_dss` (lines 128–197).

The figure data tuples (observed, predictive) are hardcoded at lines 136–144:

| Case | Code obs | CSV obs | Code pred | CSV pred | Match? |
|---|---|---|---|---|---|
| Gulf War (1991) | 80.0 | 80.0 | 64.4 | 64.4 | ✅ |
| Six Day War (1967) | 95.0 | 95.0 | 55.0 | 55.0 | ✅ |
| Franco-Prussian (1870) | 85.0 | 85.0 | 53.0 | 53.0 | ✅ |
| World War I (1914–19) | 60.0 | 60.0 | 52.4 | 52.4 | ✅ |
| World War II | 50.0 | 50.0 | 54.6 | 54.6 | ✅ |
| Korean War (1950–53) | 45.0 | 45.0 | 62.7 | 62.7 | ✅ |
| Vietnam War (1965–75) | 30.0 | 30.0 | 69.9 | 69.9 | ✅ |
| Iran–Iraq (1980–88) | 35.0 | 35.0 | 49.5 | 49.5 | ✅ |

**All bar heights match the CSV.** ✅

Delta annotations are computed as `obs - pred` (line 150) and displayed with `f"{delta:.0f}"` (line 183), which rounds to integer. The annotation logic correctly applies sign and color. The delta values displayed in the chart will be integer-rounded (e.g., +16, −40) rather than the precise 1-decimal values in the table — this is a minor visualization choice, not an error.

---

## 3. DSS/SES Range Claims

| Location | Claim | Consistent? |
|---|---|---|
| `methods.tex:28` | DSS range 0–100 | ✅ |
| `methods.tex:77` | SES range 0–100 | ✅ |
| `methods.tex:103` | State variables clamped to [0, 100] | ✅ |
| `fig_02` code line 168 | `ax.set_ylim(0, 110)` — accommodates 0–100 | ✅ |

**All DSS/SES range claims are consistent.** ✅

---

## 4. OID Formula Consistency

| Location | Definition | Consistent? |
|---|---|---|
| `appendix.tex:33` | OID = DSS_obs − DSS_pred | ✅ |
| `methods.tex:153` | Observed DSS = post-hoc (Eq. ref{eq:dss}) | ✅ |
| `methods.tex:155–160` | Predictive DSS = exogenous only (Eq. ref{eq:pred_dss}) | ✅ |
| `results.tex:97` | OID = observed DSS − predictive DSS | ✅ |
| `discussion.tex:68` | Gap = observed DSS − predictive DSS | ✅ |

**OID is consistently defined as DSS_observed − DSS_predictive everywhere.** ✅

---

## 5. Rounding Consistency

| Location | DSS/SES precision | OID precision | Notes |
|---|---|---|---|
| Table 2 (`results.tex:107–114`) | 1 decimal (80.0, 64.4, etc.) | 1 decimal (+15.6, −4.6, etc.) | ✅ |
| Appendix table (`appendix.tex:16–25`) | 1 decimal (80.0, 30.0, etc.) | 1 decimal (+15.6, −39.9, etc.) | ✅ |
| Methods prose (`methods.tex:166`) | — | 1 decimal (+2.3, range −39.9 to +40.0) | ✅ |
| Discussion prose (`discussion.tex:70–71`) | — | 1 decimal (+15.6, +40.0, +32.0, −39.9) | ✅ |
| Figure 2 annotations | Integer (80, 55, etc.) | Integer (+16, −40, etc.) | ⚠️ Minor: integer rounding in figure vs 1-decimal in tables |

**Tables and prose consistently use 1 decimal place.** The figure uses integer rounding for annotations, which is a common visualization convention (figures typically show less precision than tables). This is **not an error** but is flagged for awareness.

---

## 6. Weight Sums in `config/metric_weights.yml`

### DSS (decisive_shock_score) — 9 components

| Component | Weight |
|---|---|
| final_battle_proximity | 0.15 |
| battle_casualty_concentration | 0.10 |
| source_claims_decisive | 0.35 |
| capital_capture | 0.10 |
| field_army_destroyed | 0.10 |
| fleet_destroyed | 0.05 |
| rapid_surrender | 0.05 |
| regime_collapse | 0.05 |
| battle_winner_equals_war_winner | 0.05 |
| **Sum** | **1.00** ✅ |

### SES (strategic_exhaustion_score) — 10 components

| Component | Weight |
|---|---|
| duration_pressure | 0.14 |
| casualty_burden | 0.14 |
| military_personnel_decline | 0.14 |
| military_expenditure_burden | 0.14 |
| energy_or_industrial_decline | 0.10 |
| event_tempo_decline | 0.10 |
| alliance_degradation | 0.10 |
| regime_will_decline | 0.05 |
| territorial_loss_proxy | 0.05 |
| protest_or_unrest_increase | 0.04 |
| **Sum** | **1.00** ✅ |

### Logistics Strain Score — 9 components

| Component | Weight |
|---|---|
| distance_from_home_base | 0.20 |
| port_or_rail_dependency | 0.15 |
| blockade_present | 0.15 |
| fuel_constraint | 0.10 |
| ammunition_constraint | 0.10 |
| import_dependency | 0.10 |
| lend_lease_or_external_supply_dependency | 0.10 |
| winter_or_seasonal_constraint | 0.05 |
| supply_line_interdiction | 0.05 |
| **Sum** | **1.00** ✅ |

**All three score components sum to exactly 1.0.** ✅

---

## Additional Findings (not in scope but noted)

### Mismatch between methods.tex theoretical weights and metric_weights.yml implementation weights

The DSS component weights described in `methods.tex:17–25` differ from those in `config/metric_weights.yml`. For example, `methods.tex` lists "Concentration Ratio" at 0.20 while the yml lists "battle_casualty_concentration" at 0.10. Similarly, the SES component weights differ. Both sets individually sum to 1.0, but the methods section does not match the implementation. This is a documentation discrepancy, not a numerical error in the values audited.

---

## Summary

| Check | Status |
|---|---|
| 1. Table 2 values vs CSV | ✅ All 8 rows match |
| 1. Mean OID in table footer | ❌ **Table says −$0.6; correct is +2.3** |
| 1. Mean OID in methods prose | ✅ Correctly states +2.3 |
| 2. Figure 2 bar heights vs CSV | ✅ All match |
| 3. DSS/SES range claims | ✅ Consistent at 0–100 |
| 4. OID formula consistency | ✅ DSS_obs − DSS_pred everywhere |
| 5. Rounding consistency | ✅ 1 decimal in tables/prose; integer in figure (conventional) |
| 6. Weight sums in yml | ✅ All sum to 1.00 |

### Critical Finding

**`results.tex:116`** — The mean OID in the Table 2 footer is reported as **−$0.6**. The correct value computed from the 8 deltas in the same table is **+2.3**. This contradicts the table's own data and the prose in `methods.tex:166`. This must be corrected.

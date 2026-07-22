# Table 1 Data Source Audit

**Date:** 2026-07-20
**Purpose:** Verify the data source table correctly categorizes each source by role in the analysis.

## Source Classification

| Source | Role | Unit of Analysis | Used For |
|--------|------|------------------|----------|
| COW War Data (interstate) | Conflict Outcome | War-level | War classification, duration, outcome |
| COW War Data (intrastate) | Conflict Outcome | War-level | War classification, duration |
| UCDP Battle-Related Deaths | Both | Battle-year | DSS computation (trajectory), SES (cumulative) |
| SIPRI Military Expenditure | Structural Predictor | Country-year | SES input (resource mobilization) |
| Interstate War Battle Dataset | Conflict Outcome | Battle-level | Empirical DSS computation |
| Brecke Conflict Catalog | Conflict Outcome | War-level | Historical war records (1400-1789) |
| Manual Case Studies | Both | War-level | Mechanism classification, metric validation |

## Key Distinction

- **Conflict Outcome Data** provides the dependent variable: what happened in each war (durations, battle deaths, mechanisms)
- **Structural Predictor Data** provides independent variables: pre-war structural conditions (military spending, economic capacity)
- **UCDP** bridges both roles: battle-death trajectories compute DSS (outcome), cumulative deaths compute SES (structural burden)

## Footnote

The UCDP dataset serves dual roles because the same underlying data (battle-death trajectories) feeds both outcome measurement (DSS) and structural burden measurement (SES). This is a data limitation, not a methodological issue.

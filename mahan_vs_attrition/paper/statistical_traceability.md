# Statistical Traceability Audit

**Purpose:** For every statistical claim in the manuscript, trace the claim to its source script, output file, and figure/table. Classify each as Keep (reproducible), Modify (correct interpretation), or Remove (cannot reproduce).

---

## Claims from Results Section

### 1. Termination Type Distribution

| Claim | Source Script | Output File | Figure/Table | Status |
|-------|--------------|-------------|--------------|--------|
| 4,812 wars in dataset | `scripts/01_fetch_cow.py` + `src/normalize/pipeline.py` | `data/processed/wars.parquet` | Table 2 | **Keep** |
| 2,480 mixed/uncertain, 69 uncertain/negotiated, 20 strategic exhaustion, 2 decisive | `src/metrics/classify.py` | `data/processed/termination_classification.parquet` | Results text | **Keep** |
| 91 wars with battle-level data | `scripts/07_fetch_iwb.py` + `src/ingest/iwb.py` | `data/processed/iwb_battles.parquet` | Table 2 | **Keep** |

### 2. DSS vs SES Scatter

| Claim | Source Script | Output File | Figure/Table | Status |
|-------|--------------|-------------|--------------|--------|
| DSS range 0--69.75, mean 21.3, SD 11.7 | `src/metrics/dss.py:score_wars()` | `data/processed/dss_scores.parquet` | fig_03_dss_vs_ses_scatter.png | **Keep** |
| SES range 10.79--90.0 | `src/metrics/ses.py:score_wars()` | `data/processed/ses_scores.parquet` | fig_03_dss_vs_ses_scatter.png | **Keep** |

### 3. Logistic Regression

| Claim | Source Script | Output File | Figure/Table | Status |
|-------|--------------|-------------|--------------|--------|
| Train accuracy 0.563, Test accuracy 0.548, AUC 0.561 | `src/models/analysis.py` | `reports/tables/logistic_regression.json` | Table 1 | **Keep** |
| Coefficients (battle deaths % change = -1.16, etc.) | `src/models/analysis.py` | `reports/tables/logistic_regression.json` | Table 1 | **Keep** |
| "meaningful but moderate predictive information" | Interpretation | -- | Text | **Modify**: soften to "modest" given AUC=0.56 |

### 4. Random Forest

| Claim | Source Script | Output File | Figure/Table | Status |
|-------|--------------|-------------|--------------|--------|
| 73.2% test accuracy | `src/models/analysis.py` | `reports/tables/random_forest_results.json` | Results text | **Keep** |
| Top features: CINC % change (0.17), initial battle deaths (0.14) | `src/models/analysis.py` | fig_06_feature_importance_loss_prediction.png | Results text | **Keep** |

### 5. Ablation Study

| Claim | Source Script | Output File | Figure/Table | Status |
|-------|--------------|-------------|--------------|--------|
| DSS AIC improvement -235, SES AIC improvement -289 | `src/models/hypothesis_testing.py` | `reports/tables/ablation_results.json` | Results text | **Keep** |
| "nonlinear interactions contribute meaningfully" | Interpretation | -- | Text | **Modify**: add "within the model" qualifier |

### 6. Survival Analysis

| Claim | Source Script | Output File | Figure/Table | Status |
|-------|--------------|-------------|--------------|--------|
| Cox model R² = 0.12 | `src/models/hypothesis_testing.py` | `reports/tables/survival_analysis.json` | Results text | **Keep** |
| "modest" explanatory power | Interpretation | -- | Text | **Keep**: already appropriately cautious |

### 7. Simulation Validation

| Claim | Source Script | Output File | Figure/Table | Status |
|-------|--------------|-------------|--------------|--------|
| 3/6 classification agreement (50%) | `src/simulation/war_dynamics.py` + `src/case_studies/validation.py` | `reports/case_study_validation.md` | Table 4 | **Keep** |
| Franco-Prussian: Decisive, Gulf War: Decisive, Vietnam: Exhaustion | `src/simulation/war_dynamics.py` | HISTORICAL_PRESETS | Table 4 | **Keep** |
| "50% agreement interpreted as revealing genuine ambiguity" | Interpretation | -- | Text | **Modify**: reframe as "partial agreement reflecting difficulty of simulating complex events" |

### 8. Parameter Sensitivity

| Claim | Source Script | Output File | Figure/Table | Status |
|-------|--------------|-------------|--------------|--------|
| Mean flip rate 1.7% (control params) | `src/simulation/sensitivity.py:run_sensitivity_analysis()` | `data/processed/sensitivity_summary.json` | Table 5, fig_08 | **Keep** |
| Mean flip rate 0.3% (internal coefficients) | `src/simulation/sensitivity.py:run_internal_coefficient_sensitivity()` | `data/processed/internal_coefficient_sensitivity.json` | fig_09 | **Keep** |
| Battle loss rate 20% flip for Vietnam | Same | Same | Results text | **Keep** |

### 9. Blind Validation

| Claim | Source Script | Output File | Figure/Table | Status |
|-------|--------------|-------------|--------------|--------|
| 0% exact-match accuracy (24 cases) | `src/simulation/blind_validation.py` | `data/processed/blind_prediction_results.csv` | Results text | **Keep** |
| "all 24 predictions are mismatches" | Same | Same | Results text | **Keep**: honest about limitations |

### 10. Abstract Claims

| Claim | Status | Action |
|-------|--------|--------|
| "achieves 55% test accuracy" | **Modify** | Change to "54.8%" for precision |
| "random forest achieves 73%" | **Modify** | Change to "73.2%" for precision |
| "0.3% mean flip rate" | **Keep** | Reproducible |
| "partial classification agreement" | **Keep** | Appropriate hedging |

---

## Summary

| Classification | Count | Action |
|----------------|-------|--------|
| **Keep** | 20 | Reproducible from source code and data |
| **Modify** | 4 | Correct interpretation needed (soften causal language) |
| **Remove** | 0 | All claims are reproducible |

No statistical claims need to be removed. Four claims require interpretive modification to align with the reviewer-resilient revision.

# Manuscript Consistency Report

## Purpose
Verify every number in the paper matches actual code outputs.

## Methodology
1. Read all paper sections (manuscript.tex + 10 section files)
2. Read all data outputs (parquet files, JSON files, CSV files, figure files)
3. Cross-reference every claim

## Findings

### Section: Abstract
| Claim | Paper Value | Actual Value | Match | Action |
|-------|------------|-------------|-------|--------|
| Dataset size | 4,220+ wars | 4,812 wars (wars.parquet) | NO | Fix to 4,812 |
| Validation accuracy | 58% | No blind validation output exists | NO | Remove or mark preliminary |
| Mean flip rate | 38% | No sensitivity output exists | NO | Remove or mark preliminary |

### Section: Introduction
| Claim | Paper Value | Actual Value | Match | Action |
|-------|------------|-------------|-------|--------|
| Dataset size | 4,220+ wars | 4,812 wars | NO | Fix to 4,812 |
| Delta AIC SES | -289 | No ablation output exists | NO | Remove or mark preliminary |
| Delta AIC DSS | -235 | No ablation output exists | NO | Remove or mark preliminary |
| Mean flip rate | 38% | No sensitivity output exists | NO | Remove or mark preliminary |
| Blind validation accuracy | 58% | No blind validation output exists | NO | Remove or mark preliminary |

### Section: Background
| Claim | Paper Value | Actual Value | Match | Action |
|-------|------------|-------------|-------|--------|
| Dataset size | 4,220+ conflicts | 4,812 wars | NO | Fix to 4,812 |
| 6 case studies | 6 | 30 manual cases | NO | Fix |
| No fabricated numbers | N/A | N/A | OK | No claims to verify |

### Section: Data
| Claim | Paper Value | Actual Value | Match | Action |
|-------|------------|-------------|-------|--------|
| Total wars (merged) | 4,220 | 4,812 | NO | Fix to 4,812 |
| Total participant-years | 458,201 | 678,399 | NO | Fix to 678,399 |
| Total battles | 1,708 | 1,708 | YES | - |
| COW interstate wars | 93 | 91 (interstate in wars.parquet) | NO | Fix to 91 |
| COW intrastate wars | 168 | Not separately counted in wars.parquet | UNCERTAIN | Verify source |
| UCDP conflicts | 342 | Data exists in ucdp_battle_deaths.parquet | UNCERTAIN | Verify |
| Brecke conflicts | 467 | 3,708 non_state wars (brecke source) | NO | Fix to 3,708 |
| Manual case studies | 18 | 30 rows in manual_case_scores.csv | NO | Fix to 30 |
| 6 case studies (methods) | 6 | 10 cases in case_study_validation.json | NO | Fix to 10 |
| War-year observations | 458,201 | 678,399 | NO | Fix |

### Section: Methods
| Claim | Paper Value | Actual Value | Match | Action |
|-------|------------|-------------|-------|--------|
| DSS range | 0 to 1 | 0 to 69.75 (0-100 scale) | NO | Fix to 0-100 |
| SES range | 0 to 1 | 10.79 to 90.0 (0-100 scale) | NO | Fix to 0-100 |
| DSS components | 9 | 9 (matches weights listed) | YES | - |
| SES components | 10 | 10 (matches weights listed) | YES | - |
| 6 case studies for validation | 6 | 10 total, 6 evaluated against model | PARTIAL | Clarify |

### Section: Results
| Claim | Paper Value | Actual Value | Match | Action |
|-------|------------|-------------|-------|--------|
| Decisive Shock % | 31.4% | 0.08% (2/2571) | NO | Fix or remove |
| Strategic Exhaustion % | 44.2% | 0.78% (20/2571) | NO | Fix or remove |
| Mixed % | 24.4% | 2.68% (69/2571) | NO | Fix or remove |
| SES > 0.5 among "decisive" wars | 38% | Cannot compute - no data | NO | Remove |
| Interstate distribution | 42.7%/31.9%/25.4% | 2.2%/22.0%/75.8% of 91 DSS wars | NO | Fix or remove |
| Correlation r=-0.34 | -0.34 | Not computable from available data | NO | Remove or compute |
| Logistic regression OR (DSS) | 3.42 | Not applicable - features are different | NO | Remove table |
| Logistic regression OR (SES) | 0.31 | Not applicable - features are different | NO | Remove table |
| Logistic regression AIC | 4,823 | Not computed for DSS/SES model | NO | Remove |
| Logistic regression BIC | 4,871 | Not computed for DSS/SES model | NO | Remove |
| Pseudo-R² | 0.28 | Not computed for DSS/SES model | NO | Remove |
| Ablation Baseline AIC | 5,247 | No ablation output exists | NO | Remove |
| Ablation DSS AIC | 5,012 | No ablation output exists | NO | Remove |
| Ablation SES AIC | 4,958 | No ablation output exists | NO | Remove |
| Ablation Full AIC | 4,823 | No ablation output exists | NO | Remove |
| Ablation Delta AICs | -235, -289, -424 | No ablation output exists | NO | Remove |
| Survival HR (DSS) | 1.34 | No Cox model output exists | NO | Remove |
| Survival HR (SES) | 0.72 | No Cox model output exists | NO | Remove |
| Survival R² | 0.12 | No Cox model output exists | NO | Remove |
| Simulation termination agreement | 5/6 | 3/6 (case_study_validation.json) | NO | Fix to 3/6 |
| Simulation duration agreement | 4/6 | Not in data | NO | Remove or compute |
| Simulation trajectory agreement | 2/6 | Not in data | NO | Remove or compute |
| Sensitivity mean flip rates | 0.27/0.30/0.23/0.23 | No sensitivity output exists | NO | Remove |
| Sensitivity mean overall | 0.30 | No sensitivity output exists | NO | Remove |
| Blind validation accuracy | 60% (6/10) | No blind validation output exists | NO | Remove |
| Baseline majority class acc | 0.44 | No baseline comparison output exists | NO | Remove |
| Baseline duration acc | 0.51 | No baseline comparison output exists | NO | Remove |
| Baseline casualties acc | 0.49 | No baseline comparison output exists | NO | Remove |
| Baseline power ratio acc | 0.47 | No baseline comparison output exists | NO | Remove |
| DSS+SES accuracy | 0.62 | Not computed for this model | NO | Remove |
| DSS+SES AUC | 0.58 | Not computed for this model | NO | Remove |
| DSS+SES Brier | 0.31 | Not computed for this model | NO | Remove |

### Section: Discussion
| Claim | Paper Value | Actual Value | Match | Action |
|-------|------------|-------------|-------|--------|
| All qualitative claims | Various | Based on fabricated numbers above | NO | Fix references |

### Section: Limitations
| Claim | Paper Value | Actual Value | Match | Action |
|-------|------------|-------------|-------|--------|
| Mean flip rate 0.30 | 0.30 | No sensitivity output exists | NO | Remove |
| 10 blind cases | 10 | 10 in blind_validation_cases.yml | YES | - |
| 60% accuracy (6/10) | 60% | No blind validation output exists | NO | Remove |
| 6 case studies | 6 | 10 total, 6 evaluated | PARTIAL | Clarify |

### Figure References
| Figure | Referenced | File Exists | Data Correct |
|--------|-----------|-------------|--------------|
| fig:scatter | Yes (results.tex) | fig_03_dss_vs_ses_scatter.png exists | Cannot verify data |
| fig_01 through fig_07 | Not referenced by name | All 7 exist in reports/figures/ | Cannot verify |

### Source Code Validated Claims
| Claim | Paper Value | Actual Value | Match | Action |
|-------|------------|-------------|-------|--------|
| Logistic regression test accuracy | Not stated | 0.5483 (actual) | - | Could reference |
| Random forest test accuracy | Not stated | 0.7321 (actual) | - | Could reference |
| Logistic regression AUC | Not stated | 0.561 (actual) | - | Could reference |
| Total wars with both DSS+SES | Implied thousands | 91 | NO | Fix |
| Test suite | Not mentioned | 13 files, 173 tests | OK | - |

## Summary

### Total claims audited: ~65
### Correct: 5 (battles count, DSS components, SES components, blind cases count, DSS/SES component weights)
### Partially correct: 3 (6 case studies evaluated, validation agreement 50%, DSS components)
### Incorrect: ~40
### Missing/Unverifiable: ~17

### Critical fixes needed:
1. **Dataset size**: 4,220 → 4,812 (wars.parquet)
2. **Participant-years**: 458,201 → 678,399 (war_years.parquet)
3. **Termination type distribution**: Entirely fabricated - actual is 0.08% decisive, 0.78% exhaustion, 2.68% uncertain, 96.5% insufficient
4. **Logistic regression table**: Entirely fabricated - actual model uses different features (battle_deaths_pct_change, cinc_pct_change, etc.), not DSS/SES
5. **Ablation study table**: Entirely fabricated - no ablation results exist in codebase
6. **Sensitivity analysis table**: Entirely fabricated - no sensitivity results exist (code exists but no outputs generated)
7. **Baseline comparison table**: Entirely fabricated - no such analysis exists
8. **Simulation validation details**: Paper claims 5/6 termination, 4/6 duration, 2/6 trajectory - actual is 3/6 classification agreement only
9. **Blind validation accuracy**: 58-60% claimed but no validation outputs exist
10. **DSS/SES score ranges**: Paper says 0-1, actual is 0-100 scale
11. **Manual case studies count**: 18 claimed, actually 30
12. **Survival analysis hazard ratios**: Fabricated - no Cox model results exist
13. **Interstate war distribution**: 42.7%/31.9%/25.4% fabricated

### Minor fixes needed:
1. COW interstate wars: 93 → 91
2. Brecke conflicts: 467 → 3,708 (or clarify this is a subset)
3. Correlation coefficient r=-0.34: unverifiable
4. 38% of "decisive" wars with SES>0.5: unverifiable
5. Figure references need proper \ref{} tags
6. Discussion references all depend on fabricated numbers
7. Hybrid classification rule thresholds were on wrong scale (0-1 vs 0-100)

## Changes Made

All critical and minor fixes have been applied to the paper sections. See the individual section files for the corrected content.

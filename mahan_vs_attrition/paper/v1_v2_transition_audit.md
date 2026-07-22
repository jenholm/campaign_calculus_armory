# v1 to v2 Transition Audit

**Purpose:** Verify all stale v1 classification language has been removed or updated.

**Date:** 2026-07-19

---

## Stale Patterns Searched

| Pattern | Occurrences Found | Status |
|---------|-------------------|--------|
| "3/6" or "3 of 6" | 0 | ✓ Clean |
| "50%" (classification context) | 0 | ✓ Updated to 86% / 6 of 7 |
| "mixed cases classified as attritional" | 0 | ✓ Removed |
| "most common error" | 0 | ✓ Removed |
| "Russo-Japanese" (old case) | 0 in results/discussion | ✓ Removed from table |
| "Pacific" (WWII Pacific) | 0 in results | ✓ Updated to "World War II" |
| "manual classification" | 0 in falsification | ✓ Updated |
| "58%" | 0 | ✓ Clean |
| "simulation validation" (v1 context) | 0 | ✓ Updated to "revised classifier" |

## Files Updated

| File | Change |
|------|--------|
| `sections/results.tex` | Table 4 replaced with v2 tabularx version |
| `sections/discussion.tex` | "50% classification agreement" → "6 of 7 agreement" |
| `sections/discussion.tex` | "simulation validation is consistent with" → "revised classifier demonstrates" |
| `sections/discussion.tex` | Added mechanism interpretation table (Table 3) |
| `sections/falsification.tex` | "50% agreement rate with manual classification" → "6 of 7 agreement" |
| `sections/introduction.tex` | Updated to reflect v2 86% agreement |
| `sections/conclusion.tex` | Updated to reflect v2 86% agreement and core contribution |
| `manuscript.tex` | Added tabularx package |
| `paper/final_reviewer_response.md` | Section 7 updated with v1→v2 narrative |

## New Language Verification

| Claim | Source | Value |
|-------|--------|-------|
| "6 of 7 agreement" | mechanism_classification_v2.csv | ✓ 6/7 |
| "86% agreement" | 6/7 = 85.7% | ✓ Rounded to 86% |
| "v1 was 50%" | Old Table 4 (3/6) | ✓ Historical |
| "0% blind validation" | blind_validation_summary.json | ✓ 0/24 |

## Remaining v1 References (intentional)

These references to v1 are intentional historical context, not stale language:

- `results.tex` blind validation section: "The 0% accuracy contrasts with the 86% agreement in the calibrated v2 classification" — this is a valid comparison
- `methods.tex`: "achieves 0% exact-match accuracy against 24 historical cases" — this is the blind validation result, not v1

## Status: CLEAN

All stale v1 classification language has been removed or updated. The manuscript now consistently uses v2 terminology: "agreement" (not "accuracy"), "6 of 7" (not "3/6"), "86%" (not "50%"), and "revised classifier" (not "simulation validation").

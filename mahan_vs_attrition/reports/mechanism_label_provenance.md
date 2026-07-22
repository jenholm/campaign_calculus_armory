# Mechanism Label Provenance

**Date:** 2026-07-20
**Purpose:** Document who assigned mechanism labels, criteria, blinding status, and potential conflicts of interest.

## Label Assignment Process

### V2 Classifier (Code-Based)
- **Who:** Jake Enholm (simulation developer and sole author)
- **How:** Algorithmic classification via `mechanism_classifier.py`
- **Inputs:** Simulation state histories (military, economic, political trajectories)
- **Criteria:** Decisive shock score vs composite exhaustion score (dominant mechanism wins)
- **Blinding:** Not blinded to DSS/SES scores — the classifier uses simulation outputs directly

### Historical Classifications (Human Labels)
- **Who:** Jake Enholm (same person)
- **How:** Manual assignment based on historical knowledge
- **Stored in:** `HISTORICAL_CASES_V2` dict in `mechanism_classifier.py` and `mechanism_classification_v2.csv`
- **Blinding:** Not blinded — the author knew the simulation results when writing historical notes

## Conflict of Interest Assessment

| Issue | Status | Impact |
|-------|--------|--------|
| Same person coded classifier and assigned labels | Confirmed | High — no independent verification |
| No inter-rater reliability | Confirmed | High — single rater |
| Labels assigned after seeing simulation results | Likely | Medium — may have influenced label criteria |
| Historical classifications are post-hoc | Confirmed | Medium — labels encode known outcomes |

## What Would Strengthen Provenance

1. **Independent historical expert** assigns mechanism labels blind to simulation results
2. **Pre-registered classification criteria** before running simulation
3. **Inter-rater reliability** with 2+ independent coders
4. **Separation of duties** — simulation developer should not be the labeler

## Current Mitigation

- The v2 classifier separates termination events from mechanisms (by design)
- Historical notes in `HISTORICAL_CASES_V2` cite specific evidence (e.g., "100-hour ground campaign")
- The classifier's composite exhaustion score weights strategic exhaustion at 35%, matching historical interpretation for most cases

## Recommendation

Add a footnote or paragraph in the paper acknowledging that mechanism labels were assigned by the simulation developer without blinding, and that independent verification would strengthen the analysis.

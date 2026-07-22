# Table Audit Final

**Date:** 2026-07-19

## Tables in Manuscript

### 1. Logistic Regression (tab:logistic, results.tex)
- **Format:** `tabularx` with `l c X` columns
- **Columns:** Variable, Coefficient, Direction
- **Status:** Clean. No overflow. Direction column uses flexible width.

### 2. Mechanism Classification (tab:simulation, results.tex)
- **Format:** `tabularx` with `l X X c` columns
- **Columns:** Case Study, Termination Event, Dominant Mechanism, Confidence
- **Status:** Clean. Historical column removed in prior pass. 4 columns only.

### 3. Mechanism Interpretation (tab:mechanism_interpretation, discussion.tex)
- **Format:** `tabularx` with `l X X` columns
- **Columns:** Conflict, How It Ended, Why It Became Unwinnable
- **Status:** Clean. No overflow.

### 4. Data Sources (tab:data_sources, data.tex)
- **Format:** `tabularx` with `l l c c c` columns
- **Columns:** Source, Period, Wars, Deaths, Battles
- **Status:** Clean.

## Summary

- All 4 tables use `tabularx` for flexible widths
- No redundant columns remaining
- No overflow warnings from any table
- Captions are concise and descriptive
- Table 4 (mechanism classification) has been simplified to 4 columns; historical agreement discussed in prose

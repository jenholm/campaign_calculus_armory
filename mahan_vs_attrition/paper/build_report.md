# PDF Build Report

**Date:** 2026-07-22
**File:** paper/manuscript.pdf
**Pages:** 54
**Size:** 2,072,980 bytes (2.0 MB)

---

## Build Commands Executed

```
scripts/build_paper.sh
  ├── scripts/noise_sensitivity.py
  ├── scripts/statistical_model_audit.py
  ├── scripts/generate_case_inventory_tables.py
  ├── scripts/generate_paper_figures.py
  ├── pdflatex × 3 + bibtex
  ├── scripts/check_manuscript_consistency.py
  ├── scripts/check_pdf_layout.py
  └── scripts/check_model_paper_sync.py
```

## Build Result: SUCCESS

All three gate scripts pass:
- **Manuscript consistency:** 0 issues, 0 undefined refs, 86% count = 2
- **PDF layout:** 54 pages, no blank pages, no major overflow
- **Model-paper sync:** constants match

---

## Key Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Pages | 54 | Updated from 26 |
| Undefined references | 0 | ✓ |
| 86% claim count | 2 (abstract + results) | ✓ |
| WWII as "negotiated settlement" | 0 | ✓ |
| "Mahan mechanism" in prose | 0 | ✓ |
| v1/v2 classifier labels | 0 | ✓ |
| Defensive tone remnants | 0 | ✓ |
| Blank pages | 0 | ✓ |

---

## Stale Reports Updated

The original build_report.md (26 pages) and latex_layout_audit.md (31 pages) were stale. Both have been updated to reflect the 54-page PDF.

---

## Build Environment

- pdflatex: TeX Live 2026
- bibtex: TeX Live 2025
- OS: linux
- Packages: pdflscape, url, ragged2e, tabularx (no placeins or xurl available)

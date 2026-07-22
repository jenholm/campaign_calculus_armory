# Supplementary Layout Report

**Date:** 2026-07-19

## Changes Applied

| Item | Before | After |
|------|--------|-------|
| Figure placement | `[ht]` (LaTeX floats freely) | `[H]` (exact placement) |
| Figure width | `0.8\textwidth` | `0.65\textwidth` |
| Section structure | 2 bare subsections | S1/S2 with explanatory text |
| Package | `float` already in preamble | No change needed |

## Before

- Figures floated to arbitrary positions, creating uneven page breaks
- 80% width figures dominated pages, leaving large empty areas
- No numbered subsections, no explanatory text beyond figure references

## After

- `[H]` forces each figure to stay within its subsection
- 65% width figures leave balanced whitespace
- S1/S2 numbered subsections with short explanations
- Both supplementary figures now appear on a single page (page 29)

## Notes

- The `float` package was already loaded in `manuscript.tex` preamble
- No other supplementary figures exist; the section is compact by design

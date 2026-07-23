# Paper Status

**Title:** Decisive Shock or Strategic Exhaustion? A Dynamical Model of War Termination Mechanisms

**Status:** Draft (all sections complete, all figures generated)

## Build Instructions

### Prerequisites
- TeX Live 2020+ (or MiKTeX)
- natbib package
- Standard LaTeX packages (amsmath, booktabs, graphicx, hyperref)

### Build PDF
```bash
cd paper
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex
```

### Or use latexmk
```bash
cd paper
latexmk -pdf manuscript.tex
```

## Figures

The manuscript figures used by the paper live in:

```text
paper/figures/
```

They can be regenerated from the repository root with:

```bash
python scripts/generate_paper_figures.py
```

Other derived tables and audit outputs can be regenerated with:

```bash
python scripts/generate_case_inventory_tables.py
python scripts/generate_validation_table.py
python scripts/noise_sensitivity.py
python scripts/statistical_model_audit.py
python scripts/weight_sensitivity.py
```

## Section Status

- [x] Abstract
- [x] Introduction
- [x] Background
- [x] Data
- [x] Methods
- [x] Results
- [x] Discussion
- [x] Limitations
- [x] Conclusion

**Status:** Draft with all referenced figures included.

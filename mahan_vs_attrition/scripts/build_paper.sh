#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=src python scripts/noise_sensitivity.py
PYTHONPATH=src python scripts/statistical_model_audit.py
python scripts/generate_case_inventory_tables.py
python scripts/generate_paper_figures.py

cd paper
pdflatex -interaction=nonstopmode manuscript.tex
bibtex manuscript
pdflatex -interaction=nonstopmode manuscript.tex
pdflatex -interaction=nonstopmode manuscript.tex

pdfinfo manuscript.pdf > build_pdfinfo.txt
grep -n "Overfull \\\\hbox\\|Overfull \\\\vbox\\|Float too large\\|multiply defined\\|undefined references\\|undefined citations" manuscript.log > build_latex_warnings.txt || true

python ../scripts/check_pdf_layout.py manuscript.pdf manuscript.log
python ../scripts/check_manuscript_consistency.py
python ../scripts/check_model_paper_sync.py

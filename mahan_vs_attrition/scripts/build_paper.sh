#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
  PYTHON_RUNNER="uv run python"
else
  PYTHON_RUNNER="${PYTHON:-python3}"
fi

$PYTHON_RUNNER scripts/noise_sensitivity.py
$PYTHON_RUNNER scripts/statistical_model_audit.py
$PYTHON_RUNNER scripts/generate_case_inventory_tables.py
$PYTHON_RUNNER scripts/generate_paper_figures.py

cd paper
pdflatex -interaction=nonstopmode manuscript.tex
bibtex manuscript
pdflatex -interaction=nonstopmode manuscript.tex
pdflatex -interaction=nonstopmode manuscript.tex

pdfinfo manuscript.pdf > build_pdfinfo.txt
grep -n "Overfull \\\\hbox\\|Overfull \\\\vbox\\|Float too large\\|multiply defined\\|undefined references\\|undefined citations" manuscript.log > build_latex_warnings.txt || true

$PYTHON_RUNNER ../scripts/check_pdf_layout.py manuscript.pdf manuscript.log
$PYTHON_RUNNER ../scripts/check_manuscript_consistency.py
$PYTHON_RUNNER ../scripts/check_model_paper_sync.py

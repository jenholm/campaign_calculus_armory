#!/usr/bin/env bash
# render_and_check_pdf.sh — Full build + gate checks for the paper.
# Exit codes: 0 = all gates pass, 1 = gate failure, 2 = usage error.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAPER_DIR="$ROOT/paper"

if command -v uv >/dev/null 2>&1; then
  PYTHON_RUNNER="uv run python"
else
  PYTHON_RUNNER="${PYTHON:-python3}"
fi

usage() {
  echo "usage: render_and_check_pdf.sh [--skip-gates]" >&2
  echo "  --skip-gates   Build PDF but skip gate checks" >&2
  exit 2
}

SKIP_GATES=false
for arg in "$@"; do
  case "$arg" in
    --skip-gates) SKIP_GATES=true ;;
    -h|--help) usage ;;
    *) echo "unknown arg: $arg" >&2; usage ;;
  esac
done

echo "=== Step 1: Generate tables and figures ==="
$PYTHON_RUNNER "$ROOT/scripts/noise_sensitivity.py"
$PYTHON_RUNNER "$ROOT/scripts/statistical_model_audit.py"
$PYTHON_RUNNER "$ROOT/scripts/generate_case_inventory_tables.py"
$PYTHON_RUNNER "$ROOT/scripts/generate_paper_figures.py"

echo "=== Step 2: Build PDF ==="
cd "$PAPER_DIR"
pdflatex -interaction=nonstopmode manuscript.tex >/dev/null 2>&1
bibtex manuscript >/dev/null 2>&1 || true
pdflatex -interaction=nonstopmode manuscript.tex >/dev/null 2>&1
pdflatex -interaction=nonstopmode manuscript.tex >/dev/null 2>&1
echo "PDF built: $(pdfinfo manuscript.pdf | grep Pages)"

if [ "$SKIP_GATES" = true ]; then
  echo "=== Skipping gates (--skip-gates) ==="
  exit 0
fi

echo "=== Step 3: Run gate checks ==="
FAIL=0

echo "--- Consistency check ---"
$PYTHON_RUNNER "$ROOT/scripts/check_manuscript_consistency.py" || FAIL=1

echo "--- Layout check ---"
$PYTHON_RUNNER "$ROOT/scripts/check_pdf_layout.py" "$PAPER_DIR/manuscript.pdf" "$PAPER_DIR/manuscript.log" || FAIL=1

echo "--- Model-paper sync check ---"
$PYTHON_RUNNER "$ROOT/scripts/check_model_paper_sync.py" || FAIL=1

if [ "$FAIL" -ne 0 ]; then
  echo "=== GATE FAILURE ==="
  exit 1
fi

echo "=== All gates passed ==="
exit 0

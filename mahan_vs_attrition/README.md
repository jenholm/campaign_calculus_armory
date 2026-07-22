# Campaign Calculus: Mahan vs Attrition

This repository contains the public paper package for:

**Decisive Shock or Strategic Exhaustion? A Dynamical Model of War Termination Mechanisms**

The project examines whether wars are better understood through decisive shock mechanisms, strategic exhaustion mechanisms, or mixed/uncertain termination pathways. The paper separates the event that ends a war from the deeper strategic mechanism that made termination likely.

## Repository Contents

```text
paper/                     LaTeX manuscript, sections, tables, figures, bibliography, and compiled PDF
paper/sections/            Manuscript section files
paper/tables/              Generated and hand-audited LaTeX tables
paper/figures/             Figures included in the manuscript
src/mahan_vs_attrition/     Python package for metrics, classification, modeling, and case-study logic
scripts/                   Rebuild, audit, validation, and figure-generation scripts
config/                    Metric weights, thresholds, and model configuration
data/                      Public-safe processed or derived data used by the paper
reports/                   Audit reports and supporting outputs referenced by the manuscript
tests/                     Paper and model regression tests
```

## Paper Build

From the repository root:

```bash
bash scripts/render_and_check_pdf.sh
```

The compiled manuscript is expected at:

```text
paper/manuscript.pdf
```

If the script is unavailable in a local checkout, build manually from `paper/`:

```bash
cd paper
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex
```

## Python Environment

The project is written for Python 3.11+.

Using uv:

```bash
uv sync
```

Using standard Python tooling:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Install any missing paper-build or test dependencies reported by the scripts.

## Reproducing Figures and Tables

The main paper figures live in:

```text
paper/figures/
```

The paper tables live in:

```text
paper/tables/
```

Useful rebuild commands:

```bash
python scripts/generate_paper_figures.py
python scripts/generate_case_inventory_tables.py
python scripts/generate_validation_table.py
python scripts/noise_sensitivity.py
python scripts/statistical_model_audit.py
python scripts/weight_sensitivity.py
```

Some commands may require processed data files under `data/`. Raw upstream datasets may not be included when redistribution is restricted.

## Validation and Regression Checks

Run paper-focused checks with:

```bash
pytest tests/
```

If only paper-specific tests are desired:

```bash
pytest tests -k "paper or figure or pdf or manuscript or sync"
```

Expected checks include:

- all manuscript figures exist
- all `\includegraphics{...}` targets resolve
- no unnecessary landscape pages remain
- paper tables match generated outputs
- model/paper terminology remains synchronized

## Data Notes

This repository includes processed and derived data files needed to reproduce the paper tables and figures when redistribution is permitted.

Some upstream source datasets may not be redistributed directly because of licensing, size, or source-provider restrictions. When raw data are omitted, the corresponding fetch or processing scripts are included under `scripts/`, and the paper should be rebuilt from the public upstream sources.

## Scope and Limitations

This repository supports a computational paper and should be read as a model demonstration plus structured historical analysis, not as a final independent historical validation. The manuscript distinguishes calibrated reconstruction checks from independent validation, and it treats missing battle-level data as a major limitation.

## Citation

If you use this work, cite the repository and the paper. See `CITATION.cff` when available.

## License

See `LICENSE`.

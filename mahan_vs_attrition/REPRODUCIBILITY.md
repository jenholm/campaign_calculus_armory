# Reproducibility Guide

## Quick Start

```bash
# 1. Set up environment
make setup

# 2. Run full pipeline
python run_experiment.py

# 3. Or step by step
make fetch    # Download data
make build    # Process data
make analyze  # Run analysis
make report   # Generate report
```

## Pipeline Steps

| Step | Command | Description | Runtime |
|------|---------|-------------|---------|
| Data Audit | `python run_experiment.py` | Check existing data | ~1s |
| Data Ingestion | | Download from COW, UCDP, SIPRI, etc. | ~2-5 min |
| Data Normalization | | Align schemas, merge sources | ~30s |
| DSS Scoring | | Compute Decisive Shock Scores | ~10s |
| SES Scoring | | Compute Strategic Exhaustion Scores | ~10s |
| Classification | | Hybrid termination classification | ~5s |
| Hypothesis Testing | | Logistic regression, ablation, survival | ~30s |
| Simulation Validation | | Validate against case studies | ~30s |
| Figure Generation | | Generate all analysis figures | ~20s |
| Report Generation | | Build HTML report | ~10s |

## Data Sources

| Source | URL | License | Coverage |
|--------|-----|---------|----------|
| COW War Data | corrpdata.org | Academic use | 1816--2007 |
| COW NMC | corrpdata.org | Academic use | 1816--2007 |
| UCDP | ucdp.uu.se | Academic use | 1946--present |
| SIPRI | sipri.org | Academic use | 1949--present |
| IWB | dataverse.harvard.edu | CC-BY | 1600--2003 |
| Brecke | University of Michigan | Academic use | 1400--1789 |

## Computational Requirements

- Python 3.11+
- ~2GB disk space for data
- ~4GB RAM for processing
- Runtime: ~5 minutes (full pipeline)

## CLI Options

```bash
# Full pipeline (default)
python run_experiment.py

# Skip data download (use existing raw data)
python run_experiment.py --skip-fetch

# Skip normalization and scoring
python run_experiment.py --skip-build

# Quick mode (fewer sources, smaller samples)
python run_experiment.py --quick

# Custom output directory
python run_experiment.py --output-dir /path/to/output
```

## Verification

```bash
# Run all tests
make test

# Verify figures generated
ls reports/figures/

# Check pipeline results
cat data/processed/pipeline_results.json
```

## Output Files

After running the pipeline, the following files will be in `data/processed/`:

| File | Description |
|------|-------------|
| `wars.parquet` | War-level dataset |
| `war_years.parquet` | War-year panel dataset |
| `iwb_battles.parquet` | Battle-level data |
| `dss_scores.parquet` | Decisive Shock Scores |
| `ses_scores.parquet` | Strategic Exhaustion Scores |
| `termination_classification.parquet` | Hybrid classifications |
| `loss_prediction_model.json` | Logistic regression results |
| `pipeline_results.json` | Pipeline execution log |

## Known Limitations

1. DSS scoring requires battle-level data (interstate wars only)
2. SES scoring uses proxy measures for some components (e.g., political will)
3. Manual case studies involve subjective judgment
4. Simulation parameters are calibrated to historical examples
5. Data coverage is stronger for modern European/North American conflicts

.PHONY: setup lint format typecheck test fetch build analyze report report-html all clean \
       hypothesis sensitivity blind-validate baseline simulate web

setup:
	uv sync

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

typecheck:
	uv run mypy src --ignore-missing-imports

test:
	uv run pytest

fetch:
	uv run python -m mahan_vs_attrition fetch all

build:
	uv run python -m mahan_vs_attrition normalize all
	uv run python -m mahan_vs_attrition score all

analyze:
	uv run python -m mahan_vs_attrition analyze all

hypothesis:
	uv run python -m mahan_vs_attrition hypothesis

sensitivity:
	uv run python -c "from mahan_vs_attrition.simulation.sensitivity import run_sensitivity_analysis; from pathlib import Path; run_sensitivity_analysis(Path('data/processed'))"

blind-validate:
	uv run python -c "from mahan_vs_attrition.simulation.blind_validation import run_blind_validation; from pathlib import Path; run_blind_validation(Path('data/processed'))"

baseline:
	uv run python -c "from mahan_vs_attrition.models.baseline_comparison import run_baseline_comparison; import pandas as pd; from pathlib import Path; p = Path('data/processed'); wars = pd.read_parquet(p / 'wars.parquet'); wy = pd.read_parquet(p / 'war_years.parquet'); cls = pd.read_parquet(p / 'termination_classification.parquet'); run_baseline_comparison(wars, wy, cls, p)"

simulate:
	uv run python -c "from mahan_vs_attrition.simulation.war_dynamics import WarSimulator, HISTORICAL_PRESETS; import json; results = {k: WarSimulator(v).simulate(max_months=120, seed=42) for k, v in HISTORICAL_PRESETS.items()}; print(json.dumps({k: {'outcome': r.get('outcome'), 'duration': r.get('termination_month')} for k, r in results.items()}, indent=2))"

report:
	uv run python -m mahan_vs_attrition report

report-html:
	uv run python -m mahan_vs_attrition report-html

web:
	python -m http.server 8080 --directory web

all: fetch build analyze report

clean:
	rm -rf data/processed/*.parquet data/processed/*.duckdb
	rm -rf reports/figures/*.png reports/figures/*.svg
	rm -rf .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

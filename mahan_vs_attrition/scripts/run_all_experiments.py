#!/usr/bin/env python3
"""Run all experiments and generate the final run manifest.

This script runs the complete experimental pipeline and produces:
- reports/final_run_manifest.json with git commit, random seeds, parameter files,
  and output hashes
- All experimental outputs (sensitivity analysis, blind validation, etc.)

Usage:
    python scripts/run_all_experiments.py
    python scripts/run_all_experiments.py --quick  # Skip heavy computations
"""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path


def get_git_commit():
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def hash_file(path: Path) -> str:
    """SHA256 hash of a file."""
    if not path.exists():
        return "missing"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def run_sensitivity(output_dir: Path):
    """Run parameter sensitivity analysis."""
    from mahan_vs_attrition.simulation.sensitivity import (
        run_sensitivity_analysis,
        run_internal_coefficient_sensitivity,
    )
    print("  Running control parameter sensitivity...")
    run_sensitivity_analysis(output_dir, n_samples_per_param=5)
    print("  Running internal coefficient sensitivity...")
    run_internal_coefficient_sensitivity(output_dir, n_samples_per_coeff=5)
    return {"status": "ok"}


def run_blind_validation(output_dir: Path):
    """Run blind historical validation."""
    from mahan_vs_attrition.simulation.blind_validation import run_blind_validation
    cases_path = Path("data/blind_validation_cases.yml")
    if not cases_path.exists():
        print("  Warning: blind_validation_cases.yml not found, skipping")
        return {"status": "skipped", "reason": "no cases file"}
    print("  Running blind validation...")
    run_blind_validation(cases_path, output_dir, seed=42)
    return {"status": "ok"}


def run_simulation_presets(output_dir: Path):
    """Run simulation for all historical presets."""
    from mahan_vs_attrition.simulation.war_dynamics import WarSimulator, HISTORICAL_PRESETS
    results = {}
    for name, config in HISTORICAL_PRESETS.items():
        sim = WarSimulator(config)
        result = sim.simulate(max_months=120, seed=42)
        results[name] = {
            "outcome": result.get("outcome"),
            "termination_month": result.get("termination_month"),
        }
        print(f"    {name}: {result.get('outcome')} ({result.get('termination_month')} months)")
    
    manifest_path = output_dir / "simulation_preset_results.json"
    manifest_path.write_text(json.dumps(results, indent=2))
    return {"status": "ok", "presets": len(results)}


def run_leakage_experiment(output_dir: Path):
    """Run the outcome leakage experiment."""
    from mahan_vs_attrition.metrics.predictive_dss import run_leakage_experiment
    from mahan_vs_attrition.simulation.war_dynamics import HISTORICAL_PRESETS
    print("  Running leakage experiment...")
    run_leakage_experiment(HISTORICAL_PRESETS, str(output_dir))
    return {"status": "ok"}


def build_manifest(output_dir: Path, results: dict, elapsed: float):
    """Build the final run manifest."""
    git_commit = get_git_commit()
    
    # Hash key output files
    output_hashes = {}
    for name in [
        "dss_scores.parquet", "ses_scores.parquet",
        "termination_classification.parquet",
        "sensitivity_summary.json",
        "internal_coefficient_sensitivity.json",
        "blind_validation_summary.json",
        "simulation_preset_results.json",
        "leakage_experiment.json",
    ]:
        output_hashes[name] = hash_file(output_dir / name)
    
    # Hash parameter files
    param_hashes = {}
    for name in [
        "config/metric_weights.yml",
        "config/sources.yml",
        "config/war_taxonomy.yml",
        "data/blind_validation_cases.yml",
    ]:
        param_hashes[name] = hash_file(Path(name))
    
    manifest = {
        "git_commit": git_commit,
        "python_version": sys.version,
        "random_seed": 42,
        "elapsed_seconds": round(elapsed, 1),
        "steps": results,
        "output_hashes": output_hashes,
        "param_hashes": param_hashes,
    }
    
    manifest_path = Path("reports") / "final_run_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str))
    print(f"\nFinal manifest written to {manifest_path}")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Run all experiments")
    parser.add_argument("--quick", action="store_true", help="Quick mode")
    args = parser.parse_args()
    
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("MAHAN VS ATTRITION: FULL EXPERIMENT RUN")
    print("=" * 60)
    
    start = time.time()
    results = {}
    
    steps = [
        ("sensitivity", run_sensitivity),
        ("blind_validation", run_blind_validation),
        ("simulation_presets", run_simulation_presets),
        ("leakage_experiment", run_leakage_experiment),
    ]
    
    for name, func in steps:
        print(f"\n--- {name} ---")
        step_start = time.time()
        try:
            result = func(output_dir)
            elapsed_step = time.time() - step_start
            result["elapsed_seconds"] = round(elapsed_step, 1)
            results[name] = result
            print(f"  Completed in {elapsed_step:.1f}s")
        except Exception as e:
            elapsed_step = time.time() - step_start
            results[name] = {"status": "failed", "error": str(e), "elapsed_seconds": round(elapsed_step, 1)}
            print(f"  FAILED: {e}")
    
    total_elapsed = time.time() - start
    
    # Build manifest
    manifest = build_manifest(output_dir, results, total_elapsed)
    
    # Summary
    ok = sum(1 for r in results.values() if r.get("status") == "ok")
    print(f"\n{'=' * 60}")
    print(f"COMPLETE: {ok}/{len(results)} steps succeeded in {total_elapsed:.1f}s")
    print(f"{'=' * 60}")
    
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())

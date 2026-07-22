"""Blind historical validation: run simulator without revealing historical outcome.

The simulator receives ONLY initial conditions and must predict the mechanism.
This tests whether structural factors are sufficient to predict termination mechanism.
"""

import json
import logging
from pathlib import Path

import pandas as pd
import yaml

from mahan_vs_attrition.simulation.war_dynamics import WarSimulator

logger = logging.getLogger(__name__)


def load_blind_cases(path: Path) -> list[dict]:
    with open(path) as f:
        data = yaml.safe_load(f)
    return data.get("cases", [])


def predict_mechanism(result: dict) -> str:
    outcome = result.get("outcome", "inconclusive")
    dss_a = result.get("dss_a", [0])
    ses_a = result.get("ses_a", [0])
    duration = result.get("termination_month", 120)

    final_dss = max(dss_a) if dss_a else 0
    final_ses = max(ses_a) if ses_a else 0

    if "decisive" in outcome and duration < 12:
        return "decisive"
    elif final_ses > 70:
        return "attritional"
    elif final_dss > 50 and final_ses > 40:
        return "mixed"
    elif duration > 60:
        return "attritional"
    else:
        return "uncertain"


def compute_confidence(result: dict) -> float:
    dss_a = result.get("dss_a", [0])
    ses_a = result.get("ses_a", [0])
    final_dss = max(dss_a) if dss_a else 0
    final_ses = max(ses_a) if ses_a else 0

    signal_strength = abs(final_dss - final_ses) / 100.0
    return min(1.0, 0.5 + signal_strength)


def assess_prediction(prediction: str, human_label: str) -> str:
    """Separate exact matches from indeterminate neutral-default outputs."""
    if prediction == human_label:
        return "exact_match"
    if prediction == "uncertain":
        return "indeterminate"
    if prediction == "decisive" and human_label == "attritional":
        return "false_decisive"
    if prediction == "attritional" and human_label == "decisive":
        return "false_attritional"
    if prediction == "mixed" and human_label in {"decisive", "attritional"}:
        return "over_mixed"
    return "other_mismatch"


def run_blind_validation(
    cases_path: Path,
    output_dir: Path,
    seed: int = 42,
) -> pd.DataFrame:
    cases = load_blind_cases(cases_path)
    results = []

    for case in cases:
        config = {
            "war_type": case.get("war_type", "limited_war"),
            "side_a_name": case.get("side_a", "Side A"),
            "side_b_name": case.get("side_b", "Side B"),
        }

        init = case.get("initial", {})
        for key in ["military", "economic", "political_will", "population_support", "industrial"]:
            config[f"initial_{key}_a"] = init.get(f"{key}_a", 60)
            config[f"initial_{key}_b"] = init.get(f"{key}_b", 60)

        config["shock_strength"] = 50.0
        config["attrition_rate"] = 50.0
        config["economic_resilience"] = 50.0
        config["political_resilience"] = 50.0

        sim = WarSimulator(config)
        result = sim.simulate(max_months=120, seed=seed)

        prediction = predict_mechanism(result)
        confidence = compute_confidence(result)
        human_label = case["human_label"]

        assessment = assess_prediction(prediction, human_label)

        results.append({
            "war": case["name"],
            "human_label": human_label,
            "model_prediction": prediction,
            "confidence": round(confidence, 3),
            "assessment": assessment,
            "duration_months": result.get("termination_month", 120),
            "outcome": result.get("outcome", "inconclusive"),
            "final_dss_sim": round(max(result.get("dss_a", [0])), 1),
            "final_ses_sim": round(max(result.get("ses_a", [0])), 1),
        })

    df = pd.DataFrame(results)
    n_exact = int((df["assessment"] == "exact_match").sum())
    n_total = len(df)
    n_indeterminate = int((df["assessment"] == "indeterminate").sum())
    n_directional_errors = int(df["assessment"].isin(["false_decisive", "false_attritional"]).sum())
    exact_match_rate = n_exact / n_total if n_total else 0.0
    coverage_rate = (n_total - n_indeterminate) / n_total if n_total else 0.0

    logger.info(
        "Blind evaluation: %d/%d exact matches; %d/%d indeterminate neutral-default outputs",
        n_exact,
        n_total,
        n_indeterminate,
        n_total,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_dir / "blind_prediction_results.csv", index=False)

    summary = {
        "n_cases": n_total,
        "n_exact_matches": n_exact,
        "exact_match_rate": round(exact_match_rate, 3),
        "n_indeterminate": n_indeterminate,
        "coverage_rate": round(coverage_rate, 3),
        "n_directional_errors": n_directional_errors,
        "assessment_distribution": df["assessment"].value_counts().to_dict(),
        "by_human_label": {
            label: {
                "n": int(subset.shape[0]),
                "exact_matches": int((subset["assessment"] == "exact_match").sum()),
                "indeterminate": int((subset["assessment"] == "indeterminate").sum()),
            }
            for label, subset in df.groupby("human_label")
        },
    }
    (output_dir / "blind_validation_summary.json").write_text(
        json.dumps(summary, indent=2)
    )

    return df

"""Competing explanation tests: compare DSS+SES against simpler baselines.

Tests whether the DSS/SES framework adds predictive information beyond
simple heuristics like "long war = attrition" or "power imbalance = decisive."
"""

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    roc_auc_score,
)
from sklearn.preprocessing import label_binarize

logger = logging.getLogger(__name__)


def _ensure_binary(y_true, y_pred, classes):
    """Convert multi-class to binary for AUC computation."""
    y_true_bin = label_binarize(y_true, classes=classes)
    y_pred_bin = label_binarize(y_pred, classes=classes)
    return y_true_bin, y_pred_bin


def baseline_duration_only(wars_df: pd.DataFrame) -> dict:
    """Baseline: classify by duration only.

    - < 365 days: decisive
    - 365-730 days: mixed
    - > 730 days: attritional
    """
    predictions = []
    for _, row in wars_df.iterrows():
        dur = row.get("duration_days", 0)
        if pd.isna(dur) or dur <= 0:
            predictions.append("uncertain")
        elif dur < 365:
            predictions.append("decisive")
        elif dur < 730:
            predictions.append("mixed")
        else:
            predictions.append("attritional")
    return {"predictions": predictions, "name": "duration_only"}


def baseline_casualties_only(war_years_df: pd.DataFrame) -> dict:
    """Baseline: classify by casualty burden.

    High total casualties relative to pre-war population = attritional.
    """
    if "battle_deaths" not in war_years_df.columns or "war_id" not in war_years_df.columns:
        return {"predictions": [], "name": "casualties_only", "error": "missing columns"}

    war_casualties = war_years_df.groupby("war_id")["battle_deaths"].sum()

    predictions = {}
    for wid, total_deaths in war_casualties.items():
        if pd.isna(total_deaths) or total_deaths <= 0:
            predictions[wid] = "uncertain"
        elif total_deaths > 500000:
            predictions[wid] = "attritional"
        elif total_deaths > 100000:
            predictions[wid] = "mixed"
        else:
            predictions[wid] = "decisive"

    return {"predictions_dict": predictions, "name": "casualties_only"}


def baseline_power_ratio_only(wars_df: pd.DataFrame, war_years_df: pd.DataFrame) -> dict:
    """Baseline: classify by initial power ratio.

    Large CINC imbalance = decisive (strong side dominates).
    Near-parity = attritional (stalemate).
    """
    if "cinc" not in war_years_df.columns:
        return {"predictions": [], "name": "power_ratio_only", "error": "no CINC data"}

    predictions = {}
    for wid, group in war_years_df.groupby("war_id"):
        group_sorted = group.sort_values("year")
        if len(group_sorted) < 1:
            predictions[wid] = "uncertain"
            continue

        cinc_vals = group_sorted["cinc"].dropna()
        if len(cinc_vals) < 2:
            predictions[wid] = "uncertain"
            continue

        cinc_range = cinc_vals.max() - cinc_vals.min()
        cinc_mean = cinc_vals.mean()

        if cinc_mean > 0:
            imbalance = cinc_range / cinc_mean
        else:
            imbalance = 0

        if imbalance > 0.5:
            predictions[wid] = "decisive"
        elif imbalance > 0.2:
            predictions[wid] = "mixed"
        else:
            predictions[wid] = "attritional"

    return {"predictions_dict": predictions, "name": "power_ratio_only"}


def baseline_majority_class(classifications_df: pd.DataFrame) -> dict:
    """Baseline: always predict the majority class."""
    if "primary_mechanism" not in classifications_df.columns:
        return {"predictions": [], "name": "majority_class", "error": "no mechanism column"}

    counts = classifications_df["primary_mechanism"].value_counts()
    majority = counts.index[0]
    predictions = [majority] * len(classifications_df)

    return {"predictions": predictions, "name": "majority_class"}


def dss_ses_model(classifications_df: pd.DataFrame) -> dict:
    """Full model: use DSS/SES hybrid classification."""
    if "primary_mechanism" not in classifications_df.columns:
        return {"predictions": [], "name": "dss_ses_model", "error": "no mechanism column"}

    predictions = classifications_df["primary_mechanism"].tolist()
    return {"predictions": predictions, "name": "dss_ses_model"}


def compute_metrics(y_true: list, y_pred: list, model_name: str) -> dict:
    """Compute accuracy, AUC, and Brier score for a set of predictions."""
    valid = [
        (t, p) for t, p in zip(y_true, y_pred)
        if t and p
        and t != "data_insufficient" and p != "data_insufficient"
        and t != "ses_only_insufficient" and p != "ses_only_insufficient"
    ]

    if not valid:
        return {"model": model_name, "accuracy": 0, "auc": None, "brier": None, "n": 0}

    y_true_clean, y_pred_clean = zip(*valid)

    accuracy = accuracy_score(y_true_clean, y_pred_clean)

    classes = sorted(set(y_true_clean) | set(y_pred_clean))
    n_classes = len(classes)

    auc = None
    if n_classes >= 2:
        try:
            y_true_bin, y_pred_bin = _ensure_binary(y_true_clean, y_pred_clean, classes)
            aucs = []
            for i in range(n_classes):
                if y_true_bin[:, i].sum() > 0:
                    aucs.append(roc_auc_score(y_true_bin[:, i], y_pred_bin[:, i]))
            auc = float(np.mean(aucs)) if aucs else None
        except Exception:
            auc = None

    brier = None
    if n_classes >= 2:
        try:
            y_true_bin, y_pred_bin = _ensure_binary(y_true_clean, y_pred_clean, classes)
            brier = float(np.mean([
                brier_score_loss(y_true_bin[:, i], y_pred_bin[:, i].astype(float))
                for i in range(n_classes)
                if y_true_bin[:, i].sum() > 0
            ]))
        except Exception:
            brier = None

    return {
        "model": model_name,
        "accuracy": round(accuracy, 4),
        "auc": round(auc, 4) if auc is not None else None,
        "brier": round(brier, 4) if brier is not None else None,
        "n": len(valid),
    }


def run_baseline_comparison(
    wars_df: pd.DataFrame,
    war_years_df: pd.DataFrame,
    classifications_df: pd.DataFrame,
    output_dir: Path,
) -> dict:
    """Run all baseline comparisons and save results.

    For each baseline:
    1. Generate predictions
    2. Compare to DSS/SES model predictions
    3. Compute metrics
    4. Save results
    """
    if "primary_mechanism" not in classifications_df.columns:
        logger.warning("No primary_mechanism in classifications")
        return {"error": "no mechanism column"}

    ground_truth = classifications_df["primary_mechanism"].tolist()

    baselines = []

    # Baseline 1: Duration only
    if "duration_days" in wars_df.columns:
        merged = classifications_df.merge(
            wars_df[["war_id", "duration_days"]], on="war_id", how="left"
        )
        dur_result = baseline_duration_only(merged)
        metrics = compute_metrics(ground_truth, dur_result["predictions"], "duration_only")
        baselines.append(metrics)

    # Baseline 2: Casualties only
    cas_result = baseline_casualties_only(war_years_df)
    if "predictions_dict" in cas_result:
        cas_preds = [
            cas_result["predictions_dict"].get(wid, "uncertain")
            for wid in classifications_df["war_id"]
        ]
        metrics = compute_metrics(ground_truth, cas_preds, "casualties_only")
        baselines.append(metrics)

    # Baseline 3: Power ratio only
    pr_result = baseline_power_ratio_only(wars_df, war_years_df)
    if "predictions_dict" in pr_result:
        pr_preds = [
            pr_result["predictions_dict"].get(wid, "uncertain")
            for wid in classifications_df["war_id"]
        ]
        metrics = compute_metrics(ground_truth, pr_preds, "power_ratio_only")
        baselines.append(metrics)

    # Baseline 4: Majority class
    maj_result = baseline_majority_class(classifications_df)
    if maj_result["predictions"]:
        metrics = compute_metrics(ground_truth, maj_result["predictions"], "majority_class")
        baselines.append(metrics)

    # Full model: DSS+SES
    dss_result = dss_ses_model(classifications_df)
    if dss_result["predictions"]:
        metrics = compute_metrics(ground_truth, dss_result["predictions"], "dss_ses_model")
        baselines.append(metrics)

    # Compute improvement
    dss_metrics = next((b for b in baselines if b["model"] == "dss_ses_model"), None)
    duration_metrics = next((b for b in baselines if b["model"] == "duration_only"), None)

    improvement = {}
    if dss_metrics and duration_metrics:
        improvement["accuracy_gain_vs_duration"] = round(
            dss_metrics["accuracy"] - duration_metrics["accuracy"], 4
        )
        if dss_metrics["auc"] and duration_metrics["auc"]:
            improvement["auc_gain_vs_duration"] = round(
                dss_metrics["auc"] - duration_metrics["auc"], 4
            )

    results = {
        "baselines": baselines,
        "improvement": improvement,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "baseline_comparison.json").write_text(
        json.dumps(results, indent=2, default=str)
    )

    pd.DataFrame(baselines).to_csv(
        output_dir / "baseline_comparison.csv", index=False
    )

    logger.info(f"Baseline comparison: {len(baselines)} models evaluated")
    for b in baselines:
        logger.info(f"  {b['model']}: accuracy={b['accuracy']:.3f}, auc={b.get('auc', 'N/A')}")

    return results

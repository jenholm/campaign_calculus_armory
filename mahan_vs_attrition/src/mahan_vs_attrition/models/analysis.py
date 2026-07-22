"""Statistical analysis: duration, termination type, feature importance, survival."""

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


def analyze_duration(wars_df: pd.DataFrame, output_dir: Path) -> dict:
    """Descriptive statistics on war duration by era and type."""
    has_dur = "duration_days" in wars_df.columns
    results = {
        "total_wars": len(wars_df),
        "mean_duration_days": float(wars_df["duration_days"].mean()) if has_dur else 0,
        "median_duration_days": float(wars_df["duration_days"].median()) if has_dur else 0,
    }

    if "war_type" in wars_df.columns:
        results["by_type"] = (
            wars_df.groupby("war_type")["duration_days"].agg(["count", "mean", "median"]).to_dict()
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    pd.Series(results).to_json(output_dir / "duration_analysis.json")
    logger.info(f"Duration analysis complete: {results['total_wars']} wars")
    return results


def analyze_termination_types(
    classifications_df: pd.DataFrame,
    output_dir: Path,
) -> dict:
    """Distribution of termination types."""
    if len(classifications_df) == 0:
        return {}

    counts = classifications_df["termination_type_model"].value_counts()
    props = classifications_df["termination_type_model"].value_counts(normalize=True)

    results = {
        "counts": counts.to_dict(),
        "proportions": props.to_dict(),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    pd.Series(results).to_json(output_dir / "termination_analysis.json")
    logger.info(f"Termination analysis: {results}")
    return results


def train_loss_prediction_model(
    war_years_df: pd.DataFrame,
    output_dir: Path,
) -> dict:
    """DESCRIPTIVE ONLY: rank capability features by their structural importance
    for distinguishing war types. NOT a predictive model of war loss.

    Without winner/loser labels, no supervised "loss prediction" is meaningful.
    This function produces a random-forest feature ranking using a constant
    target as a structure-only diagnostic. Treat outputs as exploratory.

    For substantive loss prediction, winner/loser labels must first be
    collected (see Phase 3: manual_case_scores.csv).
    """
    # Try derived feature columns first
    feature_cols = [
        "casualty_burden",
        "military_personnel_decline",
        "military_expenditure_burden",
        "energy_or_industrial_decline",
    ]
    available = [c for c in feature_cols if c in war_years_df.columns]

    # If derived columns not available, construct from raw war_years cols
    if len(available) < 2:
        raw_features = {
            "military_expenditure": "military_expenditure",
            "military_personnel": "military_personnel",
            "iron_steel": "iron_steel",
            "energy_consumption": "energy_consumption",
            "population": "population",
            "cinc": "cinc",
        }
        available = [c for c in raw_features if c in war_years_df.columns]
        if len(available) < 2:
            logger.warning("Not enough feature columns for loss prediction model")
            return {}

        # Aggregate to war-level: compute decline/change across years per war
        war_groups = war_years_df.groupby("war_id")
        agg_records = []
        for wid, group in war_groups:
            group = group.sort_values("year")
            if len(group) < 2:
                continue
            rec = {"war_id": wid}
            for col in available:
                first = group[col].iloc[0]
                last = group[col].iloc[-1]
                max_val = group[col].max()
                if pd.notna(first) and first > 0 and pd.notna(last):
                    rec[f"{col}_decline"] = max(0, (first - last) / first)
                else:
                    rec[f"{col}_decline"] = 0
                rec[f"{col}_initial"] = first if pd.notna(first) else 0
            # Battle deaths as casualty proxy
            if "battle_deaths" in group.columns:
                total_deaths = group["battle_deaths"].sum()
                first_pop = group["population"].iloc[0] if "population" in group.columns else None
                if pd.notna(first_pop) and first_pop > 0:
                    rec["casualty_proxy"] = min(1.0, total_deaths / first_pop)
                else:
                    rec["casualty_proxy"] = 0.0
            agg_records.append(rec)

        if len(agg_records) < 10:
            logger.warning(f"Too few aggregated wars ({len(agg_records)}) for loss prediction")
            return {}

        df = pd.DataFrame(agg_records)
        # Use decline features and casualty proxy
        derived_feature_cols = [c for c in df.columns if c != "war_id"]
        X = df[derived_feature_cols].fillna(0).values
        y = np.zeros(len(df))  # No outcome labels available; treat as unsupervised

        if X.shape[1] < 2:
            logger.warning("Not enough features after aggregation")
            return {}

        # Normalize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Fit a random forest to compute feature importances from structure alone
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_scaled, y)

        results = {
            "random_forest": {
                "n_wars": len(df),
                "n_features": X.shape[1],
                "feature_importances": dict(zip(derived_feature_cols, rf.feature_importances_.tolist())),
            }
        }
        (output_dir / "loss_prediction_model.json").write_text(
            __import__("json").dumps(results, indent=2, default=str)
        )
        logger.info(f"Loss prediction RF trained on {len(df)} wars with {X.shape[1]} features")
        return results
    else:
        df = war_years_df.dropna(subset=available)
        if len(df) < 10:
            logger.warning(f"Too few rows ({len(df)}) for loss prediction")
            return {}

        X = df[available].values
        if "winner_loser_stalemate" in df.columns:
            y = np.where(df["winner_loser_stalemate"].fillna("").str.lower() == "loser", 1, 0)
        else:
            y = np.zeros(len(df))

        if y.sum() < 2:
            logger.warning("Too few loser labels for meaningful model training")
            return {}

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

    models = {
        "logistic_regression": LogisticRegression(max_iter=1000, random_state=42),
        "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        results[name] = {
            "train_accuracy": round(train_score, 4),
            "test_accuracy": round(test_score, 4),
            "n_features": len(available),
            "n_train": len(X_train),
            "n_test": len(X_test),
        }
        if hasattr(model, "feature_importances_"):
            fi = model.feature_importances_.tolist()
            results[name]["feature_importances"] = dict(zip(available, fi))
        if hasattr(model, "coef_"):
            results[name]["coefficients"] = dict(zip(available, model.coef_[0].tolist()))

    output_dir.mkdir(parents=True, exist_ok=True)
    pd.Series(results).to_json(output_dir / "loss_prediction_model.json")
    logger.info(f"Loss prediction models trained: {list(models.keys())}")
    return results


def survival_analysis(
    wars_df: pd.DataFrame,
    classifications_df: pd.DataFrame,
    output_dir: Path,
) -> dict:
    """Kaplan-Meier style analysis: time-to-defeat for different termination types."""
    if not {"war_id", "duration_days", "start_date", "end_date"}.issubset(wars_df.columns):
        return {"error": "Required columns missing"}

    df = wars_df[["war_id", "duration_days", "start_date", "war_type"]].copy()
    df = df.dropna(subset=["duration_days"])
    df["duration_days"] = df["duration_days"].clip(lower=1)

    # Merge termination classification
    if len(classifications_df) > 0:
        df = df.merge(
            classifications_df[["war_id", "termination_type_model"]],
            on="war_id",
            how="left",
        )
        df["termination_type_model"] = df["termination_type_model"].fillna("uncertain")

    # Compute survival estimates by termination type
    results = {}
    for term_type in df["termination_type_model"].unique():
        subset = df[df["termination_type_model"] == term_type]
        if len(subset) < 3:
            continue
        durations = subset["duration_days"].sort_values()
        n = len(durations)
        # Simple Kaplan-Meier-like survival at each event
        survival = []
        at_risk = n
        for d in durations:
            survival.append((int(d), at_risk / n))
            at_risk -= 1
        results[str(term_type)] = {
            "n_wars": n,
            "median_duration_days": int(durations.median()),
            "mean_duration_days": round(durations.mean(), 1),
            "pct_ended_within_30d": int((durations <= 30).sum() / n * 100),
            "pct_ended_within_365d": int((durations <= 365).sum() / n * 100),
            "pct_ended_within_1825d": int((durations <= 1825).sum() / n * 100),
        }

    (output_dir / "survival_analysis.json").write_text(
        json.dumps(results, indent=2, default=str)
    )
    logger.info(f"Survival analysis: {len(results)} termination types")
    return results


def logistic_regression_termination(
    war_years_df: pd.DataFrame,
    wars_df: pd.DataFrame,
    output_dir: Path,
) -> dict:
    """Logistic regression: predict short vs long wars from capability features.

    Target: short war (duration_days < 365) vs long war.
    Features: computed from war-years:
        - military_personnel_pct_change
        - military_expenditure_pct_change
        - energy_consumption_pct_change
        - cinc_pct_change
        - iron_steel_pct_change
        - avg_battle_deaths
    """
    if len(war_years_df) == 0 or len(wars_df) == 0:
        return {"error": "Empty input"}

    # Build war-level features
    feature_cols_raw = [
        "military_personnel", "military_expenditure", "energy_consumption",
        "iron_steel", "cinc", "battle_deaths",
    ]
    available = [c for c in feature_cols_raw if c in war_years_df.columns]
    if len(available) < 2:
        return {"error": "Not enough feature columns"}

    war_features = []
    for war_id, group in war_years_df.groupby("war_id"):
        group = group.sort_values("year")
        if len(group) < 2:
            continue
        rec = {"war_id": war_id}
        for col in available:
            vals = group[col]
            # Filter out -9 (COW missing code)
            vals_clean = vals[(vals >= 0) & vals.notna()]
            if len(vals_clean) < 2:
                rec[f"{col}_pct_change"] = 0.0
                rec[f"{col}_initial"] = 0.0
            else:
                initial = vals_clean.iloc[0]
                final = vals_clean.iloc[-1]
                if initial > 0:
                    rec[f"{col}_pct_change"] = (final - initial) / initial
                else:
                    rec[f"{col}_pct_change"] = 0.0
                rec[f"{col}_initial"] = float(initial)
        # Duration
        war_row = wars_df[wars_df["war_id"] == war_id]
        if len(war_row) > 0:
            rec["duration_days"] = float(war_row.iloc[0].get("duration_days", 0))
        war_features.append(rec)

    feat_df = pd.DataFrame(war_features)
    if len(feat_df) < 30:
        return {"error": f"Too few wars with features: {len(feat_df)}"}

    # Drop rows with no duration
    feat_df = feat_df.dropna(subset=["duration_days"])
    feat_df = feat_df[feat_df["duration_days"] > 0]

    # Build target: short war (< 1 year) vs long war (>= 1 year)
    feat_df["is_short_war"] = (feat_df["duration_days"] < 365).astype(int)

    # Features
    feature_names = [c for c in feat_df.columns if c not in ("war_id", "duration_days", "is_short_war")]
    X = feat_df[feature_names].fillna(0).values
    y = feat_df["is_short_war"].values

    if y.sum() < 10 or (1 - y).sum() < 10:
        return {"error": f"Class imbalance: short={int(y.sum())}, long={int((1-y).sum())}"}

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Logistic regression
    lr = LogisticRegression(max_iter=2000, random_state=42, C=1.0)
    lr.fit(X_train_scaled, y_train)
    train_acc = lr.score(X_train_scaled, y_train)
    test_acc = lr.score(X_test_scaled, y_test)

    # Try AUC if both classes present in test
    try:
        y_pred_proba = lr.predict_proba(X_test_scaled)[:, 1]
        auc = float(roc_auc_score(y_test, y_pred_proba))
    except Exception:
        auc = None

    # Coefficients
    coefs = dict(zip(feature_names, [round(float(c), 4) for c in lr.coef_[0]]))
    sorted_coefs = sorted(coefs.items(), key=lambda x: abs(x[1]), reverse=True)
    top_features = sorted_coefs[:10]

    # Random forest for comparison
    rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
    rf.fit(X_train_scaled, y_train)
    rf_test_acc = rf.score(X_test_scaled, y_test)
    importances = dict(zip(feature_names, [round(float(i), 4) for i in rf.feature_importances_]))
    top_importances = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:10]

    results = {
        "n_wars": len(feat_df),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "n_short_war": int(y.sum()),
        "n_long_war": int((1 - y).sum()),
        "logistic_regression": {
            "train_accuracy": round(train_acc, 4),
            "test_accuracy": round(test_acc, 4),
            "auc_roc": round(auc, 4) if auc else None,
            "top_coefficients": [{"feature": k, "coef": v} for k, v in top_features],
        },
        "random_forest": {
            "test_accuracy": round(rf_test_acc, 4),
            "top_importances": [{"feature": k, "importance": v} for k, v in top_importances],
        },
        "all_coefficients": coefs,
    }

    (output_dir / "logistic_regression_termination.json").write_text(
        json.dumps(results, indent=2, default=str)
    )
    logger.info(f"Logistic regression: test accuracy {test_acc:.3f}, AUC {auc if auc else 'N/A'}")
    return results


def run_all(
    wars_path: Path,
    war_years_path: Path,
    classifications_path: Path,
    output_dir: Path,
) -> dict:
    """Run all analyses."""

    def _read(path):
        return pd.read_parquet(path) if path.exists() else pd.DataFrame()

    wars = _read(wars_path)
    war_years = _read(war_years_path)
    classifications = _read(classifications_path)

    results = {}
    results["duration"] = analyze_duration(wars, output_dir)
    results["termination"] = analyze_termination_types(classifications, output_dir)
    results["loss_prediction"] = train_loss_prediction_model(war_years, output_dir)
    results["logistic_regression"] = logistic_regression_termination(war_years, wars, output_dir)
    results["survival"] = survival_analysis(wars, classifications, output_dir)

    return results


def run_all_enhanced(
    wars_path: Path,
    war_years_path: Path,
    classifications_path: Path,
    output_dir: Path,
) -> dict:
    """Run all analyses including new hypothesis testing."""

    def _read(path: Path) -> pd.DataFrame:
        return pd.read_parquet(path) if path.exists() else pd.DataFrame()

    results = run_all(wars_path, war_years_path, classifications_path, output_dir)

    wars = _read(wars_path)
    war_years = _read(war_years_path)
    classifications = _read(classifications_path)

    if len(war_years) > 0 and len(classifications) > 0:
        from mahan_vs_attrition.models.hypothesis_testing import (
            ablation_study,
            logistic_regression_hypothesis,
        )

        results["hypothesis_logistic"] = logistic_regression_hypothesis(
            war_years, classifications, output_dir, wars_df=wars,
        )
        results["ablation"] = ablation_study(
            war_years, classifications, output_dir, wars_df=wars,
        )

    if len(wars) > 0 and len(classifications) > 0:
        from mahan_vs_attrition.models.hypothesis_testing import (
            survival_analysis_hypothesis,
        )

        results["survival_hypothesis"] = survival_analysis_hypothesis(
            wars, classifications, output_dir,
        )

    return results

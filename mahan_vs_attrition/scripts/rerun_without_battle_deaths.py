#!/usr/bin/env python3
"""Re-run ML analysis excluding battle_deaths features (M77 leakage fix).

battle_deaths_initial and battle_deaths_pct_change are wartime outcomes,
not ex-ante predictors. Our own audit labels battle_deaths as
'Forbidden (outcome-dependent)'. This script re-runs the RF and LR
analysis with only the 10 material-capability features.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler

RANDOM_SEED = 42
DATA_DIR = Path("data/processed")
REPORT_DIR = Path("reports")


def load_data():
    wars = pd.read_parquet(DATA_DIR / "wars.parquet")
    war_years = pd.read_parquet(DATA_DIR / "war_years.parquet")
    return wars, war_years


def build_features_clean(war_years, wars):
    """Build feature matrix EXCLUDING battle_deaths."""
    feature_cols_raw = [
        "military_personnel",
        "military_expenditure",
        "energy_consumption",
        "iron_steel",
        "cinc",
        # battle_deaths REMOVED — wartime outcome, not ex-ante predictor
    ]
    available = [c for c in feature_cols_raw if c in war_years.columns]

    war_features = []
    for war_id, group in war_years.groupby("war_id"):
        group = group.sort_values("year")
        if len(group) < 2:
            continue
        rec = {"war_id": war_id}
        for col in available:
            vals = group[col]
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
        war_row = wars[wars["war_id"] == war_id]
        if len(war_row) > 0:
            rec["duration_days"] = float(war_row.iloc[0].get("duration_days", 0))
        war_features.append(rec)

    feat_df = pd.DataFrame(war_features)
    feat_df = feat_df.dropna(subset=["duration_days"])
    feat_df = feat_df[feat_df["duration_days"] > 0]
    feat_df["is_short_war"] = (feat_df["duration_days"] < 365).astype(int)
    feature_names = [c for c in feat_df.columns if c not in ("war_id", "duration_days", "is_short_war")]
    X = feat_df[feature_names].fillna(0).values
    y = feat_df["is_short_war"].values
    return X, y, feature_names, feat_df


def run_analysis(X, y, feature_names):
    n_samples, n_features = X.shape
    n_short = int(y.sum())
    n_long = int((1 - y).sum())
    null_acc = max(n_short, n_long) / n_samples

    print(f"Dataset: {n_samples} samples, {n_features} features")
    print(f"Target: short={n_short}, long={n_long}")
    print(f"Null baseline: {null_acc:.1%}")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)

    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=100, max_depth=5, random_state=RANDOM_SEED
        ),
        "Logistic Regression": LogisticRegression(
            max_iter=2000, random_state=RANDOM_SEED, C=1.0
        ),
    }

    results = {}
    for name, model in models.items():
        print(f"\n--- {name} ---")
        y_pred_cv = cross_val_predict(model, X_scaled, y, cv=cv, method="predict")
        y_proba_cv = cross_val_predict(model, X_scaled, y, cv=cv, method="predict_proba")

        acc = accuracy_score(y, y_pred_cv)
        bal_acc = balanced_accuracy_score(y, y_pred_cv)
        prec = precision_score(y, y_pred_cv, zero_division=0)
        rec = recall_score(y, y_pred_cv, zero_division=0)
        f1 = f1_score(y, y_pred_cv, zero_division=0)
        try:
            auc = roc_auc_score(y, y_proba_cv[:, 1])
        except Exception:
            auc = None
        cm = confusion_matrix(y, y_pred_cv)

        # Per-fold accuracies for std
        fold_accs = []
        for train_idx, test_idx in cv.split(X_scaled, y):
            m = type(model)(**model.get_params())
            m.fit(X_scaled[train_idx], y[train_idx])
            fold_accs.append(accuracy_score(y[test_idx], m.predict(X_scaled[test_idx])))
        std_acc = np.std(fold_accs)

        print(f"  Accuracy: {acc:.1%} +/- {std_acc:.1%}")
        print(f"  Balanced accuracy: {bal_acc:.1%}")
        print(f"  AUC-ROC: {auc:.3f}" if auc else "  AUC-ROC: N/A")
        print(f"  Precision: {prec:.1%}")
        print(f"  Recall: {rec:.1%}")
        print(f"  F1: {f1:.1%}")
        print(f"  Confusion matrix:\n{cm}")

        results[name] = {
            "accuracy": round(acc, 4),
            "accuracy_std": round(std_acc, 4),
            "balanced_accuracy": round(bal_acc, 4),
            "auc_roc": round(auc, 4) if auc else None,
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "confusion_matrix": cm.tolist(),
        }

    # Feature importance for RF
    rf = models["Random Forest"]
    rf.fit(X_scaled, y)
    fi_gini = pd.Series(rf.feature_importances_, index=feature_names).sort_values(ascending=False)

    # Permutation importance
    from sklearn.inspection import permutation_importance as perm_imp

    pi = perm_imp(rf, X_scaled, y, n_repeats=30, random_state=RANDOM_SEED)
    fi_perm = pd.Series(pi.importances_mean, index=feature_names).sort_values(ascending=False)

    print("\n--- Feature Importance (clean, no battle_deaths) ---")
    fi_df = pd.DataFrame({
        "feature": feature_names,
        "gini_importance": rf.feature_importances_,
        "perm_importance_mean": pi.importances_mean,
        "perm_importance_std": pi.importances_std,
    }).sort_values("gini_importance", ascending=False)
    print(fi_df.to_string(index=False))

    # LR coefficients
    lr = models["Logistic Regression"]
    lr.fit(X_scaled, y)
    coefs = pd.Series(lr.coef_[0], index=feature_names).sort_values(key=abs, ascending=False)
    print("\n--- LR Coefficients (clean, no battle_deaths) ---")
    for feat, coef in coefs.items():
        print(f"  {feat}: {coef:+.4f}")

    return results, fi_df, coefs, null_acc, n_samples, n_features


def main():
    wars, war_years = load_data()
    X, y, feature_names, feat_df = build_features_clean(war_years, wars)
    results, fi_df, coefs, null_acc, n_samples, n_features = run_analysis(X, y, feature_names)

    # Save results
    REPORT_DIR.mkdir(exist_ok=True)
    output = {
        "metadata": {
            "n_samples": n_samples,
            "n_features": n_features,
            "n_short": int(y.sum()),
            "n_long": int((1 - y).sum()),
            "null_baseline": round(null_acc, 4),
            "features_used": feature_names,
            "features_removed": ["battle_deaths_initial", "battle_deaths_pct_change"],
            "removal_reason": "Wartime outcome, not ex-ante predictor. Our own audit labels battle_deaths as 'Forbidden (outcome-dependent)'.",
            "random_seed": RANDOM_SEED,
        },
        "results": results,
        "feature_importance": fi_df.to_dict(orient="records"),
        "lr_coefficients": {k: round(v, 4) for k, v in coefs.items()},
    }
    out_path = REPORT_DIR / "rf_analysis_clean_no_battle_deaths.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {out_path}")

    # Also save feature importance CSV
    fi_df.to_csv(REPORT_DIR / "rf_feature_importance_clean.csv", index=False)

    # Summary comparison
    rf_acc = results["Random Forest"]["accuracy"]
    lr_acc = results["Logistic Regression"]["accuracy"]
    rf_auc = results["Random Forest"]["auc_roc"]
    lr_auc = results["Logistic Regression"]["auc_roc"]
    print(f"\n=== SUMMARY (without battle_deaths) ===")
    print(f"RF accuracy: {rf_acc:.1%} (was 73.9% with battle_deaths)")
    print(f"LR accuracy: {lr_acc:.1%} (was 55.2% with battle_deaths)")
    print(f"RF AUC: {rf_auc:.3f} (was 0.816)")
    print(f"LR AUC: {lr_auc:.3f} (was 0.565)")
    print(f"RF-LR gap: {(rf_acc - lr_acc)*100:.1f}pp")


if __name__ == "__main__":
    main()

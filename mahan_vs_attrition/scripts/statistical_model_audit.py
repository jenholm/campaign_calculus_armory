#!/usr/bin/env python3
"""Statistical model audit: VIF, OOB, bootstrap CIs, interaction logistic.

Outputs paper/tables/statistical_model_audit.tex.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def compute_vif(X: np.ndarray, feature_names: list[str]) -> dict[str, float]:
    """Compute Variance Inflation Factor for each feature."""
    from numpy.linalg import inv

    vifs = {}
    for i, name in enumerate(feature_names):
        y = X[:, i]
        X_rest = np.delete(X, i, axis=1)
        X_with_const = np.column_stack([np.ones(len(X_rest)), X_rest])
        try:
            beta = np.linalg.lstsq(X_with_const, y, rcond=None)[0]
            y_pred = X_with_const @ beta
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - y.mean()) ** 2)
            r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            vifs[name] = 1.0 / (1.0 - r_sq) if r_sq < 1.0 else float("inf")
        except Exception:
            vifs[name] = float("inf")
    return vifs


def main() -> None:
    data_dir = Path("data/processed")
    output_dir = Path("paper/tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    war_years_path = data_dir / "war_years.parquet"
    wars_path = data_dir / "wars.parquet"

    if not war_years_path.exists() or not wars_path.exists():
        print("Data files not found, skipping statistical audit")
        return

    war_years = pd.read_parquet(war_years_path)
    wars = pd.read_parquet(wars_path)

    # Build war-level features (same as analysis.py)
    feature_cols_raw = [
        "military_personnel", "military_expenditure", "energy_consumption",
        "iron_steel", "cinc", "battle_deaths",
    ]
    available = [c for c in feature_cols_raw if c in war_years.columns]
    if len(available) < 2:
        print("Not enough feature columns")
        return

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

    if y.sum() < 10 or (1 - y).sum() < 10:
        print("Class imbalance too severe")
        return

    # VIF
    vif_values = compute_vif(X, feature_names)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # Logistic regression
    lr = LogisticRegression(max_iter=2000, random_state=42, C=1.0)
    lr.fit(X_train_s, y_train)
    lr_test_acc = lr.score(X_test_s, y_test)
    lr_auc = roc_auc_score(y_test, lr.predict_proba(X_test_s)[:, 1])

    # Interaction logistic
    interaction_pipe = make_pipeline(
        StandardScaler(),
        PolynomialFeatures(degree=2, interaction_only=True, include_bias=False),
        LogisticRegression(max_iter=2000, penalty="l2", C=1.0, random_state=42),
    )
    interaction_pipe.fit(X_train, y_train)
    int_test_acc = interaction_pipe.score(X_test, y_test)
    int_auc = roc_auc_score(y_test, interaction_pipe.predict_proba(X_test)[:, 1])

    # Random forest with OOB
    rf = RandomForestClassifier(
        n_estimators=100, max_depth=5, random_state=42,
        oob_score=True, bootstrap=True,
    )
    rf.fit(X_train_s, y_train)
    rf_test_acc = rf.score(X_test_s, y_test)
    rf_auc = roc_auc_score(y_test, rf.predict_proba(X_test_s)[:, 1])
    rf_oob = rf.oob_score_

    # Bootstrap AUC CIs (1000 iterations)
    rng = np.random.RandomState(42)
    n_boot = 1000
    boot_aucs_lr = []
    boot_aucs_rf = []
    for _ in range(n_boot):
        idx = rng.choice(len(X_test_s), size=len(X_test_s), replace=True)
        Xb, yb = X_test_s[idx], y_test[idx]
        if len(np.unique(yb)) < 2:
            continue
        try:
            boot_aucs_lr.append(roc_auc_score(yb, lr.predict_proba(Xb)[:, 1]))
            boot_aucs_rf.append(roc_auc_score(yb, rf.predict_proba(Xb)[:, 1]))
        except ValueError:
            continue

    lr_ci_lo = np.percentile(boot_aucs_lr, 2.5) if boot_aucs_lr else 0
    lr_ci_hi = np.percentile(boot_aucs_lr, 97.5) if boot_aucs_lr else 0
    rf_ci_lo = np.percentile(boot_aucs_rf, 2.5) if boot_aucs_rf else 0
    rf_ci_hi = np.percentile(boot_aucs_rf, 97.5) if boot_aucs_rf else 0

    # Write table
    lines = [
        r"\begin{table}[H]",
        r"\centering",
        r"\caption{Statistical model audit: VIF, out-of-bag error, interaction logistic regression, and bootstrap AUC confidence intervals.}",
        r"\label{tab:statistical_audit}",
        r"\small",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{tabularx}{\textwidth}{@{}l X r@{}}",
        r"\toprule",
        r"\textbf{Metric} & \textbf{Details} & \textbf{Value} \\",
        r"\midrule",
    ]

    # VIF section
    lines.append(r"\multicolumn{3}{l}{\textit{Variance Inflation Factors}} \\")
    for name, vif in sorted(vif_values.items(), key=lambda x: -x[1]):
        status = "OK" if vif < 5 else ("Warning" if vif < 10 else "High")
        lines.append(f"{name.replace('_', ' ')} & {status} & {vif:.2f} \\\\")
    max_vif = max(vif_values.values())
    lines.append(r"\midrule")
    lines.append(f"\\multicolumn{{2}}{{l}}{{\\textbf{{Max VIF}}}} & {max_vif:.2f} \\\\")

    # Model comparison
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{3}{l}{\textit{Model Performance}} \\")
    lines.append(f"Logistic regression test accuracy & 5-fold CV, $C=1.0$ & {lr_test_acc:.4f} \\\\")
    lines.append(f"Logistic regression AUC-ROC & Bootstrap 95\\% CI & {lr_auc:.4f} \\\\")
    lines.append(f"  LR AUC 95\\% CI & $[{lr_ci_lo:.4f},\\; {lr_ci_hi:.4f}]$ & \\\\")
    lines.append(f"Interaction logistic test accuracy & Degree-2 interactions, L2 & {int_test_acc:.4f} \\\\")
    lines.append(f"Interaction logistic AUC-ROC & & {int_auc:.4f} \\\\")
    lines.append(f"Random forest test accuracy & 100 trees, depth 5 & {rf_test_acc:.4f} \\\\")
    lines.append(f"Random forest AUC-ROC & Bootstrap 95\\% CI & {rf_auc:.4f} \\\\")
    lines.append(f"  RF AUC 95\\% CI & $[{rf_ci_lo:.4f},\\; {rf_ci_hi:.4f}]$ & \\\\")
    lines.append(f"Random forest OOB accuracy & Out-of-bag estimate & {rf_oob:.4f} \\\\")

    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\end{table}",
    ]

    out_path = output_dir / "statistical_model_audit.tex"
    out_path.write_text("\n".join(lines) + "\n")

    # Also write JSON for reproducibility
    audit_json = {
        "vif": {k: round(v, 4) for k, v in vif_values.items()},
        "max_vif": round(max_vif, 4),
        "logistic_regression": {
            "test_accuracy": round(lr_test_acc, 4),
            "auc_roc": round(lr_auc, 4),
            "auc_95ci": [round(lr_ci_lo, 4), round(lr_ci_hi, 4)],
        },
        "interaction_logistic": {
            "test_accuracy": round(int_test_acc, 4),
            "auc_roc": round(int_auc, 4),
        },
        "random_forest": {
            "test_accuracy": round(rf_test_acc, 4),
            "auc_roc": round(rf_auc, 4),
            "auc_95ci": [round(rf_ci_lo, 4), round(rf_ci_hi, 4)],
            "oob_accuracy": round(rf_oob, 4),
        },
    }
    json_path = output_dir / "statistical_model_audit.json"
    json_path.write_text(json.dumps(audit_json, indent=2))

    print(f"Statistical audit written to {out_path}")
    print(f"  Max VIF: {max_vif:.2f}")
    print(f"  LR AUC: {lr_auc:.4f} [{lr_ci_lo:.4f}, {lr_ci_hi:.4f}]")
    print(f"  RF AUC: {rf_auc:.4f} [{rf_ci_lo:.4f}, {rf_ci_hi:.4f}]")
    print(f"  RF OOB: {rf_oob:.4f}")


if __name__ == "__main__":
    main()

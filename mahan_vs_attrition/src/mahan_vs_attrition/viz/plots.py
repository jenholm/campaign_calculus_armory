"""Figure generation for the Mahan vs Attrition report."""

import logging
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mahan_vs_attrition.display_names import display_war_name

logger = logging.getLogger(__name__)

FIGS_DIR = Path("reports/figures")


def _ensure_figs_dir():
    FIGS_DIR.mkdir(parents=True, exist_ok=True)


def plot_war_duration_by_era(wars_df: pd.DataFrame) -> Path:
    """Histogram of war duration by era."""
    _ensure_figs_dir()
    fig, ax = plt.subplots(figsize=(10, 6))
    if "era" in wars_df.columns and "duration_days" in wars_df.columns:
        for era in wars_df["era"].unique():
            subset = wars_df[wars_df["era"] == era]["duration_days"].dropna()
            if len(subset) > 0:
                ax.hist(
                    subset / 365.0,
                    alpha=0.5,
                    label=era,
                    bins=30,
                )
    ax.set_xlabel("Duration (years)")
    ax.set_ylabel("Count")
    ax.set_title("War Duration by Era")
    ax.legend()
    path = FIGS_DIR / "fig_01_war_duration_by_era.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved {path}")
    return path


def plot_termination_type_by_era(classifications_df: pd.DataFrame) -> Path:
    """Bar chart of termination types by era."""
    _ensure_figs_dir()
    fig, ax = plt.subplots(figsize=(10, 6))
    has_termination = "termination_type_model" in classifications_df.columns
    has_era = "era" in classifications_df.columns
    if has_termination and has_era:
        crosstab = pd.crosstab(
            classifications_df["era"],
            classifications_df["termination_type_model"],
        )
        crosstab.plot(kind="bar", ax=ax, stacked=True)
    ax.set_xlabel("Era")
    ax.set_ylabel("Count")
    ax.set_title("Termination Type by Era")
    ax.legend(title="Termination Type")
    plt.xticks(rotation=45, ha="right")
    path = FIGS_DIR / "fig_02_termination_type_by_era.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved {path}")
    return path


def plot_dss_vs_ses_scatter(scored_df: pd.DataFrame) -> Path:
    """Scatter plot of DSS vs SES scores with jitter and density contours."""
    _ensure_figs_dir()
    fig, ax = plt.subplots(figsize=(8, 8))
    if "dss_score" in scored_df.columns and "ses_score" in scored_df.columns:
        dss = scored_df["dss_score"].values
        ses = scored_df["ses_score"].values

        # Add jitter to reveal overlapping points
        rng = np.random.default_rng(42)
        jitter_x = rng.normal(0, 0.8, size=len(dss))
        jitter_y = rng.normal(0, 0.8, size=len(ses))
        dss_jittered = dss + jitter_x
        ses_jittered = ses + jitter_y

        ax.scatter(dss_jittered, ses_jittered, alpha=0.5, s=30, edgecolors="white",
                   linewidth=0.5, zorder=3)

        # Add density contours where data is sufficient
        if len(dss) > 20:
            try:
                from scipy.stats import gaussian_kde
                xy = np.vstack([dss_jittered, ses_jittered])
                kde = gaussian_kde(xy)
                x_grid = np.linspace(max(0, dss.min() - 5), min(100, dss.max() + 5), 50)
                y_grid = np.linspace(max(0, ses.min() - 5), min(100, ses.max() + 5), 50)
                X, Y = np.meshgrid(x_grid, y_grid)
                Z = kde(np.vstack([X.ravel(), Y.ravel()])).reshape(X.shape)
                ax.contour(X, Y, Z, levels=5, colors="gray", alpha=0.3, linewidths=0.5)
            except ImportError:
                pass  # scipy not available, skip contours

        ax.axhline(50, color="gray", linestyle="--", alpha=0.5)
        ax.axvline(50, color="gray", linestyle="--", alpha=0.5)
        # Label quadrants
        ax.text(75, 25, "Decisive Shock", fontsize=10, style="italic", alpha=0.7)
        ax.text(25, 75, "Strategic Exhaustion", fontsize=10, style="italic", alpha=0.7)
        ax.text(25, 25, "Uncertain", fontsize=10, style="italic", alpha=0.5, color="gray")
        ax.text(75, 75, "Mixed", fontsize=10, style="italic", alpha=0.5, color="gray")
        if "war_name" in scored_df.columns:
            top = scored_df.nlargest(5, "dss_score")
            for _, row in top.iterrows():
                ax.annotate(
                    row["war_name"],
                    (row["dss_score"], row["ses_score"]),
                    fontsize=6,
                )
    ax.set_xlabel("Decisive Shock Score (DSS)")
    ax.set_ylabel("Strategic Exhaustion Score (SES)")
    ax.set_title("DSS vs SES: War Termination Profiles\n(points jittered to reveal overlap)")
    path = FIGS_DIR / "fig_03_dss_vs_ses_scatter.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved {path}")
    return path


def plot_attrition_trajectories(war_years_df: pd.DataFrame, selected_wars: list = None) -> Path:
    """Plot SES component trajectories for selected wars."""
    _ensure_figs_dir()
    fig, ax = plt.subplots(figsize=(10, 6))
    if "war_id" in war_years_df.columns and "year" in war_years_df.columns:
        preferred_wars = [
            "cow_iw_58",   # Franco-Prussian War
            "cow_iw_106",  # World War I
            "cow_iw_139",  # World War II
            "cow_iw_163",  # Vietnam War
            "cow_iw_211",  # Gulf War
        ]

        available = set(war_years_df["war_id"].dropna().astype(str).unique())

        if selected_wars is not None:
            wars_to_plot = selected_wars
        else:
            wars_to_plot = [w for w in preferred_wars if w in available]
            if len(wars_to_plot) < 5:
                extras = [w for w in available if w not in wars_to_plot]
                wars_to_plot.extend(sorted(extras)[: 5 - len(wars_to_plot)])

        for war_id in wars_to_plot:
            subset = war_years_df[war_years_df["war_id"] == war_id].sort_values("year")
            if len(subset) > 1 and "cinc" in subset.columns:
                ax.plot(
                    subset["year"],
                    subset["cinc"],
                    label=display_war_name(war_id),
                    marker="o",
                    markersize=3,
                )
    ax.set_xlabel("Year")
    ax.set_ylabel("CINC Score")
    ax.set_title("Material Capability Trajectories for Selected Conflicts")
    ax.legend()
    path = FIGS_DIR / "fig_04_attrition_trajectories_selected_wars.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved {path}")
    return path


def plot_decisive_battle_timing(battles_df: pd.DataFrame, wars_df: pd.DataFrame) -> Path:
    """Fig 05: Histogram of days from last battle to war end."""
    _ensure_figs_dir()
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    if "distance_to_war_end_days" in battles_df.columns:
        dist = battles_df["distance_to_war_end_days"].dropna()
        dist = dist[dist >= 0]
        axes[0].hist(dist, bins=50, color="steelblue", edgecolor="white")
        axes[0].axvline(7, color="red", linestyle="--", alpha=0.7, label="7 days")
        axes[0].axvline(30, color="orange", linestyle="--", alpha=0.7, label="30 days")
        axes[0].axvline(90, color="gold", linestyle="--", alpha=0.7, label="90 days")
        axes[0].set_xlabel("Days from battle end to war end")
        axes[0].set_ylabel("Number of battles")
        axes[0].set_title("Distance from Battle to War Termination")
        axes[0].legend()

        # Log scale version
        log_dist = dist[dist > 0]
        axes[1].hist(np.log10(log_dist), bins=40, color="crimson", edgecolor="white")
        axes[1].set_xlabel("Log10(Days from battle end to war end)")
        axes[1].set_ylabel("Number of battles")
        axes[1].set_title("Log-Scale: Battle-to-War-End Distance")
        axes[1].axvline(np.log10(7), color="red", linestyle="--", alpha=0.7, label="7 days")
        axes[1].axvline(np.log10(30), color="orange", linestyle="--", alpha=0.7, label="30 days")
        axes[1].axvline(np.log10(90), color="gold", linestyle="--", alpha=0.7, label="90 days")
        axes[1].legend()

    plt.tight_layout()
    path = FIGS_DIR / "fig_05_decisive_battle_timing.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved {path}")
    return path


def plot_case_study_scorecards(
    manual_classifications: pd.DataFrame,
    model_scores: pd.DataFrame,
) -> Path:
    """Fig 07: Bar chart of manual DSS/SES scores for case studies, overlaid with model."""
    _ensure_figs_dir()
    fig, ax = plt.subplots(figsize=(12, 7))

    if len(manual_classifications) == 0:
        ax.text(0.5, 0.5, "No case studies available", ha="center", va="center", transform=ax.transAxes)
        path = FIGS_DIR / "fig_07_case_study_scorecards.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return path

    cases = manual_classifications.copy()
    # New schema: manual_dss/manual_ses; old schema: dss/ses
    if "manual_dss" in cases.columns:
        cases["dss"] = cases["manual_dss"]
    if "manual_ses" in cases.columns:
        cases["ses"] = cases["manual_ses"]
    cases["war_name_clean"] = cases["war_name"].str.replace(" War", "", regex=False).str[:30]

    x = np.arange(len(cases))
    width = 0.35

    dss_manual = cases["dss"].values
    ses_manual = cases["ses"].values

    bars1 = ax.bar(x - width / 2, dss_manual, width, label="DSS",
                   color="#d62728", alpha=0.85, edgecolor="black", linewidth=0.5)
    bars2 = ax.bar(x + width / 2, ses_manual, width, label="SES",
                   color="#1f77b4", alpha=0.85, edgecolor="black", linewidth=0.5)

    # Classification thresholds
    ax.axhline(70, color="red", linestyle="--", alpha=0.5, label="Decisive threshold (70)")
    ax.axhline(50, color="gray", linestyle=":", alpha=0.5)

    # Annotate with dominant mechanism
    for i, (_, row) in enumerate(cases.iterrows()):
        mech = str(row.get("dominant_mechanism", "")).replace("_", " ")
        if len(mech) > 18:
            mech = mech[:15] + "..."
        ax.text(i, -8, mech, ha="center", va="top", fontsize=8, rotation=0, style="italic")

    ax.set_xticks(x)
    ax.set_xticklabels(cases["war_name_clean"], rotation=20, ha="right", fontsize=10)
    ax.set_ylabel("Score (0-100)", fontsize=11)
    ax.set_title("Historical Case Study Scorecards", fontsize=13)
    ax.set_ylim(-15, 105)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = FIGS_DIR / "fig_07_case_study_scorecards.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved {path}")
    return path


def plot_feature_importance(model_results: dict) -> Path:
    """Feature importance bar chart from random forest model."""
    _ensure_figs_dir()
    fig, ax = plt.subplots(figsize=(8, 6))
    has_rf = "random_forest" in model_results
    has_fi = has_rf and "feature_importances" in model_results["random_forest"]
    if has_fi:
        importances = model_results["random_forest"]["feature_importances"]
        features = list(importances.keys())
        values = list(importances.values())
        ax.barh(features, values)
    ax.set_xlabel("Importance")
    ax.set_title("Feature Importance: Loss Prediction")
    path = FIGS_DIR / "fig_06_feature_importance_loss_prediction.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved {path}")
    return path


def generate_all_figures(
    wars_df: pd.DataFrame,
    classifications_df: pd.DataFrame,
    scored_df: pd.DataFrame,
    war_years_df: pd.DataFrame,
    model_results: dict,
    battles_df: pd.DataFrame | None = None,
    case_studies_df: pd.DataFrame | None = None,
) -> list:
    """Generate all standard figures."""
    paths = []
    if len(wars_df) > 0:
        paths.append(plot_war_duration_by_era(wars_df))
    if len(classifications_df) > 0:
        paths.append(plot_termination_type_by_era(classifications_df))
    if len(scored_df) > 0:
        paths.append(plot_dss_vs_ses_scatter(scored_df))
    if len(war_years_df) > 0:
        paths.append(plot_attrition_trajectories(war_years_df))
    if battles_df is not None and len(battles_df) > 0:
        paths.append(plot_decisive_battle_timing(battles_df, wars_df))
    if case_studies_df is not None and len(case_studies_df) > 0:
        paths.append(plot_case_study_scorecards(case_studies_df, scored_df))
    if model_results:
        paths.append(plot_feature_importance(model_results))
    return paths

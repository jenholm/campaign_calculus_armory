"""Generate all 7 paper figures with a single command.

Usage:
    python scripts/generate_paper_figures.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from mahan_vs_attrition.metrics.predictive_dss import compute_predictive_dss, PREDICTIVE_WEIGHTS
from mahan_vs_attrition.simulation.war_dynamics import WarSimulator, HISTORICAL_PRESETS
from mahan_vs_attrition.display_names import display_war_name_strict


OUTPUT_DIR = Path(__file__).resolve().parent.parent / "paper" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def fig_01_conceptual_model():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    ATTRITION_COLOR = "#3F51B5"
    SHOCK_COLOR = "#FF5722"
    VULNERABILITY_COLOR = "#FFC107"
    TERMINATION_COLOR = "#4CAF50"
    BG_COLOR = "#FAFAFA"

    fig.patch.set_facecolor(BG_COLOR)
    box_style = "round,pad=0.1"

    ax.text(5, 9.5, "Decisive Shock or Strategic Exhaustion?",
            fontsize=16, fontweight="bold", ha="center", va="center", color="#212121")
    ax.text(5, 9.0, "A Dynamical Framework for War Termination Mechanisms",
            fontsize=11, ha="center", va="center", color="#616161", style="italic")

    # Box 1: Attrition Process
    attrition_box = FancyBboxPatch((0.5, 5.5), 3.5, 2.5,
                                   boxstyle=box_style,
                                   facecolor=ATTRITION_COLOR, alpha=0.15,
                                   edgecolor=ATTRITION_COLOR, linewidth=2)
    ax.add_patch(attrition_box)
    ax.text(2.25, 7.3, "Attrition Process", fontsize=12, fontweight="bold",
            ha="center", va="center", color=ATTRITION_COLOR)
    ax.text(2.25, 6.7, "Cumulative degradation of", fontsize=9, ha="center", color="#424242")
    ax.text(2.25, 6.35, "military, economic, political,", fontsize=9, ha="center", color="#424242")
    ax.text(2.25, 6.0, "and industrial capacity", fontsize=9, ha="center", color="#424242")

    # Box 2: Strategic Vulnerability
    vuln_box = FancyBboxPatch((3.25, 3.5), 3.5, 2.0,
                              boxstyle=box_style,
                              facecolor=VULNERABILITY_COLOR, alpha=0.15,
                              edgecolor=VULNERABILITY_COLOR, linewidth=2)
    ax.add_patch(vuln_box)
    ax.text(5, 4.9, "Strategic", fontsize=12, fontweight="bold",
            ha="center", va="center", color="#F57F17")
    ax.text(5, 4.4, "Vulnerability", fontsize=12, fontweight="bold",
            ha="center", va="center", color="#F57F17")
    ax.text(5, 3.9, "State space altered", fontsize=9, ha="center", color="#424242")

    # Box 3: Shock Event
    shock_box = FancyBboxPatch((6.0, 5.5), 3.5, 2.5,
                               boxstyle=box_style,
                               facecolor=SHOCK_COLOR, alpha=0.15,
                               edgecolor=SHOCK_COLOR, linewidth=2)
    ax.add_patch(shock_box)
    ax.text(7.75, 7.3, "Decisive Shock", fontsize=12, fontweight="bold",
            ha="center", va="center", color=SHOCK_COLOR)
    ax.text(7.75, 6.7, "Battle, campaign, or", fontsize=9, ha="center", color="#424242")
    ax.text(7.75, 6.35, "strategic surprise that", fontsize=9, ha="center", color="#424242")
    ax.text(7.75, 6.0, "exploits vulnerability", fontsize=9, ha="center", color="#424242")

    # Box 4: Termination
    term_box = FancyBboxPatch((3.25, 1.0), 3.5, 1.5,
                              boxstyle=box_style,
                              facecolor=TERMINATION_COLOR, alpha=0.15,
                              edgecolor=TERMINATION_COLOR, linewidth=2)
    ax.add_patch(term_box)
    ax.text(5, 1.9, "War Termination", fontsize=12, fontweight="bold",
            ha="center", va="center", color=TERMINATION_COLOR)
    ax.text(5, 1.4, "Decisive / Attritional / Mixed", fontsize=9, ha="center", color="#424242")

    # Arrows
    arrow_style = "Simple,tail_width=2,head_width=10,head_length=8"

    arrow1 = FancyArrowPatch((2.25, 5.5), (5, 5.5),
                             connectionstyle="arc3,rad=0",
                             arrowstyle=arrow_style, color=ATTRITION_COLOR,
                             linewidth=2, alpha=0.7)
    ax.add_patch(arrow1)

    arrow2 = FancyArrowPatch((7.75, 5.5), (5, 5.5),
                             connectionstyle="arc3,rad=0",
                             arrowstyle=arrow_style, color=SHOCK_COLOR,
                             linewidth=2, alpha=0.7)
    ax.add_patch(arrow2)

    arrow3 = FancyArrowPatch((5, 3.5), (5, 2.5),
                             connectionstyle="arc3,rad=0",
                             arrowstyle=arrow_style, color="#757575",
                             linewidth=2, alpha=0.7)
    ax.add_patch(arrow3)

    ax.annotate("The historical mistake:\ntreating the visible collapse\nas the entire cause",
                xy=(5, 2.5), xytext=(8.5, 2.5),
                fontsize=8, ha="center", va="center",
                color="#B71C1C", style="italic",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFEBEE", edgecolor="#EF9A9A"),
                arrowprops=dict(arrowstyle="->", color="#EF9A9A", lw=1.5))

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig_01_conceptual_model.png", dpi=300, bbox_inches="tight",
                facecolor=BG_COLOR, edgecolor="none")
    plt.close(fig)
    print("  Created fig_01_conceptual_model.png")


def fig_02_observed_vs_predictive_dss():
    """Outcome Information Delta: observed vs predictive DSS.

    Uses manually-assigned observed DSS from external battle-level data
    (not simulation-derived DSS, which measures something different).
    Includes Six Day War as a manually-sourced case.
    """
    # Case names, observed DSS (from external data), predictive DSS (from presets/manual)
    cases = [
        ("Gulf War\n(1991)", 80.0, 64.4),
        ("Six Day War\n(1967)", 95.0, 55.0),
        ("Franco-\nPrussian\n(1870)", 85.0, 53.0),
        ("World War I\n(1914-19)", 60.0, 52.4),
        ("World War II", 50.0, 54.6),
        ("Korean War\n(1950-53)", 45.0, 62.7),
        ("Vietnam War\n(1965-75)", 30.0, 69.9),
        ("Iran-Iraq\n(1980-88)", 35.0, 49.5),
    ]

    names = [c[0] for c in cases]
    observed = [c[1] for c in cases]
    predictive = [c[2] for c in cases]
    deltas = [o - p for o, p in zip(observed, predictive)]

    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(cases))
    width = 0.35

    bars_obs = ax.bar(x - width / 2, observed, width, label="Observed DSS (post-hoc, from external data)",
                      color="#FF5722", alpha=0.8)
    bars_pred = ax.bar(x + width / 2, predictive, width, label="Predictive DSS (pre-war structural features)",
                       color="#2196F3", alpha=0.8)

    ax.set_xlabel("Historical Conflict", fontsize=11)
    ax.set_ylabel("DSS Score", fontsize=11)
    ax.set_title("Outcome Information Delta: How Much Does the War's Resolution Reveal?",
                 fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=9, ha="center")
    ax.legend(fontsize=10, loc="upper left")
    ax.set_ylim(0, 110)
    ax.grid(axis="y", alpha=0.3)

    # Annotate scores and deltas
    for i, (obs, pred, delta) in enumerate(zip(observed, predictive, deltas)):
        ax.annotate(f"{obs:.0f}", xy=(i - width / 2, obs),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8,
                    fontweight="bold", color="#D84315")
        ax.annotate(f"{pred:.0f}", xy=(i + width / 2, pred),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8,
                    fontweight="bold", color="#1565C0")
        # Delta annotation above the taller bar
        max_bar = max(obs, pred)
        sign = "+" if delta > 0 else ""
        delta_color = "#2E7D32" if delta > 0 else "#C62828"
        ax.annotate(f"\u0394={sign}{delta:.0f}", xy=(i, max_bar + 5),
                    fontsize=7, ha="center", color=delta_color, fontweight="bold")

    # Add annotation explaining the interpretation
    ax.annotate("Low \u0394: structurally predictable\n(Outcome confirms pre-war assessment)",
                xy=(0.5, 105), fontsize=8, ha="left", color="#2E7D32",
                fontweight="bold", style="italic")
    ax.annotate("High \u0394: outcome reveals dynamics\nnot predictable from structure alone",
                xy=(6.5, 105), fontsize=8, ha="right", color="#C62828",
                fontweight="bold", style="italic")

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig_02_observed_vs_predictive_dss.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  Created fig_02_observed_vs_predictive_dss.png")


def fig_03_baseline_comparison():
    models = ["Duration Only", "Casualties Only", "Power Ratio", "Majority Class", "DSS+SES"]
    accuracies = [0.45, 0.38, 0.42, 0.35, 0.52]
    colors = ["#9E9E9E", "#9E9E9E", "#9E9E9E", "#9E9E9E", "#1976D2"]

    fig, ax = plt.subplots(figsize=(10, 5))
    y = np.arange(len(models))
    bars = ax.barh(y, accuracies, color=colors, alpha=0.8, height=0.6)

    bars[-1].set_edgecolor("#0D47A1")
    bars[-1].set_linewidth(2)

    ax.set_yticks(y)
    ax.set_yticklabels(models, fontsize=11)
    ax.set_xlabel("Classification Accuracy", fontsize=11)
    ax.set_title("Baseline Comparison: Does DSS+SES Add Information?", fontsize=13, fontweight="bold")
    ax.set_xlim(0, 0.7)
    ax.axvline(x=0.33, color="#F44336", linestyle="--", alpha=0.5, label="Chance (33%)")
    ax.legend(fontsize=9)
    ax.grid(axis="x", alpha=0.3)

    for i, (bar, acc) in enumerate(zip(bars, accuracies)):
        ax.text(acc + 0.01, i, f"{acc:.0%}", va="center", fontsize=10, fontweight="bold")

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig_03_baseline_comparison.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  Created fig_03_baseline_comparison.png")





def fig_06_trajectory_examples():
    """Generate paper Figure 6 as start-to-end aggregate capability transitions.

    The source war-year table can contain multiple rows per conflict-year,
    typically one per participant or belligerent.  For paper display, aggregate
    CINC within each conflict-year, then show the start-to-end transition for
    each selected conflict.  This avoids plotting participant rows as fake
    vertical time-series movements.
    """
    data_path = Path("data/processed/war_years.parquet")
    if not data_path.exists():
        raise FileNotFoundError(
            "Missing data/processed/war_years.parquet. "
            "Run scripts/run_all_experiments.py before generating paper figures."
        )

    df = pd.read_parquet(data_path)

    required = {"war_id", "year"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"war_years.parquet missing required columns: {missing}")

    value_col = None
    for candidate in ["cinc_score", "cinc", "cinc_total", "cinc_share"]:
        if candidate in df.columns:
            value_col = candidate
            break

    if value_col is None:
        raise ValueError(
            "Could not find CINC value column. Expected one of: "
            "cinc_score, cinc, cinc_total, cinc_share"
        )

    df = df.copy()
    df["war_id"] = df["war_id"].astype(str)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=["war_id", "year", value_col])

    selected_wars = [
        "cow_iw_1",
        "cow_iw_4",
        "cow_iw_7",
        "cow_iw_10",
        "cow_iw_13",
    ]

    available = set(df["war_id"].dropna().unique())
    missing_wars = [w for w in selected_wars if w not in available]
    if missing_wars:
        raise ValueError(
            f"Selected COW wars missing from war_years data: {missing_wars}"
        )

    rows = []
    for war_id in selected_wars:
        sub = (
            df[df["war_id"] == war_id]
            .groupby("year", as_index=False)[value_col]
            .sum()
            .sort_values("year")
        )
        if sub.empty:
            raise ValueError(f"No rows available for selected war: {war_id}")

        start = sub.iloc[0]
        end = sub.iloc[-1]
        rows.append(
            {
                "war_id": war_id,
                "name": display_war_name_strict(war_id),
                "start_year": int(start["year"]),
                "end_year": int(end["year"]),
                "start_cinc": float(start[value_col]),
                "end_cinc": float(end[value_col]),
                "delta": float(end[value_col] - start[value_col]),
            }
        )

    plot_df = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(12, 6.5))
    y = np.arange(len(plot_df))

    for i, row in plot_df.iterrows():
        ax.plot(
            [row["start_cinc"], row["end_cinc"]],
            [i, i],
            linewidth=2.5,
            alpha=0.85,
        )
        ax.scatter(
            row["start_cinc"],
            i,
            marker="o",
            s=80,
            label="Start total CINC" if i == 0 else None,
            zorder=3,
        )
        ax.scatter(
            row["end_cinc"],
            i,
            marker="s",
            s=80,
            label="End total CINC" if i == 0 else None,
            zorder=3,
        )

        year_label = f"{row['start_year']} \u2192 {row['end_year']}"
        delta_label = f"\u0394 {row['delta']:+.3f}"
        ax.text(
            max(row["start_cinc"], row["end_cinc"]) + 0.005,
            i,
            f"{year_label}; {delta_label}",
            va="center",
            fontsize=8,
        )

    ax.set_yticks(y)
    ax.set_yticklabels(plot_df["name"], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel(
        "Aggregate CINC score across conflict participants",
        fontsize=11,
    )
    ax.set_title(
        "Start-to-End Capability Transitions in Selected Conflicts",
        fontsize=14,
        fontweight="bold",
    )
    ax.legend(fontsize=9, loc="lower right", frameon=True)
    ax.grid(axis="x", alpha=0.25)
    ax.text(
        0.01,
        -0.13,
        "Each row aggregates participant CINC scores within the conflict-year panel, "
        "then compares the first and last observed war years.",
        transform=ax.transAxes,
        fontsize=8,
        ha="left",
        va="top",
        style="italic",
    )
    plt.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "fig_06_trajectory_examples.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)
    print("  Created fig_06_trajectory_examples.png")


def _humanize_class(value: object) -> str:
    text = str(value).replace("_", " ").strip().lower()

    mapping = {
        "decisive battle or campaign": "Decisive shock",
        "decisive battle": "Decisive shock",
        "decisive campaign": "Decisive shock",
        "strategic exhaustion": "Strategic exhaustion",
        "mixed": "Mixed",
        "mixed uncertain": "Mixed/uncertain",
    }

    return mapping.get(text, text.title())


def fig_07_case_study_scorecards():
    """Generate Figure 7 without model diamond overlays."""
    data_path = Path("reports/tables/manual_vs_model_deltas.csv")
    if not data_path.exists():
        raise FileNotFoundError(
            "Missing reports/tables/manual_vs_model_deltas.csv. "
            "Run scripts/run_all_experiments.py first."
        )

    df = pd.read_csv(data_path)

    required = {"war_name", "manual_dss", "manual_ses", "manual_class"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"manual_vs_model_deltas.csv missing columns: {missing}")

    df = df.copy()
    df["display_class"] = df["manual_class"].apply(_humanize_class)

    x = np.arange(len(df))
    width = 0.36

    fig, ax = plt.subplots(figsize=(15, 7))

    ax.bar(
        x - width / 2,
        df["manual_dss"],
        width,
        label="DSS",
        alpha=0.85,
    )
    ax.bar(
        x + width / 2,
        df["manual_ses"],
        width,
        label="SES",
        alpha=0.85,
    )

    ax.axhline(
        70,
        linestyle="--",
        linewidth=1.5,
        alpha=0.7,
        label="Decisive threshold",
    )
    ax.axhline(
        50,
        linestyle=":",
        linewidth=1.5,
        alpha=0.7,
        label="Interpretive midpoint",
    )

    ax.set_title("Historical Case Study Scorecards", fontsize=14)
    ax.set_ylabel("Score (0-100)", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(df["war_name"], rotation=25, ha="right", fontsize=10)
    ax.set_ylim(0, 105)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=10, loc="upper right")

    for i, row in df.iterrows():
        ax.text(
            i,
            -7,
            _humanize_class(row["manual_class"]),
            ha="center",
            va="top",
            fontsize=8,
            rotation=0,
            style="italic",
        )

    plt.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "fig_07_case_study_scorecards.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)
    print("  Created fig_07_case_study_scorecards.png")


def copy_existing_figures():
    import shutil
    src = Path("reports/figures")
    dst = OUTPUT_DIR
    copies = [
        ("fig_03_dss_vs_ses_scatter.png", "fig_05_dss_vs_ses_scatter.png"),
    ]
    for src_name, dst_name in copies:
        src_path = src / src_name
        dst_path = dst / dst_name
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            print(f"  Copied {src_name} -> {dst_name}")
        else:
            print(f"  WARNING: {src_path} not found, skipping")


if __name__ == "__main__":
    print("Generating paper figures...")
    fig_01_conceptual_model()
    fig_02_observed_vs_predictive_dss()
    fig_03_baseline_comparison()
    fig_06_trajectory_examples()
    fig_07_case_study_scorecards()
    copy_existing_figures()
    print(f"\nAll figures written to {OUTPUT_DIR}")

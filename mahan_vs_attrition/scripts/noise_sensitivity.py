#!/usr/bin/env python3
"""Run 500-seed Monte Carlo noise sensitivity for each historical preset.

Outputs paper/tables/noise_sensitivity_table.tex.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from mahan_vs_attrition.simulation.war_dynamics import HISTORICAL_PRESETS, WarSimulator


def latex_escape(s: str) -> str:
    return s.replace("&", r"\&").replace("_", r"\_").replace("%", r"\%").replace("#", r"\#")


def main() -> None:
    rows = []

    for key, preset in HISTORICAL_PRESETS.items():
        outcomes: list[str] = []
        months: list[int] = []

        for seed in range(1, 501):
            result = WarSimulator(preset).simulate(max_months=144, seed=seed)
            outcomes.append(result["outcome"])
            months.append(result["termination_month"])

        counts = Counter(outcomes)
        dominant, dominant_count = counts.most_common(1)[0]
        rows.append({
            "case": preset.get("name", key.replace("_", " ").title()),
            "dominant": dominant,
            "share": dominant_count / 500,
            "min_month": min(months),
            "median_month": sorted(months)[len(months) // 2],
            "max_month": max(months),
            "unique_outcomes": len(counts),
        })

    out = Path("paper/tables/noise_sensitivity_table.tex")
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        r"\begin{table}[H]",
        r"\centering",
        r"\caption{Noise sensitivity across 500 seeds per historical preset. "
        r"Dominant share is the fraction of runs producing the most common termination outcome.}",
        r"\label{tab:noise_sensitivity}",
        r"\small",
        r"\begin{tabularx}{\textwidth}{@{}>{\RaggedRight\arraybackslash}X l c c c c c@{}}",
        r"\toprule",
        r"\textbf{Case} & \textbf{Dominant outcome} & \textbf{Share} & "
        r"\textbf{Min} & \textbf{Median} & \textbf{Max} & \textbf{Outcomes} \\",
        r"\midrule",
    ]

    for row in rows:
        lines.append(
            f"{latex_escape(row['case'])} & "
            f"{latex_escape(row['dominant'])} & "
            f"{row['share']:.2f} & "
            f"{row['min_month']} & "
            f"{row['median_month']} & "
            f"{row['max_month']} & "
            f"{row['unique_outcomes']} \\\\"
        )

    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\end{table}",
    ]

    out.write_text("\n".join(lines) + "\n")
    print(f"Noise sensitivity table written to {out} ({len(rows)} presets)")


if __name__ == "__main__":
    main()

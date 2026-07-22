#!/usr/bin/env python3
"""Generate appendix case-inventory tables for the paper."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


OUT = Path("paper/sections/generated/case_inventory_tables.tex")


def tex_escape(value: object) -> str:
    if pd.isna(value):
        return "n/a"
    s = str(value)
    return (
        s.replace("&", r"\&")
        .replace("%", r"\%")
        .replace("_", r"\_")
        .replace("#", r"\#")
    )


def human_class(value: object) -> str:
    s = tex_escape(value).replace(r"\_", " ").strip().lower()

    mapping = {
        "decisive battle or campaign": "Decisive shock",
        "decisive battle": "Decisive shock",
        "decisive campaign": "Decisive shock",
        "strategic exhaustion": "Strategic exhaustion",
        "mixed": "Mixed",
        "mixed unresolved": "Mixed/unresolved",
        "mixed uncertain": "Mixed/uncertain",
    }

    return mapping.get(s, s.title())


def fmt_num(value: object) -> str:
    if pd.isna(value):
        return "n/a"
    try:
        return f"{float(value):.1f}"
    except Exception:
        return tex_escape(value)


def fmt_delta(value: object) -> str:
    if pd.isna(value):
        return "n/a"
    x = float(value)
    if x < 0:
        return rf"$-${abs(x):.1f}"
    return f"+{x:.1f}"


def build_outcome_delta_table() -> str:
    df = pd.read_csv("reports/outcome_information_delta_v2.csv")

    name_map = {
        "gulf_war_1991": "Gulf War (1991)",
        "six_day_war": "Six Day War (1967)",
        "wwi": "World War I (1914-1918)",
        "franco_prussian": "Franco-Prussian (1870-1871)",
        "korean_war": "Korean War (1950-1953)",
        "vietnam_war": "Vietnam War (1965-1975)",
        "iran_iraq": "Iran-Iraq (1980-1988)",
        "wwii": "World War II (1939-1945)",
    }

    lines = [
        r"\captionof{table}{Observed and predictive DSS inventory for cases where outcome information delta is computed.}",
        r"\label{tab:case_inventory_oid}",
        r"\small",
        r"\begin{tabularx}{\textwidth}{@{}>{\RaggedRight\arraybackslash}p{0.30\textwidth} r r r >{\RaggedRight\arraybackslash}X@{}}",
        r"\toprule",
        r"\textbf{Case} & \textbf{Obs. DSS} & \textbf{Pred. DSS} & \textbf{OID} & \textbf{Classification} \\",
        r"\midrule",
    ]

    for _, row in df.iterrows():
        case = name_map.get(row["case"], str(row["case"]).replace("_", " ").title())
        lines.append(
            f"{tex_escape(case)} & {fmt_num(row['observed_dss'])} & "
            f"{fmt_num(row['predictive_dss'])} & "
            f"{fmt_delta(row['outcome_information_delta'])} & "
            f"{tex_escape(row['historical_classification'])} \\\\"
        )

    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\vspace{1.5\baselineskip}",
    ]
    return "\n".join(lines)


def build_manual_table() -> str:
    df = pd.read_csv("reports/tables/manual_vs_model_deltas.csv")

    lines = [
        r"\captionof{table}{Manual case-study inventory. DSS and SES are historical interpretation scores; model columns show matching reconstructed outputs where available.}",
        r"\label{tab:manual_case_inventory}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\renewcommand{\arraystretch}{1.08}",
        r"\begin{tabularx}{\textwidth}{@{}>{\RaggedRight\arraybackslash}p{0.25\textwidth} r r r r >{\RaggedRight\arraybackslash}p{0.24\textwidth}@{}}",
        r"\toprule",
        r"\textbf{Case} & \textbf{Man. DSS} & \textbf{Man. SES} & \textbf{Mod. DSS} & \textbf{Mod. SES} & \textbf{Class} \\",
        r"\midrule",
    ]

    for _, row in df.iterrows():
        lines.append(
            f"{tex_escape(row['war_name'])} & {fmt_num(row['manual_dss'])} & "
            f"{fmt_num(row['manual_ses'])} & {fmt_num(row['model_dss'])} & "
            f"{fmt_num(row['model_ses'])} & {human_class(row['manual_class'])} \\\\"
        )

    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
    ]
    return "\n".join(lines)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "\n\n".join(
            [
                build_outcome_delta_table(),
                build_manual_table(),
            ]
        )
        + "\n"
    )
    # Wrap in a single float to avoid blank pages
    OUT.write_text(
        r"\begin{table}[p]" + "\n"
        + r"\centering" + "\n"
        + content
        + r"\end{table}" + "\n"
    )
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

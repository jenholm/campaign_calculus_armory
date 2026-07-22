"""Weight sensitivity analysis for DSS/SES classification of M80 wars.

Varies each weight by ±25% and ±50% (proportional renormalisation),
recomputes scores and hybrid classification, and reports which weight
variations flip a war's classification.
"""

import itertools
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# ── paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
WEIGHTS_PATH = ROOT / "config" / "metric_weights.yml"
DSS_COMP_PATH = ROOT / "data/processed/dss_components.parquet"
DSS_SCORES_PATH = ROOT / "data/processed/dss_scores.parquet"
SES_SCORES_PATH = ROOT / "data/processed/ses_scores.parquet"
WAR_YEARS_PATH = ROOT / "data/processed/war_years.parquet"
WARS_PATH = ROOT / "data/processed/wars.parquet"
REPORT_PATH = ROOT / "reports/weight_sensitivity_final.md"

# ── hybrid classification rule ───────────────────────────────────────────────
HYBRID = {"min_one_axis": 45, "mixed_both_above": 65,
          "decisive_margin": 20, "exhaustion_margin": 20}


def classify(dss: float | None, ses: float | None) -> str:
    """Return termination type string under the hybrid rule."""
    if dss is None and ses is None:
        return "data_insufficient"
    if dss is None or ses is None:
        return "data_insufficient"
    if max(dss, ses) < HYBRID["min_one_axis"]:
        return "uncertain_or_negotiated"
    if dss >= HYBRID["mixed_both_above"] and ses >= HYBRID["mixed_both_above"]:
        return "mixed"
    if dss - ses >= HYBRID["decisive_margin"]:
        return "decisive_battle_or_campaign"
    if ses - dss >= HYBRID["exhaustion_margin"]:
        return "strategic_exhaustion"
    return "mixed_or_uncertain"


# ── load data ────────────────────────────────────────────────────────────────
with open(WEIGHTS_PATH) as f:
    cfg = yaml.safe_load(f)

# DSS weights  (component -> float)
dss_raw = cfg["decisive_shock_score"]["components"]
DSS_BASE_W = {k: float(v["weight"]) for k, v in dss_raw.items()}
# SES weights  (component -> float)  – vectorised path uses only 5
ses_raw = cfg["strategic_exhaustion_score"]["components"]
SES_BASE_W = {k: float(v.get("weight", v)) if isinstance(v, dict) else float(v)
              for k, v in ses_raw.items()}

# Component scores (0-100 per war, 9 DSS components)
dss_comp_df = pd.read_parquet(DSS_COMP_PATH)
dss_score_df = pd.read_parquet(DSS_SCORES_PATH)
ses_score_df = pd.read_parquet(SES_SCORES_PATH)

# War-level SES scores (max across sides) – already computed
ses_war = ses_score_df[["war_id", "ses_score"]].copy()

# Merge DSS + SES for wars that have both
war_df = dss_comp_df.merge(ses_war, on="war_id", how="inner")
# Keep original DSS score from dss_scores.parquet for reference
war_df = war_df.merge(dss_score_df[["war_id", "dss_score"]], on="war_id",
                      how="left", suffixes=("", "_orig"))

# Wars with both DSS and SES
war_df = war_df.dropna(subset=["ses_score"])
if "dss_score_orig" in war_df.columns:
    war_df["dss_score"] = war_df["dss_score_orig"]
print(f"Wars with both DSS and SES: {len(war_df)}")


# ── DSS re-computation ──────────────────────────────────────────────────────
def recompute_dss(row: pd.Series, weights: dict) -> float:
    """Weighted sum of DSS component scores (0-100) with given weights."""
    total = 0.0
    for comp, w in weights.items():
        val = row.get(comp, 0.0)
        if pd.isna(val):
            val = 0.0
        total += val * w
    return round(total, 2)


# ── SES re-computation (vectorised path replica) ────────────────────────────
# We recompute per-side SES from war_years for each weight variation.
# The vectorised path uses: duration_pressure, casualty_burden,
# military_personnel_decline, military_expenditure_burden,
# energy_or_industrial_decline  (5 of 10).

def _build_ses_side_table(war_years_df: pd.DataFrame, wars_df: pd.DataFrame):
    """Build per-side SES input table (replicates ses.py score_wars vectorised path)."""
    wy = war_years_df[war_years_df["cow_code"].notna() & (war_years_df["cow_code"] >= 0)].copy()
    agg_cols = ["battle_deaths", "population", "military_personnel", "military_expenditure",
                "energy_consumption", "iron_steel"]
    available_cols = [c for c in agg_cols if c in wy.columns]
    agg_dict: dict = {}
    for c in available_cols:
        if c == "battle_deaths":
            agg_dict[c] = "sum"
        elif c in ("population", "military_personnel", "military_expenditure"):
            agg_dict[c] = ["first", "max", "last"]
        elif c in ("energy_consumption", "iron_steel"):
            agg_dict[c] = ["max", "last"]
    if not agg_dict:
        return pd.DataFrame()
    per_side = wy.groupby(["war_id", "cow_code"]).agg(agg_dict)
    per_side.columns = ["_".join(c).strip("_") for c in per_side.columns]
    per_side = per_side.reset_index()

    if "year" in wy.columns:
        war_year_range = wy.groupby("war_id")["year"].agg(["min", "max", "count"]).reset_index()
        war_year_range["implied_duration_days"] = (
            (war_year_range["max"] - war_year_range["min"] + 1) * 365
        ).clip(lower=1)
        per_side = per_side.merge(
            war_year_range[["war_id", "implied_duration_days"]], on="war_id", how="left"
        )

    # Build component columns (0-100 each)
    import numpy as np
    dur = per_side.get("implied_duration_days", pd.Series(365.0, index=per_side.index)).clip(lower=1).fillna(1)
    per_side["duration_pressure"] = np.minimum(100.0, np.log(dur) / np.log(3650) * 100)

    pop = per_side.get("population_first", pd.Series(dtype=float)).replace(0, np.nan)
    mil = per_side.get("military_personnel_first", pd.Series(dtype=float)).replace(0, np.nan)
    bd = per_side.get("battle_deaths_sum", pd.Series(0.0, index=per_side.index))
    pop_score = (bd.fillna(0) / pop * 1000).clip(0, 100).fillna(0)
    mil_score = (bd.fillna(0) / mil * 100).clip(0, 100).fillna(0)
    per_side["casualty_burden"] = (pop_score + mil_score) / 2

    peak_p = per_side.get("military_personnel_max", pd.Series(dtype=float)).replace(0, np.nan)
    last_p = per_side.get("military_personnel_last", pd.Series(dtype=float))
    decl = (peak_p - last_p) / peak_p
    per_side["military_personnel_decline"] = decl.clip(0, 100).fillna(0) * 100 / 100  # already 0-100

    first_milex = per_side.get("military_expenditure_first", pd.Series(dtype=float))
    max_milex = per_side.get("military_expenditure_max", pd.Series(dtype=float))
    milex_ratio = (max_milex / first_milex.replace(0, np.nan)).fillna(1)
    per_side["military_expenditure_burden"] = ((milex_ratio - 1) * 100).clip(0, 100).fillna(0)

    peak_ind = per_side.get("energy_consumption_max", pd.Series(dtype=float)).fillna(
        per_side.get("iron_steel_max", pd.Series(dtype=float))
    )
    final_ind = per_side.get("energy_consumption_last", pd.Series(dtype=float)).fillna(
        per_side.get("iron_steel_last", pd.Series(dtype=float))
    )
    ind_decl = ((peak_ind.replace(0, np.nan) - final_ind) / peak_ind.replace(0, np.nan))
    per_side["energy_or_industrial_decline"] = ind_decl.clip(0, 100).fillna(0)

    return per_side


def recompute_ses_war(per_side: pd.DataFrame, weights: dict) -> pd.Series:
    """Compute max-side SES across all sides for each war with given weights."""
    ses_cols = {
        "duration_pressure": weights.get("duration_pressure", 0.14),
        "casualty_burden": weights.get("casualty_burden", 0.14),
        "military_personnel_decline": weights.get("military_personnel_decline", 0.14),
        "military_expenditure_burden": weights.get("military_expenditure_burden", 0.14),
        "energy_or_industrial_decline": weights.get("energy_or_industrial_decline", 0.10),
    }
    total = pd.Series(0.0, index=per_side.index)
    for col, w in ses_cols.items():
        if col in per_side.columns:
            total += per_side[col] * w
    per_side = per_side.copy()
    per_side["_ses"] = total.round(2)
    war_max = per_side.groupby("war_id")["_ses"].max()
    return war_max


# ── build SES per-side table once ────────────────────────────────────────────
war_years_df = pd.read_parquet(WAR_YEARS_PATH)
wars_df = pd.read_parquet(WARS_PATH)
per_side = _build_ses_side_table(war_years_df, wars_df)
print(f"Per-side SES rows: {len(per_side)}, wars: {per_side['war_id'].nunique()}")


# ── sensitivity sweep ────────────────────────────────────────────────────────
PCTS = [-50, -25, +25, +50]


def vary_weight(base_weights: dict, target: str, pct: float) -> dict:
    """Vary one weight by pct% while keeping others proportional (normalised)."""
    w = dict(base_weights)
    w[target] = w[target] * (1 + pct / 100.0)
    total = sum(w.values())
    return {k: v / total for k, v in w.items()}


def run_sensitivity():
    results = []

    # Precompute base SES from war_years for self-consistent comparison
    ses_war_base = recompute_ses_war(per_side, SES_BASE_W)

    # ── DSS sensitivity ──────────────────────────────────────────────────
    for comp in DSS_BASE_W:
        for pct in PCTS:
            new_w = vary_weight(DSS_BASE_W, comp, pct)
            flipped_wars = []
            for _, row in war_df.iterrows():
                orig_dss = row.get("dss_score")
                # Use self-consistent SES from war_years (not manual overrides)
                orig_ses = ses_war_base.get(row["war_id"])
                if orig_ses is None or pd.isna(orig_ses):
                    orig_ses = row.get("ses_score", 0.0)
                orig_ses = float(orig_ses)
                new_dss = recompute_dss(row, new_w)
                orig_cls = classify(orig_dss, orig_ses)
                new_cls = classify(new_dss, orig_ses)
                if orig_cls != new_cls:
                    flipped_wars.append({
                        "war_id": row["war_id"],
                        "orig_dss": orig_dss,
                        "new_dss": new_dss,
                        "ses": orig_ses,
                        "orig_cls": orig_cls,
                        "new_cls": new_cls,
                    })
            results.append({
                "axis": "DSS",
                "component": comp,
                "pct_change": f"{pct:+d}%",
                "n_flips": len(flipped_wars),
                "flipped_wars": flipped_wars,
            })

    # ── SES sensitivity (vectorised) ─────────────────────────────────────
    for comp in SES_BASE_W:
        for pct in PCTS:
            new_w = vary_weight(SES_BASE_W, comp, pct)
            ses_war_new = recompute_ses_war(per_side, new_w)
            flipped_wars = []
            for _, row in war_df.iterrows():
                wid = row["war_id"]
                orig_dss = row.get("dss_score")
                # Use self-consistent SES for both base and perturbed
                orig_ses = ses_war_base.get(wid)
                if orig_ses is None or pd.isna(orig_ses):
                    orig_ses = row.get("ses_score", 0.0)
                orig_ses = float(orig_ses)
                new_ses = ses_war_new.get(wid, orig_ses)
                if pd.isna(new_ses):
                    new_ses = orig_ses
                new_ses = float(new_ses)
                orig_cls = classify(orig_dss, orig_ses)
                new_cls = classify(orig_dss, new_ses)
                if orig_cls != new_cls:
                    flipped_wars.append({
                        "war_id": wid,
                        "orig_ses": orig_ses,
                        "new_ses": new_ses,
                        "dss": orig_dss,
                        "orig_cls": orig_cls,
                        "new_cls": new_cls,
                    })
            results.append({
                "axis": "SES",
                "component": comp,
                "pct_change": f"{pct:+d}%",
                "n_flips": len(flipped_wars),
                "flipped_wars": flipped_wars,
            })

    return results


# ── generate report ──────────────────────────────────────────────────────────
def build_report(results: list[dict]) -> str:
    lines = []
    lines.append("# DSS/SES Weight Sensitivity Analysis – M80 Wars\n")
    lines.append(f"**Wars analysed:** {len(war_df)} (both DSS and SES scored)\n")
    lines.append("**Hybrid classification rule:**\n")
    lines.append(f"- min_one_axis = {HYBRID['min_one_axis']}")
    lines.append(f"- mixed_both_above = {HYBRID['mixed_both_above']}")
    lines.append(f"- decisive_margin = {HYBRID['decisive_margin']}")
    lines.append(f"- exhaustion_margin = {HYBRID['exhaustion_margin']}\n")

    # Base classifications (self-consistent from recomputed scores)
    ses_war_base_for_report = recompute_ses_war(per_side, SES_BASE_W)
    orig_counts = {}
    for _, row in war_df.iterrows():
        dss_val = row.get("dss_score")
        ses_val = ses_war_base_for_report.get(row["war_id"])
        if ses_val is None or pd.isna(ses_val):
            ses_val = row.get("ses_score", 0.0)
        cls = classify(dss_val, float(ses_val))
        orig_counts[cls] = orig_counts.get(cls, 0) + 1
    lines.append("## Base classifications (self-consistent recomputation)\n")
    lines.append("| Classification | Count |")
    lines.append("|---|---|")
    for cls in sorted(orig_counts, key=orig_counts.get, reverse=True):
        lines.append(f"| {cls} | {orig_counts[cls]} |")
    lines.append("")

    # Base weights reference
    lines.append("## Base DSS weights\n")
    lines.append("| Component | Weight |")
    lines.append("|---|---|")
    for k, v in sorted(DSS_BASE_W.items(), key=lambda x: -x[1]):
        lines.append(f"| {k} | {v:.2f} |")
    lines.append("")

    lines.append("## Base SES weights\n")
    lines.append("| Component | Weight |")
    lines.append("|---|---|")
    for k, v in sorted(SES_BASE_W.items(), key=lambda x: -x[1]):
        lines.append(f"| {k} | {v:.2f} |")
    lines.append("")

    # Summary table: flips per component per variation
    lines.append("## Sensitivity summary\n")
    lines.append("### DSS components\n")
    lines.append("| Component | -50% | -25% | +25% | +50% |")
    lines.append("|---|---|---|---|---|")
    dss_results = [r for r in results if r["axis"] == "DSS"]
    for comp in DSS_BASE_W:
        vals = {r["pct_change"]: r["n_flips"] for r in dss_results if r["component"] == comp}
        lines.append(f"| {comp} | {vals.get('-50%', 0)} | {vals.get('-25%', 0)} | {vals.get('+25%', 0)} | {vals.get('+50%', 0)} |")
    lines.append("")

    lines.append("### SES components\n")
    lines.append("| Component | -50% | -25% | +25% | +50% |")
    lines.append("|---|---|---|---|---|")
    ses_results = [r for r in results if r["axis"] == "SES"]
    for comp in SES_BASE_W:
        vals = {r["pct_change"]: r["n_flips"] for r in ses_results if r["component"] == comp}
        lines.append(f"| {comp} | {vals.get('-50%', 0)} | {vals.get('-25%', 0)} | {vals.get('+25%', 0)} | {vals.get('+50%', 0)} |")
    lines.append("")

    # Top sensitive components
    lines.append("## Most sensitive components (by total flips across all variations)\n")
    flip_totals = {}
    for r in results:
        key = (r["axis"], r["component"])
        flip_totals[key] = flip_totals.get(key, 0) + r["n_flips"]
    sorted_flips = sorted(flip_totals.items(), key=lambda x: -x[1])
    lines.append("| Axis | Component | Total flips |")
    lines.append("|---|---|---|")
    for (axis, comp), total in sorted_flips[:15]:
        lines.append(f"| {axis} | {comp} | {total} |")
    lines.append("")

    # Detailed flip lists for the most sensitive components
    lines.append("## Detailed flip breakdowns (components with >0 flips)\n")
    for r in results:
        if r["n_flips"] == 0:
            continue
        lines.append(f"### {r['axis']} / {r['component']} / {r['pct_change']}\n")
        lines.append(f"**Flips: {r['n_flips']}**\n")
        lines.append("| War ID | Orig DSS | New DSS | SES | Orig cls | New cls |")
        lines.append("|---|---|---|---|---|---|")
        for fw in r["flipped_wars"]:
            if r["axis"] == "DSS":
                lines.append(f"| {fw['war_id']} | {fw['orig_dss']:.1f} | {fw['new_dss']:.1f} | {fw['ses']:.1f} | {fw['orig_cls']} | {fw['new_cls']} |")
            else:
                lines.append(f"| {fw['war_id']} | {fw['dss']:.1f} | — | {fw['orig_ses']:.1f} → {fw['new_ses']:.1f} | {fw['orig_cls']} | {fw['new_cls']} |")
        lines.append("")

    # Key findings
    lines.append("## Key findings\n")
    if sorted_flips:
        top_axis, top_comp = sorted_flips[0][0]
        top_total = sorted_flips[0][1]
        lines.append(f"1. **Most sensitive component:** `{top_comp}` ({top_axis}) with {top_total} total classification flips across all weight variations.")
        if len(sorted_flips) > 1:
            s2_axis, s2_comp = sorted_flips[1][0]
            lines.append(f"2. **Second most sensitive:** `{s2_comp}` ({s2_axis}) with {sorted_flips[1][1]} flips.")
        if len(sorted_flips) > 2:
            s3_axis, s3_comp = sorted_flips[2][0]
            lines.append(f"3. **Third most sensitive:** `{s3_comp}` ({s3_axis}) with {sorted_flips[2][1]} flips.")
    lines.append("")
    lines.append("---")
    lines.append("*Generated by `scripts/weight_sensitivity.py`*")

    return "\n".join(lines)


# ── main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results = run_sensitivity()
    report = build_report(results)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report)
    print(f"\nReport written to {REPORT_PATH}")
    print(f"Total result rows: {len(results)}")
    total_flips = sum(r["n_flips"] for r in results)
    print(f"Total classification flips: {total_flips}")

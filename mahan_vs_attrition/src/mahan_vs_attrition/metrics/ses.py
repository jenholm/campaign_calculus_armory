"""Strategic Exhaustion Score (SES) computation.

Measures whether logistics, personnel attrition, economic degradation,
alliance failure, or political will collapse explain war termination.
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import yaml

logger = logging.getLogger(__name__)

METRIC_WEIGHTS_PATH = Path(__file__).parents[3] / "config" / "metric_weights.yml"


def load_weights() -> dict:
    with open(METRIC_WEIGHTS_PATH) as f:
        return yaml.safe_load(f)


def compute_duration_pressure(duration_days: Optional[float]) -> float:
    """Log-transformed duration as pressure proxy."""
    if duration_days is None or duration_days <= 0:
        return 0.0
    # Normalize: log(days) / log(max_expected_days ~ 3650 = 10 years)
    log_days = np.log(duration_days)
    max_log = np.log(3650)
    return min(100.0, (log_days / max_log) * 100.0)


def compute_casualty_burden(
    casualties: Optional[float],
    pre_war_population: Optional[float],
    pre_war_military: Optional[float],
) -> float:
    """Casualties relative to pre-war population and military."""
    if not casualties or casualties <= 0:
        return 0.0

    pop_score = 0.0
    mil_score = 0.0

    if pre_war_population and pre_war_population > 0:
        ratio = casualties / pre_war_population
        pop_score = min(100.0, ratio * 1000.0)  # 0.1% population = 100

    if pre_war_military and pre_war_military > 0:
        ratio = casualties / pre_war_military
        mil_score = min(100.0, ratio * 100.0)  # 100% of military = 100

    return (pop_score + mil_score) / 2.0


def compute_military_personnel_decline(
    peak_personnel: Optional[float],
    final_personnel: Optional[float],
) -> float:
    """Decline in military personnel over war years."""
    if not peak_personnel or not final_personnel or peak_personnel == 0:
        return 0.0
    decline = (peak_personnel - final_personnel) / peak_personnel
    return min(100.0, max(0.0, decline * 100.0))


def compute_military_expenditure_burden(
    milex_as_gdp_pct: Optional[float],
    pre_war_baseline_pct: Optional[float],
) -> float:
    """Military expenditure burden vs pre-war baseline."""
    if not milex_as_gdp_pct or not pre_war_baseline_pct or pre_war_baseline_pct == 0:
        return 0.0
    burden = milex_as_gdp_pct / pre_war_baseline_pct
    return min(100.0, (burden - 1.0) * 100.0)


def compute_energy_or_industrial_decline(
    peak_energy: Optional[float],
    final_energy: Optional[float],
) -> float:
    """Decline in energy consumption or industrial proxies."""
    if not peak_energy or not final_energy or peak_energy == 0:
        return 0.0
    decline = (peak_energy - final_energy) / peak_energy
    return min(100.0, max(0.0, decline * 100.0))


def compute_event_tempo_decline(
    peak_events_per_month: Optional[float],
    final_events_per_month: Optional[float],
) -> float:
    """Decline in military event frequency."""
    if not peak_events_per_month or not final_events_per_month or peak_events_per_month == 0:
        return 0.0
    decline = (peak_events_per_month - final_events_per_month) / peak_events_per_month
    return min(100.0, max(0.0, decline * 100.0))


def compute_alliance_degradation(
    initial_allies: Optional[int],
    final_allies: Optional[int],
) -> float:
    """Loss of allies during conflict."""
    if initial_allies is None or final_allies is None or initial_allies == 0:
        return 0.0
    if final_allies >= initial_allies:
        return 0.0
    decline = (initial_allies - final_allies) / initial_allies
    return min(100.0, decline * 100.0)


def compute_regime_will_decline(instability_score: Optional[float]) -> float:
    """Regime instability proxy."""
    if instability_score is None:
        return 0.0
    return min(100.0, max(0.0, instability_score))


def compute_protest_unrest(unrest_score: Optional[float]) -> float:
    """Domestic protest and unrest increase."""
    if unrest_score is None:
        return 0.0
    return min(100.0, max(0.0, unrest_score))


def compute_territorial_loss(
    initial_territory: Optional[float],
    final_territory: Optional[float],
) -> float:
    """Proportion of territory lost during conflict."""
    if initial_territory is None or final_territory is None or initial_territory == 0:
        return 0.0
    loss = (initial_territory - final_territory) / initial_territory
    return min(100.0, max(0.0, loss * 100.0))


def compute_ses(
    duration_days: Optional[float] = None,
    casualties: Optional[float] = None,
    pre_war_population: Optional[float] = None,
    pre_war_military: Optional[float] = None,
    peak_personnel: Optional[float] = None,
    final_personnel: Optional[float] = None,
    milex_as_gdp_pct: Optional[float] = None,
    pre_war_baseline_pct: Optional[float] = None,
    peak_energy: Optional[float] = None,
    final_energy: Optional[float] = None,
    peak_events_per_month: Optional[float] = None,
    final_events_per_month: Optional[float] = None,
    initial_allies: Optional[int] = None,
    final_allies: Optional[int] = None,
    instability_score: Optional[float] = None,
    unrest_score: Optional[float] = None,
    initial_territory: Optional[float] = None,
    final_territory: Optional[float] = None,
    weights: Optional[dict] = None,
) -> dict:
    """Compute SES with component breakdown."""
    if weights is None:
        weights = load_weights()["strategic_exhaustion_score"]["components"]

    components = {
        "duration_pressure": compute_duration_pressure(duration_days),
        "casualty_burden": compute_casualty_burden(
            casualties, pre_war_population, pre_war_military
        ),
        "military_personnel_decline": compute_military_personnel_decline(
            peak_personnel, final_personnel
        ),
        "military_expenditure_burden": compute_military_expenditure_burden(
            milex_as_gdp_pct, pre_war_baseline_pct
        ),
        "energy_or_industrial_decline": compute_energy_or_industrial_decline(
            peak_energy, final_energy
        ),
        "event_tempo_decline": compute_event_tempo_decline(
            peak_events_per_month, final_events_per_month
        ),
        "alliance_degradation": compute_alliance_degradation(initial_allies, final_allies),
        "regime_will_decline": compute_regime_will_decline(instability_score),
        "protest_or_unrest_increase": compute_protest_unrest(unrest_score),
        "territorial_loss_proxy": compute_territorial_loss(initial_territory, final_territory),
    }

    total = 0.0
    for name, value in components.items():
        w = weights.get(name, {}).get("weight", 0.1)
        total += value * w

    return {
        "ses_score": round(total, 2),
        "ses_components": components,
        "ses_weighted_total": round(total, 2),
    }


def compute_ses_vectorized(df: pd.DataFrame, weights: Optional[dict] = None) -> pd.Series:
    """Compute SES for many rows at once using vectorized pandas ops.

    Expected columns in df:
        duration_days, casualties, pre_war_population, pre_war_military,
        peak_personnel, final_personnel, milex_ratio (peak/first), peak_industrial,
        final_industrial

    Returns:
        Series of SES scores (0-100).
    """
    if weights is None:
        weights = load_weights().get("strategic_exhaustion_score", {}).get("components", {})
    # Normalize weights
    if weights and isinstance(next(iter(weights.values()), {}), dict):
        w = {k: float(v.get("weight", 0.1)) for k, v in weights.items()}
    else:
        w = {k: float(v) for k, v in weights.items()}

    def _clamp(s, lo=0.0, hi=100.0):
        return s.fillna(0).clip(lo, hi)

    # duration_pressure: log(duration)/log(3650) * 100
    dur = df["duration_days"].clip(lower=1).fillna(1)
    dur_pressure = _clamp(np.log(dur) / np.log(3650) * 100)

    # casualty_burden: casualties / pre_war_pop * 1000 (capped)
    pop = df["pre_war_population"].replace(0, np.nan)
    pop_score = _clamp(df["casualties"].fillna(0) / pop * 1000)
    mil = df["pre_war_military"].replace(0, np.nan)
    mil_score = _clamp(df["casualties"].fillna(0) / mil * 100)
    casualty_burden = (pop_score.fillna(0) + mil_score.fillna(0)) / 2

    # military_personnel_decline: (peak - final) / peak * 100
    peak_p = df["peak_personnel"].replace(0, np.nan)
    decl = (peak_p - df["final_personnel"]) / peak_p
    personnel_decline = _clamp(decl * 100)

    # military_expenditure_burden: (peak/first - 1) * 100
    milex_ratio = df.get("milex_ratio")
    if milex_ratio is not None:
        milex_burden = _clamp((milex_ratio.fillna(1) - 1) * 100)
    else:
        milex_burden = pd.Series(0.0, index=df.index)

    # energy/industrial decline: (peak - final) / peak * 100
    peak_i = df["peak_industrial"].replace(0, np.nan)
    ind = (peak_i - df["final_industrial"]) / peak_i
    industrial_decline = _clamp(ind * 100)

    # Compute total
    total = (
        w.get("duration_pressure", 0.15) * dur_pressure
        + w.get("casualty_burden", 0.15) * casualty_burden
        + w.get("military_personnel_decline", 0.15) * personnel_decline
        + w.get("military_expenditure_burden", 0.15) * milex_burden
        + w.get("energy_or_industrial_decline", 0.10) * industrial_decline
    )
    return total.fillna(0).round(2)


def _load_aow_data(output_dir: Path) -> pd.DataFrame | None:
    """Load AoW regime data for regime_will_decline component."""
    p = output_dir / "aow.parquet"
    if p.exists():
        return pd.read_parquet(p)
    return None


def _compute_regime_instability(
    group: pd.DataFrame, aow_df: pd.DataFrame | None
) -> float | None:
    """Compute regime instability from AoW leader transition data."""
    if aow_df is None:
        return None
    merged = group.merge(
        aow_df[["ccode", "year", "trans", "occup", "interreg"]],
        left_on=["cow_code", "year"],
        right_on=["ccode", "year"],
        how="left",
    )
    total_instability = 0.0
    count = 0
    for _, row in merged.iterrows():
        score = 0.0
        if pd.notna(row.get("trans")) and row["trans"] > 0:
            score += 50.0
        if pd.notna(row.get("occup")) and row["occup"] > 0:
            score += 30.0
        if pd.notna(row.get("interreg")) and row["interreg"] > 0:
            score += 20.0
        if score > 0:
            total_instability += score
            count += 1
    return total_instability / count if count > 0 else None


MANUAL_CASE_PATH_SES = Path("data/manual/manual_case_scores.csv")


def _load_manual_ses() -> dict[str, float]:
    """Load manual_ses values for case study war_ids."""
    if not MANUAL_CASE_PATH_SES.exists():
        return {}
    try:
        df = pd.read_csv(MANUAL_CASE_PATH_SES)
    except Exception:
        return {}
    out = {}
    for _, r in df.iterrows():
        wid = str(r.get("war_id", ""))
        v = r.get("manual_ses")
        if wid and pd.notna(v):
            try:
                out[wid] = float(v)
            except (ValueError, TypeError):
                pass
    return out


def _compute_side_ses(
    side_df: pd.DataFrame,
    duration_days: float | None,
    aow_df: pd.DataFrame | None,
) -> dict:
    """Compute SES for a single side (state-year rows for one war)."""
    if len(side_df) < 2:
        return {}
    side_df = side_df.sort_values("year")
    cols = side_df.columns
    bd = side_df["battle_deaths"] if "battle_deaths" in cols else None
    casualties = bd.sum() if bd is not None else None
    pop = side_df["population"] if "population" in cols else None
    mp = side_df["military_personnel"] if "military_personnel" in cols else None
    milex = side_df["military_expenditure"] if "military_expenditure" in cols else None
    energy = side_df["energy_consumption"] if "energy_consumption" in cols else None
    steel = side_df["iron_steel"] if "iron_steel" in cols else None

    pre_war_pop = pop.iloc[0] if pop is not None else None
    pre_war_mil = mp.iloc[0] if mp is not None else None
    peak_personnel = mp.max() if mp is not None else None
    final_personnel = mp.iloc[-1] if mp is not None else None

    milex_burden = None
    if milex is not None:
        baseline = milex.iloc[0]
        peak_milex = milex.max()
        if pd.notna(baseline) and baseline > 0 and pd.notna(peak_milex):
            milex_burden = peak_milex / baseline

    peak_energy_val = energy.max() if energy is not None else None
    final_energy_val = energy.iloc[-1] if energy is not None else None
    peak_steel_val = steel.max() if steel is not None else None
    final_steel_val = steel.iloc[-1] if steel is not None else None

    if pd.notna(peak_energy_val) and pd.notna(final_energy_val) and peak_energy_val > 0:
        peak_industrial = peak_energy_val
        final_industrial = final_energy_val
    elif pd.notna(peak_steel_val) and pd.notna(final_steel_val) and peak_steel_val > 0:
        peak_industrial = peak_steel_val
        final_industrial = final_steel_val
    else:
        peak_industrial = None
        final_industrial = None

    regime_instability = _compute_regime_instability(side_df, aow_df)

    def _n(v):
        return float(v) if v is not None and pd.notna(v) else None

    return compute_ses(
        duration_days=duration_days,
        casualties=_n(casualties),
        pre_war_population=_n(pre_war_pop),
        pre_war_military=_n(pre_war_mil),
        peak_personnel=_n(peak_personnel),
        final_personnel=_n(final_personnel),
        milex_as_gdp_pct=_n(milex_burden),
        pre_war_baseline_pct=1.0 if milex_burden and _n(milex_burden) else None,
        peak_energy=_n(peak_industrial),
        final_energy=_n(final_industrial),
        instability_score=_n(regime_instability),
    )


def score_wars(
    war_years_df: pd.DataFrame,
    output_dir: Path,
    wars_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Compute SES for all wars with participant-year data.

    Per-side calculation: aggregates by (war_id, cow_code), computes SES for each
    side, and reports the **max SES across sides** (representing the most
    exhausted participant — the loser).

    Also writes a per-side table to data/processed/ses_components.parquet.
    """
    war_durations: dict[str, float] = {}
    if wars_df is not None and len(wars_df) > 0:
        for _, r in wars_df.iterrows():
            d = r.get("duration_days")
            if pd.notna(d):
                war_durations[r["war_id"]] = float(d)

    aow_df = _load_aow_data(output_dir)
    manual_ses = _load_manual_ses()

    if "cow_code" not in war_years_df.columns or not war_years_df["cow_code"].notna().any():
        # No side info; treat whole war as one side
        results = []
        for war_id, group in war_years_df.groupby("war_id"):
            duration_days = war_durations.get(war_id)
            ses_result = _compute_side_ses(group, duration_days, aow_df)
            if ses_result:
                results.append({"war_id": war_id, **ses_result})
        result_df = pd.DataFrame(results)
        output_dir.mkdir(parents=True, exist_ok=True)
        result_df.to_parquet(output_dir / "ses_scores.parquet", index=False)
        logger.info(f"SES scores written: {len(result_df)} wars (no side info)")
        return result_df

    # Vectorized per-side aggregation
    # Filter COW missing codes (-9) and missing cow_code
    wy = war_years_df[war_years_df["cow_code"].notna() & (war_years_df["cow_code"] >= 0)].copy()

    # Per (war_id, cow_code) aggregates
    agg_cols = ["battle_deaths", "population", "military_personnel", "military_expenditure",
                "energy_consumption", "iron_steel"]
    available_cols = [c for c in agg_cols if c in wy.columns]

    # We need first, last, max, sum per group
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

    # Compute duration_days from war years coverage
    if "year" in wy.columns:
        war_year_range = wy.groupby("war_id")["year"].agg(["min", "max", "count"]).reset_index()
        war_year_range["implied_duration_days"] = (
            (war_year_range["max"] - war_year_range["min"] + 1) * 365
        ).clip(lower=1)
        per_side = per_side.merge(
            war_year_range[["war_id", "implied_duration_days"]], on="war_id", how="left"
        )

    # Apply compute_ses per row
    def _row_to_ses(row) -> dict:
        duration = war_durations.get(row["war_id"]) or row.get("implied_duration_days", 365)

        # First, max, last values
        first_mp = row.get("military_personnel_first")
        max_mp = row.get("military_personnel_max")
        last_mp = row.get("military_personnel_last")
        first_milex = row.get("military_expenditure_first")
        max_milex = row.get("military_expenditure_max")

        milex_burden = None
        if pd.notna(first_milex) and first_milex > 0 and pd.notna(max_milex):
            milex_burden = max_milex / first_milex

        peak_energy = row.get("energy_consumption_max")
        final_energy = row.get("energy_consumption_last")
        peak_steel = row.get("iron_steel_max")
        final_steel = row.get("iron_steel_last")

        if pd.notna(peak_energy) and pd.notna(final_energy) and peak_energy > 0:
            peak_ind, final_ind = peak_energy, final_energy
        elif pd.notna(peak_steel) and pd.notna(final_steel) and peak_steel > 0:
            peak_ind, final_ind = peak_steel, final_steel
        else:
            peak_ind, final_ind = None, None

        return compute_ses(
            duration_days=float(duration) if pd.notna(duration) else None,
            casualties=float(row.get("battle_deaths_sum", 0)) if pd.notna(row.get("battle_deaths_sum")) else None,
            pre_war_population=float(first_mp) if pd.notna(first_mp) else None,
            pre_war_military=float(first_mp) if pd.notna(first_mp) else None,
            peak_personnel=float(max_mp) if pd.notna(max_mp) else None,
            final_personnel=float(last_mp) if pd.notna(last_mp) else None,
            milex_as_gdp_pct=float(milex_burden) if milex_burden else None,
            pre_war_baseline_pct=1.0 if milex_burden else None,
            peak_energy=float(peak_ind) if peak_ind is not None else None,
            final_energy=float(final_ind) if final_ind is not None else None,
            instability_score=None,  # skip regime instability for performance
        )

    # Vectorized compute_ses across all per-side rows
    ses_input = pd.DataFrame({
        "duration_days": per_side.get("implied_duration_days"),
        "casualties": per_side.get("battle_deaths_sum"),
        "pre_war_population": per_side.get("population_first"),
        "pre_war_military": per_side.get("military_personnel_first"),
        "peak_personnel": per_side.get("military_personnel_max"),
        "final_personnel": per_side.get("military_personnel_last"),
        "milex_ratio": per_side.get("military_expenditure_max") / per_side.get("military_expenditure_first").replace(0, np.nan),
        "peak_industrial": per_side.get("energy_consumption_max").fillna(per_side.get("iron_steel_max")),
        "final_industrial": per_side.get("energy_consumption_last").fillna(per_side.get("iron_steel_last")),
    })
    per_side["ses_score"] = compute_ses_vectorized(ses_input)

    # Take the max SES across sides per war
    war_max = per_side.groupby("war_id")["ses_score"].max().reset_index()
    war_max.columns = ["war_id", "ses_score"]
    # Pick the side with max SES to get its components
    idx_max = per_side.groupby("war_id")["ses_score"].idxmax()
    top_sides = per_side.loc[idx_max, ["war_id", "ses_score"]].rename(
        columns={"ses_score": "top_side_ses"}
    )
    war_max = war_max.merge(top_sides, on="war_id", how="left")

    result_df = pd.DataFrame({
        "war_id": war_max["war_id"],
        "ses_score": war_max["ses_score"],
        "ses_components": war_max.apply(
            lambda r: {"max_side_ses": r["ses_score"], "n_sides": 1}, axis=1
        ),
        "ses_weighted_total": war_max["ses_score"],
    })

    # Apply manual SES override for case study war_ids (where structured data is incomplete)
    if manual_ses:
        for wid, manual_val in manual_ses.items():
            mask = result_df["war_id"] == wid
            if mask.any():
                result_df.loc[mask, "ses_score"] = manual_val
                result_df.loc[mask, "ses_weighted_total"] = manual_val
                # Update component dict to flag manual source
                result_df.loc[mask, "ses_components"] = result_df.loc[mask].apply(
                    lambda r: {"max_side_ses": r["ses_score"], "n_sides": 1, "source": "manual_override"}, axis=1
                )

    output_dir.mkdir(parents=True, exist_ok=True)
    result_df.to_parquet(output_dir / "ses_scores.parquet", index=False)
    # Per-side output
    per_side_out = per_side[["war_id", "cow_code", "ses_score"]].copy()
    per_side_out.to_parquet(output_dir / "ses_components.parquet", index=False)
    logger.info(f"SES scores written: {len(result_df)} wars, {len(per_side_out)} per-side records")
    return result_df

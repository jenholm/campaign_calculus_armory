"""Decisive Shock Score (DSS) computation with component-level auditability.

DSS measures whether a single battle, campaign, or operational event directly
preceded surrender, regime collapse, or irreversible strategic defeat.

Components (each scored 0-100):
- final_battle_proximity: days from final major battle to war end
- battle_casualty_concentration: largest battle casualties / total casualties
- source_claims_decisive: historical consensus (manual coding or Wikipedia)
- capital_capture: capital or main fleet lost in war
- field_army_destroyed: main field army destroyed
- fleet_destroyed: main fleet destroyed
- rapid_surrender: surrender within 30 days of final battle
- regime_collapse: government collapse in war
- battle_winner_equals_war_winner: whether battle victor was war victor

For IWB wars, components are computed from structured data. For manual case
studies with cow_iw_* ids, the source_claims_decisive and other components
are taken from the manual CSV.
"""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import yaml

logger = logging.getLogger(__name__)

METRIC_WEIGHTS_PATH = Path(__file__).parents[3] / "config" / "metric_weights.yml"
MANUAL_CASE_PATH = Path("data/manual/manual_case_scores.csv")

# Default weights (loaded from config but defined here for clarity)
DEFAULT_COMPONENTS = {
    "final_battle_proximity": 0.20,
    "battle_casualty_concentration": 0.15,
    "source_claims_decisive": 0.20,
    "capital_capture": 0.10,
    "field_army_destroyed": 0.10,
    "fleet_destroyed": 0.05,
    "rapid_surrender": 0.08,
    "regime_collapse": 0.07,
    "battle_winner_equals_war_winner": 0.05,
}


def load_weights() -> dict:
    try:
        with open(METRIC_WEIGHTS_PATH) as f:
            cfg = yaml.safe_load(f)
        raw = cfg.get("decisive_shock_score", {}).get("components", DEFAULT_COMPONENTS)
        # Normalize: yaml has {component: {weight: 0.x, description: "..."}}
        comps = {}
        for k, v in raw.items():
            if isinstance(v, dict) and "weight" in v:
                comps[k] = float(v["weight"])
            elif isinstance(v, (int, float)):
                comps[k] = float(v)
            else:
                comps[k] = DEFAULT_COMPONENTS.get(k, 0.05)
        return comps
    except Exception:
        return DEFAULT_COMPONENTS


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    if pd.isna(x):
        return 0.0
    return max(lo, min(hi, float(x)))


def compute_final_battle_proximity(days_to_end: Optional[float]) -> float:
    if days_to_end is None or pd.isna(days_to_end):
        return 0.0
    d = abs(float(days_to_end))
    if d <= 7:
        return 100.0
    if d <= 30:
        return 80.0
    if d <= 90:
        return 60.0
    if d <= 180:
        return 30.0
    return 0.0


def compute_battle_casualty_concentration(
    max_battle_casualties: Optional[float],
    total_war_casualties: Optional[float],
) -> float:
    if not max_battle_casualties or not total_war_casualties or total_war_casualties <= 0:
        return 0.0
    if pd.isna(max_battle_casualties) or pd.isna(total_war_casualties):
        return 0.0
    ratio = float(max_battle_casualties) / float(total_war_casualties)
    return _clamp(ratio * 100.0)


def _bool_score(value) -> float:
    """Convert boolean / '1' / 'yes' to 100 or 0."""
    if value is None or pd.isna(value):
        return 0.0
    s = str(value).strip().lower()
    if s in ("1", "true", "yes", "y", "t"):
        return 100.0
    if s in ("0", "false", "no", "n", "f", ""):
        return 0.0
    try:
        v = float(s)
        return 100.0 if v > 0 else 0.0
    except ValueError:
        return 0.0


def compute_dss(
    final_battle_proximity: Optional[float] = None,
    battle_casualty_concentration: Optional[float] = None,
    source_claims_decisive: Optional[float] = None,
    capital_capture: Optional[bool] = None,
    field_army_destroyed: Optional[bool] = None,
    fleet_destroyed: Optional[bool] = None,
    rapid_surrender: Optional[bool] = None,
    regime_collapse: Optional[bool] = None,
    battle_winner_equals_war_winner: Optional[bool] = None,
    weights: Optional[dict] = None,
) -> dict:
    """Compute DSS with component breakdown.

    Returns:
        Dict with dss_score, dss_components (dict), and component_confidence.
    """
    if weights is None:
        weights = load_weights()

    components = {
        "final_battle_proximity": compute_final_battle_proximity(final_battle_proximity),
        "battle_casualty_concentration": compute_battle_casualty_concentration(
            battle_casualty_concentration, None
        ),
        "source_claims_decisive": _clamp(source_claims_decisive) if source_claims_decisive is not None else 0.0,
        "capital_capture": _bool_score(capital_capture),
        "field_army_destroyed": _bool_score(field_army_destroyed),
        "fleet_destroyed": _bool_score(fleet_destroyed),
        "rapid_surrender": _bool_score(rapid_surrender),
        "regime_collapse": _bool_score(regime_collapse),
        "battle_winner_equals_war_winner": _bool_score(battle_winner_equals_war_winner),
    }

    total = 0.0
    confidence_count = 0
    for name, value in components.items():
        w = weights.get(name, 0.0)
        if not isinstance(w, (int, float)) or w <= 0:
            w = DEFAULT_COMPONENTS.get(name, 0.05)
        total += value * w
        if value > 0:
            confidence_count += 1
    component_confidence = confidence_count / len(components)

    return {
        "dss_score": round(total, 2),
        "dss_components": components,
        "dss_weighted_total": round(total, 2),
        "component_confidence": round(component_confidence, 2),
    }


def _load_manual_case_studies() -> pd.DataFrame:
    """Load manual case scores if available."""
    if not MANUAL_CASE_PATH.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(MANUAL_CASE_PATH)
    except Exception as e:
        logger.warning(f"Could not load manual cases: {e}")
        return pd.DataFrame()


def _aggregate_iwb_battle_casualties(iwb_df: pd.DataFrame, cow_war_df: pd.DataFrame) -> dict:
    """For each war, compute total casualties (sum of batdtha+batdthb per dyad) and
    the largest single-battle battle (using IWB approximation).

    Since IWB has no per-battle casualties, we approximate
    `battle_casualty_concentration` from COW totals only when we have a
    largest-battle estimate from a Wikipedia infobox. Otherwise this is 0.
    """
    out = {}
    if len(cow_war_df) == 0:
        return out
    for _, row in cow_war_df.iterrows():
        wn = row.get("warnum")
        if pd.isna(wn):
            continue
        wid = f"cow_iw_{int(float(wn))}"
        bd_a = row.get("batdtha", 0) or 0
        bd_b = row.get("batdthb", 0) or 0
        total = float(bd_a) + float(bd_b)
        out[wid] = {
            "cow_total_casualties": total,
            "winner_war_level": row.get("outcomea"),  # '1' = initiator wins, etc.
        }
    return out


def _find_largest_battle_casualties(war_id: str, battles_df: pd.DataFrame) -> float:
    """Find the largest single-battle casualty figure for a war from Wikipedia
    infoboxes (where present in battles.parquet as wikipedia_casualties_a/b).
    Returns 0 if no data.
    """
    if "wikipedia_casualties_a" not in battles_df.columns:
        return 0.0
    war_battles = battles_df[battles_df["war_id"] == war_id]
    max_val = 0.0
    for _, b in war_battles.iterrows():
        for col in ("wikipedia_casualties_a", "wikipedia_casualties_b"):
            v = b.get(col, "")
            if not isinstance(v, str) or not v.strip():
                continue
            # Try to extract first integer from the string
            import re
            m = re.search(r"(\d[\d,]*)", v.replace(",", ""))
            if m:
                try:
                    val = float(m.group(1))
                    if val > max_val:
                        max_val = val
                except ValueError:
                    pass
    return max_val


def score_wars(
    battles_df: pd.DataFrame,
    wars_df: pd.DataFrame,
    output_dir: Path,
    cow_war_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Compute DSS for interstate wars with IWB battle data.

    Falls back to manual case study scores when available.
    """
    if "cowNum" in battles_df.columns and "war_id" not in battles_df.columns:
        battles_df = battles_df.copy()
        battles_df["war_id"] = "cow_iw_" + battles_df["cowNum"].astype(int).astype(str)

    # Load manual cases and build a war_id -> manual score map
    manual_df = _load_manual_case_studies()
    manual_by_wid: dict[str, dict] = {}
    if len(manual_df) > 0:
        for _, m in manual_df.iterrows():
            wid = str(m.get("war_id", ""))
            if wid:
                manual_by_wid[wid] = m.to_dict()

    # Aggregate IWB + COW totals for casualty concentration
    cow_totals = _aggregate_iwb_battle_casualties(battles_df, cow_war_df if cow_war_df is not None else pd.DataFrame())

    # DSS only makes sense for wars with battle data. Filter to:
    # 1) interstate COW wars that have IWB battles
    # 2) manual case studies with cow_iw_* ids
    interstate = wars_df[wars_df["war_type"] == "interstate"] if "war_type" in wars_df.columns else wars_df
    iwb_war_ids = set(battles_df["war_id"].dropna().unique()) if "war_id" in battles_df.columns else set()
    manual_wids = set(manual_by_wid.keys())
    candidate_wids = iwb_war_ids | manual_wids
    candidate_wars = interstate[interstate["war_id"].isin(candidate_wids)]

    results = []
    for _, war in candidate_wars.iterrows():
        wid = war["war_id"]
        war_battles = battles_df[battles_df["war_id"] == wid] if len(battles_df) > 0 else pd.DataFrame()

        war_end = war.get("end_date")
        war_start = war.get("start_date")

        # Last battle end date and proximity
        last_battle_end = None
        proximity = None
        if len(war_battles) > 0 and "endDate" in war_battles.columns:
            dates = pd.to_datetime(war_battles["endDate"], errors="coerce")
            valid = dates.notna()
            if valid.any():
                last_idx = dates[valid].idxmax()
                last_battle_end = dates[last_idx]
                if pd.notna(war_end):
                    proximity = (pd.to_datetime(war_end) - last_battle_end).days

        # Battle casualty concentration
        max_battle_cas = _find_largest_battle_casualties(wid, battles_df)
        total_cas = cow_totals.get(wid, {}).get("cow_total_casualties", 0)
        casualty_conc = max_battle_cas / total_cas if total_cas and total_cas > 0 else None

        # Battle winner = war winner
        battle_winner_equals_war_winner = None
        if len(war_battles) > 0 and "victorWarLevel" in war_battles.columns:
            vwl = str(war_battles["victorWarLevel"].iloc[-1] if len(war_battles) else "").lower()
            battle_winner_equals_war_winner = vwl in ("target", "initiator")
            if vwl == "inconclusive":
                battle_winner_equals_war_winner = False

        # Wikipedia decisive flag (from battles.parquet)
        wiki_decisive = False
        if "decisive_claimed_by_sources" in war_battles.columns and len(war_battles) > 0:
            wiki_decisive = (
                war_battles["decisive_claimed_by_sources"].astype(str).str.strip() == "1"
            ).any()

        # If manual case study exists, use it
        if wid in manual_by_wid:
            m = manual_by_wid[wid]
            # Parse composite fields
            cap_regime_val = str(m.get("capital_or_regime_collapse", "")).strip().lower()
            capital_captured = cap_regime_val in ("yes", "1", "true", "captured", "fell")
            regime_collapsed = cap_regime_val in ("yes", "1", "true") or \
                str(m.get("will_collapse_evidence", "")).strip().lower() not in (
                    "", "n/a", "no", "false", "0"
                )
            # Personnel attrition evidence implies field army weakened
            personnel_ev = str(m.get("personnel_attrition_evidence", "")).strip().lower()
            field_army_destroyed = bool(personnel_ev) and personnel_ev not in ("no", "false", "0", "n/a", "")
            # Logistics evidence can imply fleet or supply collapse
            logistics_ev = str(m.get("logistics_collapse_evidence", "")).strip().lower()
            fleet_destroyed = "fleet" in logistics_ev or "navy" in logistics_ev
            dss_result = compute_dss(
                final_battle_proximity=proximity,
                battle_casualty_concentration=casualty_conc,
                source_claims_decisive=float(m.get("source_claims_decisive", 0) or 0),
                capital_capture=capital_captured,
                field_army_destroyed=field_army_destroyed,
                fleet_destroyed=fleet_destroyed,
                rapid_surrender=bool(proximity is not None and abs(proximity) <= 30),
                regime_collapse=regime_collapsed,
                battle_winner_equals_war_winner=battle_winner_equals_war_winner,
            )
        else:
            # Compute from IWB only
            source_claims = 50.0 if wiki_decisive else 0.0
            dss_result = compute_dss(
                final_battle_proximity=proximity,
                battle_casualty_concentration=casualty_conc,
                source_claims_decisive=source_claims,
                rapid_surrender=bool(proximity is not None and abs(proximity) <= 30),
                battle_winner_equals_war_winner=battle_winner_equals_war_winner,
            )

        results.append({
            "war_id": wid,
            "war_name": war.get("war_name", ""),
            **dss_result,
        })

    result_df = pd.DataFrame(results)
    output_dir.mkdir(parents=True, exist_ok=True)
    result_df.to_parquet(output_dir / "dss_scores.parquet", index=False)

    # Also save component-level table for audit
    if len(result_df) > 0:
        comp_records = []
        for r in results:
            comp_records.append({"war_id": r["war_id"], **r["dss_components"]})
        pd.DataFrame(comp_records).to_parquet(output_dir / "dss_components.parquet", index=False)

    logger.info(f"DSS scores written: {len(result_df)} wars")
    return result_df

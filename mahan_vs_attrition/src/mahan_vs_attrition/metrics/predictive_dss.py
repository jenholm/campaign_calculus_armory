"""Predictive DSS: exogenous features only, no outcome leakage.

This module computes a "predictive DSS" using only features that are
observable BEFORE the outcome is known. This allows genuine prediction
of termination mechanism rather than post-hoc classification.

Components (all exogenous):
1. Force ratio (military strength ratio between sides)
2. Economic disparity (GDP ratio)
3. Industrial capacity ratio (war production capacity)
4. Logistics vulnerability (distance, supply lines, terrain)
5. Surprise indicator (force mobilization, positioning)
6. Alliance asymmetry (balance of alliance support)
7. Mobilization speed (rate of force generation)
8. Regime stability (political cohesion indicators)

Each component is scored 0-100 based on observable pre-war or early-war data.
The weighted sum produces a predictive DSS (0-100).
"""

import logging
from typing import Optional

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Component weights for predictive DSS
PREDICTIVE_WEIGHTS = {
    "force_ratio": 0.20,
    "economic_disparity": 0.15,
    "industrial_capacity_ratio": 0.15,
    "logistics_vulnerability": 0.15,
    "surprise_indicator": 0.10,
    "alliance_asymmetry": 0.10,
    "mobilization_speed": 0.10,
    "regime_stability": 0.05,
}


def compute_force_ratio(
    military_a: float, military_b: float
) -> float:
    """Compute force ratio component (0-100).
    
    Higher ratio = more decisive potential.
    Ratio > 2:1 → high score (80-100)
    Ratio ~1:1 → medium score (40-60)
    Ratio < 1:2 → low score (0-40)
    """
    if military_b <= 0:
        return 100.0
    ratio = military_a / military_b
    # Map ratio to 0-100: ratio of 1 = 50, ratio of 3+ = 90+
    score = min(100, max(0, 50 + (ratio - 1) * 30))
    return round(score, 1)


def compute_economic_disparity(
    economic_a: float, economic_b: float
) -> float:
    """Compute economic disparity component (0-100)."""
    if economic_b <= 0:
        return 100.0
    ratio = economic_a / economic_b
    score = min(100, max(0, 50 + (ratio - 1) * 25))
    return round(score, 1)


def compute_industrial_capacity_ratio(
    industrial_a: float, industrial_b: float
) -> float:
    """Compute industrial capacity ratio (0-100)."""
    if industrial_b <= 0:
        return 100.0
    ratio = industrial_a / industrial_b
    score = min(100, max(0, 50 + (ratio - 1) * 25))
    return round(score, 1)


def compute_logistics_vulnerability(
    distance_factor: float = 50.0,
    supply_line_length: float = 50.0,
    terrain_difficulty: float = 50.0,
) -> float:
    """Compute logistics vulnerability (0-100).
    
    Higher = more vulnerable to attrition.
    All inputs are pre-war observable factors.
    """
    score = (distance_factor * 0.4 + supply_line_length * 0.35 + terrain_difficulty * 0.25)
    return round(min(100, max(0, score)), 1)


def compute_surprise_indicator(
    mobilization_asymmetry: float = 50.0,
    force_positioning: float = 50.0,
) -> float:
    """Compute surprise potential (0-100).
    
    Higher = greater surprise advantage for initiator.
    """
    score = (mobilization_asymmetry * 0.6 + force_positioning * 0.4)
    return round(min(100, max(0, score)), 1)


def compute_alliance_asymmetry(
    allies_a: int = 1,
    allies_b: int = 1,
    ally_strength_a: float = 50.0,
    ally_strength_b: float = 50.0,
) -> float:
    """Compute alliance asymmetry (0-100).
    
    Higher = Side A has stronger alliance support.
    """
    strength_ratio = (ally_strength_a * allies_a) / max(1, ally_strength_b * allies_b)
    score = min(100, max(0, 50 + (strength_ratio - 1) * 30))
    return round(score, 1)


def compute_mobilization_speed(
    mobilization_rate_a: float = 50.0,
    mobilization_rate_b: float = 50.0,
) -> float:
    """Compute mobilization speed advantage (0-100).
    
    Higher = Side A mobilizes faster.
    """
    if mobilization_rate_b <= 0:
        return 100.0
    ratio = mobilization_rate_a / mobilization_rate_b
    score = min(100, max(0, 50 + (ratio - 1) * 40))
    return round(score, 1)


def compute_regime_stability(
    regime_cohesion_a: float = 70.0,
    regime_cohesion_b: float = 70.0,
) -> float:
    """Compute regime stability advantage (0-100).
    
    Higher = Side A has more stable regime.
    """
    score = regime_cohesion_a - regime_cohesion_b * 0.3 + 15
    return round(min(100, max(0, score)), 1)


def compute_predictive_dss(
    military_a: float = 70.0,
    military_b: float = 70.0,
    economic_a: float = 70.0,
    economic_b: float = 70.0,
    industrial_a: float = 70.0,
    industrial_b: float = 70.0,
    distance_factor: float = 50.0,
    supply_line_length: float = 50.0,
    terrain_difficulty: float = 50.0,
    mobilization_asymmetry: float = 50.0,
    force_positioning: float = 50.0,
    allies_a: int = 1,
    allies_b: int = 1,
    ally_strength_a: float = 50.0,
    ally_strength_b: float = 50.0,
    mobilization_rate_a: float = 50.0,
    mobilization_rate_b: float = 50.0,
    regime_cohesion_a: float = 70.0,
    regime_cohesion_b: float = 70.0,
) -> dict:
    """Compute predictive DSS from exogenous features only.
    
    Returns dict with component scores and weighted total.
    """
    components = {
        "force_ratio": compute_force_ratio(military_a, military_b),
        "economic_disparity": compute_economic_disparity(economic_a, economic_b),
        "industrial_capacity_ratio": compute_industrial_capacity_ratio(industrial_a, industrial_b),
        "logistics_vulnerability": compute_logistics_vulnerability(
            distance_factor, supply_line_length, terrain_difficulty
        ),
        "surprise_indicator": compute_surprise_indicator(
            mobilization_asymmetry, force_positioning
        ),
        "alliance_asymmetry": compute_alliance_asymmetry(
            allies_a, allies_b, ally_strength_a, ally_strength_b
        ),
        "mobilization_speed": compute_mobilization_speed(
            mobilization_rate_a, mobilization_rate_b
        ),
        "regime_stability": compute_regime_stability(
            regime_cohesion_a, regime_cohesion_b
        ),
    }

    # Weighted sum
    total = sum(
        components[k] * PREDICTIVE_WEIGHTS[k]
        for k in PREDICTIVE_WEIGHTS
    )

    return {
        "components": components,
        "predictive_dss": round(min(100, max(0, total)), 2),
    }


def compare_observed_vs_predictive(
    observed_dss: dict,
    predictive_dss: dict,
) -> dict:
    """Compare observed (post-hoc) DSS with predictive (exogenous) DSS.
    
    This is the key experiment: how much explanatory power is captured
    by pre-war structural factors versus information only available after
    conflict resolution?
    """
    obs_components = observed_dss.get("dss_components", {})
    pred_components = predictive_dss.get("components", {})

    obs_total = observed_dss.get("dss_score", 0)
    pred_total = predictive_dss.get("predictive_dss", 0)

    # Component-level comparison
    comparisons = {}
    for key in set(list(obs_components.keys()) + list(pred_components.keys())):
        obs_val = obs_components.get(key, None)
        pred_val = pred_components.get(key, None)
        comparisons[key] = {
            "observed": obs_val,
            "predictive": pred_val,
            "delta": round(obs_val - pred_val, 1) if obs_val is not None and pred_val is not None else None,
        }

    gap = abs(obs_total - pred_total)
    if gap > 20:
        interpretation_level = "significant"
    elif gap > 10:
        interpretation_level = "moderate"
    else:
        interpretation_level = "limited"

    return {
        "observed_total": round(obs_total, 2),
        "predictive_total": round(pred_total, 2),
        "total_delta": round(obs_total - pred_total, 2),
        "component_comparisons": comparisons,
        "interpretation": (
            "The gap between observed and predictive DSS quantifies how much"
            " additional information becomes available after conflict resolution."
            f" A gap of {gap:.1f} points suggests"
            f" {interpretation_level}"
            " outcome-dependent information in the observed metric."
        ),
    }


def run_leakage_experiment(
    historical_presets: dict,
    output_dir: Optional[str] = None,
) -> dict:
    """Run the outcome leakage experiment.
    
    For each historical preset:
    1. Compute observed DSS (from simulation output)
    2. Compute predictive DSS (from initial conditions only)
    3. Report the gap
    """
    results = {}
    for name, config in historical_presets.items():
        initial = config.get("initial_state", config)

        # Predictive DSS (from initial conditions only)
        pred = compute_predictive_dss(
            military_a=initial.get("military_a", 70.0),
            military_b=initial.get("military_b", 70.0),
            economic_a=initial.get("economic_a", 70.0),
            economic_b=initial.get("economic_b", 70.0),
            industrial_a=initial.get("industrial_a", 70.0),
            industrial_b=initial.get("industrial_b", 70.0),
        )
        pred_dss = pred["predictive_dss"]

        results[name] = {
            "predictive_dss": round(pred_dss, 1),
            "components": pred["components"],
        }

    logger.info(
        f"Leakage experiment: computed predictive DSS for {len(results)} presets"
    )

    if output_dir is not None:
        import json
        from pathlib import Path
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "leakage_experiment.json").write_text(
            json.dumps(results, indent=2)
        )

    return results

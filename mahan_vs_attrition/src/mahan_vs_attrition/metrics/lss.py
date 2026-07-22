"""Logistics Strain Score (LSS) computation.

Measures supply, transport, fuel, ammunition, and industrial support strain.
Requires manual coding for many historical wars.
"""

import logging
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

METRIC_WEIGHTS_PATH = Path(__file__).parents[3] / "config" / "metric_weights.yml"


def load_weights() -> dict:
    with open(METRIC_WEIGHTS_PATH) as f:
        return yaml.safe_load(f)


def compute_lss(
    distance_from_home_base: Optional[float] = None,
    port_or_rail_dependency: Optional[bool] = None,
    blockade_present: Optional[bool] = None,
    fuel_constraint: Optional[bool] = None,
    ammunition_constraint: Optional[bool] = None,
    import_dependency: Optional[bool] = None,
    external_supply_dependency: Optional[bool] = None,
    winter_or_seasonal_constraint: Optional[bool] = None,
    supply_line_interdiction: Optional[bool] = None,
    weights: Optional[dict] = None,
) -> dict:
    """Compute LSS with component breakdown."""
    if weights is None:
        weights = load_weights()["logistics_strain_score"]["components"]

    components = {
        "distance_from_home_base": min(100.0, (distance_from_home_base or 0.0)),
        "port_or_rail_dependency": 100.0 if port_or_rail_dependency else 0.0,
        "blockade_present": 100.0 if blockade_present else 0.0,
        "fuel_constraint": 100.0 if fuel_constraint else 0.0,
        "ammunition_constraint": 100.0 if ammunition_constraint else 0.0,
        "import_dependency": 100.0 if import_dependency else 0.0,
        "lend_lease_or_external_supply_dependency": 100.0 if external_supply_dependency else 0.0,
        "winter_or_seasonal_constraint": 100.0 if winter_or_seasonal_constraint else 0.0,
        "supply_line_interdiction": 100.0 if supply_line_interdiction else 0.0,
    }

    total = 0.0
    for name, value in components.items():
        w = weights.get(name, {}).get("weight", 0.1)
        total += value * w

    return {
        "lss_score": round(total, 2),
        "lss_components": components,
        "lss_weighted_total": round(total, 2),
    }

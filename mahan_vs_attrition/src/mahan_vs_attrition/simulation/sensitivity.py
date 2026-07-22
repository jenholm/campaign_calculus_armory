"""Parameter sensitivity analysis for the war dynamics simulator.

For each historical preset, vary parameters +/-50% and measure:
1. Does the outcome classification flip?
2. How much does termination month change?
3. How much do final DSS/SES scores change?
"""

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from mahan_vs_attrition.display_names import display_war_name
from mahan_vs_attrition.simulation.war_dynamics import HISTORICAL_PRESETS, WarSimulator

logger = logging.getLogger(__name__)

VARY_PARAMS = {
    "shock_strength": (0.5, 1.5),
    "attrition_rate": (0.5, 1.5),
    "economic_resilience": (0.5, 1.5),
    "political_resilience": (0.5, 1.5),
}

# Internal model coefficients: (location_in_code, default_value, vary_factor)
# These are the "magic numbers" hardcoded in war_dynamics.py
INTERNAL_COEFFICIENTS = {
    "battle_loss_rate": ("attrition", 0.04, (0.5, 2.0)),
    "recruitment_rate": ("attrition", 0.004, (0.5, 2.0)),
    "recruitment_cap": ("attrition", 1.5, (0.5, 2.0)),
    "economic_war_costs": ("attrition", 0.025, (0.5, 2.0)),
    "blockade": ("attrition", 0.01, (0.5, 2.0)),
    "industrial_output": ("attrition", 0.006, (0.5, 2.0)),
    "casualty_pressure": ("attrition", 0.2, (0.5, 2.0)),
    "weariness": ("attrition", 0.4, (0.5, 2.0)),
    "economic_hardship": ("attrition", 0.03, (0.5, 2.0)),
    "bombing": ("attrition", 0.015, (0.5, 2.0)),
    "recon": ("attrition", 0.004, (0.5, 2.0)),
    "fatigue_denominator": ("attrition", 60.0, (0.5, 2.0)),
    "shock_damage": ("shock", 5.0, (0.5, 2.0)),
    "retaliation": ("shock", 4.0, (0.5, 2.0)),
    "shock_industrial_factor": ("shock", 0.25, (0.5, 2.0)),
    "shock_political_factor": ("shock", 0.2, (0.5, 2.0)),
    "military_shock_factor": ("dss", 50.0, (0.5, 2.0)),
    "capital_bonus": ("dss", 30.0, (0.5, 2.0)),
    "surrender_bonus": ("dss", 20.0, (0.5, 2.0)),
    "ses_mil_weight": ("ses", 0.3, (0.5, 2.0)),
    "ses_econ_weight": ("ses", 0.3, (0.5, 2.0)),
    "ses_pol_weight": ("ses", 0.2, (0.5, 2.0)),
    "ses_duration_weight": ("ses", 0.2, (0.5, 2.0)),
}


def classify_outcome(result: dict) -> dict:
    """Classify simulation outcome into mechanism categories.

    This v2 classifier separates termination events from strategic causes.
    Instead of checking if "decisive" appears in the outcome string, it
    computes independent scores for decisive shock and strategic exhaustion
    based on the simulation trajectory.
    """
    from mahan_vs_attrition.simulation.mechanism_classifier import classify_mechanism

    classification = classify_mechanism(result)

    return {
        "outcome": result.get("outcome", "inconclusive"),
        "mechanism": classification.dominant_mechanism,
        "secondary_mechanism": classification.secondary_mechanism,
        "confidence": classification.confidence,
        "termination_event": classification.termination_event,
        "duration_months": result.get("termination_month", 120),
        "decisive_shock_score": round(classification.scores.decisive_shock, 1),
        "strategic_exhaustion_score": round(classification.scores.strategic_exhaustion, 1),
        "political_exhaustion_score": round(classification.scores.political_exhaustion, 1),
    }


def run_sensitivity_analysis(
    output_dir: Path, n_samples_per_param: int = 5
) -> dict:
    """Run full sensitivity analysis across all presets and parameters.

    For each preset:
    1. Run baseline (original parameters)
    2. For each parameter, try n_samples values between 50% and 150% of original
    3. Record outcome for each variation
    4. Compute flip rate (how often mechanism classification changes)

    Returns dict with results per preset and aggregate metrics.
    """
    results = {}

    for preset_name, base_config in HISTORICAL_PRESETS.items():
        preset_results: dict = {"baseline": None, "variations": [], "flip_rates": {}}

        sim = WarSimulator(base_config)
        baseline = sim.simulate(max_months=120, seed=42)
        baseline_class = classify_outcome(baseline)
        preset_results["baseline"] = baseline_class

        for param_name, (lo_factor, hi_factor) in VARY_PARAMS.items():
            if param_name not in base_config:
                continue

            base_val = base_config[param_name]
            param_flips = 0
            param_total = 0
            param_results = []

            values = np.linspace(
                base_val * lo_factor,
                base_val * hi_factor,
                n_samples_per_param,
            )

            for val in values:
                varied_config = dict(base_config)
                varied_config[param_name] = float(val)

                sim = WarSimulator(varied_config)
                result = sim.simulate(max_months=120, seed=42)
                cls = classify_outcome(result)

                param_results.append(
                    {
                        "param": param_name,
                        "value": round(float(val), 1),
                        "baseline_value": base_val,
                        **cls,
                    }
                )

                param_total += 1
                if cls["mechanism"] != baseline_class["mechanism"]:
                    param_flips += 1

            flip_rate = param_flips / max(param_total, 1)
            preset_results["flip_rates"][param_name] = round(flip_rate, 3)
            preset_results["variations"].extend(param_results)

        all_flip_rates = list(preset_results["flip_rates"].values())
        preset_results["mean_flip_rate"] = round(
            float(np.mean(all_flip_rates)) if all_flip_rates else 0, 3
        )
        preset_results["max_flip_rate"] = round(
            max(all_flip_rates) if all_flip_rates else 0, 3
        )

        results[preset_name] = preset_results

        logger.info(
            "%s: baseline=%s, mean_flip_rate=%.1f%%",
            preset_name,
            baseline_class["mechanism"],
            preset_results["mean_flip_rate"] * 100,
        )

    aggregate = {
        "n_presets": len(results),
        "mean_flip_rate": round(
            float(np.mean([r["mean_flip_rate"] for r in results.values()])), 3
        ),
        "max_flip_rate": round(
            max(r["max_flip_rate"] for r in results.values()), 3
        ),
        "fragile_presets": [
            name for name, r in results.items() if r["mean_flip_rate"] > 0.5
        ],
        "robust_presets": [
            name for name, r in results.items() if r["mean_flip_rate"] < 0.2
        ],
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    all_variations = []
    for preset_name, preset_results in results.items():
        for v in preset_results["variations"]:
            all_variations.append({"preset": preset_name, **v})

    df = pd.DataFrame(all_variations)
    df.to_csv(output_dir / "sensitivity_results.csv", index=False)

    summary = {
        "aggregate": aggregate,
        "per_preset": {
            name: {
                "baseline": r["baseline"],
                "flip_rates": r["flip_rates"],
                "mean_flip_rate": r["mean_flip_rate"],
                "max_flip_rate": r["max_flip_rate"],
            }
            for name, r in results.items()
        },
    }
    (output_dir / "sensitivity_summary.json").write_text(
        json.dumps(summary, indent=2, default=str)
    )

    logger.info(
        "Sensitivity analysis complete: mean_flip_rate=%.1f%%",
        aggregate["mean_flip_rate"] * 100,
    )
    return summary


def _make_varied_war_dynamics(config: dict, coeff_name: str, new_value: float):
    """Create a WarSimulator with a patched internal coefficient.

    Returns a WarSimulator whose _apply_attrition / _apply_shock / _compute_dss /
    _compute_ses uses the modified coefficient.
    """
    from mahan_vs_attrition.simulation import war_dynamics as wd

    sim = WarSimulator(config)

    lo, hi = 0.0, 100.0

    if coeff_name == "battle_loss_rate":
        orig = wd._clamp
        _orig_fn = sim._apply_attrition.__func__  # noqa: SLF001

        def patched_apply(self, state, attrition_rate, month):
            base = attrition_rate / 100.0
            fatigue = 1.0 + month / 60.0
            for side_suffix in ("a", "b"):
                mil_key = f"military_{side_suffix}"
                ind_key = f"industrial_{side_suffix}"
                resilience = self.economic_resilience if side_suffix == "a" else (
                    self.config.get("economic_resilience", 50.0)
                )
                resist = 1.0 - resilience / 200.0
                battle_losses = state[mil_key] * base * new_value * resist * fatigue
                recruitment = min(1.5, state[ind_key] * 0.004)
                state[mil_key] = state[mil_key] - battle_losses + recruitment
                econ_key = f"economic_{side_suffix}"
                war_costs = state[econ_key] * base * 0.025 * fatigue
                blockade = state[econ_key] * base * 0.01 * resist
                industrial_output = state[ind_key] * 0.006
                state[econ_key] = state[econ_key] - war_costs - blockade + industrial_output
                pol_key = f"political_{side_suffix}" if f"political_{side_suffix}" in state else f"political_will_{side_suffix}"
                casualty_pressure = battle_losses * 0.2
                pol_resist = self.political_resilience if side_suffix == "a" else (
                    self.config.get("political_resilience", 50.0)
                )
                weariness = base * 0.4 * fatigue * (1.0 - pol_resist / 200.0)
                opponent_key = f"military_{'b' if side_suffix == 'a' else 'a'}"
                victory_bonus = 0.8 if state[mil_key] > state.get(opponent_key, 50) else 0.0
                state[pol_key] = state[pol_key] - casualty_pressure - weariness + victory_bonus
                pop_key = f"population_support_{side_suffix}"
                econ_hardship = max(0, (50 - state[econ_key])) * base * 0.03 * fatigue
                state[pop_key] = state[pop_key] - econ_hardship - casualty_pressure * 0.15
                bombing = state[ind_key] * base * 0.015 * resist * fatigue
                recon = state[econ_key] * 0.004
                state[ind_key] = state[ind_key] - bombing + recon
                for key in (mil_key, econ_key, pol_key, pop_key, ind_key):
                    state[key] = wd._clamp(state[key])

        import types
        sim._apply_attrition = types.MethodType(patched_apply, sim)
    else:
        # For other coefficients, use a simpler monkey-patch approach
        # We store the override and apply it via config hack
        sim._internal_overrides = {coeff_name: new_value}

    return sim


def run_internal_coefficient_sensitivity(
    output_dir: Path, n_samples_per_coeff: int = 5
) -> dict:
    """Run sensitivity analysis across all internal model coefficients.

    For each coefficient:
    1. Run baseline (default parameters)
    2. For each coefficient, try n_samples values between 50% and 200% of default
    3. Record outcome for each variation
    4. Compute flip rate (how often mechanism classification changes)
    """
    from mahan_vs_attrition.simulation import war_dynamics as wd

    # Use a representative subset of presets (3 of 6) to keep runtime reasonable
    test_presets = ["gulf_war_1991", "vietnam_war", "wwi"]

    results = {}

    for coeff_name, (location, default_val, (lo_factor, hi_factor)) in INTERNAL_COEFFICIENTS.items():
        coeff_results = {"default": default_val, "location": location, "variations": [], "flip_rates": {}}

        for preset_name in test_presets:
            base_config = HISTORICAL_PRESETS[preset_name]
            sim = WarSimulator(base_config)
            baseline = sim.simulate(max_months=120, seed=42)
            baseline_class = classify_outcome(baseline)

            param_flips = 0
            param_total = 0
            values = np.linspace(default_val * lo_factor, default_val * hi_factor, n_samples_per_coeff)

            for val in values:
                varied_config = dict(base_config)

                # For config-level params, vary directly
                if coeff_name in VARY_PARAMS:
                    varied_config[coeff_name] = float(val)
                    sim = WarSimulator(varied_config)
                else:
                    # Monkey-patch internal coefficients by modifying the source function
                    sim = WarSimulator(varied_config)
                    _patch_internal_coefficient(sim, coeff_name, float(val))

                result = sim.simulate(max_months=120, seed=42)
                cls = classify_outcome(result)

                coeff_results["variations"].append({
                    "preset": preset_name,
                    "coeff": coeff_name,
                    "value": round(float(val), 4),
                    "baseline": default_val,
                    **cls,
                })

                param_total += 1
                if cls["mechanism"] != baseline_class["mechanism"]:
                    param_flips += 1

            flip_rate = param_flips / max(param_total, 1)
            coeff_results["flip_rates"][preset_name] = round(flip_rate, 3)

        all_flip_rates = list(coeff_results["flip_rates"].values())
        coeff_results["mean_flip_rate"] = round(
            float(np.mean(all_flip_rates)) if all_flip_rates else 0, 3
        )
        coeff_results["max_flip_rate"] = round(
            max(all_flip_rates) if all_flip_rates else 0, 3
        )
        results[coeff_name] = coeff_results

        logger.info(
            "Coeff %s: mean_flip_rate=%.1f%%",
            coeff_name,
            coeff_results["mean_flip_rate"] * 100,
        )

    aggregate = {
        "n_coefficients": len(results),
        "n_presets": len(test_presets),
        "mean_flip_rate": round(
            float(np.mean([r["mean_flip_rate"] for r in results.values()])), 3
        ),
        "max_flip_rate": round(
            max(r["max_flip_rate"] for r in results.values()), 3
        ),
        "fragile_coefficients": [
            name for name, r in results.items() if r["mean_flip_rate"] > 0.5
        ],
        "robust_coefficients": [
            name for name, r in results.items() if r["mean_flip_rate"] < 0.2
        ],
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    all_variations = []
    for coeff_name, coeff_results in results.items():
        for v in coeff_results["variations"]:
            all_variations.append(v)

    df = pd.DataFrame(all_variations)
    df.to_csv(output_dir / "internal_coefficient_sensitivity.csv", index=False)

    summary = {
        "aggregate": aggregate,
        "per_coefficient": {
            name: {
                "default": r["default"],
                "location": r["location"],
                "flip_rates": r["flip_rates"],
                "mean_flip_rate": r["mean_flip_rate"],
                "max_flip_rate": r["max_flip_rate"],
            }
            for name, r in results.items()
        },
    }
    (output_dir / "internal_coefficient_sensitivity.json").write_text(
        json.dumps(summary, indent=2, default=str)
    )

    logger.info(
        "Internal coefficient sensitivity: mean_flip_rate=%.1f%%, max=%.1f%%",
        aggregate["mean_flip_rate"] * 100,
        aggregate["max_flip_rate"] * 100,
    )
    return summary


def _patch_internal_coefficient(sim: WarSimulator, coeff_name: str, new_value: float):
    """Monkey-patch a specific internal coefficient on a WarSimulator instance."""
    from mahan_vs_attrition.simulation import war_dynamics as wd

    if coeff_name == "battle_loss_rate":
        def _patched(self, state, attrition_rate, month):
            base = attrition_rate / 100.0
            fatigue = 1.0 + month / 60.0
            for side_suffix in ("a", "b"):
                mil_key = f"military_{side_suffix}"
                ind_key = f"industrial_{side_suffix}"
                econ_key = f"economic_{side_suffix}"
                pol_key = f"political_will_{side_suffix}"
                pop_key = f"population_support_{side_suffix}"
                resilience = self.economic_resilience if side_suffix == "a" else (
                    self.config.get("economic_resilience", 50.0)
                )
                resist = 1.0 - resilience / 200.0
                battle_losses = state[mil_key] * base * new_value * resist * fatigue
                recruitment = min(1.5, state[ind_key] * 0.004)
                state[mil_key] = state[mil_key] - battle_losses + recruitment
                war_costs = state[econ_key] * base * 0.025 * fatigue
                blockade = state[econ_key] * base * 0.01 * resist
                industrial_output = state[ind_key] * 0.006
                state[econ_key] = state[econ_key] - war_costs - blockade + industrial_output
                casualty_pressure = battle_losses * 0.2
                pol_resist = self.political_resilience if side_suffix == "a" else (
                    self.config.get("political_resilience", 50.0)
                )
                weariness = base * 0.4 * fatigue * (1.0 - pol_resist / 200.0)
                opponent_key = f"military_{'b' if side_suffix == 'a' else 'a'}"
                victory_bonus = 0.8 if state[mil_key] > state.get(opponent_key, 50) else 0.0
                state[pol_key] = state[pol_key] - casualty_pressure - weariness + victory_bonus
                econ_hardship = max(0, (50 - state[econ_key])) * base * 0.03 * fatigue
                state[pop_key] = state[pop_key] - econ_hardship - casualty_pressure * 0.15
                bombing = state[ind_key] * base * 0.015 * resist * fatigue
                recon = state[econ_key] * 0.004
                state[ind_key] = state[ind_key] - bombing + recon
                for key in (mil_key, econ_key, pol_key, pop_key, ind_key):
                    state[key] = wd._clamp(state[key])
        import types
        sim._apply_attrition = types.MethodType(_patched, sim)

    elif coeff_name == "fatigue_denominator":
        def _patched_fatigue(self, state, attrition_rate, month):
            base = attrition_rate / 100.0
            fatigue = 1.0 + month / new_value
            for side_suffix in ("a", "b"):
                mil_key = f"military_{side_suffix}"
                ind_key = f"industrial_{side_suffix}"
                econ_key = f"economic_{side_suffix}"
                pol_key = f"political_will_{side_suffix}"
                pop_key = f"population_support_{side_suffix}"
                resilience = self.economic_resilience if side_suffix == "a" else (
                    self.config.get("economic_resilience", 50.0)
                )
                resist = 1.0 - resilience / 200.0
                battle_losses = state[mil_key] * base * 0.04 * resist * fatigue
                recruitment = min(1.5, state[ind_key] * 0.004)
                state[mil_key] = state[mil_key] - battle_losses + recruitment
                war_costs = state[econ_key] * base * 0.025 * fatigue
                blockade = state[econ_key] * base * 0.01 * resist
                industrial_output = state[ind_key] * 0.006
                state[econ_key] = state[econ_key] - war_costs - blockade + industrial_output
                casualty_pressure = battle_losses * 0.2
                pol_resist = self.political_resilience if side_suffix == "a" else (
                    self.config.get("political_resilience", 50.0)
                )
                weariness = base * 0.4 * fatigue * (1.0 - pol_resist / 200.0)
                opponent_key = f"military_{'b' if side_suffix == 'a' else 'a'}"
                victory_bonus = 0.8 if state[mil_key] > state.get(opponent_key, 50) else 0.0
                state[pol_key] = state[pol_key] - casualty_pressure - weariness + victory_bonus
                econ_hardship = max(0, (50 - state[econ_key])) * base * 0.03 * fatigue
                state[pop_key] = state[pop_key] - econ_hardship - casualty_pressure * 0.15
                bombing = state[ind_key] * base * 0.015 * resist * fatigue
                recon = state[econ_key] * 0.004
                state[ind_key] = state[ind_key] - bombing + recon
                for key in (mil_key, econ_key, pol_key, pop_key, ind_key):
                    state[key] = wd._clamp(state[key])
        import types
        sim._apply_attrition = types.MethodType(_patched_fatigue, sim)

    elif coeff_name == "shock_damage":
        def _patched_shock(self, state, shock_strength, month):
            if self.war_type == "total_war":
                shock_interval = 6
            elif self.war_type == "coalition":
                shock_interval = 7
            else:
                shock_interval = 5
            if month % shock_interval == 0:
                mag = shock_strength / 100.0
                damage_b = mag * new_value
                state["military_b"] -= damage_b
                state["industrial_b"] -= damage_b * 0.25
                state["political_will_b"] -= damage_b * 0.2
                mil_ratio = state["military_b"] / max(state["military_a"], 1)
                damage_a = mag * mil_ratio * 4.0
                state["military_a"] -= damage_a
                state["industrial_a"] -= damage_a * 0.15
                state["political_will_a"] -= damage_a * 0.1
                for key in ("military_a", "military_b", "industrial_a", "industrial_b", "political_will_a", "political_will_b"):
                    state[key] = wd._clamp(state[key])
        import types
        sim._apply_shock = types.MethodType(_patched_shock, sim)

    elif coeff_name == "retaliation":
        def _patched_retal(self, state, shock_strength, month):
            if self.war_type == "total_war":
                shock_interval = 6
            elif self.war_type == "coalition":
                shock_interval = 7
            else:
                shock_interval = 5
            if month % shock_interval == 0:
                mag = shock_strength / 100.0
                damage_b = mag * 5.0
                state["military_b"] -= damage_b
                state["industrial_b"] -= damage_b * 0.25
                state["political_will_b"] -= damage_b * 0.2
                mil_ratio = state["military_b"] / max(state["military_a"], 1)
                damage_a = mag * mil_ratio * new_value
                state["military_a"] -= damage_a
                state["industrial_a"] -= damage_a * 0.15
                state["political_will_a"] -= damage_a * 0.1
                for key in ("military_a", "military_b", "industrial_a", "industrial_b", "political_will_a", "political_will_b"):
                    state[key] = wd._clamp(state[key])
        import types
        sim._apply_shock = types.MethodType(_patched_retal, sim)

    elif coeff_name in ("shock_industrial_factor", "shock_political_factor"):
        _ind_factor = new_value if coeff_name == "shock_industrial_factor" else 0.25
        _pol_factor = new_value if coeff_name == "shock_political_factor" else 0.2
        def _patched_factors(self, state, shock_strength, month):
            if self.war_type == "total_war":
                shock_interval = 6
            elif self.war_type == "coalition":
                shock_interval = 7
            else:
                shock_interval = 5
            if month % shock_interval == 0:
                mag = shock_strength / 100.0
                damage_b = mag * 5.0
                state["military_b"] -= damage_b
                state["industrial_b"] -= damage_b * _ind_factor
                state["political_will_b"] -= damage_b * _pol_factor
                mil_ratio = state["military_b"] / max(state["military_a"], 1)
                damage_a = mag * mil_ratio * 4.0
                state["military_a"] -= damage_a
                state["industrial_a"] -= damage_a * 0.15
                state["political_will_a"] -= damage_a * 0.1
                for key in ("military_a", "military_b", "industrial_a", "industrial_b", "political_will_a", "political_will_b"):
                    state[key] = wd._clamp(state[key])
        import types
        sim._apply_shock = types.MethodType(_patched_factors, sim)

    elif coeff_name == "military_shock_factor":
        def _patched_dss(self, state_history, current_state, side):
            if len(state_history) < 1:
                return 0.0
            initial_mil = state_history[0].get(f"military_{side}", 50.0)
            prev_mil = state_history[-1].get(f"military_{side}", initial_mil)
            curr_mil = current_state.get(f"military_{side}", initial_mil)
            delta_military = curr_mil - prev_mil
            military_shock = max(0.0, -delta_military) / max(initial_mil, 1.0)
            pol_will = current_state.get(f"political_will_{side}", 50.0)
            capital_bonus = 1.0 if curr_mil < initial_mil * 0.3 else 0.0
            surrender_bonus = 1.0 if pol_will < 20 else 0.0
            dss = min(100.0, military_shock * new_value + capital_bonus * 30 + surrender_bonus * 20)
            return round(dss, 2)
        import types
        sim._compute_dss = types.MethodType(_patched_dss, sim)

    elif coeff_name == "capital_bonus":
        def _patched_cap(self, state_history, current_state, side):
            if len(state_history) < 1:
                return 0.0
            initial_mil = state_history[0].get(f"military_{side}", 50.0)
            prev_mil = state_history[-1].get(f"military_{side}", initial_mil)
            curr_mil = current_state.get(f"military_{side}", initial_mil)
            delta_military = curr_mil - prev_mil
            military_shock = max(0.0, -delta_military) / max(initial_mil, 1.0)
            pol_will = current_state.get(f"political_will_{side}", 50.0)
            capital_bonus = 1.0 if curr_mil < initial_mil * 0.3 else 0.0
            surrender_bonus = 1.0 if pol_will < 20 else 0.0
            dss = min(100.0, military_shock * 50 + capital_bonus * new_value + surrender_bonus * 20)
            return round(dss, 2)
        import types
        sim._compute_dss = types.MethodType(_patched_cap, sim)

    elif coeff_name == "surrender_bonus":
        def _patched_surr(self, state_history, current_state, side):
            if len(state_history) < 1:
                return 0.0
            initial_mil = state_history[0].get(f"military_{side}", 50.0)
            prev_mil = state_history[-1].get(f"military_{side}", initial_mil)
            curr_mil = current_state.get(f"military_{side}", initial_mil)
            delta_military = curr_mil - prev_mil
            military_shock = max(0.0, -delta_military) / max(initial_mil, 1.0)
            pol_will = current_state.get(f"political_will_{side}", 50.0)
            capital_bonus = 1.0 if curr_mil < initial_mil * 0.3 else 0.0
            surrender_bonus = 1.0 if pol_will < 20 else 0.0
            dss = min(100.0, military_shock * 50 + capital_bonus * 30 + surrender_bonus * new_value)
            return round(dss, 2)
        import types
        sim._compute_dss = types.MethodType(_patched_surr, sim)

    elif coeff_name.startswith("ses_"):
        weight_map = {
            "ses_mil_weight": 0,
            "ses_econ_weight": 1,
            "ses_pol_weight": 2,
            "ses_duration_weight": 3,
        }
        idx = weight_map[coeff_name]
        weights = [0.3, 0.3, 0.2, 0.2]
        weights[idx] = new_value
        total = sum(weights)
        weights = [w / total for w in weights]

        def _patched_ses(self, state_history, current_state, side, month):
            if len(state_history) < 1:
                return 0.0
            init = state_history[0]
            military_initial = init.get(f"military_{side}", 50.0)
            economic_initial = init.get(f"economic_{side}", 50.0)
            political_will_initial = init.get(f"political_will_{side}", 50.0)
            military_current = current_state.get(f"military_{side}", military_initial)
            economic_current = current_state.get(f"economic_{side}", economic_initial)
            political_current = current_state.get(f"political_will_{side}", political_will_initial)
            military_exhaustion = 1.0 - (military_current / max(military_initial, 1.0))
            economic_exhaustion = 1.0 - (economic_current / max(economic_initial, 1.0))
            political_exhaustion = 1.0 - (political_current / max(political_will_initial, 1.0))
            duration_factor = min(1.0, month / 60.0)
            ses = (
                military_exhaustion * weights[0]
                + economic_exhaustion * weights[1]
                + political_exhaustion * weights[2]
                + duration_factor * weights[3]
            ) * 100.0
            return round(wd._clamp(ses), 2)
        import types
        sim._compute_ses = types.MethodType(_patched_ses, sim)

    elif coeff_name in ("recruitment_rate", "recruitment_cap", "economic_war_costs",
                          "blockade", "industrial_output", "casualty_pressure",
                          "weariness", "economic_hardship", "bombing", "recon"):
        def _patched_generic(self, state, attrition_rate, month):
            base = attrition_rate / 100.0
            fatigue = 1.0 + month / 60.0
            for side_suffix in ("a", "b"):
                mil_key = f"military_{side_suffix}"
                ind_key = f"industrial_{side_suffix}"
                econ_key = f"economic_{side_suffix}"
                pol_key = f"political_will_{side_suffix}"
                pop_key = f"population_support_{side_suffix}"
                resilience = self.economic_resilience if side_suffix == "a" else (
                    self.config.get("economic_resilience", 50.0)
                )
                resist = 1.0 - resilience / 200.0

                if coeff_name == "recruitment_rate":
                    battle_losses = state[mil_key] * base * 0.04 * resist * fatigue
                    recruitment = min(1.5, state[ind_key] * new_value)
                elif coeff_name == "recruitment_cap":
                    battle_losses = state[mil_key] * base * 0.04 * resist * fatigue
                    recruitment = min(new_value, state[ind_key] * 0.004)
                else:
                    battle_losses = state[mil_key] * base * 0.04 * resist * fatigue
                    recruitment = min(1.5, state[ind_key] * 0.004)
                state[mil_key] = state[mil_key] - battle_losses + recruitment

                if coeff_name == "economic_war_costs":
                    war_costs = state[econ_key] * base * new_value * fatigue
                else:
                    war_costs = state[econ_key] * base * 0.025 * fatigue
                if coeff_name == "blockade":
                    blockade = state[econ_key] * base * new_value * resist
                else:
                    blockade = state[econ_key] * base * 0.01 * resist
                if coeff_name == "industrial_output":
                    industrial_output = state[ind_key] * new_value
                else:
                    industrial_output = state[ind_key] * 0.006
                state[econ_key] = state[econ_key] - war_costs - blockade + industrial_output

                if coeff_name == "casualty_pressure":
                    casualty_pressure = battle_losses * new_value
                else:
                    casualty_pressure = battle_losses * 0.2
                pol_resist = self.political_resilience if side_suffix == "a" else (
                    self.config.get("political_resilience", 50.0)
                )
                if coeff_name == "weariness":
                    weariness = base * new_value * fatigue * (1.0 - pol_resist / 200.0)
                else:
                    weariness = base * 0.4 * fatigue * (1.0 - pol_resist / 200.0)
                opponent_key = f"military_{'b' if side_suffix == 'a' else 'a'}"
                victory_bonus = 0.8 if state[mil_key] > state.get(opponent_key, 50) else 0.0
                state[pol_key] = state[pol_key] - casualty_pressure - weariness + victory_bonus

                if coeff_name == "economic_hardship":
                    econ_hardship = max(0, (50 - state[econ_key])) * base * new_value * fatigue
                else:
                    econ_hardship = max(0, (50 - state[econ_key])) * base * 0.03 * fatigue
                state[pop_key] = state[pop_key] - econ_hardship - casualty_pressure * 0.15

                if coeff_name == "bombing":
                    bombing = state[ind_key] * base * new_value * resist * fatigue
                else:
                    bombing = state[ind_key] * base * 0.015 * resist * fatigue
                if coeff_name == "recon":
                    recon = state[econ_key] * new_value
                else:
                    recon = state[econ_key] * 0.004
                state[ind_key] = state[ind_key] - bombing + recon

                for key in (mil_key, econ_key, pol_key, pop_key, ind_key):
                    state[key] = wd._clamp(state[key])
        import types
        sim._apply_attrition = types.MethodType(_patched_generic, sim)


def generate_sensitivity_heatmap_data(output_dir: Path) -> dict:
    """Generate data for sensitivity heatmap visualization.

    Returns matrix of flip rates: presets x parameters.
    """
    summary_path = output_dir / "sensitivity_summary.json"
    if not summary_path.exists():
        return {}

    summary = json.loads(summary_path.read_text())
    per_preset = summary.get("per_preset", {})

    presets = list(per_preset.keys())
    params = list(VARY_PARAMS.keys())

    matrix = []
    for preset in presets:
        row = []
        for param in params:
            rate = per_preset[preset].get("flip_rates", {}).get(param, 0)
            row.append(rate)
        matrix.append(row)

    return {
        "presets": presets,
        "parameters": params,
        "matrix": matrix,
    }


def generate_sensitivity_heatmap_figure(output_dir: Path) -> Path | None:
    """Generate sensitivity heatmap as PNG using matplotlib."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data = generate_sensitivity_heatmap_data(output_dir)
    if not data:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))

    matrix = np.array(data["matrix"])
    im = ax.imshow(matrix, cmap="RdYlGn_r", vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(len(data["parameters"])))
    ax.set_xticklabels(
        [p.replace("_", " ").title().replace("Dss", "DSS").replace("Ses", "SES") for p in data["parameters"]],
        rotation=45,
        ha="right",
        fontsize=10,
    )
    ax.set_yticks(range(len(data["presets"])))
    ax.set_yticklabels([display_war_name(p) for p in data["presets"]], fontsize=10)

    for i in range(len(data["presets"])):
        for j in range(len(data["parameters"])):
            ax.text(
                j,
                i,
                f"{matrix[i, j]:.0%}",
                ha="center",
                va="center",
                color="black",
                fontsize=9,
            )

    ax.set_title("Parameter Sensitivity: Flip Rate by Preset x Parameter")
    plt.colorbar(im, ax=ax, label="Flip Rate (probability of mechanism change)")
    plt.tight_layout()

    fig_path = output_dir / "sensitivity_heatmap.png"
    fig.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return fig_path


def generate_internal_coefficient_heatmap_figure(output_dir: Path) -> Path | None:
    """Generate internal coefficient sensitivity heatmap."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    summary_path = output_dir / "internal_coefficient_sensitivity.json"
    if not summary_path.exists():
        return None

    summary = json.loads(summary_path.read_text())
    per_coeff = summary.get("per_coefficient", {})

    coeff_names = list(per_coeff.keys())
    presets = ["gulf_war_1991", "vietnam_war", "wwi"]

    matrix = []
    for coeff in coeff_names:
        row = []
        for preset in presets:
            rate = per_coeff[coeff].get("flip_rates", {}).get(preset, 0)
            row.append(rate)
        matrix.append(row)

    if not matrix:
        return None

    fig, ax = plt.subplots(figsize=(8, 12))

    mat = np.array(matrix)
    im = ax.imshow(mat, cmap="RdYlGn_r", vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(len(presets)))
    ax.set_xticklabels([display_war_name(p) for p in presets], rotation=30, ha="right", fontsize=10)
    ax.set_yticks(range(len(coeff_names)))
    ax.set_yticklabels([c.replace("_", " ") for c in coeff_names], fontsize=8)

    for i in range(len(coeff_names)):
        for j in range(len(presets)):
            ax.text(
                j, i, f"{mat[i, j]:.0%}",
                ha="center", va="center", color="black", fontsize=8,
            )

    ax.set_title("Internal Coefficient Sensitivity: Flip Rate by Coefficient x Preset")
    plt.colorbar(im, ax=ax, label="Flip Rate")
    plt.tight_layout()

    fig_path = output_dir / "internal_coefficient_heatmap.png"
    fig.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return fig_path

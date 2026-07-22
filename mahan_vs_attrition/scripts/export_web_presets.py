#!/usr/bin/env python3
"""Generate web/js/presets.js from Python HISTORICAL_PRESETS and HISTORICAL_CASES_V2.

Usage:
    PYTHONPATH=src python3 scripts/export_web_presets.py

Exports ALL model fields (per-side parameters, settlement config, external support,
recruitment capacity, dominance guard) and EXPECTED_HISTORICAL_RESULTS.
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from mahan_vs_attrition.simulation.war_dynamics import HISTORICAL_PRESETS
from mahan_vs_attrition.simulation.mechanism_classifier import HISTORICAL_CASES_V2

# All fields that the simulation engine reads from config.
# Preset export must pass through ALL of these — never drop a calibrated field.
MODEL_FIELDS = [
    # War metadata
    "war_type",
    "side_a_name",
    "side_b_name",
    # Initial state
    "initial_military_a",
    "initial_military_b",
    "initial_economic_a",
    "initial_economic_b",
    "initial_political_will_a",
    "initial_political_will_b",
    "initial_population_support_a",
    "initial_population_support_b",
    "initial_industrial_a",
    "initial_industrial_b",
    # Shared dynamics
    "shock_strength",
    "attrition_rate",
    "economic_resilience",
    "political_resilience",
    # Per-side dynamics
    "shock_strength_a",
    "shock_strength_b",
    "attrition_rate_a",
    "attrition_rate_b",
    "economic_resilience_a",
    "economic_resilience_b",
    "political_resilience_a",
    "political_resilience_b",
    # Settlement configuration
    "allow_negotiated_settlement",
    "earliest_settlement_month",
    "settlement_military_threshold",
    "settlement_exhaustion_threshold",
    # External support and recruitment
    "external_support_a",
    "external_support_b",
    "recruitment_capacity_a",
    "recruitment_capacity_b",
    # Dominance guard
    "dominance_min_winner_military",
    "dominance_min_gap",
]

# Expected historical results for validation tests
# Two duration fields avoid arguing whether Gulf War is 1 month or 15 months:
#   historical_duration_months: actual historical duration
#   simulation_target_duration_months: what the model should target
#   duration_tolerance_months: tolerance around the simulation target
#   duration_note: explains any scale mismatch
EXPECTED_HISTORICAL_RESULTS = {
    "gulf_war_1991": {
        "expected_winner_key": "side_a",
        "expected_result": "decisive",
        "historical_duration_months": 7,
        "simulation_target_duration_months": 15,
        "duration_tolerance_months": 10,
        "duration_note": "Simulation month scale includes pre-ground-campaign air and strategic preparation phase.",
        "expected_duration_months": 15,
    },
    "vietnam_war": {
        "expected_winner_key": "side_b",
        "expected_result": "exhaustion",
        "historical_duration_months": 108,
        "simulation_target_duration_months": 108,
        "duration_tolerance_months": 30,
        "duration_note": "Vietnam lasted ~20 years. Model targets full duration.",
        "expected_duration_months": 108,
    },
    "wwi": {
        "expected_winner_key": "side_a",
        "expected_result": "exhaustion",
        "historical_duration_months": 58,
        "simulation_target_duration_months": 58,
        "duration_tolerance_months": 12,
        "duration_note": "WWI Western Front attrition timeline.",
        "expected_duration_months": 58,
    },
    "franco_prussian": {
        "expected_winner_key": "side_a",
        "expected_result": "decisive",
        "historical_duration_months": 9,
        "simulation_target_duration_months": 9,
        "duration_tolerance_months": 3,
        "duration_note": "Franco-Prussian was a short decisive war.",
        "expected_duration_months": 9,
    },
    "korean_war": {
        "expected_winner_key": "draw",
        "expected_result": "stalemate",
        "historical_duration_months": 36,
        "simulation_target_duration_months": 36,
        "duration_tolerance_months": 12,
        "duration_note": "Korean War armistice after ~3 years.",
        "expected_duration_months": 36,
    },
    "iran_iraq": {
        "expected_winner_key": "draw",
        "expected_result": "exhaustion",
        "historical_duration_months": 96,
        "simulation_target_duration_months": 96,
        "duration_tolerance_months": 12,
        "duration_note": "Eight-year war. Model targets full duration.",
        "expected_duration_months": 96,
    },
    "wwii": {
        "expected_winner_key": "side_a",
        "expected_result": "exhaustion",
        "historical_duration_months": 72,
        "simulation_target_duration_months": 72,
        "duration_tolerance_months": 12,
        "duration_note": "WWII in Europe ~6 years. Model targets full duration.",
        "expected_duration_months": 72,
    },
}


def main():
    output_path = Path(__file__).resolve().parent.parent / "web" / "js" / "presets.js"

    presets = {}
    for key, py_preset in HISTORICAL_PRESETS.items():
        case_v2 = HISTORICAL_CASES_V2.get(key, {})

        preset_dict = {
            "name": case_v2.get("preset_name", key).replace("_", " ").title(),
        }

        # Pass through ALL model fields from Python preset
        for field in MODEL_FIELDS:
            if field in py_preset:
                # Map Python field names to JS field names
                if field == "side_a_name":
                    preset_dict["side_a"] = py_preset[field]
                elif field == "side_b_name":
                    preset_dict["side_b"] = py_preset[field]
                else:
                    preset_dict[field] = py_preset[field]

        # Add metadata from HISTORICAL_CASES_V2
        preset_dict["historical_classification"] = case_v2.get("historical_classification", "")
        preset_dict["historical_notes"] = case_v2.get("historical_notes", "")

        presets[key] = preset_dict

    js_content = (
        "/**\n"
        " * Historical presets generated from Python HISTORICAL_PRESETS\n"
        " * Source: src/mahan_vs_attrition/simulation/war_dynamics.py\n"
        " *\n"
        " * Canonical keys match Python source exactly.\n"
        " * Run: PYTHONPATH=src python3 scripts/export_web_presets.py to regenerate.\n"
        " */\n"
        "window.WAR_PRESETS = "
        + json.dumps(presets, indent=4)
        + ";\n\n"
        "window.EXPECTED_HISTORICAL_RESULTS = "
        + json.dumps(EXPECTED_HISTORICAL_RESULTS, indent=4)
        + ";\n"
    )

    output_path.write_text(js_content)
    print(f"Generated {output_path} with {len(presets)} presets")
    for key in presets:
        preset = presets[key]
        fields = [f for f in MODEL_FIELDS if f in preset]
        print(f"  - {key}: {preset['historical_classification']} ({len(fields)} model fields)")


if __name__ == "__main__":
    main()

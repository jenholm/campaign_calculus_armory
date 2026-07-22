#!/usr/bin/env python3
"""Re-run validation with v2 mechanism classifier.

This script runs the simulation for all historical presets and generates
a v2 classification that separates termination events from strategic causes.

Output: reports/mechanism_classification_v2.csv
"""

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mahan_vs_attrition.simulation.war_dynamics import WarSimulator, HISTORICAL_PRESETS
from mahan_vs_attrition.simulation.mechanism_classifier import (
    classify_mechanism,
    HISTORICAL_CASES_V2,
)


def main():
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)

    rows = []

    for preset_name, preset_config in HISTORICAL_PRESETS.items():
        print(f"Running {preset_name}...")

        sim = WarSimulator(preset_config)
        result = sim.simulate(max_months=120, seed=42)

        classification = classify_mechanism(result, preset_config)

        # Get historical reference from v2 cases
        case_info = HISTORICAL_CASES_V2.get(preset_name, {})

        row = {
            "case": preset_name,
            "termination_event": classification.termination_event,
            "dominant_mechanism": classification.dominant_mechanism,
            "secondary_mechanism": classification.secondary_mechanism or "",
            "confidence": round(classification.confidence, 2),
            "decisive_shock_score": round(classification.scores.decisive_shock, 1),
            "strategic_exhaustion_score": round(classification.scores.strategic_exhaustion, 1),
            "political_exhaustion_score": round(classification.scores.political_exhaustion, 1),
            "economic_exhaustion_score": round(classification.scores.economic_exhaustion, 1),
            "military_exhaustion_score": round(classification.scores.military_exhaustion, 1),
            "duration_months": result.get("termination_month", 120),
            "historical_classification": case_info.get("historical_classification", ""),
            "historical_notes": case_info.get("historical_notes", ""),
            "interpretation": classification.interpretation,
        }
        rows.append(row)

        print(f"  Termination: {classification.termination_event}")
        print(f"  Dominant mechanism: {classification.dominant_mechanism} ({classification.confidence:.0%})")
        print(f"  Historical: {case_info.get('historical_classification', 'N/A')}")
        print()

    # Write CSV
    csv_path = output_dir / "mechanism_classification_v2.csv"
    if rows:
        fieldnames = list(rows[0].keys())
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Written to {csv_path}")

    # Write JSON
    json_path = output_dir / "mechanism_classification_v2.json"
    json_path.write_text(json.dumps(rows, indent=2))
    print(f"Written to {json_path}")

    # Print summary table
    print("\n" + "=" * 80)
    print("MECHANISM CLASSIFICATION V2")
    print("=" * 80)
    print(f"{'Case':<20} {'Endpoint':<30} {'Mechanism':<25} {'Conf':<6} {'Historical'}")
    print("-" * 80)
    for row in rows:
        print(
            f"{row['case']:<20} "
            f"{row['termination_event'][:30]:<30} "
            f"{row['dominant_mechanism']:<25} "
            f"{row['confidence']:<6.0%} "
            f"{row['historical_classification']}"
        )


if __name__ == "__main__":
    main()

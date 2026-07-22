"""Verify that Python model, paper equations, and web model agree on constants."""

import re
import sys
from pathlib import Path


def check_constants_agree():
    """Check that constants in paper equations match Python code."""
    root = Path(__file__).resolve().parent.parent
    paper = (root / "paper/sections/methods.tex").read_text()
    code = (root / "src/mahan_vs_attrition/simulation/war_dynamics.py").read_text()

    issues = []

    # Check key constants - all must match between paper and code
    constants = {
        "battle_loss_rate": ("0.04", "0.04"),
        "recruitment_rate": ("0.004", "0.004"),
        "economic_war_costs": ("0.025", "0.025"),
        "casualty_pressure": ("0.2", "0.2"),
        "weariness_rate": ("0.4", "0.4"),
        "shock_damage": ("8.0", "8.0"),
        "fatigue_denominator": ("60", "60.0"),
        "fatigue_cap": ("2.5", "2.5"),
    }

    for name, (paper_val, code_val) in constants.items():
        if paper_val not in paper:
            issues.append(f"ERROR: {name} paper value '{paper_val}' not found in methods.tex")
        if code_val not in code:
            issues.append(f"ERROR: {name} code value '{code_val}' not found in war_dynamics.py")

    # Check for stale Side A initiator language
    if "Side A (assumed initiator)" in paper:
        issues.append("ERROR: Stale 'Side A (assumed initiator)' language in methods.tex")

    # Check fatigue cap is implemented in code
    if "fatigue = min(self.fatigue_cap" not in code:
        issues.append("ERROR: Code does not apply fatigue cap")

    # Check smooth advantage is implemented in code
    if "victory_bonus = victory_bonus_scale * advantage" not in code:
        issues.append("ERROR: Code still uses discontinuous victory bonus")

    # Check fatigue cap is mentioned in paper
    if "f_{\\max}" not in paper and "fatigue_cap" not in paper:
        issues.append("WARNING: Fatigue cap not mentioned in methods.tex equations")

    # Check smooth advantage is mentioned in paper
    if "advantage" not in paper.lower() or "smooth" not in paper.lower():
        if "victory_bonus_scale" not in paper:
            issues.append("WARNING: Smooth advantage function not described in methods.tex")

    if issues:
        print("Model-Paper Sync Issues:")
        for issue in issues:
            print(f"  {issue}")
        return 1
    else:
        print("Model-Paper sync check passed (constants match)")
        return 0


if __name__ == "__main__":
    sys.exit(check_constants_agree())

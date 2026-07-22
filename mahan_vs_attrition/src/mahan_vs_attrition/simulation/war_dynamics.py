"""Time-step war dynamics model simulating war progression through state variables.

Each month, five state variables (military, economic, political will, population
support, industrial capacity) evolve according to update equations. Derived metrics
DSS and SES are computed from the state history, and termination conditions are
checked each step.

v2: Per-side dynamics, configurable settlement, external support, zombie dominance
guard. Canonical source — web engine is a port of this module.
"""

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


class WarSimulator:
    """Simulate war progression through coupled state variables.

    Args:
        config: Dictionary with war parameters.  See *HISTORICAL_PRESETS* for
            examples of required keys.  Supports per-side parameters:
            shock_strength_a/b, attrition_rate_a/b, economic_resilience_a/b,
            political_resilience_a/b, external_support_a/b,
            recruitment_capacity_a/b, dominance_min_winner_military,
            dominance_min_gap, allow_negotiated_settlement,
            earliest_settlement_month, settlement_military_threshold,
            settlement_exhaustion_threshold.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.war_type: str = config.get("war_type", "limited_war")
        self.side_a_name: str = config.get("side_a_name", "Side A")
        self.side_b_name: str = config.get("side_b_name", "Side B")

        # Initial state for side A
        self.initial_military_a: float = config.get("initial_military_a", 70.0)
        self.initial_economic_a: float = config.get("initial_economic_a", 70.0)
        self.initial_political_will_a: float = config.get("initial_political_will_a", 70.0)
        self.initial_population_support_a: float = config.get(
            "initial_population_support_a", 70.0
        )
        self.initial_industrial_a: float = config.get("initial_industrial_a", 70.0)

        # Initial state for side B
        self.initial_military_b: float = config.get("initial_military_b", 60.0)
        self.initial_economic_b: float = config.get("initial_economic_b", 60.0)
        self.initial_political_will_b: float = config.get("initial_political_will_b", 60.0)
        self.initial_population_support_b: float = config.get(
            "initial_population_support_b", 60.0
        )
        self.initial_industrial_b: float = config.get("initial_industrial_b", 60.0)

        # Shared Mahan / Attrition parameters
        self.shock_strength: float = config.get("shock_strength", 50.0)
        self.attrition_rate: float = config.get("attrition_rate", 50.0)
        self.economic_resilience: float = config.get("economic_resilience", 50.0)
        self.political_resilience: float = config.get("political_resilience", 50.0)

        # Per-side parameters (resolve nulls/missing to shared values)
        self.shock_strength_a: float = config.get("shock_strength_a") or self.shock_strength
        self.shock_strength_b: float = config.get("shock_strength_b") or self.shock_strength
        self.attrition_rate_a: float = config.get("attrition_rate_a") or self.attrition_rate
        self.attrition_rate_b: float = config.get("attrition_rate_b") or self.attrition_rate
        self.economic_resilience_a: float = config.get("economic_resilience_a") or self.economic_resilience
        self.economic_resilience_b: float = config.get("economic_resilience_b") or self.economic_resilience
        self.political_resilience_a: float = config.get("political_resilience_a") or self.political_resilience
        self.political_resilience_b: float = config.get("political_resilience_b") or self.political_resilience

        # External support and recruitment
        self.external_support_a: float = config.get("external_support_a", 0.0)
        self.external_support_b: float = config.get("external_support_b", 0.0)
        self.recruitment_capacity_a: float = config.get("recruitment_capacity_a", 1.0)
        self.recruitment_capacity_b: float = config.get("recruitment_capacity_b", 1.0)

        # Settlement configuration
        self.allow_negotiated_settlement: bool = config.get("allow_negotiated_settlement", True)
        self.earliest_settlement_month: int = config.get("earliest_settlement_month", 0)
        self.settlement_military_threshold: float = config.get("settlement_military_threshold", 50.0)
        self.settlement_exhaustion_threshold: float = config.get("settlement_exhaustion_threshold", 80.0)

        # Zombie dominance guard
        self.dominance_min_winner_military: float = config.get("dominance_min_winner_military", 25.0)
        self.dominance_min_gap: float = config.get("dominance_min_gap", 20.0)

        # Fatigue cap
        self.fatigue_cap: float = float(config.get("fatigue_cap", 2.5))

    # ------------------------------------------------------------------
    # Simulation entry point
    # ------------------------------------------------------------------

    def simulate(
        self, max_months: int = 120, seed: int = 42
    ) -> dict[str, Any]:
        """Run simulation and return time-series results.

        Args:
            max_months: Maximum number of monthly timesteps.
            seed: Random seed for reproducibility.

        Returns:
            Dictionary with monthly state histories, DSS, SES, outcome, and
            termination month.
        """
        rng = np.random.default_rng(seed)

        months: list[int] = []
        military_a: list[float] = []
        military_b: list[float] = []
        economic_a: list[float] = []
        economic_b: list[float] = []
        political_will_a: list[float] = []
        political_will_b: list[float] = []
        population_support_a: list[float] = []
        population_support_b: list[float] = []
        industrial_a: list[float] = []
        industrial_b: list[float] = []
        dss_a: list[float] = []
        dss_b: list[float] = []
        ses_a: list[float] = []
        ses_b: list[float] = []

        # Current state
        state: dict[str, float] = {
            "military_a": self.initial_military_a,
            "military_b": self.initial_military_b,
            "economic_a": self.initial_economic_a,
            "economic_b": self.initial_economic_b,
            "political_will_a": self.initial_political_will_a,
            "political_will_b": self.initial_political_will_b,
            "population_support_a": self.initial_population_support_a,
            "population_support_b": self.initial_population_support_b,
            "industrial_a": self.initial_industrial_a,
            "industrial_b": self.initial_industrial_b,
        }

        # Keep a full history for DSS/SES computation
        state_history: list[dict[str, float]] = [dict(state)]

        outcome = "inconclusive"
        termination_month = max_months

        for month in range(1, max_months + 1):
            # --- Apply dynamics ---
            self._apply_attrition(state, month)
            self._apply_shock(state, month)

            # Noise (small random perturbation)
            for key in state:
                state[key] += rng.normal(0, 0.5)
                state[key] = _clamp(state[key])

            # --- Derived metrics ---
            dss_a_val = self._compute_dss(state_history, state, side="a")
            dss_b_val = self._compute_dss(state_history, state, side="b")
            ses_a_val = self._compute_ses(state_history, state, side="a", month=month)
            ses_b_val = self._compute_ses(state_history, state, side="b", month=month)

            # --- Record ---
            months.append(month)
            military_a.append(state["military_a"])
            military_b.append(state["military_b"])
            economic_a.append(state["economic_a"])
            economic_b.append(state["economic_b"])
            political_will_a.append(state["political_will_a"])
            political_will_b.append(state["political_will_b"])
            population_support_a.append(state["population_support_a"])
            population_support_b.append(state["population_support_b"])
            industrial_a.append(state["industrial_a"])
            industrial_b.append(state["industrial_b"])
            dss_a.append(dss_a_val)
            dss_b.append(dss_b_val)
            ses_a.append(ses_a_val)
            ses_b.append(ses_b_val)

            state_history.append(dict(state))

            # --- Check termination ---
            term = self._check_termination(state, ses_a_val, ses_b_val, month)
            if term is not None:
                outcome = term
                termination_month = month
                break

        return {
            "months": months,
            "military_a": military_a,
            "military_b": military_b,
            "economic_a": economic_a,
            "economic_b": economic_b,
            "political_will_a": political_will_a,
            "political_will_b": political_will_b,
            "population_support_a": population_support_a,
            "population_support_b": population_support_b,
            "industrial_a": industrial_a,
            "industrial_b": industrial_b,
            "dss_a": dss_a,
            "dss_b": dss_b,
            "ses_a": ses_a,
            "ses_b": ses_b,
            "outcome": outcome,
            "termination_month": termination_month,
        }

    # ------------------------------------------------------------------
    # Dynamics
    # ------------------------------------------------------------------

    def _apply_shock(
        self, state: dict[str, float], month: int
    ) -> None:
        """Apply decisive shock event (Mahan mechanism).

        Symmetric: each side inflicts shock proportional to own shock_strength.
        Shock frequency depends on war type.
        """
        if self.war_type == "total_war":
            shock_interval = 6
        elif self.war_type in ("coalition", "coalition_war"):
            shock_interval = 7
        elif self.war_type == "limited_war":
            shock_interval = 3
        else:
            shock_interval = 5

        if month % shock_interval != 0:
            return

        mag_a = self.shock_strength_a / 100.0
        mag_b = self.shock_strength_b / 100.0

        # Side A inflicts shock on B
        damage_b = mag_a * 8.0
        state["military_b"] -= damage_b
        state["industrial_b"] -= damage_b * 0.3
        state["political_will_b"] -= damage_b * 0.25

        # Side B inflicts shock on A
        damage_a = mag_b * 8.0
        state["military_a"] -= damage_a
        state["industrial_a"] -= damage_a * 0.25
        state["political_will_a"] -= damage_a * 0.2

        for key in (
            "military_a", "military_b",
            "industrial_a", "industrial_b",
            "political_will_a", "political_will_b",
        ):
            state[key] = _clamp(state[key])

    def _apply_attrition(
        self, state: dict[str, float], month: int
    ) -> None:
        """Apply gradual attrition (Exhaustion mechanism).

        Per-side attrition_rate and resilience. External support and
        recruitment capacity affect military replenishment.
        """
        fatigue = min(self.fatigue_cap, 1.0 + month / 60.0)

        for suffix in ("a", "b"):
            mil_key = f"military_{suffix}"
            econ_key = f"economic_{suffix}"
            pop_key = f"population_support_{suffix}"
            pol_key = f"political_will_{suffix}"
            ind_key = f"industrial_{suffix}"

            attrition_rate = self.attrition_rate_a if suffix == "a" else self.attrition_rate_b
            base = attrition_rate / 100.0

            resilience = self.economic_resilience_a if suffix == "a" else self.economic_resilience_b
            resist = 1.0 - resilience / 200.0

            external_support = self.external_support_a if suffix == "a" else self.external_support_b
            recruitment_capacity = self.recruitment_capacity_a if suffix == "a" else self.recruitment_capacity_b

            # --- Military ---
            battle_losses = state[mil_key] * base * 0.04 * resist * fatigue
            recruitment = (
                min(1.5 * recruitment_capacity, state[ind_key] * 0.004 * recruitment_capacity)
                + external_support * 0.01
            )
            state[mil_key] = state[mil_key] - battle_losses + recruitment

            # --- Economic ---
            war_costs = state[econ_key] * base * 0.025 * fatigue
            blockade = state[econ_key] * base * 0.01 * resist
            industrial_output = state[ind_key] * 0.006
            econ_support = external_support * 0.005
            state[econ_key] = state[econ_key] - war_costs - blockade + industrial_output + econ_support

            # --- Political will ---
            casualty_pressure = battle_losses * 0.2
            pol_resilience = self.political_resilience_a if suffix == "a" else self.political_resilience_b
            weariness = base * 0.4 * fatigue * (1.0 - pol_resilience / 200.0)
            opponent_key = f"military_{'b' if suffix == 'a' else 'a'}"
            own_mil = state[mil_key]
            opp_mil = state.get(opponent_key, 50.0)
            advantage = max(0.0, (own_mil - opp_mil) / max(own_mil + opp_mil, 1.0))
            victory_bonus_scale = 0.15 if self.war_type == "limited_war" else 0.8
            victory_bonus = victory_bonus_scale * advantage
            political_support = min(5.0, external_support * 0.003)
            state[pol_key] = state[pol_key] - casualty_pressure - weariness + victory_bonus + political_support

            # --- Population support ---
            econ_hardship = max(0, (50 - state[econ_key])) * base * 0.03 * fatigue
            state[pop_key] = state[pop_key] - econ_hardship - casualty_pressure * 0.15

            # --- Industrial ---
            bombing = state[ind_key] * base * 0.015 * resist * fatigue
            recon = state[econ_key] * 0.004
            state[ind_key] = state[ind_key] - bombing + recon

            for key in (mil_key, econ_key, pol_key, pop_key, ind_key):
                state[key] = _clamp(state[key])

    # ------------------------------------------------------------------
    # Derived metrics
    # ------------------------------------------------------------------

    def _compute_dss(
        self,
        state_history: list[dict[str, float]],
        current_state: dict[str, float],
        side: str,
    ) -> float:
        """Compute Decisive Shock Score from state history."""
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

        dss = min(100.0, military_shock * 50 + capital_bonus * 30 + surrender_bonus * 20)
        return round(dss, 2)

    def _compute_ses(
        self,
        state_history: list[dict[str, float]],
        current_state: dict[str, float],
        side: str,
        month: int,
    ) -> float:
        """Compute Strategic Exhaustion Score from state history.

        Political weight is dynamic: higher political_resilience reduces
        the contribution of political exhaustion to SES.
        """
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

        # Dynamic political weight: higher resilience → less exhaustion from political losses
        pol_res = self.political_resilience_a if side == "a" else self.political_resilience_b
        pol_weight = 0.2 * (1.0 - pol_res / 200.0)

        ses = (
            military_exhaustion * 0.3
            + economic_exhaustion * 0.3
            + political_exhaustion * pol_weight
            + (1.0 - pol_weight) * 0.1
            + duration_factor * 0.2
        ) * 100.0
        return round(_clamp(ses), 2)

    # ------------------------------------------------------------------
    # Termination
    # ------------------------------------------------------------------

    def _check_termination(
        self,
        state: dict[str, float],
        ses_a_val: float,
        ses_b_val: float,
        month: int,
    ) -> str | None:
        """Check war termination conditions. Returns outcome string or None."""
        mil_a = state["military_a"]
        mil_b = state["military_b"]
        pol_a = state["political_will_a"]
        pol_b = state["political_will_b"]
        pop_a = state["population_support_a"]
        pop_b = state["population_support_b"]
        econ_a = state["economic_a"]
        econ_b = state["economic_b"]

        # Total collapse: political will AND population support collapse
        if pol_a < 8 and pop_a < 12:
            return "collapse_a"
        if pol_b < 8 and pop_b < 12:
            return "collapse_b"

        # Decisive dominance: absolute viability requirements prevent zombie wins
        if (mil_a >= self.dominance_min_winner_military
                and mil_a - mil_b >= self.dominance_min_gap
                and mil_a > mil_b * 2 and mil_b < 25 and pol_b < 25):
            return "dominance_a"
        if (mil_b >= self.dominance_min_winner_military
                and mil_b - mil_a >= self.dominance_min_gap
                and mil_b > mil_a * 2 and mil_a < 25 and pol_a < 25):
            return "dominance_b"

        # Attritional exhaustion (SES thresholds)
        if ses_a_val > 85 and ses_b_val > 85:
            return "mutual_exhaustion"
        if ses_a_val > 85 and pol_a < 20:
            return "exhaustion_a"
        if ses_b_val > 85 and pol_b < 20:
            return "exhaustion_b"

        # Combined economic + political collapse
        if econ_a < 10 and pol_a < 15:
            return "exhaustion_a"
        if econ_b < 10 and pol_b < 15:
            return "exhaustion_b"

        # Negotiated settlement: configurable thresholds
        if (self.allow_negotiated_settlement
                and month >= self.earliest_settlement_month):
            if (mil_a < self.settlement_military_threshold
                    and mil_b < self.settlement_military_threshold
                    and ses_a_val > self.settlement_exhaustion_threshold
                    and ses_b_val > self.settlement_exhaustion_threshold):
                return "negotiated_settlement"

        # Coalition war: draw if both sides exhausted
        if (self.war_type in ("coalition", "coalition_war")
                and ses_a_val > 60 and ses_b_val > 60
                and mil_a < 35 and mil_b < 35):
            return "negotiated_settlement"

        # Limited war withdrawal: political will collapse triggers withdrawal
        if (self.war_type == "limited_war"
                and pol_a < 30 and ses_a_val > 75 and month > 40):
            return "withdrawal_a"
        if (self.war_type == "limited_war"
                and pol_b < 30 and ses_b_val > 75 and month > 40):
            return "withdrawal_b"

        # Combined political-population collapse (secondary)
        if pol_a < 10 and pop_a < 15:
            return "collapse_a"
        if pol_b < 10 and pop_b < 15:
            return "collapse_b"

        return None


# ------------------------------------------------------------------
# Historical presets (canonical — web presets.js is generated from here)
# ------------------------------------------------------------------

HISTORICAL_PRESETS: dict[str, dict[str, Any]] = {
    "gulf_war_1991": {
        "war_type": "limited_war",
        "side_a_name": "Coalition",
        "side_b_name": "Iraq",
        "initial_military_a": 95,
        "initial_military_b": 55,
        "initial_economic_a": 95,
        "initial_economic_b": 40,
        "initial_political_will_a": 85,
        "initial_political_will_b": 45,
        "initial_population_support_a": 75,
        "initial_population_support_b": 50,
        "initial_industrial_a": 95,
        "initial_industrial_b": 35,
        "shock_strength": 90,
        "attrition_rate": 30,
        "economic_resilience": 80,
        "political_resilience": 70,
        "shock_strength_a": 95,
        "shock_strength_b": 10,
        "attrition_rate_a": 12,
        "attrition_rate_b": 80,
        "economic_resilience_a": 90,
        "economic_resilience_b": 8,
        "political_resilience_a": 85,
        "political_resilience_b": 5,
        "dominance_min_winner_military": 15,
        "dominance_min_gap": 15,
        "allow_negotiated_settlement": False,
    },
    "vietnam_war": {
        "war_type": "limited_war",
        "side_a_name": "USA/South Vietnam",
        "side_b_name": "North Vietnam/Viet Cong",
        "initial_military_a": 85,
        "initial_military_b": 50,
        "initial_economic_a": 95,
        "initial_economic_b": 30,
        "initial_political_will_a": 70,
        "initial_political_will_b": 95,
        "initial_population_support_a": 60,
        "initial_population_support_b": 85,
        "initial_industrial_a": 95,
        "initial_industrial_b": 25,
        "shock_strength": 25,
        "attrition_rate": 75,
        "economic_resilience": 70,
        "political_resilience": 40,
        "shock_strength_a": 30,
        "shock_strength_b": 15,
        "attrition_rate_a": 55,
        "attrition_rate_b": 60,
        "economic_resilience_a": 30,
        "economic_resilience_b": 90,
        "political_resilience_a": 45,
        "political_resilience_b": 95,
        "allow_negotiated_settlement": True,
        "earliest_settlement_month": 60,
        "settlement_military_threshold": 20,
        "settlement_exhaustion_threshold": 92,
        "external_support_a": 35,
        "external_support_b": 50,
        "recruitment_capacity_a": 1.3,
        "recruitment_capacity_b": 2.0,
    },
    "wwi": {
        "war_type": "total_war",
        "side_a_name": "Allies",
        "side_b_name": "Central Powers",
        "initial_military_a": 80,
        "initial_military_b": 75,
        "initial_economic_a": 85,
        "initial_economic_b": 70,
        "initial_political_will_a": 80,
        "initial_political_will_b": 75,
        "initial_population_support_a": 75,
        "initial_population_support_b": 70,
        "initial_industrial_a": 85,
        "initial_industrial_b": 75,
        "shock_strength": 40,
        "attrition_rate": 80,
        "economic_resilience": 60,
        "political_resilience": 50,
        "shock_strength_a": 40,
        "shock_strength_b": 35,
        "attrition_rate_a": 75,
        "attrition_rate_b": 95,
        "economic_resilience_a": 65,
        "economic_resilience_b": 28,
        "political_resilience_a": 60,
        "political_resilience_b": 20,
        "allow_negotiated_settlement": True,
        "earliest_settlement_month": 36,
        "settlement_military_threshold": 25,
        "settlement_exhaustion_threshold": 90,
    },
    "franco_prussian": {
        "war_type": "limited_war",
        "side_a_name": "Prussia/Germany",
        "side_b_name": "France",
        "initial_military_a": 90,
        "initial_military_b": 50,
        "initial_economic_a": 75,
        "initial_economic_b": 80,
        "initial_political_will_a": 90,
        "initial_political_will_b": 40,
        "initial_population_support_a": 85,
        "initial_population_support_b": 35,
        "initial_industrial_a": 80,
        "initial_industrial_b": 75,
        "shock_strength": 90,
        "attrition_rate": 35,
        "economic_resilience": 70,
        "political_resilience": 60,
        "shock_strength_a": 95,
        "shock_strength_b": 15,
        "attrition_rate_a": 18,
        "attrition_rate_b": 90,
        "economic_resilience_a": 80,
        "economic_resilience_b": 10,
        "political_resilience_a": 90,
        "political_resilience_b": 5,
        "dominance_min_winner_military": 15,
        "dominance_min_gap": 15,
        "allow_negotiated_settlement": False,
    },
    "korean_war": {
        "war_type": "coalition",
        "side_a_name": "UN/South Korea",
        "side_b_name": "North Korea/China",
        "initial_military_a": 80,
        "initial_military_b": 65,
        "initial_economic_a": 90,
        "initial_economic_b": 40,
        "initial_political_will_a": 70,
        "initial_political_will_b": 85,
        "initial_population_support_a": 65,
        "initial_population_support_b": 80,
        "initial_industrial_a": 90,
        "initial_industrial_b": 35,
        "shock_strength": 50,
        "attrition_rate": 60,
        "economic_resilience": 75,
        "political_resilience": 55,
        "shock_strength_a": 45,
        "shock_strength_b": 50,
        "attrition_rate_a": 70,
        "attrition_rate_b": 65,
        "economic_resilience_a": 60,
        "economic_resilience_b": 70,
        "political_resilience_a": 45,
        "political_resilience_b": 70,
        "allow_negotiated_settlement": True,
        "earliest_settlement_month": 24,
        "settlement_military_threshold": 40,
        "settlement_exhaustion_threshold": 70,
        "external_support_a": 30,
        "external_support_b": 35,
        "recruitment_capacity_a": 1.0,
        "recruitment_capacity_b": 1.3,
    },
    "iran_iraq": {
        "war_type": "limited_war",
        "side_a_name": "Iran",
        "side_b_name": "Iraq",
        "initial_military_a": 60,
        "initial_military_b": 65,
        "initial_economic_a": 50,
        "initial_economic_b": 55,
        "initial_political_will_a": 90,
        "initial_political_will_b": 75,
        "initial_population_support_a": 85,
        "initial_population_support_b": 70,
        "initial_industrial_a": 45,
        "initial_industrial_b": 50,
        "shock_strength": 30,
        "attrition_rate": 85,
        "economic_resilience": 40,
        "political_resilience": 50,
        "shock_strength_a": 25,
        "shock_strength_b": 30,
        "attrition_rate_a": 60,
        "attrition_rate_b": 65,
        "economic_resilience_a": 50,
        "economic_resilience_b": 48,
        "political_resilience_a": 90,
        "political_resilience_b": 70,
        "allow_negotiated_settlement": True,
        "earliest_settlement_month": 72,
        "settlement_military_threshold": 20,
        "settlement_exhaustion_threshold": 92,
        "external_support_a": 35,
        "external_support_b": 40,
        "recruitment_capacity_a": 1.2,
        "recruitment_capacity_b": 1.0,
    },
    "wwii": {
        "war_type": "total_war",
        "side_a_name": "Allies",
        "side_b_name": "Axis",
        "initial_military_a": 85,
        "initial_military_b": 80,
        "initial_economic_a": 95,
        "initial_economic_b": 60,
        "initial_political_will_a": 90,
        "initial_political_will_b": 85,
        "initial_population_support_a": 80,
        "initial_population_support_b": 75,
        "initial_industrial_a": 95,
        "initial_industrial_b": 70,
        "shock_strength": 60,
        "attrition_rate": 80,
        "economic_resilience": 50,
        "political_resilience": 40,
        "shock_strength_a": 55,
        "shock_strength_b": 60,
        "attrition_rate_a": 70,
        "attrition_rate_b": 95,
        "economic_resilience_a": 60,
        "economic_resilience_b": 15,
        "political_resilience_a": 75,
        "political_resilience_b": 18,
        "allow_negotiated_settlement": True,
        "earliest_settlement_month": 48,
        "settlement_military_threshold": 20,
        "settlement_exhaustion_threshold": 92,
    },
}

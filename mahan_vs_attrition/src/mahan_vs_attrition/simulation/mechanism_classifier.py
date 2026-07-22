"""Mechanism classifier that separates termination events from strategic causes.

The core insight: a war may END because of a political collapse, military
destruction, or negotiated settlement. But the REASON it became unwinnable
may be exhaustion, attrition, or decisive shock. These are different questions.

This module computes independent scores for each mechanism and classifies
based on the dominant strategic dynamic, not the termination trigger.
"""

from dataclasses import dataclass, field


@dataclass
class MechanismScores:
    """Independent scores for each strategic mechanism."""

    decisive_shock: float = 0.0
    strategic_exhaustion: float = 0.0
    political_exhaustion: float = 0.0
    economic_exhaustion: float = 0.0
    military_exhaustion: float = 0.0
    duration_factor: float = 0.0


@dataclass
class MechanismClassification:
    """Full classification of a war's strategic dynamics."""

    termination_event: str
    dominant_mechanism: str
    secondary_mechanism: str | None
    confidence: float
    scores: MechanismScores
    interpretation: str
    historical_reference: str

    def to_dict(self) -> dict:
        return {
            "termination_event": self.termination_event,
            "dominant_mechanism": self.dominant_mechanism,
            "secondary_mechanism": self.secondary_mechanism,
            "confidence": round(self.confidence, 2),
            "decisive_shock_score": round(self.scores.decisive_shock, 1),
            "strategic_exhaustion_score": round(self.scores.strategic_exhaustion, 1),
            "political_exhaustion_score": round(self.scores.political_exhaustion, 1),
            "economic_exhaustion_score": round(self.scores.economic_exhaustion, 1),
            "military_exhaustion_score": round(self.scores.military_exhaustion, 1),
            "interpretation": self.interpretation,
            "historical_reference": self.historical_reference,
        }


def classify_mechanism(
    result: dict,
    preset_config: dict | None = None,
) -> MechanismClassification:
    """Classify the dominant strategic mechanism from simulation results.

    This function separates the termination EVENT (how the war ended) from
    the dominant MECHANISM (why the war became unwinnable).

    Args:
        result: Simulation result dict with state histories, DSS, SES, outcome.
        preset_config: Original preset config (used for initial conditions).

    Returns:
        MechanismClassification with independent scores and interpretation.
    """
    outcome = result.get("outcome", "inconclusive")
    termination_month = result.get("termination_month", 120)

    # Extract state histories
    mil_a = result.get("military_a", [])
    mil_b = result.get("military_b", [])
    econ_a = result.get("economic_a", [])
    econ_b = result.get("economic_b", [])
    pol_a = result.get("political_will_a", [])
    pol_b = result.get("political_will_b", [])
    dss_a = result.get("dss_a", [])
    dss_b = result.get("dss_b", [])
    ses_a = result.get("ses_a", [])
    ses_b = result.get("ses_b", [])

    # Get initial values from config or first state
    if preset_config:
        init_mil_a = preset_config.get("initial_military_a", mil_a[0] if mil_a else 70)
        init_mil_b = preset_config.get("initial_military_b", mil_b[0] if mil_b else 70)
        init_econ_a = preset_config.get("initial_economic_a", econ_a[0] if econ_a else 70)
        init_econ_b = preset_config.get("initial_economic_b", econ_b[0] if econ_b else 70)
        init_pol_a = preset_config.get("initial_political_will_a", pol_a[0] if pol_a else 70)
        init_pol_b = preset_config.get("initial_political_will_b", pol_b[0] if pol_b else 70)
        shock_strength = preset_config.get("shock_strength", 50)
        attrition_rate = preset_config.get("attrition_rate", 50)
    else:
        init_mil_a = mil_a[0] if mil_a else 70
        init_mil_b = mil_b[0] if mil_b else 70
        init_econ_a = econ_a[0] if econ_a else 70
        init_econ_b = econ_b[0] if econ_b else 70
        init_pol_a = pol_a[0] if pol_a else 70
        init_pol_b = pol_b[0] if pol_b else 70
        shock_strength = 50
        attrition_rate = 50

    # --- Compute independent mechanism scores ---

    # 1. Decisive shock score: based on shock parameter and DSS trajectory
    #    High shock_strength + high DSS values = decisive dynamics
    if dss_a:
        peak_dss = max(dss_a)
        avg_dss = sum(dss_a) / len(dss_a)
    else:
        peak_dss = 0
        avg_dss = 0

    decisive_score = (
        shock_strength * 0.4
        + peak_dss * 0.4
        + avg_dss * 0.2
    )

    # 2. Strategic exhaustion score: based on attrition parameter and SES trajectory
    #    High attrition_rate + high SES values = exhaustion dynamics
    if ses_a:
        peak_ses = max(ses_a)
        avg_ses = sum(ses_a) / len(ses_a)
    else:
        peak_ses = 0
        avg_ses = 0

    strategic_exhaustion_score = (
        attrition_rate * 0.3
        + peak_ses * 0.4
        + avg_ses * 0.3
    )

    # 3. Military exhaustion: decline in military capacity
    if mil_a and init_mil_a > 0:
        mil_a_min = min(mil_a)
        mil_decline_a = (init_mil_a - mil_a_min) / init_mil_a * 100
    else:
        mil_decline_a = 0

    if mil_b and init_mil_b > 0:
        mil_b_min = min(mil_b)
        mil_decline_b = (init_mil_b - mil_b_min) / init_mil_b * 100
    else:
        mil_decline_b = 0

    military_exhaustion = max(mil_decline_a, mil_decline_b)

    # 4. Economic exhaustion: decline in economic capacity
    if econ_a and init_econ_a > 0:
        econ_a_min = min(econ_a)
        econ_decline_a = (init_econ_a - econ_a_min) / init_econ_a * 100
    else:
        econ_decline_a = 0

    if econ_b and init_econ_b > 0:
        econ_b_min = min(econ_b)
        econ_decline_b = (init_econ_b - econ_b_min) / init_econ_b * 100
    else:
        econ_decline_b = 0

    economic_exhaustion = max(econ_decline_a, econ_decline_b)

    # 5. Political exhaustion: decline in political will
    if pol_a and init_pol_a > 0:
        pol_a_min = min(pol_a)
        pol_decline_a = (init_pol_a - pol_a_min) / init_pol_a * 100
    else:
        pol_decline_a = 0

    if pol_b and init_pol_b > 0:
        pol_b_min = min(pol_b)
        pol_decline_b = (init_pol_b - pol_b_min) / init_pol_b * 100
    else:
        pol_decline_b = 0

    political_exhaustion = max(pol_decline_a, pol_decline_b)

    # Duration factor: longer wars tend toward exhaustion
    duration_factor = min(100, termination_month / 120 * 100)

    # --- Build scores ---
    scores = MechanismScores(
        decisive_shock=decisive_score,
        strategic_exhaustion=strategic_exhaustion_score,
        political_exhaustion=political_exhaustion,
        economic_exhaustion=economic_exhaustion,
        military_exhaustion=military_exhaustion,
        duration_factor=duration_factor,
    )

    # --- Classify dominant mechanism ---
    # Use composite exhaustion score (weighted average of sub-scores)
    composite_exhaustion = (
        strategic_exhaustion_score * 0.35
        + military_exhaustion * 0.25
        + economic_exhaustion * 0.2
        + political_exhaustion * 0.1
        + duration_factor * 0.1
    )

    # Determine dominant and secondary mechanisms
    mechanisms = {
        "decisive_shock": decisive_score,
        "strategic_exhaustion": composite_exhaustion,
    }

    sorted_mechanisms = sorted(mechanisms.items(), key=lambda x: x[1], reverse=True)
    dominant = sorted_mechanisms[0]
    secondary = sorted_mechanisms[1]

    # Confidence: based on gap between top two scores
    total = dominant[1] + secondary[1]
    if total > 0:
        confidence = dominant[1] / total
    else:
        confidence = 0.5

    # Map to human-readable labels
    mechanism_labels = {
        "decisive_shock": "decisive shock",
        "strategic_exhaustion": "strategic exhaustion",
    }

    dominant_label = mechanism_labels[dominant[0]]
    secondary_label = mechanism_labels[secondary[0]]

    # Termination event labels
    event_labels = {
        "decisive_victory_a": "political/military collapse of side B",
        "decisive_victory_b": "political/military collapse of side A",
        "dominance_a": "decisive dominance of side A",
        "dominance_b": "decisive dominance of side B",
        "collapse_a": "political/military collapse of side A",
        "collapse_b": "political/military collapse of side B",
        "exhaustion_a": "exhaustion of side A",
        "exhaustion_b": "exhaustion of side B",
        "mutual_exhaustion": "mutual exhaustion",
        "negotiated_settlement": "negotiated settlement",
        "withdrawal_a": "strategic withdrawal of side A",
        "withdrawal_b": "strategic withdrawal of side B",
        "inconclusive": "inconclusive",
    }
    termination_event = event_labels.get(outcome, outcome)

    # Generate interpretation
    if dominant[0] == "strategic_exhaustion":
        interpretation = (
            f"Strategic exhaustion dominant ({composite_exhaustion:.0f}/100). "
            f"The war became unwinnable through cumulative attrition of military, "
            f"economic, and political capacity. Termination was triggered by "
            f"{termination_event}, but the underlying cause was exhaustion."
        )
    else:
        interpretation = (
            f"Decisive shock dominant ({decisive_score:.0f}/100). "
            f"A decisive operational event or campaign was the primary mechanism "
            f"of strategic change. Termination was triggered by "
            f"{termination_event}."
        )

    return MechanismClassification(
        termination_event=termination_event,
        dominant_mechanism=dominant_label,
        secondary_mechanism=secondary_label if confidence < 0.7 else None,
        confidence=confidence,
        scores=scores,
        interpretation=interpretation,
        historical_reference="",
    )


# ------------------------------------------------------------------
# Historical case study presets (v2 - with WWII and revised parameters)
# ------------------------------------------------------------------

HISTORICAL_CASES_V2: dict[str, dict] = {
    "gulf_war_1991": {
        "preset_name": "gulf_war_1991",
        "historical_classification": "decisive shock",
        "historical_notes": (
            "Coalition air superiority + 100-hour ground campaign. "
            "Iraqi military destroyed as fighting force. Clear decisive dynamics."
        ),
    },
    "vietnam_war": {
        "preset_name": "vietnam_war",
        "historical_classification": "strategic exhaustion",
        "historical_notes": (
            "US military never defeated in field, but political will eroded. "
            "North Vietnam sustained losses over 20 years. "
            "Terminal event: fall of Saigon. Underlying cause: exhaustion."
        ),
    },
    "wwi": {
        "preset_name": "wwi",
        "historical_classification": "strategic exhaustion",
        "historical_notes": (
            "Western Front = industrial attrition system. "
            "Economic blockade degraded German capacity. "
            "Final collapse was political and systemic, not battlefield defeat. "
            "Hundred Days was operational breakthrough atop exhaustion substrate."
        ),
    },
    "wwii": {
        "preset_name": "wwii",
        "historical_classification": "strategic exhaustion with decisive accelerators",
        "historical_notes": (
            "Axis defeat driven by industrial mismatch, manpower depletion, "
            "fuel collapse, multi-front pressure. Decisive events (Barbarossa "
            "failure, Midway, Normandy) accelerated but did not cause defeat. "
            "Germany and Japan could not replace losses."
        ),
    },
    "franco_prussian": {
        "preset_name": "franco_prussian",
        "historical_classification": "decisive shock",
        "historical_notes": (
            "Battle of Sedan destroyed French army. "
            "But France was already degraded: manpower depletion, economic strain. "
            "Shock completed an exhaustion process. Classic iceberg."
        ),
    },
    "korean_war": {
        "preset_name": "korean_war",
        "historical_classification": "mixed / unresolved",
        "historical_notes": (
            "Rapid territorial shifts, Chinese intervention, stalemate. "
            "Neither decisive nor purely attritional. "
            "Armistice without peace treaty = unresolved."
        ),
    },
    "iran_iraq": {
        "preset_name": "iran_iraq",
        "historical_classification": "strategic exhaustion",
        "historical_notes": (
            "Eight years of attritional warfare. "
            "Neither side achieved decisive breakthrough. "
            "Exhaustion led to ceasefire."
        ),
    },
}

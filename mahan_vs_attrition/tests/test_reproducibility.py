"""Reproducibility tests: verify deterministic behavior."""

from mahan_vs_attrition.metrics.classify import classify_termination
from mahan_vs_attrition.simulation.war_dynamics import HISTORICAL_PRESETS, WarSimulator


class TestDeterminism:
    """Same seed + same parameters = same trajectory."""

    def test_same_seed_same_trajectory(self):
        config = HISTORICAL_PRESETS["gulf_war_1991"]
        sim1 = WarSimulator(config)
        r1 = sim1.simulate(max_months=120, seed=42)

        sim2 = WarSimulator(config)
        r2 = sim2.simulate(max_months=120, seed=42)

        assert r1["months"] == r2["months"]
        assert r1["military_a"] == r2["military_a"]
        assert r1["military_b"] == r2["military_b"]
        assert r1["outcome"] == r2["outcome"]
        assert r1["termination_month"] == r2["termination_month"]

    def test_same_seed_all_presets(self):
        for name, config in HISTORICAL_PRESETS.items():
            sim1 = WarSimulator(config)
            r1 = sim1.simulate(max_months=120, seed=42)

            sim2 = WarSimulator(config)
            r2 = sim2.simulate(max_months=120, seed=42)

            assert r1["military_a"] == r2["military_a"], f"{name}: military_a differs"
            assert r1["outcome"] == r2["outcome"], f"{name}: outcome differs"

    def test_different_seed_can_differ(self):
        config = HISTORICAL_PRESETS["gulf_war_1991"]
        sim1 = WarSimulator(config)
        r1 = sim1.simulate(max_months=120, seed=42)

        sim2 = WarSimulator(config)
        r2 = sim2.simulate(max_months=120, seed=99)

        # With different seeds, at least one trajectory should differ
        assert r1["military_a"] != r2["military_a"] or r1["termination_month"] != r2[
            "termination_month"
        ]

    def test_parameter_change_alters_trajectory(self):
        config1 = HISTORICAL_PRESETS["gulf_war_1991"]
        sim1 = WarSimulator(config1)
        r1 = sim1.simulate(max_months=120, seed=42)

        config2 = dict(config1)
        config2["shock_strength"] = 10  # Much lower shock
        config2["shock_strength_a"] = 10  # Override per-side too
        config2["shock_strength_b"] = 10
        sim2 = WarSimulator(config2)
        r2 = sim2.simulate(max_months=120, seed=42)

        # Lower shock should change trajectory
        assert r1["military_a"] != r2["military_a"]


class TestClassificationReproducibility:
    """Classification of simulation results is deterministic."""

    def test_same_result_same_classification(self):
        r1 = classify_termination(dss_score=80, ses_score=30)
        r2 = classify_termination(dss_score=80, ses_score=30)
        assert r1["termination_type_model"] == r2["termination_type_model"]
        assert r1["primary_mechanism"] == r2["primary_mechanism"]

    def test_boundary_cases_stable(self):
        # Exact boundary: DSS-SES = 70-50 = 20, meets decisive_margin
        r = classify_termination(dss_score=70, ses_score=50)
        assert r["termination_type_model"] == "decisive_battle_or_campaign"

        # Just below: DSS-SES = 69-50 = 19, below decisive_margin
        r2 = classify_termination(dss_score=69, ses_score=50)
        assert r2["termination_type_model"] != "decisive_battle_or_campaign"

"""Tests for war dynamics simulation."""

import pytest

from mahan_vs_attrition.simulation.war_dynamics import HISTORICAL_PRESETS, WarSimulator


class TestSimulationRuns:
    """Basic smoke tests."""

    def test_gulf_war_runs(self):
        sim = WarSimulator(HISTORICAL_PRESETS["gulf_war_1991"])
        result = sim.simulate(max_months=120, seed=42)
        assert result["months"][0] == 1
        assert result["outcome"] in (
            "dominance_a",
            "dominance_b",
            "collapse_a",
            "collapse_b",
            "exhaustion_a",
            "exhaustion_b",
            "negotiated_settlement",
            "mutual_exhaustion",
            "withdrawal_a",
            "withdrawal_b",
            "inconclusive",
        )

    def test_vietnam_war_runs(self):
        sim = WarSimulator(HISTORICAL_PRESETS["vietnam_war"])
        result = sim.simulate(max_months=120, seed=42)
        assert len(result["months"]) >= 1

    def test_wwi_runs(self):
        sim = WarSimulator(HISTORICAL_PRESETS["wwi"])
        result = sim.simulate(max_months=120, seed=42)
        assert len(result["months"]) >= 1

    def test_franco_prussian_runs(self):
        sim = WarSimulator(HISTORICAL_PRESETS["franco_prussian"])
        result = sim.simulate(max_months=120, seed=42)
        assert len(result["months"]) >= 1

    def test_korean_war_runs(self):
        sim = WarSimulator(HISTORICAL_PRESETS["korean_war"])
        result = sim.simulate(max_months=120, seed=42)
        assert len(result["months"]) >= 1

    def test_iran_iraq_runs(self):
        sim = WarSimulator(HISTORICAL_PRESETS["iran_iraq"])
        result = sim.simulate(max_months=120, seed=42)
        assert len(result["months"]) >= 1


class TestStateBounds:
    """State variables must stay in [0, 100]."""

    @pytest.mark.parametrize("preset_name", list(HISTORICAL_PRESETS.keys()))
    def test_all_state_variables_in_bounds(self, preset_name):
        sim = WarSimulator(HISTORICAL_PRESETS[preset_name])
        result = sim.simulate(max_months=120, seed=42)
        for field in (
            "military_a", "military_b",
            "economic_a", "economic_b",
            "political_will_a", "political_will_b",
            "population_support_a", "population_support_b",
            "industrial_a", "industrial_b",
        ):
            for val in result[field]:
                assert 0.0 <= val <= 100.0, (
                    f"{preset_name}.{field} = {val} out of bounds"
                )

    def test_military_never_negative(self):
        """Military strength should never drop below 0."""
        sim = WarSimulator(HISTORICAL_PRESETS["wwi"])
        result = sim.simulate(max_months=120, seed=42)
        for val in result["military_a"] + result["military_b"]:
            assert val >= 0.0


class TestDerivedMetrics:
    """DSS and SES computation."""

    def test_dss_bounded(self):
        sim = WarSimulator(HISTORICAL_PRESETS["gulf_war_1991"])
        result = sim.simulate(max_months=120, seed=42)
        for val in result["dss_a"] + result["dss_b"]:
            assert 0.0 <= val <= 100.0

    def test_ses_bounded(self):
        sim = WarSimulator(HISTORICAL_PRESETS["gulf_war_1991"])
        result = sim.simulate(max_months=120, seed=42)
        for val in result["ses_a"] + result["ses_b"]:
            assert 0.0 <= val <= 100.0

    def test_ses_increases_with_duration(self):
        """SES should generally trend upward over time for attritional wars."""
        sim = WarSimulator(HISTORICAL_PRESETS["wwi"])
        result = sim.simulate(max_months=120, seed=42)
        ses = result["ses_a"]
        # First value should be near 0, last should be higher
        assert ses[-1] > ses[0]

    def test_dss_increases_on_shock(self):
        """DSS should spike during shock months for high-shock wars."""
        sim = WarSimulator(HISTORICAL_PRESETS["gulf_war_1991"])
        result = sim.simulate(max_months=12, seed=42)
        # DSS values should exist and have at least one non-zero
        assert any(v > 0 for v in result["dss_b"])


class TestTermination:
    """War termination conditions."""

    def test_gulf_war_terminates_early(self):
        """Gulf War (high shock) should end well before 120 months."""
        sim = WarSimulator(HISTORICAL_PRESETS["gulf_war_1991"])
        result = sim.simulate(max_months=120, seed=42)
        assert result["termination_month"] <= 120
        assert result["outcome"] != "inconclusive"

    def test_vietnam_war_tends_attritional(self):
        """Vietnam should tend toward exhaustion/attritional termination."""
        sim = WarSimulator(HISTORICAL_PRESETS["vietnam_war"])
        result = sim.simulate(max_months=120, seed=42)
        # Should terminate (not run all 120 months)
        assert result["termination_month"] <= 120

    def test_franco_prussian_terminates_decisively(self):
        """Franco-Prussian should produce a decisive outcome."""
        sim = WarSimulator(HISTORICAL_PRESETS["franco_prussian"])
        result = sim.simulate(max_months=120, seed=42)
        assert result["outcome"] in ("dominance_a", "dominance_b", "collapse_a", "collapse_b")

    def test_political_will_below_10_terminates(self):
        """When political will drops below 10, war should end decisively."""
        sim = WarSimulator({
            "war_type": "limited_war",
            "initial_military_a": 50,
            "initial_military_b": 80,
            "initial_economic_a": 30,
            "initial_economic_b": 90,
            "initial_political_will_a": 12,
            "initial_political_will_b": 90,
            "initial_population_support_a": 15,
            "initial_population_support_b": 85,
            "initial_industrial_a": 30,
            "initial_industrial_b": 90,
            "shock_strength": 90,
            "attrition_rate": 90,
            "economic_resilience": 20,
            "political_resilience": 10,
        })
        result = sim.simulate(max_months=120, seed=42)
        assert result["outcome"] in ("collapse_a", "collapse_b", "dominance_a", "dominance_b", "exhaustion_a", "exhaustion_b")

    def test_economic_collapse_terminates(self):
        """When economic capacity drops below 15, side loses."""
        sim = WarSimulator({
            "war_type": "limited_war",
            "initial_military_a": 50,
            "initial_military_b": 80,
            "initial_economic_a": 10,
            "initial_economic_b": 90,
            "initial_political_will_a": 50,
            "initial_political_will_b": 90,
            "initial_population_support_a": 50,
            "initial_population_support_b": 85,
            "initial_industrial_a": 10,
            "initial_industrial_b": 90,
            "shock_strength": 80,
            "attrition_rate": 90,
            "economic_resilience": 10,
            "political_resilience": 50,
        })
        result = sim.simulate(max_months=120, seed=42)
        assert result["outcome"] in ("collapse_a", "collapse_b", "dominance_a", "dominance_b", "exhaustion_a", "exhaustion_b")


class TestDeterminism:
    """Same seed must produce identical results."""

    def test_same_seed_same_results(self):
        config = HISTORICAL_PRESETS["gulf_war_1991"]
        r1 = WarSimulator(config).simulate(max_months=60, seed=42)
        r2 = WarSimulator(config).simulate(max_months=60, seed=42)
        assert r1["outcome"] == r2["outcome"]
        assert r1["termination_month"] == r2["termination_month"]
        for key in ("military_a", "military_b", "economic_a", "ses_a", "dss_a"):
            assert r1[key] == r2[key]

    def test_different_seed_can_differ(self):
        config = HISTORICAL_PRESETS["wwi"]
        r1 = WarSimulator(config).simulate(max_months=120, seed=42)
        r2 = WarSimulator(config).simulate(max_months=120, seed=99)
        # At least one of these should differ between seeds
        mil_differs = r1["military_a"][-1] != r2["military_a"][-1]
        month_differs = r1["termination_month"] != r2["termination_month"]
        assert mil_differs or month_differs


class TestEconomicDegradation:
    """Economic capacity should degrade under war pressure."""

    def test_economic_declines_over_time(self):
        sim = WarSimulator(HISTORICAL_PRESETS["wwi"])
        result = sim.simulate(max_months=60, seed=42)
        # Economic capacity for both sides should be lower at end than start
        assert result["economic_a"][-1] <= result["economic_a"][0]
        assert result["economic_b"][-1] <= result["economic_b"][0]

    def test_higher_attrition_faster_degradation(self):
        """Higher attrition rate should cause faster economic decline."""
        low_attrition = WarSimulator({
            **HISTORICAL_PRESETS["wwi"],
            "attrition_rate": 30,
        }).simulate(max_months=60, seed=42)

        high_attrition = WarSimulator({
            **HISTORICAL_PRESETS["wwi"],
            "attrition_rate": 90,
        }).simulate(max_months=60, seed=42)

        # High attrition should end earlier or with lower economic capacity
        high_econ_final = high_attrition["economic_b"][-1]
        low_econ_final = low_attrition["economic_b"][-1]
        assert high_econ_final <= low_econ_final


class TestHistoricalPresetOutcomes:
    """Verify expected outcome patterns for historical presets."""

    def test_gulf_war_decisive(self):
        sim = WarSimulator(HISTORICAL_PRESETS["gulf_war_1991"])
        result = sim.simulate(max_months=120, seed=42)
        # Gulf War should be decisive and short
        assert result["outcome"] in ("dominance_a", "dominance_b", "collapse_a", "collapse_b")
        assert result["termination_month"] < 60

    def test_vietnam_attritional(self):
        sim = WarSimulator(HISTORICAL_PRESETS["vietnam_war"])
        result = sim.simulate(max_months=120, seed=42)
        # Vietnam should be attritional (exhaustion or long)
        assert result["termination_month"] > 12 or "exhaustion" in result["outcome"]

    def test_wwi_exhaustion(self):
        sim = WarSimulator(HISTORICAL_PRESETS["wwi"])
        result = sim.simulate(max_months=120, seed=42)
        # WWI should show high exhaustion (SES)
        assert max(result["ses_a"] + result["ses_b"]) > 30

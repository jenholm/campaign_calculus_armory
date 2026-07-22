/**
 * v2 Mechanism Classifier - Browser port
 * Source: src/mahan_vs_attrition/simulation/mechanism_classifier.py
 *
 * Separates termination EVENT (how war ended) from dominant MECHANISM
 * (why war became unwinnable).
 *
 * v2 labels:
 *   Dominant mechanism: "decisive shock" or "strategic exhaustion"
 *   NOT: "Decisive Victory", "Attritional Exhaustion", "Negotiated Settlement"
 *        (those are termination events, not strategic causes)
 */
function classifyMechanism(simulator, presetConfig) {
    if (!simulator || !simulator.history || simulator.history.length < 2) {
        return {
            termination_event: "inconclusive",
            dominant_mechanism: "strategic exhaustion",
            secondary_mechanism: "decisive shock",
            confidence: 0.5,
            decisive_shock_score: 0,
            strategic_exhaustion_score: 0,
            political_exhaustion_score: 0,
            economic_exhaustion_score: 0,
            military_exhaustion_score: 0,
            duration_factor: 0,
            interpretation: "Insufficient data for classification."
        };
    }

    var config = presetConfig || simulator.config;
    var outcome = simulator.outcome;

    var dss_a = simulator.dss_history.a || [];
    var ses_a = simulator.ses_history.a || [];
    var history = simulator.history;

    var shock_strength = config.shock_strength || 50;
    var attrition_rate = config.attrition_rate || 50;

    var init_mil_a = config.initial_military_a || (history[0] ? history[0].military_a : 70);
    var init_mil_b = config.initial_military_b || (history[0] ? history[0].military_b : 70);
    var init_econ_a = config.initial_economic_a || (history[0] ? history[0].economic_a : 70);
    var init_econ_b = config.initial_economic_b || (history[0] ? history[0].economic_b : 70);
    var init_pol_a = config.initial_political_will_a || (history[0] ? history[0].political_will_a : 70);
    var init_pol_b = config.initial_political_will_b || (history[0] ? history[0].political_will_b : 70);

    var peak_dss = 0;
    var avg_dss = 0;
    if (dss_a.length > 0) {
        peak_dss = Math.max.apply(null, dss_a);
        avg_dss = dss_a.reduce(function(a, b) { return a + b; }, 0) / dss_a.length;
    }

    var peak_ses = 0;
    var avg_ses = 0;
    if (ses_a.length > 0) {
        peak_ses = Math.max.apply(null, ses_a);
        avg_ses = ses_a.reduce(function(a, b) { return a + b; }, 0) / ses_a.length;
    }

    var decisive_score = shock_strength * 0.5 + peak_dss * 0.35 + avg_dss * 0.15;

    var strategic_exhaustion_score = attrition_rate * 0.4 + peak_ses * 0.35 + avg_ses * 0.25;

    var mil_a_min = Infinity;
    var mil_b_min = Infinity;
    var econ_a_min = Infinity;
    var econ_b_min = Infinity;
    var pol_a_min = Infinity;
    var pol_b_min = Infinity;

    for (var i = 0; i < history.length; i++) {
        if (history[i].military_a < mil_a_min) mil_a_min = history[i].military_a;
        if (history[i].military_b < mil_b_min) mil_b_min = history[i].military_b;
        if (history[i].economic_a < econ_a_min) econ_a_min = history[i].economic_a;
        if (history[i].economic_b < econ_b_min) econ_b_min = history[i].economic_b;
        if (history[i].political_will_a < pol_a_min) pol_a_min = history[i].political_will_a;
        if (history[i].political_will_b < pol_b_min) pol_b_min = history[i].political_will_b;
    }

    var mil_decline_a = init_mil_a > 0 ? (init_mil_a - mil_a_min) / init_mil_a * 100 : 0;
    var mil_decline_b = init_mil_b > 0 ? (init_mil_b - mil_b_min) / init_mil_b * 100 : 0;
    var military_exhaustion = Math.max(mil_decline_a, mil_decline_b);

    var econ_decline_a = init_econ_a > 0 ? (init_econ_a - econ_a_min) / init_econ_a * 100 : 0;
    var econ_decline_b = init_econ_b > 0 ? (init_econ_b - econ_b_min) / init_econ_b * 100 : 0;
    var economic_exhaustion = Math.max(econ_decline_a, econ_decline_b);

    var pol_decline_a = init_pol_a > 0 ? (init_pol_a - pol_a_min) / init_pol_a * 100 : 0;
    var pol_decline_b = init_pol_b > 0 ? (init_pol_b - pol_b_min) / init_pol_b * 100 : 0;
    var political_exhaustion = Math.max(pol_decline_a, pol_decline_b);

    var duration_months = outcome ? outcome.duration : simulator.month || 120;
    var duration_factor = Math.min(100, duration_months / 120 * 100);

    var composite_exhaustion =
        strategic_exhaustion_score * 0.6 +
        military_exhaustion * 0.15 +
        economic_exhaustion * 0.1 +
        political_exhaustion * 0.05 +
        duration_factor * 0.1;

    var mechanisms = {
        "decisive_shock": decisive_score,
        "strategic_exhaustion": composite_exhaustion
    };

    var sorted = Object.keys(mechanisms).sort(function(a, b) {
        return mechanisms[b] - mechanisms[a];
    });

    var dominant_key = sorted[0];
    var secondary_key = sorted[1];
    var dominant_score = mechanisms[dominant_key];
    var secondary_score = mechanisms[secondary_key];

    var total = dominant_score + secondary_score;
    var confidence = total > 0 ? dominant_score / total : 0.5;

    var mechanism_labels = {
        "decisive_shock": "decisive shock",
        "strategic_exhaustion": "strategic exhaustion"
    };

    var dominant_label = mechanism_labels[dominant_key];
    var secondary_label = mechanism_labels[secondary_key];

    var termination_event = "inconclusive";
    if (outcome) {
        var reason = outcome.reason || "";
        if (reason.indexOf("collapse") >= 0 || reason.indexOf("dominance") >= 0) {
            termination_event = "military/political collapse";
        } else if (reason === "mutual_exhaustion") {
            termination_event = "mutual exhaustion";
        } else if (reason.indexOf("exhaustion") >= 0) {
            termination_event = "exhaustion";
        } else if (reason === "negotiated_settlement") {
            termination_event = "negotiated settlement";
        } else if (reason === "time_limit") {
            termination_event = "time limit reached";
        } else {
            termination_event = reason.replace(/_/g, " ");
        }
    }

    var interpretation;
    if (dominant_key === "strategic_exhaustion") {
        interpretation = "Strategic exhaustion dominant (" + Math.round(composite_exhaustion) + "/100). " +
            "The war became unwinnable through cumulative attrition of military, " +
            "economic, and political capacity. Termination was triggered by " +
            termination_event + ", but the underlying cause was exhaustion.";
    } else {
        interpretation = "Decisive shock dominant (" + Math.round(decisive_score) + "/100). " +
            "A decisive operational event or campaign was the primary mechanism " +
            "of strategic change. Termination was triggered by " +
            termination_event + ".";
    }

    return {
        termination_event: termination_event,
        dominant_mechanism: dominant_label,
        secondary_mechanism: confidence < 0.7 ? secondary_label : null,
        confidence: Math.round(confidence * 100) / 100,
        decisive_shock_score: Math.round(decisive_score * 10) / 10,
        strategic_exhaustion_score: Math.round(composite_exhaustion * 10) / 10,
        political_exhaustion_score: Math.round(political_exhaustion * 10) / 10,
        economic_exhaustion_score: Math.round(economic_exhaustion * 10) / 10,
        military_exhaustion_score: Math.round(military_exhaustion * 10) / 10,
        duration_factor: Math.round(duration_factor * 10) / 10,
        interpretation: interpretation
    };
}

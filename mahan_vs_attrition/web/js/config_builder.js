/**
 * DOM-free simulation config builder (MVS-WEB-23)
 *
 * Pure function that builds a simulation config from a preset and UI controls.
 * When a preset is provided, the full preset calibration is used.
 * When no preset is provided, custom slider values are used.
 */

function buildSimulationConfig(preset, controls) {
    var cfg = preset ? Object.assign({}, preset) : {};

    cfg.war_type = controls.war_type || cfg.war_type || 'total_war';
    cfg.side_a = controls.side_a || cfg.side_a || 'Side A';
    cfg.side_b = controls.side_b || cfg.side_b || 'Side B';

    if (!preset) {
        cfg.shock_strength = controls.shock_strength;
        cfg.attrition_rate = controls.attrition_rate;
        cfg.economic_resilience = controls.economic_resilience;
        cfg.political_resilience = controls.political_resilience;
    }

    return cfg;
}

if (typeof window !== 'undefined') {
    window.buildSimulationConfig = buildSimulationConfig;
}

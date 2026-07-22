/**
 * UI-config equivalence test (MVS-WEB-23)
 *
 * Tests that buildSimulationConfig(WAR_PRESETS[key], controls) produces
 * a config that runs identically to direct WarSimulator(WAR_PRESETS[key]).
 *
 * Also tests that the config builder preserves all preset fields.
 *
 * Run: node web/tests/ui_config_equivalence_check.mjs
 */

import { readFileSync } from 'fs';
import vm from 'vm';

const ctx = vm.createContext({
    window: {},
    console,
    Math,
    Number,
    JSON,
    Object,
    Array,
    String,
    Boolean,
    RegExp,
    Date,
    Map,
    Set,
    Promise,
    Symbol,
    isNaN,
    isFinite,
    parseInt,
    parseFloat,
    Infinity,
    NaN,
    Error,
    TypeError,
    RangeError,
    requestAnimationFrame: () => {},
    cancelAnimationFrame: () => {},
    setTimeout,
    clearTimeout
});

function loadFile(path) {
    const code = readFileSync(new URL(path, import.meta.url), 'utf8');
    vm.runInContext(code, ctx, { filename: path });
}

loadFile('../js/war_simulation.js');
loadFile('../js/presets.js');
loadFile('../js/config_builder.js');

vm.runInContext('var presets = window.WAR_PRESETS', ctx);
vm.runInContext('var buildSimulationConfig = window.buildSimulationConfig', ctx);

const presets = vm.runInContext('presets', ctx);

let passed = 0;
let failed = 0;

function assert(condition, msg) {
    if (condition) {
        passed++;
        console.log('  PASS: ' + msg);
    } else {
        failed++;
        console.log('  FAIL: ' + msg);
    }
}

const MAX_MONTHS = 144;
const SEED = 42;

console.log('=== UI-Config Equivalence Test (MVS-WEB-23) ===\n');

// Test 1: buildSimulationConfig preserves preset fields
console.log('--- Config Builder Field Preservation ---');
for (const key of Object.keys(presets)) {
    const p = presets[key];
    vm.runInContext(`
        var _bldCfg_${key} = buildSimulationConfig(presets["${key}"], {
            war_type: presets["${key}"].war_type,
            side_a: presets["${key}"].side_a,
            side_b: presets["${key}"].side_b
        });
    `, ctx);

    const cfg = vm.runInContext(`_bldCfg_${key}`, ctx);

    assert(cfg.shock_strength_a === p.shock_strength_a,
        key + ': shock_strength_a preserved (' + cfg.shock_strength_a + ' === ' + p.shock_strength_a + ')');
    assert(cfg.attrition_rate_b === p.attrition_rate_b,
        key + ': attrition_rate_b preserved (' + cfg.attrition_rate_b + ' === ' + p.attrition_rate_b + ')');
    assert(cfg.economic_resilience_a === p.economic_resilience_a,
        key + ': economic_resilience_a preserved (' + cfg.economic_resilience_a + ' === ' + p.economic_resilience_a + ')');
    assert(cfg.political_resilience_b === p.political_resilience_b,
        key + ': political_resilience_b preserved (' + cfg.political_resilience_b + ' === ' + p.political_resilience_b + ')');

    if (p.earliest_settlement_month !== undefined) {
        assert(cfg.earliest_settlement_month === p.earliest_settlement_month,
            key + ': earliest_settlement_month preserved (' + cfg.earliest_settlement_month + ' === ' + p.earliest_settlement_month + ')');
    }
    if (p.external_support_b !== undefined) {
        assert(cfg.external_support_b === p.external_support_b,
            key + ': external_support_b preserved (' + cfg.external_support_b + ' === ' + p.external_support_b + ')');
    }
    if (p.recruitment_capacity_a !== undefined) {
        assert(cfg.recruitment_capacity_a === p.recruitment_capacity_a,
            key + ': recruitment_capacity_a preserved (' + cfg.recruitment_capacity_a + ' === ' + p.recruitment_capacity_a + ')');
    }
}

// Test 2: Direct preset run vs UI-built config run produce same results
console.log('\n--- Direct vs UI-Built Config Equivalence ---');
for (const key of Object.keys(presets)) {
    vm.runInContext(`
        var _dirSim_${key} = new WarSimulator(presets["${key}"]);
        var _dirOut_${key} = _dirSim_${key}.simulate(${MAX_MONTHS}, ${SEED});

        var _uiCfg_${key} = buildSimulationConfig(presets["${key}"], {
            war_type: presets["${key}"].war_type,
            side_a: presets["${key}"].side_a,
            side_b: presets["${key}"].side_b
        });
        var _uiSim_${key} = new WarSimulator(_uiCfg_${key});
        var _uiOut_${key} = _uiSim_${key}.simulate(${MAX_MONTHS}, ${SEED});
    `, ctx);

    const dirOut = vm.runInContext(`_dirOut_${key}`, ctx);
    const uiOut = vm.runInContext(`_uiOut_${key}`, ctx);

    assert(dirOut.winner === uiOut.winner,
        key + ': winner matches (' + dirOut.winner + ' === ' + uiOut.winner + ')');
    assert(dirOut.duration === uiOut.duration,
        key + ': duration matches (' + dirOut.duration + ' === ' + uiOut.duration + ')');
    assert(dirOut.reason === uiOut.reason,
        key + ': reason matches (' + dirOut.reason + ' === ' + uiOut.reason + ')');

    const dirHistLen = vm.runInContext(`_dirSim_${key}.history.length`, ctx);
    const uiHistLen = vm.runInContext(`_uiSim_${key}.history.length`, ctx);
    assert(dirHistLen === uiHistLen,
        key + ': history length matches (' + dirHistLen + ' === ' + uiHistLen + ')');
}

// Test 3: UI-stripped config (no preset) should produce DIFFERENT results
console.log('\n--- Stripped Config Should Differ ---');
for (const key of Object.keys(presets)) {
    vm.runInContext(`
        var _stripCfg_${key} = {
            war_type: presets["${key}"].war_type,
            side_a: presets["${key}"].side_a,
            side_b: presets["${key}"].side_b,
            shock_strength: presets["${key}"].shock_strength,
            attrition_rate: presets["${key}"].attrition_rate,
            economic_resilience: presets["${key}"].economic_resilience,
            political_resilience: presets["${key}"].political_resilience,
            initial_military_a: presets["${key}"].initial_military_a,
            initial_military_b: presets["${key}"].initial_military_b,
            initial_economic_a: presets["${key}"].initial_economic_a,
            initial_economic_b: presets["${key}"].initial_economic_b,
            initial_political_will_a: presets["${key}"].initial_political_will_a,
            initial_political_will_b: presets["${key}"].initial_political_will_b,
            initial_population_support_a: presets["${key}"].initial_population_support_a,
            initial_population_support_b: presets["${key}"].initial_population_support_b,
            initial_industrial_a: presets["${key}"].initial_industrial_a,
            initial_industrial_b: presets["${key}"].initial_industrial_b
        };
        var _stripSim_${key} = new WarSimulator(_stripCfg_${key});
        var _stripOut_${key} = _stripSim_${key}.simulate(${MAX_MONTHS}, ${SEED});
    `, ctx);

    const dirOut = vm.runInContext(`_dirOut_${key}`, ctx);
    const stripOut = vm.runInContext(`_stripOut_${key}`, ctx);

    const differs = dirOut.duration !== stripOut.duration || dirOut.reason !== stripOut.reason;
    assert(differs,
        key + ': stripped config differs from direct (dur=' + stripOut.duration + ', reason=' + stripOut.reason + ')');
}

console.log('\n=== Results ===');
console.log('Passed: ' + passed);
console.log('Failed: ' + failed);
console.log(failed === 0 ? '\nALL TESTS PASSED' : '\nSOME CHECKS FAILED');

process.exit(failed > 0 ? 1 : 0);

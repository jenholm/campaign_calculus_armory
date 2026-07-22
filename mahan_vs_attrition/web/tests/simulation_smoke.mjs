/**
 * Node.js simulation smoke test
 * Tests that WarSimulator works correctly with shared step engine.
 *
 * Run: node web/tests/simulation_smoke.mjs
 */

import { readFileSync } from 'fs';
import vm from 'vm';

const fakeWindow = {};
const ctx = vm.createContext({
    window: fakeWindow,
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
loadFile('../js/mechanism_classifier.js');

// Inject presets into vm context for later access
vm.runInContext('var presets = window.WAR_PRESETS', ctx);

const WarSimulator = vm.runInContext('typeof WarSimulator !== "undefined" ? WarSimulator : undefined', ctx);
const presets = vm.runInContext('presets', ctx);
const classifyMechanism = vm.runInContext('typeof classifyMechanism !== "undefined" ? classifyMechanism : undefined', ctx);

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

console.log('=== WarSimulator Smoke Tests ===\n');

assert(typeof WarSimulator === 'function', 'WarSimulator exists');

// Create instance via vm
vm.runInContext('var _sim = new WarSimulator({ initial_military_a: 80, initial_military_b: 80 })', ctx);
assert(vm.runInContext('typeof _sim.reset === "function"', ctx), 'reset() exists');
assert(vm.runInContext('typeof _sim.stepOneMonth === "function"', ctx), 'stepOneMonth() exists');

// Run simulate
vm.runInContext('var _outcome = _sim.simulate(120, 42)', ctx);
assert(vm.runInContext('_outcome !== null && _outcome !== undefined', ctx), 'simulate() returns outcome');
assert(vm.runInContext('_outcome.duration > 0', ctx), 'simulate() produces non-zero duration (got ' + vm.runInContext('_outcome.duration', ctx) + ')');
assert(vm.runInContext('_outcome.final_dss_a !== undefined', ctx), 'outcome has final_dss_a');
assert(vm.runInContext('_outcome.final_ses_a !== undefined', ctx), 'outcome has final_ses_a');
assert(vm.runInContext('_outcome.turning_point !== undefined', ctx), 'outcome has turning_point');

assert(vm.runInContext('_sim.history.length > 1', ctx), 'history has more than 1 entry (got ' + vm.runInContext('_sim.history.length', ctx) + ')');
assert(
    vm.runInContext('_sim.dss_history.a.length === _sim.ses_history.a.length', ctx),
    'dss_history.a length matches ses_history.a length (' + vm.runInContext('_sim.dss_history.a.length', ctx) + ')'
);
assert(
    vm.runInContext('_sim.dss_history.a.length === _sim.history.length - 1', ctx),
    'dss_history.a length == history.length - 1 (' + vm.runInContext('_sim.dss_history.a.length', ctx) + ' vs ' + vm.runInContext('_sim.history.length - 1', ctx) + ')'
);

console.log('\n=== Preset Tests ===');
const presetKeys = ['gulf_war_1991', 'vietnam_war', 'wwi', 'franco_prussian', 'korean_war', 'iran_iraq', 'wwii'];

for (const key of presetKeys) {
    const p = presets[key];
    assert(p !== undefined, 'Preset "' + key + '" exists');
    if (!p) continue;

    vm.runInContext(`
        var _pcfg_${key} = {
            war_type: presets["${key}"].war_type,
            side_a: presets["${key}"].side_a,
            side_b: presets["${key}"].side_b,
            initial_military_a: presets["${key}"].initial_military_a,
            initial_military_b: presets["${key}"].initial_military_b,
            initial_economic_a: presets["${key}"].initial_economic_a,
            initial_economic_b: presets["${key}"].initial_economic_b,
            initial_political_will_a: presets["${key}"].initial_political_will_a,
            initial_political_will_b: presets["${key}"].initial_political_will_b,
            initial_population_support_a: presets["${key}"].initial_population_support_a,
            initial_population_support_b: presets["${key}"].initial_population_support_b,
            initial_industrial_a: presets["${key}"].initial_industrial_a,
            initial_industrial_b: presets["${key}"].initial_industrial_b,
            shock_strength: presets["${key}"].shock_strength,
            attrition_rate: presets["${key}"].attrition_rate,
            economic_resilience: presets["${key}"].economic_resilience,
            political_resilience: presets["${key}"].political_resilience,
            shock_strength_a: presets["${key}"].shock_strength_a,
            shock_strength_b: presets["${key}"].shock_strength_b,
            attrition_rate_a: presets["${key}"].attrition_rate_a,
            attrition_rate_b: presets["${key}"].attrition_rate_b,
            economic_resilience_a: presets["${key}"].economic_resilience_a,
            economic_resilience_b: presets["${key}"].economic_resilience_b,
            political_resilience_a: presets["${key}"].political_resilience_a,
            political_resilience_b: presets["${key}"].political_resilience_b,
            allow_negotiated_settlement: presets["${key}"].allow_negotiated_settlement,
            earliest_settlement_month: presets["${key}"].earliest_settlement_month,
            settlement_military_threshold: presets["${key}"].settlement_military_threshold,
            settlement_exhaustion_threshold: presets["${key}"].settlement_exhaustion_threshold
        };
        var _s_${key} = new WarSimulator(_pcfg_${key});
        var _o_${key} = _s_${key}.simulate(120, 42);
    `, ctx);

    assert(vm.runInContext(`_o_${key} !== null`, ctx), key + ': simulate() returns outcome');
    assert(vm.runInContext(`_s_${key}.history.length > 1`, ctx), key + ': history non-empty (' + vm.runInContext(`_s_${key}.history.length`, ctx) + ' entries)');
    assert(vm.runInContext(`_s_${key}.dss_history.a.length === _s_${key}.history.length - 1`, ctx), key + ': dss_history length matches history');
    assert(vm.runInContext(`_s_${key}.ses_history.a.length === _s_${key}.history.length - 1`, ctx), key + ': ses_history length matches history');
    assert(vm.runInContext(`_o_${key}.duration > 0`, ctx), key + ': duration > 0 (' + vm.runInContext(`_o_${key}.duration`, ctx) + ')');
    assert(vm.runInContext(`_o_${key}.final_dss_a >= 0`, ctx), key + ': final_dss_a >= 0');
    assert(vm.runInContext(`_o_${key}.final_ses_a >= 0`, ctx), key + ': final_ses_a >= 0');
}

console.log('\n=== Step vs Simulate Consistency ===');
vm.runInContext(`
    var _stepCfg = {
        initial_military_a: 80, initial_military_b: 80,
        initial_economic_a: 80, initial_economic_b: 80,
        initial_political_will_a: 80, initial_political_will_b: 80,
        initial_population_support_a: 80, initial_population_support_b: 80,
        initial_industrial_a: 80, initial_industrial_b: 80,
        shock_strength: 60, attrition_rate: 60,
        economic_resilience: 60, political_resilience: 60,
        side_a: 'A', side_b: 'B'
    };
    var _simBatch = new WarSimulator(_stepCfg);
    var _batchOutcome = _simBatch.simulate(120, 42);

    var _simStep = new WarSimulator(_stepCfg);
    _simStep.reset(42);
    var _stepOutcome = null;
    for (var i = 0; i < 120; i++) {
        _stepOutcome = _simStep.stepOneMonth();
        if (_stepOutcome) break;
    }
    if (!_stepOutcome) {
        _stepOutcome = _simStep._buildOutcome(
            { winner: 'draw', reason: 'time_limit' },
            _simStep.dss_history.a[_simStep.dss_history.a.length - 1] || 0,
            _simStep.dss_history.b[_simStep.dss_history.b.length - 1] || 0,
            _simStep.ses_history.a[_simStep.ses_history.a.length - 1] || 0,
            _simStep.ses_history.b[_simStep.ses_history.b.length - 1] || 0,
            _simStep.month
        );
    }
`, ctx);

assert(
    vm.runInContext('_batchOutcome.duration === _stepOutcome.duration', ctx),
    'Batch and step durations match (' + vm.runInContext('_batchOutcome.duration', ctx) + ' vs ' + vm.runInContext('_stepOutcome.duration', ctx) + ')'
);
assert(
    vm.runInContext('_batchOutcome.reason === _stepOutcome.reason', ctx),
    'Batch and step reasons match (' + vm.runInContext('_batchOutcome.reason', ctx) + ' vs ' + vm.runInContext('_stepOutcome.reason', ctx) + ')'
);
assert(
    vm.runInContext('_simBatch.history.length === _simStep.history.length', ctx),
    'Batch and step history lengths match (' + vm.runInContext('_simBatch.history.length', ctx) + ' vs ' + vm.runInContext('_simStep.history.length', ctx) + ')'
);

console.log('\n=== Mechanism Classifier Tests ===');
assert(vm.runInContext('typeof classifyMechanism === "function"', ctx), 'classifyMechanism() exists');

console.log('\n=== Expected Mechanism Classifications ===');

function classifyPreset(key) {
    vm.runInContext(`
        var _cls_${key} = new WarSimulator({
            initial_military_a: presets["${key}"].initial_military_a,
            initial_military_b: presets["${key}"].initial_military_b,
            initial_economic_a: presets["${key}"].initial_economic_a,
            initial_economic_b: presets["${key}"].initial_economic_b,
            initial_political_will_a: presets["${key}"].initial_political_will_a,
            initial_political_will_b: presets["${key}"].initial_political_will_b,
            initial_population_support_a: presets["${key}"].initial_population_support_a,
            initial_population_support_b: presets["${key}"].initial_population_support_b,
            initial_industrial_a: presets["${key}"].initial_industrial_a,
            initial_industrial_b: presets["${key}"].initial_industrial_b,
            shock_strength: presets["${key}"].shock_strength,
            attrition_rate: presets["${key}"].attrition_rate,
            economic_resilience: presets["${key}"].economic_resilience,
            political_resilience: presets["${key}"].political_resilience,
            shock_strength_a: presets["${key}"].shock_strength_a,
            shock_strength_b: presets["${key}"].shock_strength_b,
            attrition_rate_a: presets["${key}"].attrition_rate_a,
            attrition_rate_b: presets["${key}"].attrition_rate_b,
            economic_resilience_a: presets["${key}"].economic_resilience_a,
            economic_resilience_b: presets["${key}"].economic_resilience_b,
            political_resilience_a: presets["${key}"].political_resilience_a,
            political_resilience_b: presets["${key}"].political_resilience_b,
            allow_negotiated_settlement: presets["${key}"].allow_negotiated_settlement,
            earliest_settlement_month: presets["${key}"].earliest_settlement_month,
            settlement_military_threshold: presets["${key}"].settlement_military_threshold,
            settlement_exhaustion_threshold: presets["${key}"].settlement_exhaustion_threshold
        });
        _cls_${key}.simulate(120, 42);
        var _clsResult_${key} = classifyMechanism(_cls_${key}, {
            initial_military_a: presets["${key}"].initial_military_a,
            initial_military_b: presets["${key}"].initial_military_b,
            initial_economic_a: presets["${key}"].initial_economic_a,
            initial_economic_b: presets["${key}"].initial_economic_b,
            initial_political_will_a: presets["${key}"].initial_political_will_a,
            initial_political_will_b: presets["${key}"].initial_political_will_b,
            shock_strength: presets["${key}"].shock_strength,
            attrition_rate: presets["${key}"].attrition_rate
        });
    `, ctx);
    return vm.runInContext(`_clsResult_${key}`, ctx);
}

const gulf = classifyPreset('gulf_war_1991');
assert(gulf.dominant_mechanism === 'decisive shock',
    'Gulf War 1991: decisive shock (got "' + gulf.dominant_mechanism + '")');

const franco = classifyPreset('franco_prussian');
assert(franco.dominant_mechanism === 'decisive shock',
    'Franco-Prussian: decisive shock (got "' + franco.dominant_mechanism + '")');

const vietnam = classifyPreset('vietnam_war');
assert(vietnam.dominant_mechanism === 'strategic exhaustion',
    'Vietnam: strategic exhaustion (got "' + vietnam.dominant_mechanism + '")');

const wwiResult = classifyPreset('wwi');
assert(wwiResult.dominant_mechanism === 'strategic exhaustion',
    'WWI: strategic exhaustion (got "' + wwiResult.dominant_mechanism + '")');

const wwiiResult = classifyPreset('wwii');
assert(wwiiResult.dominant_mechanism === 'strategic exhaustion',
    'WWII: strategic exhaustion (got "' + wwiiResult.dominant_mechanism + '")');

const korean = classifyPreset('korean_war');
assert(korean.dominant_mechanism === 'strategic exhaustion',
    'Korean War: strategic exhaustion in model (got "' + korean.dominant_mechanism + '")');

const iran = classifyPreset('iran_iraq');
assert(iran.dominant_mechanism === 'strategic exhaustion',
    'Iran-Iraq: strategic exhaustion (got "' + iran.dominant_mechanism + '")');

console.log('\n=== Results ===');
console.log('Passed: ' + passed);
console.log('Failed: ' + failed);
console.log(failed === 0 ? '\nALL TESTS PASSED' : '\nSOME TESTS FAILED');

process.exit(failed > 0 ? 1 : 0);

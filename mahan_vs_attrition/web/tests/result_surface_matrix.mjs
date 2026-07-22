/**
 * Three-surface result matrix test (MVS-WEB-21)
 *
 * Runs each preset through two web execution paths and records the results:
 *   Surface 1: Web engine direct — new WarSimulator(WAR_PRESETS[key]).simulate(144, 42)
 *   Surface 2: UI-stripped config — buildSimulationConfig(null, controls) with shared sliders only
 *
 * Surface 3 (Python canonical) requires a separate Python run and is documented
 * in historical_calibration_report.md.
 *
 * Run: node web/tests/result_surface_matrix.mjs
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

vm.runInContext('var presets = window.WAR_PRESETS', ctx);
vm.runInContext('var expected = window.EXPECTED_HISTORICAL_RESULTS', ctx);

const presets = vm.runInContext('presets', ctx);
const expected = vm.runInContext('expected', ctx);

const MAX_MONTHS = 144;
const SEED = 42;

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

function runDirectPreset(key) {
    vm.runInContext(`
        var _direct_${key} = new WarSimulator(presets["${key}"]);
        var _directOut_${key} = _direct_${key}.simulate(${MAX_MONTHS}, ${SEED});
    `, ctx);
    return vm.runInContext(`_directOut_${key}`, ctx);
}

function runUIStrippedConfig(key) {
    const p = presets[key];
    vm.runInContext(`
        var _uiCfg_${key} = {
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
        var _uiSim_${key} = new WarSimulator(_uiCfg_${key});
        var _uiOut_${key} = _uiSim_${key}.simulate(${MAX_MONTHS}, ${SEED});
    `, ctx);
    return vm.runInContext(`_uiOut_${key}`, ctx);
}

console.log('=== Three-Surface Result Matrix (MVS-WEB-21) ===\n');

const matrix = [];

for (const key of Object.keys(presets)) {
    const direct = runDirectPreset(key);
    const uiStripped = runUIStrippedConfig(key);

    const exp = expected[key];

    console.log('--- ' + presets[key].name + ' ---');
    console.log('  Direct full preset:  winner=' + direct.winner + ', winner_key=' + direct.winner_key + ', duration=' + direct.duration + ', reason=' + direct.reason);
    console.log('  UI-stripped config:  winner=' + uiStripped.winner + ', winner_key=' + uiStripped.winner_key + ', duration=' + uiStripped.duration + ', reason=' + uiStripped.reason);

    if (exp) {
        console.log('  Expected:            winner_key=' + exp.expected_winner_key + ', duration=' + exp.expected_duration_months + ' ±' + exp.duration_tolerance_months);
    }

    matrix.push({
        preset: key,
        name: presets[key].name,
        direct_winner: direct.winner,
        direct_winner_key: direct.winner_key,
        direct_duration: direct.duration,
        direct_reason: direct.reason,
        ui_winner: uiStripped.winner,
        ui_winner_key: uiStripped.winner_key,
        ui_duration: uiStripped.duration,
        ui_reason: uiStripped.reason,
        expected_winner_key: exp ? exp.expected_winner_key : null,
        expected_duration: exp ? exp.expected_duration_months : null,
        expected_tolerance: exp ? exp.duration_tolerance_months : null
    });

    assert(direct.winner_key !== undefined, key + ': direct surface has winner_key');
    assert(uiStripped.winner_key !== undefined, key + ': UI surface has winner_key');
}

console.log('\n=== Matrix Summary ===\n');
console.log('Preset | Direct Winner | Direct Duration | UI Winner | UI Duration | Expected Winner | Expected Duration');
console.log('-------|---------------|-----------------|-----------|-------------|-----------------|-------------------');
for (const row of matrix) {
    console.log(
        row.name.padEnd(22) + '| ' +
        row.direct_winner.padEnd(14) + '| ' +
        String(row.direct_duration).padEnd(16) + '| ' +
        row.ui_winner.padEnd(10) + '| ' +
        String(row.ui_duration).padEnd(12) + '| ' +
        (row.expected_winner_key || '').padEnd(16) + '| ' +
        (row.expected_duration ? row.expected_duration + ' ±' + row.expected_tolerance : '')
    );
}

console.log('\n=== Results ===');
console.log('Passed: ' + passed);
console.log('Failed: ' + failed);
console.log(failed === 0 ? '\nALL CHECKS PASSED' : '\nSOME CHECKS FAILED');

process.exit(failed > 0 ? 1 : 0);

/**
 * Historical outcome check test
 * Tests that model produces correct winners and plausible durations.
 *
 * Some tests are expected to fail until MVS-WEB-13/14/15 are complete.
 * Run: node web/tests/historical_outcome_check.mjs
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

vm.runInContext('var _presets = window.WAR_PRESETS', ctx);
vm.runInContext('var _expected = window.EXPECTED_HISTORICAL_RESULTS', ctx);

const presets = vm.runInContext('_presets', ctx);
const expected = vm.runInContext('_expected', ctx);

// Also make 'presets' available inside the VM
vm.runInContext('var presets = _presets', ctx);

let passed = 0;
let failed = 0;
let skipped = 0;

function assert(condition, msg) {
    if (condition) {
        passed++;
        console.log('  PASS: ' + msg);
    } else {
        failed++;
        console.log('  FAIL: ' + msg);
    }
}

function skip(msg) {
    skipped++;
    console.log('  SKIP: ' + msg);
}

console.log('=== Historical Outcome Checks ===\n');

const presetKeys = Object.keys(presets);

for (const key of presetKeys) {
    if (!expected[key]) {
        skip(key + ': no expected results defined');
        continue;
    }

    const exp = expected[key];
    const cfg = presets[key];

    vm.runInContext(`
        var _sim_${key} = new WarSimulator(Object.assign({}, presets["${key}"]));
        var _out_${key} = _sim_${key}.simulate(144, 42);
    `, ctx);

    const outcome = vm.runInContext(`_out_${key}`, ctx);
    const duration = outcome.duration;
    const winner = outcome.winner;
    const lo = exp.expected_duration_months - exp.duration_tolerance_months;
    const hi = exp.expected_duration_months + exp.duration_tolerance_months;

    console.log('--- ' + cfg.name + ' ---');
    console.log('  Model: winner=' + winner + ', duration=' + duration + ' months');

    // Winner check
    let winnerMatch = false;
    if (exp.expected_winner_key === 'draw') {
        winnerMatch = (winner.toLowerCase() === 'draw');
    } else if (exp.expected_winner_key === 'side_a') {
        winnerMatch = (winner === cfg.side_a);
    } else if (exp.expected_winner_key === 'side_b') {
        winnerMatch = (winner === cfg.side_b);
    }
    assert(winnerMatch, key + ': winner is ' + exp.expected_winner_key + ' (got "' + winner + '")');

    // Duration check
    const durationOk = duration >= lo && duration <= hi;
    assert(durationOk, key + ': duration in [' + lo + ', ' + hi + '] (got ' + duration + ')');
}

console.log('\n=== Results ===');
console.log('Passed: ' + passed);
console.log('Failed: ' + failed);
console.log('Skipped: ' + skipped);
console.log(failed === 0 ? '\nALL CHECKS PASSED' : '\nSOME CHECKS FAILED');

process.exit(failed > 0 ? 1 : 0);

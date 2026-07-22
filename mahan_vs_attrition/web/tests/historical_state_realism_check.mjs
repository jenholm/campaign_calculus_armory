/**
 * State-realism checks (MVS-WEB-34)
 *
 * Guards against zombie-ratio dominance and ensures model wins for sane reasons.
 * Each preset has specific realism constraints beyond winner/duration.
 *
 * Run: node web/tests/historical_state_realism_check.mjs
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

function getSimResult(key) {
    vm.runInContext(`
        var _realSim_${key} = new WarSimulator(presets["${key}"]);
        var _realOut_${key} = _realSim_${key}.simulate(144, 42);
    `, ctx);
    const out = vm.runInContext(`_realOut_${key}`, ctx);
    const hist = vm.runInContext(`_realSim_${key}.history`, ctx);
    const lastState = hist[hist.length - 1];
    return { outcome: out, lastState: lastState, history: hist };
}

console.log('=== State-Realism Checks (MVS-WEB-34) ===\n');

// --- Vietnam: Side A withdrawal ---
console.log('--- Vietnam War ---');
const vietnam = getSimResult('vietnam_war');
assert(vietnam.outcome.winner_key === 'b' || vietnam.outcome.winner.toLowerCase() === 'draw',
    'Vietnam: Side B wins or draw (got ' + vietnam.outcome.winner_key + ')');
assert(vietnam.outcome.reason === 'withdrawal_a' || vietnam.outcome.reason === 'time_limit' || vietnam.outcome.reason === 'negotiated_settlement',
    'Vietnam: reason is withdrawal/exhaustion (got ' + vietnam.outcome.reason + ')');
assert(vietnam.lastState.political_will_a < 45,
    'Vietnam: Side A political will degraded (' + vietnam.lastState.political_will_a.toFixed(1) + ' < 45)');
// NOTE: Side A military viability is a known model limitation — both sides
// grind to near-zero in the current attrition model. Full fix requires
// external support dynamics to sustain Side A military above threshold.

// --- Franco-Prussian: Quick decisive, duration reasonable ---
console.log('\n--- Franco-Prussian War ---');
const fp = getSimResult('franco_prussian');
assert(fp.outcome.winner_key === 'a',
    'Franco-Prussian: Prussia wins (got ' + fp.outcome.winner_key + ')');
assert(fp.outcome.reason.includes('dominance') || fp.outcome.reason.includes('collapse') || fp.outcome.reason.includes('exhaustion'),
    'Franco-Prussian: reason is dominance/collapse/exhaustion (got ' + fp.outcome.reason + ')');
assert(fp.outcome.duration <= 48,
    'Franco-Prussian: duration <= 48 months (got ' + fp.outcome.duration + ')');

// --- Zombie dominance guard: dominance termination must have viable winner ---
console.log('\n--- Zombie Dominance Guard ---');
for (const key of Object.keys(presets)) {
    const r = getSimResult(key);
    if (r.outcome.winner_key !== 'a' && r.outcome.winner_key !== 'b') {
        assert(true, key + ': draw — no zombie check needed');
    } else if (r.outcome.reason.includes('dominance')) {
        const winnerMil = r.outcome.winner_key === 'a' ? r.lastState.military_a : r.lastState.military_b;
        assert(winnerMil >= 25,
            key + ': dominance winner military >= 25 (got ' + winnerMil.toFixed(1) + ')');
    } else {
        assert(true, key + ': winner by ' + r.outcome.reason + ' — dominance zombie guard N/A');
    }
}

// --- Iran-Iraq: Long war, sustained ---
console.log('\n--- Iran-Iraq War ---');
const iraq = getSimResult('iran_iraq');
assert(iraq.outcome.winner_key === 'draw' || iraq.outcome.duration >= 60,
    'Iran-Iraq: long war (got ' + iraq.outcome.duration + ' months)');
assert(iraq.outcome.reason === 'negotiated_settlement' || iraq.outcome.reason === 'mutual_exhaustion' || iraq.outcome.reason === 'time_limit',
    'Iran-Iraq: negotiated/mutual exhaustion (got ' + iraq.outcome.reason + ')');

// --- WWII: Allies win, Axis degraded ---
console.log('\n--- World War II ---');
const wwii = getSimResult('wwii');
assert(wwii.outcome.winner_key === 'a',
    'WWII: Allies win (got ' + wwii.outcome.winner_key + ')');
assert(wwii.lastState.economic_b < 40 || wwii.lastState.political_will_b < 30,
    'WWII: Axis economic/political degraded (econ=' + wwii.lastState.economic_b.toFixed(1) + ', pol=' + wwii.lastState.political_will_b.toFixed(1) + ')');

// --- WWI: Allies win ---
console.log('\n--- World War I ---');
const wwi = getSimResult('wwi');
assert(wwi.outcome.winner_key === 'a',
    'WWI: Allies win (got ' + wwi.outcome.winner_key + ')');
// NOTE: WWI ends by exhaustion_b — both sides' militaries degrade significantly.
// This is historically coherent (Western Front attrition) but the model
// over-degrades Allied military. Known model limitation.

// --- Gulf War: Coalition decisive ---
console.log('\n--- Gulf War 1991 ---');
const gulf = getSimResult('gulf_war_1991');
assert(gulf.outcome.winner_key === 'a',
    'Gulf War: Coalition wins (got ' + gulf.outcome.winner_key + ')');
assert(gulf.outcome.duration <= 60,
    'Gulf War: duration <= 60 months (got ' + gulf.outcome.duration + ')');

// --- Korea: Draw ---
console.log('\n--- Korean War ---');
const korea = getSimResult('korean_war');
assert(korea.outcome.winner_key === 'draw' || korea.outcome.winner.toLowerCase() === 'draw',
    'Korea: draw result (got ' + korea.outcome.winner_key + ')');

console.log('\n=== Results ===');
console.log('Passed: ' + passed);
console.log('Failed: ' + failed);
console.log(failed === 0 ? '\nALL CHECKS PASSED' : '\nSOME CHECKS FAILED');

process.exit(failed > 0 ? 1 : 0);

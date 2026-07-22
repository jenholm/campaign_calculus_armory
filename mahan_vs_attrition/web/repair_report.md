# Web Simulator Repair Report

## Status: REPAIRED

### Hard Failure 1: Charts cannot draw

| Field | Value |
|-------|-------|
| **Observed failure** | `TypeError: this._drawSeries is not a function` |
| **File** | `web/js/charts.js:190` |
| **Trigger** | Clicking "Run Simulation" calls `trajectoryChart.setData(...)` which calls `_draw()` which calls `this._drawSeries()` |
| **Root cause** | `_drawSeries()` method is referenced in `_draw()` but never defined in the `TimelineChart` class |
| **Impact** | Charts never render; trajectory and mechanism panels remain blank |
| **Status before repair** | NOT FIXED |

### Hard Failure 2: Animation calls nonexistent simulator method

| Field | Value |
|-------|-------|
| **Observed failure** | `TypeError: simulator._applyStep is not a function` |
| **File** | `web/js/app.js:210-211` |
| **Trigger** | Clicking "Run Animation" calls `simulator._applyStep('a')` and `simulator._applyStep('b')` |
| **Root cause** | `WarSimulator` class in `war_simulation.js` has `_applyAttrition(month)` and `_applyShock(month)` but no `_applyStep()` method |
| **Impact** | Animation loop crashes on first frame; no animation plays |
| **Status before repair** | NOT FIXED |

### Hard Failure 3: Preset loading fails in file:// mode

| Field | Value |
|-------|-------|
| **Observed failure** | Silent failure; `fetch('data/presets.json')` blocked by CORS when opened via `file://` |
| **File** | `web/js/app.js:62` |
| **Trigger** | Opening `index.html` directly without a server, then clicking any preset button |
| **Root cause** | `loadPresets()` uses `fetch()` which is blocked in `file://` context on most browsers |
| **Impact** | Preset buttons silently do nothing; user sees no error |
| **Status before repair** | NOT FIXED |

### Alignment Problem 1: v1 classifier in browser vs v2 in paper

| Field | Value |
|-------|-------|
| **Observed failure** | Outcome panel shows termination event (e.g., "Decisive Victory") as if it were the mechanism classification |
| **File** | `web/js/app.js:337` |
| **Trigger** | Any simulation run |
| **Root cause** | `renderOutcome()` displays `outcome.type` which is `_determineOutcome()` output -- a termination event label, not a v2 mechanism classification |
| **Impact** | Vietnam shows "Decisive Victory" when paper says "strategic exhaustion"; WWI shows "Negotiated Settlement" when paper says "strategic exhaustion" |
| **Status before repair** | NOT FIXED |

### Alignment Problem 2: Missing World War II preset

| Field | Value |
|-------|-------|
| **Observed failure** | WWII preset absent from UI |
| **Files** | `web/index.html` (buttons), `web/data/presets.json`, `web/js/war_simulation.js` (HISTORICAL_EVENTS) |
| **Root cause** | Only 6 presets in web vs 7 in Python `HISTORICAL_PRESETS` |
| **Impact** | WWII cannot be simulated or compared |
| **Status before repair** | NOT FIXED |

### Alignment Problem 3: Only 3 of 5 state variables charted

| Field | Value |
|-------|-------|
| **Observed failure** | Charts show military, political will, economic -- omit population support and industrial capacity |
| **File** | `web/js/app.js:268-275` |
| **Impact** | Users/reviewers cannot see full model behavior |
| **Status before repair** | NOT FIXED |

### Alignment Problem 4: Key mismatch between web and Python

| Field | Value |
|-------|-------|
| **Observed failure** | Web uses `vietnam`/`korean`; Python uses `vietnam_war`/`korean_war` |
| **Impact** | Drift between canonical source and web demo |
| **Status before repair** | NOT FIXED |

## Evidence Captured

- Code review of all web/ files completed
- Python source `war_dynamics.py` HISTORICAL_PRESETS (7 presets) documented
- Python source `mechanism_classifier.py` v2 logic documented
- All failure paths confirmed via static analysis

## Acceptance Gate

This report will be updated to "REPAIRED" when all items below pass:
- [x] No console errors on page load
- [x] Preset buttons work (embedded presets, no fetch())
- [x] Run Simulation works (shared stepOneMonth engine)
- [x] Run Animation works (uses stepOneMonth, same path as simulate())
- [x] Animation final result matches Run Simulation final result (same seed, same engine)
- [x] Export JSON works
- [x] History Mode works (all 7 presets including WWII)
- [x] Charts render trajectories (_drawSeries implemented)
- [x] Mechanism chart renders DSS/SES
- [x] Outcome panel shows termination event separately from dominant mechanism (v2 classifier)
- [x] Vietnam displays strategic exhaustion as dominant mechanism
- [x] WWI displays strategic exhaustion as dominant mechanism
- [x] Gulf War displays decisive shock as dominant mechanism
- [x] WWII exists as a preset
- [x] README no longer lies about file/server mode
- [x] Tests exist (static_check.sh + simulation_smoke.mjs)

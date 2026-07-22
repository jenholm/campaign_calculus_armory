#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Static Web Checks ==="

# Check _drawSeries exists in charts.js
if grep -q "_drawSeries" js/charts.js; then
    echo "PASS: _drawSeries found in charts.js"
else
    echo "FAIL: _drawSeries not found in charts.js"
    exit 1
fi

# Check _applyStep is NOT in app.js
if grep -q "_applyStep" js/app.js; then
    echo "FAIL: _applyStep still referenced in app.js"
    exit 1
else
    echo "PASS: No _applyStep references in app.js"
fi

# Check _applyStep is NOT in war_simulation.js
if grep -q "_applyStep" js/war_simulation.js; then
    echo "FAIL: _applyStep still referenced in war_simulation.js"
    exit 1
else
    echo "PASS: No _applyStep references in war_simulation.js"
fi

# Check wwii in index.html
if grep -q "wwii" index.html; then
    echo "PASS: wwii found in index.html"
else
    echo "FAIL: wwii not found in index.html"
    exit 1
fi

# Check vietnam_war in index.html
if grep -q "vietnam_war" index.html; then
    echo "PASS: vietnam_war found in index.html"
else
    echo "FAIL: vietnam_war not found in index.html"
    exit 1
fi

# Check korean_war in index.html
if grep -q "korean_war" index.html; then
    echo "PASS: korean_war found in index.html"
else
    echo "FAIL: korean_war not found in index.html"
    exit 1
fi

# Check presets.js exists and has all 7 presets
for preset in gulf_war_1991 vietnam_war wwi franco_prussian korean_war iran_iraq wwii; do
    if grep -q "\"$preset\"" js/presets.js; then
        echo "PASS: Preset '$preset' found in presets.js"
    else
        echo "FAIL: Preset '$preset' not found in presets.js"
        exit 1
    fi
done

# Check historical_events.js has all 7 presets
for preset in gulf_war_1991 vietnam_war wwi franco_prussian korean_war iran_iraq wwii; do
    if grep -q "\"$preset\"" js/historical_events.js; then
        echo "PASS: Historical events '$preset' found in historical_events.js"
    else
        echo "FAIL: Historical events '$preset' not found in historical_events.js"
        exit 1
    fi
done

# Check mechanism_classifier.js exists
if [ -f js/mechanism_classifier.js ]; then
    echo "PASS: mechanism_classifier.js exists"
else
    echo "FAIL: mechanism_classifier.js not found"
    exit 1
fi

# Check no fetch() for presets in app.js
if grep -q "fetch.*presets.json" js/app.js; then
    echo "FAIL: fetch('data/presets.json') still in app.js"
    exit 1
else
    echo "PASS: No fetch() for presets in app.js"
fi

# Check HISTORICAL_EVENTS not hardcoded in war_simulation.js
if grep -q "HISTORICAL_EVENTS = {" js/war_simulation.js; then
    echo "FAIL: HISTORICAL_EVENTS still hardcoded in war_simulation.js"
    exit 1
else
    echo "PASS: HISTORICAL_EVENTS removed from war_simulation.js"
fi

# Check v2 classifier in renderOutcome
if grep -q "classifyMechanism" js/app.js; then
    echo "PASS: classifyMechanism used in app.js"
else
    echo "FAIL: classifyMechanism not used in app.js"
    exit 1
fi

# Check full-state toggle in index.html
if grep -q "full-state-toggle" index.html; then
    echo "PASS: full-state-toggle found in index.html"
else
    echo "FAIL: full-state-toggle not found in index.html"
    exit 1
fi

# Check footer version
if grep -q "v2.0" index.html; then
    echo "PASS: Footer shows v2.0"
else
    echo "FAIL: Footer does not show v2.0"
    exit 1
fi

echo ""
echo "=== All static checks passed ==="

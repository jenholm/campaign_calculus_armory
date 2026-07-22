#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Running All Web Tests ==="
echo ""

FAILED=0

echo "--- 1. Simulation Smoke Tests ---"
if node tests/simulation_smoke.mjs; then
    echo ""
else
    echo "SMOKE TESTS FAILED"
    FAILED=1
fi

echo "--- 2. Historical Outcome Checks ---"
if node tests/historical_outcome_check.mjs; then
    echo ""
else
    echo "HISTORICAL OUTCOME CHECKS FAILED"
    FAILED=1
fi

echo "--- 3. UI Config Equivalence Check ---"
if node tests/ui_config_equivalence_check.mjs; then
    echo ""
else
    echo "UI CONFIG EQUIVALENCE CHECK FAILED"
    FAILED=1
fi

echo "--- 4. Static Checks ---"
if bash tests/static_check.sh; then
    echo ""
else
    echo "STATIC CHECKS FAILED"
    FAILED=1
fi

echo "=== All Web Tests Complete ==="
if [ $FAILED -eq 0 ]; then
    echo "ALL TEST SUITES PASSED"
else
    echo "SOME TEST SUITES FAILED"
    exit 1
fi

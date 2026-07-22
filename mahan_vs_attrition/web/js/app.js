/**
 * UI Controller for War Dynamics Simulator
 */

(function () {
    'use strict';

    let presets = {};
    let trajectoryChart = null;
    let mechanismChart = null;
    let simulator = null;
    let animationId = null;
    let historyMode = false;
    let activePresetKey = null;
    let selectedEventIndex = -1;

    const COLORS = {
        militaryA: '#2196F3',
        militaryADark: '#1976D2',
        politicalA: '#03A9F4',
        economicA: '#00BCD4',
        militaryB: '#F44336',
        militaryBDark: '#D32F2F',
        politicalB: '#E91E63',
        economicB: '#FF5722',
        dssA: '#FF9800',
        dssB: '#FFC107',
        sesA: '#9C27B0',
        sesB: '#CE93D8'
    };

    const PRESET_KEY_MAP = {
        'gulf_war_1991': 'gulf_war_1991',
        'vietnam_war': 'vietnam_war',
        'wwi': 'wwi',
        'franco_prussian': 'franco_prussian',
        'korean_war': 'korean_war',
        'iran_iraq': 'iran_iraq',
        'wwii': 'wwii'
    };

    let fullStateMode = false;
    let animationPaused = false;

    function getAnimSpeed() {
        const checked = document.querySelector('input[name="anim-speed"]:checked');
        return checked ? parseInt(checked.value) : 250;
    }

    function init() {
        trajectoryChart = new TimelineChart('trajectory-chart', {
            xLabel: 'Months',
            yLabel: 'Strength'
        });

        mechanismChart = new TimelineChart('mechanism-chart', {
            xLabel: 'Months',
            yLabel: 'Score',
            thresholdLines: [
                { value: 45, label: 'Low', color: '#BDBDBD' },
                { value: 65, label: 'Med', color: '#9E9E9E' },
                { value: 80, label: 'High', color: '#757575' }
            ]
        });

        loadPresets();
        bindEvents();
        setStatus('Ready');
    }

    function setStatus(msg) {
        var el = document.getElementById('app-status');
        if (el) el.textContent = msg;
    }

    function loadPresets() {
        if (window.WAR_PRESETS) {
            presets = window.WAR_PRESETS;
        } else {
            console.warn('WAR_PRESETS not found. Using fallback.');
            presets = {};
            setStatus('Preset loading failed. Custom simulation still available.');
        }
    }

    function bindEvents() {
        document.querySelectorAll('.preset-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                const key = this.dataset.preset;
                if (presets[key]) {
                    applyPreset(presets[key]);
                    activePresetKey = key;
                    document.querySelectorAll('.preset-btn').forEach(function (b) {
                        b.classList.remove('active');
                    });
                    this.classList.add('active');
                    updateHistorySidebar();
                }
            });
        });

        document.querySelectorAll('.control-panel input[type="range"], .control-panel select').forEach(function (el) {
            if (el.type === 'range') {
                el.addEventListener('input', function () {
                    const valSpan = document.getElementById(this.id + '-val');
                    if (valSpan) valSpan.textContent = this.value;
                });
            }
        });

        document.getElementById('run-btn').addEventListener('click', function () {
            runSimulation();
        });

        document.getElementById('animate-btn').addEventListener('click', function () {
            runAnimation();
        });

        document.getElementById('pause-btn').addEventListener('click', function () {
            pauseAnimation();
        });

        document.getElementById('reset-btn').addEventListener('click', function () {
            resetAnimation();
        });

        document.getElementById('export-btn').addEventListener('click', function () {
            exportResults();
        });

        document.getElementById('history-mode-toggle').addEventListener('change', function () {
            historyMode = this.checked;
            document.querySelector('.app-container').classList.toggle('history-active', historyMode);
            updateHistorySidebar();
            if (simulator) renderCharts();
        });

        document.getElementById('full-state-toggle').addEventListener('change', function () {
            fullStateMode = this.checked;
            if (simulator) renderCharts();
        });
    }

    function applyPreset(p) {
        document.getElementById('war-type').value = p.war_type || p.type || 'total_war';
        document.getElementById('side-a-name').value = p.side_a || 'Side A';
        document.getElementById('side-b-name').value = p.side_b || 'Side B';

        setSlider('shock-strength', p.shock_strength);
        setSlider('attrition-rate', p.attrition_rate);
        setSlider('economic-resilience', p.economic_resilience);
        setSlider('political-resilience', p.political_resilience);
    }

    function setSlider(id, val) {
        const slider = document.getElementById(id);
        if (slider) {
            slider.value = val;
            const valSpan = document.getElementById(id + '-val');
            if (valSpan) valSpan.textContent = val;
        }
    }

    function getConfig() {
        var presetKey = document.querySelector('.preset-btn.active');
        var presetName = presetKey ? presetKey.dataset.preset : null;
        var preset = presetName ? presets[presetName] : null;

        var controls = {
            war_type: document.getElementById('war-type').value,
            side_a: document.getElementById('side-a-name').value || 'Side A',
            side_b: document.getElementById('side-b-name').value || 'Side B',
            shock_strength: parseInt(document.getElementById('shock-strength').value),
            attrition_rate: parseInt(document.getElementById('attrition-rate').value),
            economic_resilience: parseInt(document.getElementById('economic-resilience').value),
            political_resilience: parseInt(document.getElementById('political-resilience').value)
        };

        return window.buildSimulationConfig(preset, controls);
    }

    function runSimulation() {
        if (animationId) {
            clearTimeout(animationId);
            animationId = null;
        }
        animationPaused = false;
        document.getElementById('pause-btn').disabled = true;
        document.getElementById('pause-btn').textContent = 'Pause';

        const config = getConfig();
        simulator = new WarSimulator(config);
        const outcome = simulator.simulate(120, 42);

        selectedEventIndex = -1;
        renderCharts();
        renderOutcome(outcome);
        updateConfidencePanel(config, outcome);
        updateHistorySidebar();
        renderMechanismBreakdown();
    }

    function finishAnimation(config, maxMonths) {
        if (!simulator.outcome) {
            simulator.outcome = simulator._buildOutcome(
                { winner: 'draw', reason: 'time_limit' },
                simulator.dss_history.a[simulator.dss_history.a.length - 1] || 0,
                simulator.dss_history.b[simulator.dss_history.b.length - 1] || 0,
                simulator.ses_history.a[simulator.ses_history.a.length - 1] || 0,
                simulator.ses_history.b[simulator.ses_history.b.length - 1] || 0,
                simulator.month
            );
        }

        renderOutcome(simulator.outcome);
        updateConfidencePanel(config, simulator.outcome);
        updateHistorySidebar();
        renderMechanismBreakdown();
        document.getElementById('run-btn').disabled = false;
        document.getElementById('animate-btn').disabled = false;
        document.getElementById('pause-btn').disabled = true;
    }

    function runAnimation() {
        if (animationId) {
            clearTimeout(animationId);
            animationId = null;
        }

        animationPaused = false;
        document.getElementById('pause-btn').disabled = false;
        document.getElementById('pause-btn').textContent = 'Pause';
        document.getElementById('run-btn').disabled = true;
        document.getElementById('animate-btn').disabled = true;

        const config = getConfig();
        simulator = new WarSimulator(config);
        simulator.reset(42);

        selectedEventIndex = -1;
        renderCharts();
        renderOutcome(null);

        const maxMonths = 120;

        function step() {
            if (!simulator || simulator.terminated || simulator.month >= maxMonths) {
                animationId = null;
                finishAnimation(config, maxMonths);
                return;
            }

            if (animationPaused) return;

            simulator.stepOneMonth();
            renderCharts();

            animationId = setTimeout(step, getAnimSpeed());
        }

        animationId = setTimeout(step, getAnimSpeed());
    }

    function pauseAnimation() {
        if (!animationId) return;
        animationPaused = !animationPaused;
        const btn = document.getElementById('pause-btn');
        if (animationPaused) {
            clearTimeout(animationId);
            animationId = null;
            btn.textContent = 'Resume';
        } else {
            const maxMonths = 120;
            const config = getConfig();
            const step = function () {
                if (!simulator || simulator.terminated || simulator.month >= maxMonths) {
                    animationId = null;
                    finishAnimation(config, maxMonths);
                    return;
                }
                if (animationPaused) return;
                simulator.stepOneMonth();
                renderCharts();
                animationId = setTimeout(step, getAnimSpeed());
            };
            animationId = setTimeout(step, getAnimSpeed());
            btn.textContent = 'Pause';
        }
    }

    function resetAnimation() {
        if (animationId) {
            clearTimeout(animationId);
            animationId = null;
        }
        animationPaused = false;
        document.getElementById('pause-btn').disabled = true;
        document.getElementById('pause-btn').textContent = 'Pause';
        document.getElementById('run-btn').disabled = false;
        document.getElementById('animate-btn').disabled = false;
        simulator = null;
        trajectoryChart.setData([], []);
        mechanismChart.setData([], []);
        buildLegend('trajectory-legend', []);
        buildLegend('mechanism-legend', []);
        renderOutcome(null);
        document.getElementById('mechanism-breakdown').style.display = 'none';
        document.getElementById('confidencePanel').style.display = 'none';
    }

    function renderCharts() {
        if (!simulator || simulator.history.length === 0) return;

        const months = simulator.history.map(function (h) { return h.month; });

        var trajectorySeries = [
            { name: (simulator.config.side_a || 'A') + ' Military', data: simulator.history.map(function (h) { return h.military_a; }), color: COLORS.militaryA, width: 2.5 },
            { name: (simulator.config.side_a || 'A') + ' Political Will', data: simulator.history.map(function (h) { return h.political_will_a; }), color: COLORS.politicalA, width: 1.5 },
            { name: (simulator.config.side_a || 'A') + ' Economic', data: simulator.history.map(function (h) { return h.economic_a; }), color: COLORS.economicA, width: 1.5 },
            { name: (simulator.config.side_b || 'B') + ' Military', data: simulator.history.map(function (h) { return h.military_b; }), color: COLORS.militaryB, width: 2.5 },
            { name: (simulator.config.side_b || 'B') + ' Political Will', data: simulator.history.map(function (h) { return h.political_will_b; }), color: COLORS.politicalB, width: 1.5 },
            { name: (simulator.config.side_b || 'B') + ' Economic', data: simulator.history.map(function (h) { return h.economic_b; }), color: COLORS.economicB, width: 1.5 }
        ];

        if (fullStateMode) {
            trajectorySeries.push(
                { name: (simulator.config.side_a || 'A') + ' Population', data: simulator.history.map(function (h) { return h.population_support_a; }), color: '#795548', width: 1.5, dash: [4, 2] },
                { name: (simulator.config.side_b || 'B') + ' Population', data: simulator.history.map(function (h) { return h.population_support_b; }), color: '#8D6E63', width: 1.5, dash: [4, 2] },
                { name: (simulator.config.side_a || 'A') + ' Industrial', data: simulator.history.map(function (h) { return h.industrial_a; }), color: '#607D8B', width: 1.5, dash: [2, 2] },
                { name: (simulator.config.side_b || 'B') + ' Industrial', data: simulator.history.map(function (h) { return h.industrial_b; }), color: '#90A4AE', width: 1.5, dash: [2, 2] }
            );
        }

        trajectoryChart.setData(months, trajectorySeries);

        var events = window.HISTORICAL_EVENTS || {};

        if (historyMode && activePresetKey && events[activePresetKey]) {
            trajectoryChart.setEventMarkers(events[activePresetKey]);
            var maxEventMonth = 0;
            for (var ei = 0; ei < events[activePresetKey].length; ei++) {
                if (events[activePresetKey][ei].month > maxEventMonth) {
                    maxEventMonth = events[activePresetKey][ei].month;
                }
            }
            var xMax = Math.max(months.length > 0 ? months[months.length - 1] : 0, maxEventMonth) + 5;
            trajectoryChart.setXMax(xMax);
            mechanismChart.setXMax(xMax);
        } else {
            trajectoryChart.setEventMarkers([]);
            trajectoryChart.setXMax(null);
            mechanismChart.setXMax(null);
        }

        trajectoryChart.setSelectedEventMonth(
            (historyMode && selectedEventIndex >= 0 && events[activePresetKey])
                ? events[activePresetKey][selectedEventIndex].month
                : null
        );

        var legendItems = [
            { name: (simulator.config.side_a || 'A') + ' Military', color: COLORS.militaryA },
            { name: (simulator.config.side_a || 'A') + ' Political', color: COLORS.politicalA },
            { name: (simulator.config.side_a || 'A') + ' Economic', color: COLORS.economicA },
            { name: (simulator.config.side_b || 'B') + ' Military', color: COLORS.militaryB },
            { name: (simulator.config.side_b || 'B') + ' Political', color: COLORS.politicalB },
            { name: (simulator.config.side_b || 'B') + ' Economic', color: COLORS.economicB }
        ];

        if (fullStateMode) {
            legendItems.push(
                { name: (simulator.config.side_a || 'A') + ' Population', color: '#795548' },
                { name: (simulator.config.side_b || 'B') + ' Population', color: '#8D6E63' },
                { name: (simulator.config.side_a || 'A') + ' Industrial', color: '#607D8B' },
                { name: (simulator.config.side_b || 'B') + ' Industrial', color: '#90A4AE' }
            );
        }

        buildLegend('trajectory-legend', legendItems);

        const mechMonths = months.slice(1);

        mechanismChart.setData(mechMonths, [
            { name: 'DSS ' + (simulator.config.side_a || 'A'), data: simulator.dss_history.a, color: COLORS.dssA, width: 2.5 },
            { name: 'DSS ' + (simulator.config.side_b || 'B'), data: simulator.dss_history.b, color: COLORS.dssB, width: 2 },
            { name: 'SES ' + (simulator.config.side_a || 'A'), data: simulator.ses_history.a, color: COLORS.sesA, width: 2.5 },
            { name: 'SES ' + (simulator.config.side_b || 'B'), data: simulator.ses_history.b, color: COLORS.sesB, width: 2 }
        ]);

        if (historyMode && activePresetKey && events[activePresetKey]) {
            mechanismChart.setEventMarkers(events[activePresetKey]);
        } else {
            mechanismChart.setEventMarkers([]);
        }

        mechanismChart.setSelectedEventMonth(
            (historyMode && selectedEventIndex >= 0 && events[activePresetKey])
                ? events[activePresetKey][selectedEventIndex].month
                : null
        );

        buildLegend('mechanism-legend', [
            { name: 'DSS ' + (simulator.config.side_a || 'A'), color: COLORS.dssA },
            { name: 'DSS ' + (simulator.config.side_b || 'B'), color: COLORS.dssB },
            { name: 'SES ' + (simulator.config.side_a || 'A'), color: COLORS.sesA },
            { name: 'SES ' + (simulator.config.side_b || 'B'), color: COLORS.sesB }
        ]);
    }

    function normalizeWinnerKey(key) {
        if (key === 'side_a') return 'a';
        if (key === 'side_b') return 'b';
        return key;
    }

    function renderModelStats(outcome, mechanism) {
        var secondaryText = mechanism.secondary_mechanism ? mechanism.secondary_mechanism : 'none';
        return '' +
            '<div class="stat-item"><div class="stat-label">Termination Event</div><div class="stat-value">' + mechanism.termination_event + '</div></div>' +
            '<div class="stat-item"><div class="stat-label">Dominant Mechanism</div><div class="stat-value">' + mechanism.dominant_mechanism + '</div></div>' +
            '<div class="stat-item"><div class="stat-label">Secondary Mechanism</div><div class="stat-value">' + secondaryText + '</div></div>' +
            '<div class="stat-item"><div class="stat-label">Confidence</div><div class="stat-value">' + Math.round(mechanism.confidence * 100) + '%</div></div>' +
            '<div class="stat-item"><div class="stat-label">Duration</div><div class="stat-value">' + outcome.duration + ' months</div></div>' +
            '<div class="stat-item"><div class="stat-label">Winner</div><div class="stat-value">' + outcome.winner + '</div></div>' +
            '<div class="stat-item"><div class="stat-label">Decisive Shock Score</div><div class="stat-value">' + mechanism.decisive_shock_score.toFixed(1) + '</div></div>' +
            '<div class="stat-item"><div class="stat-label">Strategic Exhaustion Score</div><div class="stat-value">' + mechanism.strategic_exhaustion_score.toFixed(1) + '</div></div>' +
            '<div class="stat-item"><div class="stat-label">Final DSS (' + (simulator.config.side_a || 'A') + ')</div><div class="stat-value">' + outcome.final_dss_a.toFixed(1) + '</div></div>' +
            '<div class="stat-item"><div class="stat-label">Final SES (' + (simulator.config.side_a || 'A') + ')</div><div class="stat-value">' + outcome.final_ses_a.toFixed(1) + '</div></div>' +
            '<div class="stat-item"><div class="stat-label">Turning Point</div><div class="stat-value">Month ' + outcome.turning_point + '</div></div>' +
            '<div class="stat-item"><div class="stat-label">Cause</div><div class="stat-value">' + outcome.reason.replace(/_/g, ' ') + '</div></div>';
    }

    function renderOutcome(outcome) {
        const textEl = document.getElementById('outcome-text');
        const statsEl = document.getElementById('outcome-stats');

        if (!outcome) {
            textEl.textContent = 'Awaiting simulation...';
            statsEl.innerHTML = '';
            return;
        }

        const presetKey = activePresetKey;
        const presetConfig = presetKey ? presets[presetKey] : null;
        const mechanism = classifyMechanism(simulator, presetConfig);

        textEl.innerHTML =
            '<strong>Dominant mechanism:</strong> ' + mechanism.dominant_mechanism +
            ' (' + Math.round(mechanism.confidence * 100) + '% confidence)';

        var modelStatsHtml = renderModelStats(outcome, mechanism);

        var expectedResults = window.EXPECTED_HISTORICAL_RESULTS || {};
        var html = '';
        if (presetKey && expectedResults[presetKey]) {
            var exp = expectedResults[presetKey];
            var modelWinnerKey = normalizeWinnerKey(outcome.winner_key || (outcome.winner === 'Draw' ? 'draw' : null));
            var expectedNormKey = normalizeWinnerKey(exp.expected_winner_key);
            var winnerMatch = (modelWinnerKey === expectedNormKey);

            var lo = exp.expected_duration_months - exp.duration_tolerance_months;
            var hi = exp.expected_duration_months + exp.duration_tolerance_months;
            var durationMatch = outcome.duration >= lo && outcome.duration <= hi;

            var matchClass = (winnerMatch && durationMatch) ? 'match' : (winnerMatch ? 'partial-match' : 'mismatch');
            var matchLabel = (winnerMatch && durationMatch) ? 'Model matches history' :
                winnerMatch ? 'Winner matches, duration differs' : 'Model differs from history';

            var histWinnerLabel = (expectedNormKey === 'draw') ? 'Draw' :
                (expectedNormKey === 'a' ? (presetConfig ? presetConfig.side_a : 'Side A') : (presetConfig ? presetConfig.side_b : 'Side B'));

            html =
                '<div class="historical-comparison ' + matchClass + '">' +
                    '<div class="comparison-header">' + matchLabel + '</div>' +
                    '<div class="comparison-row"><span class="comp-label">Historical winner:</span><span>' + histWinnerLabel + '</span></div>' +
                    '<div class="comparison-row"><span class="comp-label">Model winner:</span><span>' + outcome.winner + (winnerMatch ? ' ✓' : ' ✗') + '</span></div>' +
                    '<div class="comparison-row"><span class="comp-label">Historical duration:</span><span>' + exp.expected_duration_months + ' months (±' + exp.duration_tolerance_months + ')</span></div>' +
                    '<div class="comparison-row"><span class="comp-label">Model duration:</span><span>' + outcome.duration + ' months' + (durationMatch ? ' ✓' : ' ✗') + '</span></div>' +
                '</div>' +
                '<hr class="comparison-divider">';
        }

        statsEl.innerHTML = html + modelStatsHtml;
    }

    function updateHistorySidebar() {
        const container = document.getElementById('history-events-container');
        const detailEl = document.getElementById('event-detail');
        container.innerHTML = '';

        var events = window.HISTORICAL_EVENTS || {};

        if (!historyMode || !activePresetKey || !events[activePresetKey]) {
            container.innerHTML = '<div class="no-history-msg">Select a preset and run a simulation to see historical events.</div>';
            detailEl.classList.remove('visible');
            selectedEventIndex = -1;
            return;
        }

        const evList = events[activePresetKey];
        const list = document.createElement('ul');
        list.className = 'event-list';

        evList.forEach(function (ev, idx) {
            const li = document.createElement('li');
            li.className = 'event-item';
            if (idx === selectedEventIndex) li.classList.add('active');
            li.dataset.type = ev.type;
            li.dataset.index = idx;

            const monthSpan = document.createElement('span');
            monthSpan.className = 'event-month';
            monthSpan.textContent = 'Month ' + ev.month;

            const badge = document.createElement('span');
            badge.className = 'event-type-badge ' + ev.type;
            badge.textContent = ev.type;

            const labelSpan = document.createElement('span');
            labelSpan.className = 'event-label';
            labelSpan.textContent = ev.label;

            li.appendChild(monthSpan);
            li.appendChild(badge);
            li.appendChild(labelSpan);

            li.addEventListener('click', function () {
                selectEvent(parseInt(this.dataset.index));
            });

            list.appendChild(li);
        });

        container.appendChild(list);

        if (selectedEventIndex >= 0) {
            showEventDetail(evList[selectedEventIndex]);
        } else {
            detailEl.classList.remove('visible');
        }
    }

    function selectEvent(index) {
        selectedEventIndex = index;
        updateHistorySidebar();
        renderCharts();
    }

    function showEventDetail(ev) {
        const detailEl = document.getElementById('event-detail');
        const titleEl = document.getElementById('event-detail-title');
        const bodyEl = document.getElementById('event-detail-body');

        titleEl.textContent = ev.label;

        if (!simulator || simulator.history.length === 0) {
            bodyEl.innerHTML = '<p style="color:#999">Run a simulation to see model state at this month.</p>';
            detailEl.classList.add('visible');
            return;
        }

        const monthIdx = Math.min(Math.round(ev.month), simulator.history.length - 1);
        const state = simulator.history[monthIdx];

        const dssIdx = Math.max(0, monthIdx - 1);
        const dssA = simulator.dss_history.a[dssIdx] !== undefined ? simulator.dss_history.a[dssIdx].toFixed(1) : 'N/A';
        const dssB = simulator.dss_history.b[dssIdx] !== undefined ? simulator.dss_history.b[dssIdx].toFixed(1) : 'N/A';
        const sesA = simulator.ses_history.a[dssIdx] !== undefined ? simulator.ses_history.a[dssIdx].toFixed(1) : 'N/A';
        const sesB = simulator.ses_history.b[dssIdx] !== undefined ? simulator.ses_history.b[dssIdx].toFixed(1) : 'N/A';

        var html =
            '<div class="model-state">' +
                '<span class="label">' + (simulator.config.side_a || 'A') + ' Military:</span><span>' + state.military_a.toFixed(1) + '</span>' +
                '<span class="label">' + (simulator.config.side_b || 'B') + ' Military:</span><span>' + state.military_b.toFixed(1) + '</span>' +
                '<span class="label">' + (simulator.config.side_a || 'A') + ' Political:</span><span>' + state.political_will_a.toFixed(1) + '</span>' +
                '<span class="label">' + (simulator.config.side_b || 'B') + ' Political:</span><span>' + state.political_will_b.toFixed(1) + '</span>' +
                '<span class="label">' + (simulator.config.side_a || 'A') + ' Economic:</span><span>' + state.economic_a.toFixed(1) + '</span>' +
                '<span class="label">' + (simulator.config.side_b || 'B') + ' Economic:</span><span>' + state.economic_b.toFixed(1) + '</span>';

        if (fullStateMode) {
            html +=
                '<span class="label">' + (simulator.config.side_a || 'A') + ' Population:</span><span>' + state.population_support_a.toFixed(1) + '</span>' +
                '<span class="label">' + (simulator.config.side_b || 'B') + ' Population:</span><span>' + state.population_support_b.toFixed(1) + '</span>' +
                '<span class="label">' + (simulator.config.side_a || 'A') + ' Industrial:</span><span>' + state.industrial_a.toFixed(1) + '</span>' +
                '<span class="label">' + (simulator.config.side_b || 'B') + ' Industrial:</span><span>' + state.industrial_b.toFixed(1) + '</span>';
        }

        html +=
                '<span class="label">DSS (' + (simulator.config.side_a || 'A') + '):</span><span>' + dssA + '</span>' +
                '<span class="label">SES (' + (simulator.config.side_a || 'A') + '):</span><span>' + sesA + '</span>' +
                '<span class="label">DSS (' + (simulator.config.side_b || 'B') + '):</span><span>' + dssB + '</span>' +
                '<span class="label">SES (' + (simulator.config.side_b || 'B') + '):</span><span>' + sesB + '</span>' +
            '</div>';

        bodyEl.innerHTML = html;

        detailEl.classList.add('visible');
    }

    function computeConfidence(config, result) {
        let score = 50;

        const shock = config.shock_strength || 50;
        const attrition = config.attrition_rate || 50;
        const extremity = Math.abs(shock - 50) + Math.abs(attrition - 50);
        score += extremity * 0.3;

        const dss = result.final_dss_a || 0;
        const ses = result.final_ses_a || 0;
        const separation = Math.abs(dss - ses);
        score += separation * 0.2;

        const duration = result.duration || 120;
        if (duration < 12 || duration > 80) score += 10;

        score = Math.max(0, Math.min(100, score));

        let level, text;
        if (score >= 70) {
            level = "high";
            text = "Mechanism robust: parameter changes unlikely to flip classification.";
        } else if (score >= 40) {
            level = "medium";
            text = "Multiple pathways possible: outcome depends on parameter balance.";
        } else {
            level = "low";
            text = "Outcome depends on assumptions: small changes may alter classification.";
        }

        return { score: score, level: level, text: text };
    }

    function updateConfidencePanel(config, result) {
        const panel = document.getElementById('confidencePanel');
        if (!panel) return;

        const conf = computeConfidence(config, result);

        const levelEl = document.getElementById('confidenceLevel');
        const fillEl = document.getElementById('confidenceFill');
        const textEl = document.getElementById('confidenceText');

        if (levelEl) {
            levelEl.textContent = conf.level.charAt(0).toUpperCase() + conf.level.slice(1);
            levelEl.className = 'confidence-level ' + conf.level;
        }
        if (fillEl) {
            fillEl.className = 'confidence-fill ' + conf.level;
        }
        if (textEl) {
            textEl.textContent = conf.text;
        }

        panel.style.display = 'block';
    }

    function renderMechanismBreakdown() {
        const breakdownEl = document.getElementById('mechanism-breakdown');
        if (!historyMode || !simulator || !simulator.outcome) {
            breakdownEl.style.display = 'none';
            return;
        }

        const bd = computeMechanismBreakdown({
            ses_a: simulator.ses_history.a,
            dss_a: simulator.dss_history.a
        });

        const exhaustPct = Math.round(bd.exhaustion * 100);
        const shockPct = Math.round(bd.shock * 100);
        const mixedPct = Math.round(bd.mixed * 100);

        document.getElementById('mech-bar-exhaustion').style.width = exhaustPct + '%';
        document.getElementById('mech-bar-exhaustion').textContent = exhaustPct > 8 ? exhaustPct + '%' : '';
        document.getElementById('mech-bar-shock').style.width = shockPct + '%';
        document.getElementById('mech-bar-shock').textContent = shockPct > 8 ? shockPct + '%' : '';
        document.getElementById('mech-bar-mixed').style.width = mixedPct + '%';
        document.getElementById('mech-bar-mixed').textContent = mixedPct > 8 ? mixedPct + '%' : '';

        document.getElementById('mechanism-labels').innerHTML =
            '<span class="pct lbl-exhaustion">' + exhaustPct + '%</span> exhaustion driven · ' +
            '<span class="pct lbl-shock">' + shockPct + '%</span> decisive shock';

        breakdownEl.style.display = 'block';
    }

    function exportResults() {
        if (!simulator) {
            alert('Run a simulation first.');
            return;
        }
        const json = simulator.exportJSON();
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'simulation_results.json';
        a.click();
        URL.revokeObjectURL(url);
    }

    document.addEventListener('DOMContentLoaded', init);
})();

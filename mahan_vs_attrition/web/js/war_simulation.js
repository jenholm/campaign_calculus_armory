/**
 * War Dynamics Simulator Engine
 * Ported from Python WarSimulator (src/mahan_vs_attrition/simulation/war_dynamics.py)
 * Tests Mahan (decisive shock) vs Attrition (strategic exhaustion) hypotheses
 */

function computeMechanismBreakdown(result) {
    let exhaustionMonths = 0;
    let shockMonths = 0;
    let mixedMonths = 0;

    const len = Math.min(result.ses_a.length, result.dss_a.length);
    for (let i = 0; i < len; i++) {
        const ses = result.ses_a[i];
        const dss = result.dss_a[i];
        if (ses > dss * 1.5) exhaustionMonths++;
        else if (dss > ses * 1.5) shockMonths++;
        else mixedMonths++;
    }

    const total = exhaustionMonths + shockMonths + mixedMonths || 1;
    return {
        exhaustion: exhaustionMonths / total,
        shock: shockMonths / total,
        mixed: mixedMonths / total,
    };
}

class WarSimulator {
    constructor(config) {
        this.config = Object.assign({
            initial_military_a: 80,
            initial_military_b: 80,
            initial_economic_a: 80,
            initial_economic_b: 80,
            initial_political_will_a: 80,
            initial_political_will_b: 80,
            initial_population_support_a: 80,
            initial_population_support_b: 80,
            initial_industrial_a: 80,
            initial_industrial_b: 80,
            shock_strength: 60,
            attrition_rate: 60,
            economic_resilience: 60,
            political_resilience: 60,
            shock_strength_a: null,
            shock_strength_b: null,
            attrition_rate_a: null,
            attrition_rate_b: null,
            economic_resilience_a: null,
            economic_resilience_b: null,
            political_resilience_a: null,
            political_resilience_b: null,
            allow_negotiated_settlement: true,
            earliest_settlement_month: 0,
            settlement_military_threshold: 50,
            settlement_exhaustion_threshold: 80,
            external_support_a: 0,
            external_support_b: 0,
            recruitment_capacity_a: 1.0,
            recruitment_capacity_b: 1.0,
            war_type: 'total_war',
            side_a: 'Side A',
            side_b: 'Side B'
        }, config);

        // Resolve per-side nulls to shared values
        if (this.config.shock_strength_a === null) this.config.shock_strength_a = this.config.shock_strength;
        if (this.config.shock_strength_b === null) this.config.shock_strength_b = this.config.shock_strength;
        if (this.config.attrition_rate_a === null) this.config.attrition_rate_a = this.config.attrition_rate;
        if (this.config.attrition_rate_b === null) this.config.attrition_rate_b = this.config.attrition_rate;
        if (this.config.economic_resilience_a === null) this.config.economic_resilience_a = this.config.economic_resilience;
        if (this.config.economic_resilience_b === null) this.config.economic_resilience_b = this.config.economic_resilience;
        if (this.config.political_resilience_a === null) this.config.political_resilience_a = this.config.political_resilience;
        if (this.config.political_resilience_b === null) this.config.political_resilience_b = this.config.political_resilience;

        this.state = {
            military_a: this.config.initial_military_a,
            military_b: this.config.initial_military_b,
            economic_a: this.config.initial_economic_a,
            economic_b: this.config.initial_economic_b,
            political_will_a: this.config.initial_political_will_a,
            political_will_b: this.config.initial_political_will_b,
            population_support_a: this.config.initial_population_support_a,
            population_support_b: this.config.initial_population_support_b,
            industrial_a: this.config.initial_industrial_a,
            industrial_b: this.config.initial_industrial_b
        };

        this.history = [];
        this.dss_history = { a: [], b: [] };
        this.ses_history = { a: [], b: [] };
        this.month = 0;
        this.terminated = false;
        this.outcome = null;
    }

    /**
     * Seeded PRNG (Mulberry32)
     */
    static createPRNG(seed) {
        let s = seed | 0;
        return function () {
            s = (s + 0x6D2B79F5) | 0;
            let t = Math.imul(s ^ (s >>> 15), 1 | s);
            t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
            return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
    }

    /**
     * Clamp value between 0 and 100
     */
    static clamp(val) {
        return Math.max(0, Math.min(100, val));
    }

    /**
     * Shock interval by war type (matching Python war_dynamics.py)
     */
    _getShockInterval() {
        if (this.config.war_type === 'total_war') return 6;
        if (this.config.war_type === 'coalition' || this.config.war_type === 'coalition_war') return 7;
        if (this.config.war_type === 'limited_war') return 3;
        return 5;
    }

    /**
     * Apply attrition dynamics — per-side attrition_rate and resilience
     */
    _applyAttrition(month) {
        const fatigue = 1.0 + month / 60.0;

        for (const suffix of ['a', 'b']) {
            const milKey = `military_${suffix}`;
            const econKey = `economic_${suffix}`;
            const popKey = `population_support_${suffix}`;
            const polKey = `political_will_${suffix}`;
            const indKey = `industrial_${suffix}`;

            const base = this.config[`attrition_rate_${suffix}`] / 100.0;
            const resilience = this.config[`economic_resilience_${suffix}`];
            const polResilience = this.config[`political_resilience_${suffix}`];
            const resist = 1.0 - resilience / 200.0;

            // Military
            const battleLosses = this.state[milKey] * base * 0.04 * resist * fatigue;
            const recruitmentCapacity = this.config[`recruitment_capacity_${suffix}`] ?? 1.0;
            const externalSupport = this.config[`external_support_${suffix}`] ?? 0;
            const recruitment = Math.min(1.5 * recruitmentCapacity, this.state[indKey] * 0.004 * recruitmentCapacity)
                + externalSupport * 0.01;
            this.state[milKey] = this.state[milKey] - battleLosses + recruitment;

            // Economic
            const warCosts = this.state[econKey] * base * 0.025 * fatigue;
            const blockade = this.state[econKey] * base * 0.01 * resist;
            const industrialOutput = this.state[indKey] * 0.006;
            const econSupport = externalSupport * 0.005;
            this.state[econKey] = this.state[econKey] - warCosts - blockade + industrialOutput + econSupport;

            // Political will
            const casualtyPressure = battleLosses * 0.2;
            const weariness = base * 0.4 * fatigue * (1.0 - polResilience / 200.0);
            const opponentKey = `military_${suffix === 'a' ? 'b' : 'a'}`;
            const isWinning = this.state[milKey] > this.state[opponentKey];
            const victoryBonus = (this.config.war_type === 'limited_war') ? (isWinning ? 0.15 : 0.0) : (isWinning ? 0.8 : 0.0);
            const politicalSupport = Math.min(5, externalSupport * 0.003);
            this.state[polKey] = this.state[polKey] - casualtyPressure - weariness + victoryBonus + politicalSupport;

            // Population support
            const econHardship = Math.max(0, (50 - this.state[econKey])) * base * 0.03 * fatigue;
            this.state[popKey] = this.state[popKey] - econHardship - casualtyPressure * 0.15;

            // Industrial
            const bombing = this.state[indKey] * base * 0.015 * resist * fatigue;
            const recon = this.state[econKey] * 0.004;
            this.state[indKey] = this.state[indKey] - bombing + recon;

            // Clamp all
            for (const key of [milKey, econKey, polKey, popKey, indKey]) {
                this.state[key] = WarSimulator.clamp(this.state[key]);
            }
        }
    }

    /**
     * Apply shock dynamics — symmetrical: each side inflicts shock proportional to own shock_strength
     */
    _applyShock(month) {
        const shockInterval = this._getShockInterval();
        if (month % shockInterval !== 0) return;

        const magA = this.config.shock_strength_a / 100.0;
        const magB = this.config.shock_strength_b / 100.0;

        // Side A inflicts shock on B
        const damageB = magA * 8.0;
        this.state.military_b -= damageB;
        this.state.industrial_b -= damageB * 0.3;
        this.state.political_will_b -= damageB * 0.25;

        // Side B inflicts shock on A
        const damageA = magB * 8.0;
        this.state.military_a -= damageA;
        this.state.industrial_a -= damageA * 0.25;
        this.state.political_will_a -= damageA * 0.2;

        // Clamp
        for (const key of ['military_a', 'military_b', 'industrial_a', 'industrial_b', 'political_will_a', 'political_will_b']) {
            this.state[key] = WarSimulator.clamp(this.state[key]);
        }
    }

    /**
     * Compute DSS from state history (matching Python _compute_dss)
     */
    _computeDSS(side) {
        const stateHistory = this.history;
        if (stateHistory.length < 1) return 0.0;

        const initialMil = stateHistory[0][`military_${side}`] || 50.0;
        const prevMil = stateHistory[stateHistory.length - 1][`military_${side}`] || initialMil;
        const currMil = this.state[`military_${side}`] || initialMil;

        const deltaMilitary = currMil - prevMil;
        const militaryShock = Math.max(0.0, -deltaMilitary) / Math.max(initialMil, 1.0);

        const polWill = this.state[`political_will_${side}`] || 50.0;
        const capitalBonus = currMil < initialMil * 0.3 ? 1.0 : 0.0;
        const surrenderBonus = polWill < 20 ? 1.0 : 0.0;

        const dss = Math.min(100.0, militaryShock * 50 + capitalBonus * 30 + surrenderBonus * 20);
        return Math.round(dss * 100) / 100;
    }

    /**
     * Compute SES from state history (matching Python _compute_ses)
     */
    _computeSES(side, month) {
        const stateHistory = this.history;
        if (stateHistory.length < 1) return 0.0;

        const init = stateHistory[0];
        const militaryInitial = init[`military_${side}`] || 50.0;
        const economicInitial = init[`economic_${side}`] || 50.0;
        const politicalWillInitial = init[`political_will_${side}`] || 50.0;

        const militaryCurrent = this.state[`military_${side}`] || militaryInitial;
        const economicCurrent = this.state[`economic_${side}`] || economicInitial;
        const politicalCurrent = this.state[`political_will_${side}`] || politicalWillInitial;

        const militaryExhaustion = 1.0 - (militaryCurrent / Math.max(militaryInitial, 1.0));
        const economicExhaustion = 1.0 - (economicCurrent / Math.max(economicInitial, 1.0));
        const politicalExhaustion = 1.0 - (politicalCurrent / Math.max(politicalWillInitial, 1.0));
        const durationFactor = Math.min(1.0, month / 60.0);

        // Weight political exhaustion by political resilience: higher resilience → less exhaustion from political losses
        const polResKey = `political_resilience_${side}`;
        const polRes = this.config[polResKey] || this.config.political_resilience || 50;
        const polWeight = 0.2 * (1.0 - polRes / 200.0);

        const ses = (
            militaryExhaustion * 0.3
            + economicExhaustion * 0.3
            + politicalExhaustion * polWeight
            + (1.0 - polWeight) * 0.1
            + durationFactor * 0.2
        ) * 100.0;
        return Math.round(WarSimulator.clamp(ses) * 100) / 100;
    }

    /**
     * Check termination conditions (matching Python _check_termination)
     */
    _checkTermination() {
        const milA = this.state.military_a;
        const milB = this.state.military_b;
        const polA = this.state.political_will_a;
        const polB = this.state.political_will_b;
        const popA = this.state.population_support_a;
        const popB = this.state.population_support_b;
        const econA = this.state.economic_a;
        const econB = this.state.economic_b;

        // Total collapse: political will AND population support collapse
        if (polA < 8 && popA < 12) return { terminated: true, winner: 'b', reason: 'collapse_a' };
        if (polB < 8 && popB < 12) return { terminated: true, winner: 'a', reason: 'collapse_b' };

        // Decisive dominance: absolute viability requirements prevent zombie wins
        const domMinWinnerMil = this.config.dominance_min_winner_military ?? 25;
        const domMinGap = this.config.dominance_min_gap ?? 20;
        if (milA >= domMinWinnerMil && milA - milB >= domMinGap && milA > milB * 2 && milB < 25 && polB < 25) return { terminated: true, winner: 'a', reason: 'dominance_a' };
        if (milB >= domMinWinnerMil && milB - milA >= domMinGap && milB > milA * 2 && milA < 25 && polA < 25) return { terminated: true, winner: 'b', reason: 'dominance_b' };

        // Attritional exhaustion (SES thresholds) — requires political weakness
        const sesA = this.ses_history.a.length > 0 ? this.ses_history.a[this.ses_history.a.length - 1] : 0;
        const sesB = this.ses_history.b.length > 0 ? this.ses_history.b[this.ses_history.b.length - 1] : 0;

        if (sesA > 85 && sesB > 85) return { terminated: true, winner: 'draw', reason: 'mutual_exhaustion' };
        if (sesA > 85 && polA < 20) return { terminated: true, winner: 'b', reason: 'exhaustion_a' };
        if (sesB > 85 && polB < 20) return { terminated: true, winner: 'a', reason: 'exhaustion_b' };

        // Combined economic + political collapse
        if (econA < 10 && polA < 15) return { terminated: true, winner: 'b', reason: 'exhaustion_a' };
        if (econB < 10 && polB < 15) return { terminated: true, winner: 'a', reason: 'exhaustion_b' };

        // Negotiated settlement: only after earliest_settlement_month and only if configured
        if (this.config.allow_negotiated_settlement && this.month >= this.config.earliest_settlement_month) {
            const milThreshold = this.config.settlement_military_threshold;
            const sesThreshold = this.config.settlement_exhaustion_threshold;
            if (milA < milThreshold && milB < milThreshold && sesA > sesThreshold && sesB > sesThreshold) {
                return { terminated: true, winner: 'draw', reason: 'negotiated_settlement' };
            }
        }

        // Coalition war: draw if both sides exhausted (Korean War style)
        if (this.config.war_type === 'coalition' && sesA > 60 && sesB > 60 && milA < 35 && milB < 35) {
            return { terminated: true, winner: 'draw', reason: 'negotiated_settlement' };
        }

        // Limited war withdrawal: political will collapse triggers withdrawal even if military isn't defeated
        if (this.config.war_type === 'limited_war' && polA < 30 && sesA > 75 && this.month > 40) return { terminated: true, winner: 'b', reason: 'withdrawal_a' };
        if (this.config.war_type === 'limited_war' && polB < 30 && sesB > 75 && this.month > 40) return { terminated: true, winner: 'a', reason: 'withdrawal_b' };

        // Combined political-population collapse (secondary)
        if (polA < 10 && popA < 15) return { terminated: true, winner: 'b', reason: 'collapse_a' };
        if (polB < 10 && popB < 15) return { terminated: true, winner: 'a', reason: 'collapse_b' };

        return { terminated: false };
    }

    /**
     * Determine final outcome type
     */
    _determineOutcome(result) {
        const { winner, reason } = result;

        if (reason.startsWith('collapse') || reason.startsWith('dominance')) {
            return 'Decisive Victory';
        }
        if (reason === 'mutual_exhaustion' || reason.startsWith('exhaustion')) {
            return 'Attritional Exhaustion';
        }
        if (reason === 'negotiated_settlement') {
            return 'Negotiated Settlement';
        }
        if (reason.startsWith('withdrawal')) {
            return 'Strategic Withdrawal';
        }
        if (winner === 'draw') {
            return 'Stalemate';
        }

        const dssA = this.dss_history.a[this.dss_history.a.length - 1] || 0;
        const dssB = this.dss_history.b[this.dss_history.b.length - 1] || 0;
        const sesA = this.ses_history.a[this.ses_history.a.length - 1] || 0;
        const sesB = this.ses_history.b[this.ses_history.b.length - 1] || 0;

        if (winner === 'a' && dssA > sesA) return 'Shock-Driven Decisive Victory';
        if (winner === 'b' && dssB > sesB) return 'Shock-Driven Decisive Victory';
        if (winner === 'a' && sesA <= sesB) return 'Attritional Exhaustion Victory';
        if (winner === 'b' && sesB <= sesA) return 'Attritional Exhaustion Victory';

        return 'Decisive Victory';
    }

    /**
     * Find key turning point
     */
    _findTurningPoint() {
        let maxDiff = 0;
        let turnMonth = 0;
        const minLen = Math.min(this.dss_history.a.length, this.dss_history.b.length);

        for (let i = 1; i < minLen; i++) {
            const diffA = this.dss_history.a[i] - this.ses_history.a[i];
            const diffB = this.dss_history.b[i] - this.ses_history.b[i];
            const delta = Math.abs(diffA - diffB);
            if (delta > maxDiff) {
                maxDiff = delta;
                turnMonth = i;
            }
        }

        return turnMonth;
    }

    /**
     * Reset simulator state for a fresh run
     */
    reset(seed = 42) {
        this._rng = WarSimulator.createPRNG(seed);
        this.state = {
            military_a: this.config.initial_military_a,
            military_b: this.config.initial_military_b,
            economic_a: this.config.initial_economic_a,
            economic_b: this.config.initial_economic_b,
            political_will_a: this.config.initial_political_will_a,
            political_will_b: this.config.initial_political_will_b,
            population_support_a: this.config.initial_population_support_a,
            population_support_b: this.config.initial_population_support_b,
            industrial_a: this.config.initial_industrial_a,
            industrial_b: this.config.initial_industrial_b
        };
        this.history = [{
            month: 0,
            ...JSON.parse(JSON.stringify(this.state))
        }];
        this.dss_history = { a: [], b: [] };
        this.ses_history = { a: [], b: [] };
        this.month = 0;
        this.terminated = false;
        this.outcome = null;
    }

    /**
     * Build outcome object from termination result
     */
    _buildOutcome(result, dssA, dssB, sesA, sesB, month) {
        return {
            type: this._determineOutcome(result),
            winner: result.winner === 'a' ? this.config.side_a :
                    result.winner === 'b' ? this.config.side_b : 'Draw',
            winner_key: result.winner,
            reason: result.reason,
            duration: month,
            final_dss_a: dssA,
            final_dss_b: dssB,
            final_ses_a: sesA,
            final_ses_b: sesB,
            turning_point: this._findTurningPoint()
        };
    }

    /**
     * Advance simulation by one month (shared engine for simulate() and animation)
     */
    stepOneMonth() {
        if (this.terminated) return this.outcome;

        const m = this.month + 1;

        this._applyAttrition(m);
        this._applyShock(m);

        for (const key of Object.keys(this.state)) {
            const u1 = this._rng();
            const u2 = this._rng();
            const z = Math.sqrt(-2 * Math.log(u1 || 0.001)) * Math.cos(2 * Math.PI * u2);
            this.state[key] += z * 0.5;
            this.state[key] = WarSimulator.clamp(this.state[key]);
        }

        const dssA = this._computeDSS('a');
        const dssB = this._computeDSS('b');
        const sesA = this._computeSES('a', m);
        const sesB = this._computeSES('b', m);

        this.dss_history.a.push(dssA);
        this.dss_history.b.push(dssB);
        this.ses_history.a.push(sesA);
        this.ses_history.b.push(sesB);

        this.history.push({
            month: m,
            ...JSON.parse(JSON.stringify(this.state))
        });

        this.month = m;

        const result = this._checkTermination();
        if (result.terminated) {
            this.terminated = true;
            this.outcome = this._buildOutcome(result, dssA, dssB, sesA, sesB, m);
            return this.outcome;
        }
        return null;
    }

    /**
     * Run full simulation (matching Python simulate())
     */
    simulate(maxMonths = 120, seed = 42) {
        this.reset(seed);

        for (let m = 1; m <= maxMonths; m++) {
            const outcome = this.stepOneMonth();
            if (outcome) {
                return outcome;
            }
        }

        this.outcome = this._buildOutcome(
            { winner: 'draw', reason: 'time_limit' },
            this.dss_history.a[this.dss_history.a.length - 1] || 0,
            this.dss_history.b[this.dss_history.b.length - 1] || 0,
            this.ses_history.a[this.ses_history.a.length - 1] || 0,
            this.ses_history.b[this.ses_history.b.length - 1] || 0,
            maxMonths
        );

        return this.outcome;
    }

    /**
     * Export results as JSON
     */
    exportJSON() {
        return JSON.stringify({
            config: this.config,
            outcome: this.outcome,
            history: this.history,
            dss_history: this.dss_history,
            ses_history: this.ses_history
        }, null, 2);
    }
}

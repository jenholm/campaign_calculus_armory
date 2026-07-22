# DSS Information Availability Audit v2

**Date:** 2026-07-20
**Purpose:** Rigorously classify every DSS component by when its information becomes available to a strategic observer, distinguishing genuinely predictive components from those that require outcome knowledge.

## Core Problem

The current observed DSS (9 components) is effectively a battle narrative reconstruction metric. Most components measure "how obvious was the decisive battle after we know the war outcome?" rather than "how predictable was the war outcome before the first shot?"

The model asks: "Was the battle decisive?" after the battle is over.
It should ask: "Was the outcome structurally predictable before the battle?"

## Observed DSS Components (Current)

| # | Component | Weight | Available Before Conflict? | Classification | Rationale |
|---|-----------|--------|---------------------------|----------------|-----------|
| 1 | Concentration Ratio | 0.15 | No | Post-hoc | Requires knowing which battle was largest and its share of total casualties. Only measurable after battles occur. A pre-war analyst cannot know this. |
| 2 | Temporal Clustering | 0.10 | No | Post-hoc | Requires the full timeline of battle events to compute clustering. Cannot be measured before or during the war. |
| 3 | Force Ratio at Peak | 0.12 | Partially | Early-war | The ratio of forces in the largest battle to total forces can be estimated early in a campaign but is only precise after the battle occurs. Pre-war, force ratio is a structural observable; "at peak" is not. |
| 4 | Outcome Proximity | 0.18 | No | Post-hoc | Measures temporal distance between largest battle and war end. Fundamentally requires knowing when the war ended. This is pure hindsight. |
| 5 | Morale Cascade Index | 0.10 | No | Post-hoc | Measures rapid collapse after the largest battle. Requires observing the decline in subsequent battles. Only knowable after the cascade occurs. |
| 6 | Territorial Swing | 0.10 | No | Post-hoc | Measures territorial change after the largest battle. Only observable after the battle and subsequent operations. |
| 7 | Force Destruction Ratio | 0.08 | No | Post-hoc | Fraction of capability destroyed in a single engagement. Requires knowing the engagement's outcome. |
| 8 | Surprise Index | 0.04 | Partially | Pre-war/early-war | Degree of surprise can be partially estimated from force positioning and intelligence before the battle, but precise measurement requires knowing the attack location and timing. |
| 9 | Alliance Cascade | 0.03 | No | Post-hoc | Whether the battle triggered alliance defections. Only observable after the battle and subsequent diplomatic events. |

**Summary:** Of the 9 observed DSS components:
- 0 are fully available before conflict
- 2 are partially available (Force Ratio at Peak, Surprise Index)
- 7 require post-hoc knowledge

**The current observed DSS is 82% post-hoc information by weight.** This means the observed DSS is primarily measuring battle narrative reconstruction, not structural predictability.

## Predictive DSS Components (Current, v1)

| # | Component | Weight | Available Before Conflict? | Classification | Notes |
|---|-----------|--------|---------------------------|----------------|-------|
| 1 | Force Ratio | 0.20 | Yes | Pre-war | Military strength ratio known from intelligence assessments before hostilities |
| 2 | Economic Disparity | 0.15 | Yes | Pre-war | GDP ratios publicly available or estimable from intelligence |
| 3 | Industrial Capacity Ratio | 0.15 | Yes | Pre-war | War production capacity estimable from economic indicators |
| 4 | Logistics Vulnerability | 0.15 | Partially | Pre-war | Distance, supply lines, terrain known from geography; actual vulnerability only known in practice |
| 5 | Surprise Indicator | 0.10 | Partially | Pre-war | Mobilization patterns observable; actual surprise level depends on execution |
| 6 | Alliance Asymmetry | 0.10 | Yes | Pre-war | Alliance structures publicly known or estimable |
| 7 | Mobilization Speed | 0.10 | Partially | Pre-war | Force generation rates estimable from industrial base; actual speed only known once it occurs |
| 8 | Regime Stability | 0.05 | Partially | Pre-war | Political cohesion estimable but uncertain; may shift rapidly |

**Summary:** Of the 8 predictive DSS components:
- 4 are fully available before conflict (Force Ratio, Economic Disparity, Industrial Capacity, Alliance Asymmetry)
- 4 are partially available (Logistics, Surprise, Mobilization Speed, Regime Stability)
- 0 require post-hoc knowledge

**The predictive DSS is 100% pre-conflict or early-conflict information by weight.**

## The Key Insight: Gulf War Case

For the Gulf War 1991, a competent analyst in January 1991 had:

**Available before conflict:**
- Coalition air dominance (air superiority was assured)
- Iraqi air force weakness (known from 1980s data)
- Poor Iraqi logistics (desert warfare, supply lines known)
- Poor NCO/officer initiative (Iran-Iraq War experience)
- Massive GDP/resource imbalance (coalition GDP >> Iraq GDP)
- Sanctions damage (in effect since August 1990)
- No realistic replacement capacity (Iraq's industrial base was small)
- Coalition naval/air deployment (publicly known)
- Iraqi aircraft fleeing to Iran (happened before ground war)

**The uncertainty was NOT:**
- "Will Iraq defeat the coalition?" (No serious analyst believed this)

**The uncertainty WAS:**
- "How many coalition casualties will this cost?"
- "How long will the ground war take?"
- "Will Iraq use chemical weapons?"

**Therefore the Gulf War should have:**
- Very high predictive DSS (structural factors overwhelmingly predicted coalition victory)
- Low outcome information delta (the outcome added relatively little new information)

**Current model behavior:** The predictive DSS for Gulf War uses only force_ratio, economic_disparity, and industrial_capacity (the other 5 components default to neutral values). This produces a predictive DSS of 64.4, which is moderate. But the actual pre-war evidence was overwhelming. The model is underestimating what was knowable because it lacks data for the other 5 components.

**This is not a failure of the framework.** The framework correctly distinguishes between predictive and observed DSS. The problem is data availability for the predictive components. The paper should acknowledge this data limitation explicitly.

## The Key Insight: WWI Case

For WWI, a military analyst in August 1914 had:

**Available before conflict:**
- Force ratios were roughly balanced (score ~50)
- Economic disparities were moderate (score ~55)
- Alliance structures were complex but known (score ~50)
- Mobilization speed was a known German advantage (score ~65)
- Regime stability was uncertain for all parties (score ~50)

**The genuine uncertainty:**
- Could France hold against the Schlieffen Plan?
- Would Russia mobilize fast enough?
- Would Britain enter the war?
- How long could Germany fight on two fronts?

**Therefore WWI should have:**
- Moderate predictive DSS (structural factors were ambiguous)
- Higher outcome information delta (the outcome revealed dynamics not predictable from structure alone)

## Revised Outcome Information Delta Concept

**Formula:**
OID = DSS_observed - DSS_predictive

**Interpretation:**
- **Low OID:** Outcome was structurally predictable (Gulf War, Six Day War)
- **High OID:** Important dynamics emerged during conflict that weren't predictable from structure (WWI, Eastern Front WWII, Vietnam political collapse)

**Key theoretical distinction:**
- A decisive battle can end a war.
- A decisive imbalance can make that ending predictable before it happens.
- The current DSS framework captures the first. The revision captures the second.

## Proposed DSS v2 Component Classification

### Observed DSS (Post-Hoc Classification)

| Component | Weight | Classification | Status |
|-----------|--------|----------------|--------|
| Concentration Ratio | 0.15 | Post-hoc | RETAIN for explanatory analysis |
| Temporal Clustering | 0.10 | Post-hoc | RETAIN for explanatory analysis |
| Force Ratio at Peak | 0.12 | Early-war | RETAIN (partial predictive value) |
| Outcome Proximity | 0.18 | Post-hoc | RETAIN for explanatory analysis |
| Morale Cascade Index | 0.10 | Post-hoc | RETAIN for explanatory analysis |
| Territorial Swing | 0.10 | Post-hoc | RETAIN for explanatory analysis |
| Force Destruction Ratio | 0.08 | Post-hoc | RETAIN for explanatory analysis |
| Surprise Index | 0.04 | Pre-war/early-war | RETAIN (partial predictive value) |
| Alliance Cascade | 0.03 | Post-hoc | RETAIN for explanatory analysis |

### Predictive DSS (Pre-War Classification)

| Component | Weight | Classification | Status |
|-----------|--------|----------------|--------|
| Force Ratio | 0.20 | Pre-war | RETAIN |
| Economic Disparity | 0.15 | Pre-war | RETAIN |
| Industrial Capacity Ratio | 0.15 | Pre-war | RETAIN |
| Logistics Vulnerability | 0.15 | Pre-war | RETAIN (with data caveat) |
| Surprise Indicator | 0.10 | Pre-war | RETAIN (with data caveat) |
| Alliance Asymmetry | 0.10 | Pre-war | RETAIN |
| Mobilization Speed | 0.10 | Pre-war | RETAIN (with data caveat) |
| Regime Stability | 0.05 | Pre-war | RETAIN (with data caveat) |

## Recommendations

1. **Rename the metric:** Replace "Hindsight Bias Delta" with "Outcome Information Delta" throughout the paper.
2. **Reclassify the comparison:** The comparison between observed and predictive DSS answers: "How much additional information becomes available after conflict resolution?"
3. **Acknowledge data limitations:** The predictive DSS currently varies across only 3 components (force ratio, economic disparity, industrial capacity). The remaining 5 use fixed neutral values. This is a data limitation, not a methodological one.
4. **Gulf War interpretation:** The Gulf War becomes a demonstration that not all decisive wars are surprising wars. A decisive battle can end a war, but a decisive imbalance can make that ending predictable before it happens.
5. **WWI interpretation:** WWI shows that structural factors alone cannot predict complex multi-front wars with uncertain alliance dynamics. The outcome information delta is higher because important dynamics emerged during the conflict.
6. **Table creation:** Create a per-component classification table showing which components are pre-war, early-war, and post-hoc, with weights and rationale.

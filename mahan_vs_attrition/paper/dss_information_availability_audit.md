# DSS Information Availability Audit

**Date:** 2026-07-19

## Purpose

Audit every DSS component to classify when its information becomes available to a strategic observer. This distinguishes genuinely predictive components from those that require outcome knowledge.

## Observed DSS Components (9 components)

| # | Component | Weight | Available Before Conflict? | Classification | Notes |
|---|-----------|--------|---------------------------|----------------|-------|
| w1 | Concentration Ratio | 0.20 | No | Outcome-dependent | Requires knowing which battle was the largest and its share of total casualties. Only measurable after battles occur. |
| w2 | Temporal Clustering | 0.15 | No | Outcome-dependent | Requires the full timeline of battle events to compute clustering. Only measurable after the war. |
| w3 | Force Ratio at Peak | 0.12 | Partially | Early-war observable | The ratio of forces in the largest battle to total forces can be estimated early in a campaign but is only precise after the battle occurs. |
| w4 | Outcome Proximity | 0.18 | No | Post-hoc | Measures temporal distance between largest battle and war end. Fundamentally requires knowing when the war ended. |
| w5 | Morale Cascade Index | 0.10 | No | Post-hoc | Measures rapid collapse after the largest battle. Requires observing the decline in subsequent battles. |
| w6 | Territorial Swing | 0.10 | No | Post-hoc | Measures territorial change after the largest battle. Only observable after the battle and subsequent operations. |
| w7 | Force Destruction Ratio | 0.08 | No | Outcome-dependent | Fraction of capability destroyed in a single engagement. Requires knowing the engagement's outcome. |
| w8 | Surprise Index | 0.04 | Partially | Pre-war/early-war | The degree of surprise can be partially estimated from force positioning and intelligence before the battle, but precise measurement requires knowing the attack location and timing. |
| w9 | Alliance Cascade | 0.03 | No | Post-hoc | Whether the battle triggered alliance defections. Only observable after the battle and subsequent diplomatic events. |

**Summary:** Of the 9 observed DSS components, 0 are fully available before conflict, 2 are partially available, and 7 require post-hoc knowledge.

## Predictive DSS Components (8 components)

| # | Component | Weight | Available Before Conflict? | Classification | Notes |
|---|-----------|--------|---------------------------|----------------|-------|
| u1 | Force Ratio | 0.20 | Yes | Pre-war | Military strength ratio is known from intelligence assessments before hostilities. |
| u2 | Economic Disparity | 0.15 | Yes | Pre-war | GDP ratios and economic capacity are publicly available or estimable from intelligence. |
| u3 | Industrial Capacity Ratio | 0.15 | Yes | Pre-war | War production capacity is estimable from economic indicators before conflict. |
| u4 | Logistics Vulnerability | 0.15 | Yes | Pre-war | Distance, supply lines, and terrain difficulty are known from geography and intelligence. |
| u5 | Surprise Indicator | 0.10 | Yes | Pre-war | Mobilization patterns and force positioning are observable through intelligence before conflict. |
| u6 | Alliance Asymmetry | 0.10 | Yes | Pre-war | Alliance structures and commitments are publicly known or estimable. |
| u7 | Mobilization Speed | 0.10 | Partially | Pre-war/early-war | Force generation rates can be estimated from industrial base and training infrastructure, but actual mobilization speed is only known once it occurs. |
| u8 | Regime Stability | 0.05 | Partially | Pre-war | Political cohesion is estimable but uncertain. Domestic political dynamics may shift rapidly. |

**Summary:** Of the 8 predictive DSS components, 6 are fully available before conflict, 2 are partially available, and 0 require post-hoc knowledge.

## Cross-Reference: Observed vs Predictive DSS

The observed and predictive DSS use different component sets. They are not simply different subsets of the same components. The observed DSS measures battle-level dynamics (concentration, clustering, proximity, morale, territory), while the predictive DSS measures structural pre-war conditions (force ratios, economics, logistics, alliances).

The comparison between them answers: "How much of the observed decisive dynamics is explained by pre-war structural conditions versus information that only became available through the conflict?"

## Gulf War Implications

For the Gulf War, the predictive DSS would score high on many components:
- Force ratio: Coalition had overwhelming numerical superiority (score ~85)
- Economic disparity: Coalition GDP far exceeded Iraq's (score ~80)
- Industrial capacity: Coalition had overwhelming technological advantage (score ~90)
- Logistics: Iraq's supply lines were vulnerable; coalition had forward bases (score ~75)
- Surprise: Coalition achieved strategic surprise despite公开buildup (score ~60)
- Alliance: 35-nation coalition vs isolated Iraq (score ~95)

A military analyst in January 1991 would have assessed most of these structural factors. The predictive DSS should be high for the Gulf War, not low. If the current model produces a low predictive DSS, the model is underestimating what was knowable.

## WWI Implications

For WWI, the predictive DSS would be more ambiguous:
- Force ratios were roughly balanced (score ~50)
- Economic disparities were moderate (score ~55)
- Alliance structures were complex and uncertain (score ~50)
- Mobilization speed was a known German advantage (score ~65)
- Regime stability was uncertain for all parties (score ~50)

A military analyst in August 1914 would have had genuine uncertainty about the outcome. The predictive DSS should be moderate for WWI, reflecting this uncertainty.

## Recommendation

The paper should:
1. Reclassify the DSS comparison as "outcome information delta" rather than "hindsight bias"
2. Create a per-preset table showing observed DSS, predictive DSS, and the delta
3. Discuss which components are genuinely predictive vs outcome-dependent
4. Note that the Gulf War delta should be small (structural factors were highly predictive) while WWI delta should be large (structural factors were ambiguous)

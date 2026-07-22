# Simulation Language Audit v2

Audit of simulation-related language in `paper/sections/*.tex` for overclaiming risk.
Generated from full-text grep of target terms across all section files.

## Method

Each occurrence of the target terms was read in full context. Risk is assigned as:
- **HIGH**: Claims the simulation proves/validates/predicts something about history without appropriate qualification.
- **MEDIUM**: Borderline phrasing that could be misread as overclaiming, or uses words ("validates", "confirms", "predicted") that imply stronger epistemic status than warranted.
- **LOW**: Clearly appropriate usage (descriptive, statistical, or appropriately hedged).

Replacements suggested for HIGH and MEDIUM items follow the rules:
- "validated" → "evaluated against" (unless truly out-of-sample)
- "predicted" → "generated" or "suggested" (unless genuine forecasting was performed)
- "confirmed" → "consistent with" or "is consistent with"

---

## Audit Results

| # | File : Line | Current Phrase (in context) | Risk | Suggested Replacement |
|---|-------------|---------------------------|------|----------------------|
| 1 | `data.tex:29` | "metric validation" in table footnote | MEDIUM | "metric evaluation" |
| 2 | `data.tex:59` | "To **validate** our quantitative metrics against detailed historical analysis, we selected 30 wars…" | HIGH | "To **evaluate** our quantitative metrics against…" |
| 3 | `data.tex:59` | "strategic assessments to **validate** our automated metrics" | HIGH | "strategic assessments to **assess** our automated metrics" |
| 4 | `background.tex:27` | "simulation models of war dynamics have not been **validated** against historical data at scale" | MEDIUM | "have not been **systematically evaluated** against historical data at scale" |
| 5 | `methods.tex:166` | "A leakage analysis **confirms** that the correlation… is *r* = 0.31, **confirming** these capture substantially different information" | LOW | (Statistical usage; no change needed) |
| 6 | `methods.tex:231` | "We distinguish two **validation** strategies with fundamentally different epistemic status" | MEDIUM | "two **evaluation** strategies" |
| 7 | `methods.tex:233` | "tests whether mechanism combinations can **reproduce** historically observed trajectory classes" | MEDIUM | "can **generate trajectory classes consistent with** historically observed patterns" |
| 8 | `methods.tex:233` | "it **confirms** internal model consistency, not independent prediction" | LOW | (Appropriately hedged with "not independent prediction"; no change needed) |
| 9 | `methods.tex:239` | "The calibrated reconstruction **demonstrates** that the model *can* **reproduce** observed patterns" | MEDIUM | "The calibrated reconstruction **shows** that the model *can* **generate patterns consistent with** observations" |
| 10 | `results.tex:89` | "The classifier **correctly identifies** the Gulf War and Franco-Prussian War as decisive shock, and Vietnam, WWI, WWII, and Iran–Iraq as strategic exhaustion" | MEDIUM | "The classifier **identifies** the Gulf War and Franco-Prussian War as decisive shock…" (remove "correctly") |
| 11 | `results.tex:91` | "the termination event (political/military collapse) is **correctly identified**, but the dominant mechanism is **correctly classified** as strategic exhaustion" | MEDIUM | "the termination event (political/military collapse) **matches the historical record**, and the dominant mechanism is **classified** as strategic exhaustion" |
| 12 | `results.tex:107` | Gulf War row: "Structural factors strongly predictive; outcome **confirms**" | HIGH | "Structural factors strongly predictive; outcome **consistent with**" |
| 13 | `results.tex:112` | Korean War row: "Structure **predicted** decisiveness; war proved attritional" | MEDIUM | "Structure **suggested** decisiveness; war proved attritional" |
| 14 | `results.tex:113` | Vietnam row: "Structure strongly **predicted** decisiveness; outcome was exhaustion" | MEDIUM | "Structure strongly **suggested** decisiveness; outcome was exhaustion" |
| 15 | `results.tex:114` | Iran–Iraq row: "Structure **predicted** moderate decisiveness; outcome was attritional" | MEDIUM | "Structure **suggested** moderate decisiveness; outcome was attritional" |
| 16 | `results.tex:123` | "pre-war structural factors **predicted** a decisive outcome, but the actual wars proved attritional" | MEDIUM | "pre-war structural factors **suggested** a decisive outcome" |
| 17 | `results.tex:123` | "the structural assessment (69.9) strongly **predicted** decisive shock" | MEDIUM | "the structural assessment (69.9) strongly **indicated** decisive shock" |
| 18 | `results.tex:149` | "we developed a blind **validation** framework… is asked to **predict** the mechanism category" | MEDIUM | "blind **evaluation** framework"; "is asked to **classify** the mechanism category" |
| 19 | `results.tex:151` | "Blind **validation** results show that the default-parameter simulation **predicts** 'uncertain'… **correctly** identifies 0 cases as decisive" | MEDIUM | "Blind **evaluation** results… **classifies** 'uncertain'… **identifies** 0 cases as decisive" (remove "correctly") |
| 20 | `introduction.tex:18` | "The model's **prediction** target is deliberately narrow. It **predicts**:" | MEDIUM | "The model's **classification** target is deliberately narrow. It **generates**:" |
| 21 | `introduction.tex:26` | "The model does *not* attempt to **predict**:" | MEDIUM | "The model does *not* attempt to **generate**:" |
| 22 | `introduction.tex:37` | "This demonstration **confirms** internal model consistency while also revealing the fundamental difficulty of **predicting** specific historical outcomes with simplified models" | MEDIUM | "This demonstration **is consistent with** internal model consistency…" |
| 23 | `discussion.tex:3` | "demonstrating that terminal events and strategic mechanisms can diverge" | LOW | (Appropriate usage; the classifier does show this) |
| 24 | `discussion.tex:30` | "The revised classifier **demonstrates** that the Franco-Prussian War and Gulf War are characterized by decisive shock dynamics" | MEDIUM | "The revised classifier **indicates** that the Franco-Prussian War and Gulf War…" |
| 25 | `discussion.tex:40` | "achieves 86\% agreement with historical classifications" | LOW | (Factual reporting of agreement metric; no change needed) |
| 26 | `discussion.tex:54` | "Our logistic regression analysis **confirms** that material-capability features contain meaningful predictive information" | MEDIUM | "Our logistic regression analysis **shows** that material-capability features contain meaningful predictive information" |
| 27 | `discussion.tex:54` | "the Vietnam War is **correctly identified** as strategic exhaustion" | MEDIUM | "the Vietnam War is **identified** as strategic exhaustion" (remove "correctly") |
| 28 | `discussion.tex:54` | "the simulation mechanism demonstration **shows** that the model… classifies the Franco-Prussian War and Gulf War as decisive" | LOW | (Appropriate hedging with "shows"; no change needed) |
| 29 | `discussion.tex:70` | "the outcome **confirmed** what analysts could have predicted" | HIGH | "the outcome **was consistent with** what analysts could have predicted" |
| 30 | `discussion.tex:76` | "not in **reproducing** the precise trajectory of any individual conflict" | LOW | (Appropriate disclaimer; no change needed) |
| 31 | `discussion.tex:88` | "The model **forecasts** mechanism classes… It **predicts** the qualitative trajectory shape" | LOW | (Appropriate in context of describing what the model does; properly scoped) |
| 32 | `falsification.tex:8` | "the simulation's ability to **predict** termination mechanism from initial conditions alone would be falsified" | LOW | (Describing a falsification criterion; appropriately conditional) |
| 33 | `conclusion.tex:5` | "when it merely **confirms** an outcome that exhaustion has already made inevitable" | MEDIUM | "when it merely **is consistent with** an outcome that exhaustion has already made inevitable" |
| 34 | `limitations.tex:5` | "demonstrating that DSS and SES can emerge from interacting attritional and shock processes" | LOW | (Appropriate; limited to what the simulation demonstrates about itself) |
| 35 | `limitations.tex:25` | "not in **reproducing** the precise trajectory of any individual war" | LOW | (Appropriate limitation statement) |

---

## Summary

| Risk Level | Count |
|-----------|-------|
| HIGH | 4 |
| MEDIUM | 18 |
| LOW | 12 |
| **Total flagged** | **34** |

### HIGH-Risk Items Requiring Immediate Attention

1. **`data.tex:59`** (×2): "validate" used twice in the same sentence to describe evaluating metrics against case studies. This is comparison, not validation.
2. **`results.tex:107`**: "outcome confirms" in the Gulf War table row implies the outcome proves the structural assessment correct.
3. **`discussion.tex:70`**: "the outcome confirmed what analysts could have predicted" — same overclaiming pattern as #3.

### Systematic Patterns

1. **"validate" vs. "evaluate"**: Used in `data.tex` (×2) and `methods.tex` (×1) and `background.tex` (×1) when "evaluate" or "assess" would be more accurate. The calibrated reconstruction is not validation; the authors say so explicitly in `methods.tex:233`, but the word "validation" persists elsewhere.

2. **"predicted" for structural scores**: The outcome delta table (`results.tex:112–114`) and surrounding text use "predicted" to describe what the predictive DSS score suggested. The predictive DSS is a pre-war scoring metric, not a forecasting model in the traditional sense. "Suggested" or "indicated" would be more precise.

3. **"correctly identifies/classified"**: Used in `results.tex:89,91` and `discussion.tex:54`. The word "correctly" implies the simulation achieved ground truth, when it achieved agreement with historical interpretation. "Identifies" or "classifies" (without "correctly") is sufficient.

4. **"confirms"**: Used in `results.tex:107`, `discussion.tex:54,70`, `introduction.tex:37`, and `conclusion.tex:5`. In every case, "shows", "is consistent with", or "indicates" would be more epistemically appropriate.

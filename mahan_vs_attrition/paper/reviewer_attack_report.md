# Hostile Reviewer Report

**Reviewer:** #2
**Journal:** Journal of Peace Research
**Manuscript:** Decisive Shock or Strategic Exhaustion? A Dynamical Model of War Termination Mechanisms

---

## Major Criticisms

### 1. Circularity in Core Metric

The DSS (Decisive Shock Score) computed within the simulation is tautological. The shock function (`_apply_shock`) reduces `state["military_b"]` by `σ · 5.0` every 5–7 months. The simulation-derived DSS then measures `ΔMil` between consecutive months — literally reading back the shock function's output. The capital bonus triggers when `Mil < 0.3 · Mil(0)`, a threshold the shock function drives state toward. The surrender bonus triggers when `Pol < 20`, likewise reachable through shock-induced cascades.

The authors acknowledge this in their Limitations section (Section 6.1), but acknowledgment is not remedy. The entire simulation validation exercise (Table 4) is built on these circular metrics. When the simulation "validates" that the Franco-Prussian War is decisive, it is confirming that its shock function (parameterized at `shock_strength=90`) produces large `ΔMil` values, which DSS measures. This is circular reasoning dressed as empirical validation. The authors claim to mitigate this by "validating against external historical data," but the external DSS (Section 2, Equation 1) and the simulation DSS (Section 3, Equation 5) are entirely different metrics with the same name — a source of confusion that borders on misleading.

### 2. Historical Presets Encode the Answer

The simulation validation is a Potemkin exercise. The Gulf War preset has `shock_strength=90`, `attrition_rate=30`, initial military of 95 vs 70, economic 95 vs 40 — of course it produces a decisive victory. WWI has `shock_strength=40`, `attrition_rate=80` — of course it produces attrition. The Franco-Prussian War has `shock_strength=90`, `attrition_rate=35` — of course it's decisive.

The model assumptions audit (which the authors themselves produced!) states explicitly: "The preset encodes the hypothesis rather than testing it" (Section on Franco-Prussian War). If the authors' own internal audit identifies this problem, how can they present the validation in the paper as meaningful? The blind validation (Section 3.7) is the only genuine test, and it achieves 58% accuracy on 10 cases — a result so imprecise (95% CI: [26%, 90%]) as to be uninformative.

### 3. Sample Selection Bias and Cherry-Picking

The 30 case studies are hand-picked (Section 2.7). The authors "selected" 18 wars for in-depth analysis chosen to "represent variation across time periods, geographic regions, conflict types, and outcome types" — but this selection was made by the authors with full knowledge of the expected results. Where are the anomalous cases? Where are wars that should be decisive but aren't, or vice versa?

The 4,220-war dataset is assembled from seven sources with wildly different coding standards, temporal coverage, and definitions of "war." The Brecke Conflict Catalog covers European conflicts 1400–1789; the UCDP covers 1946–present; the IWB covers 1600–2003 for interstate wars only. Merging these requires "normalization" through a pipeline that imputes missing data and aligns heterogeneous coding schemes. The resulting dataset is a Frankenstein compilation where a 15th-century European border dispute and a 21st-century African civil war are forced into the same analytical framework. The authors report 4,220 wars as if this number reflects comprehensive coverage, when in reality it reflects aggressive merging of incompatible sources.

### 4. Untested Parameters Are Magic Numbers

The simulation has at minimum 15 free parameters with no historical calibration: `0.04` (battle loss rate), `0.004` (recruitment per industrial unit), `1.5` (recruitment cap), `5.0` (shock damage to B), `4.0` (retaliation damage to A), `0.025` (war costs), `0.01` (blockade), `0.006` (industrial output), `0.2` (casualty pressure), `0.4` (weariness), `0.8` (victory bonus), `0.03` (economic hardship), `0.015` (bombing), `0.004` (recon/industrial), and the fatigue denominator `60`.

The sensitivity analysis (Table 5) varies only 4 parameters (shock strength, attrition rate, economic resilience, political resilience) while holding all 11+ internal coefficients fixed. The authors' own audit states: "No sensitivity analysis has been performed" on the internal coefficients, and "changing any one of them could flip conclusions for marginal cases." The fatigue function denominator of 60 is identified as a "single point of failure" — changing it to 40 makes wars end 33% faster. Yet this parameter is never tested.

The sensitivity analysis presented as robustness evidence is therefore deeply misleading: it tests the parameters that *control* the mechanism balance (which are inherently robust to perturbation because they *are* the mechanism) while ignoring the parameters that *implement* the mechanisms (which are untested).

### 5. The Model Ignores Every Variable That Actually Matters

The simulation models war as five scalars (military, economic, political will, population support, industrial capacity) updated by fixed-form equations. It omits:

- **Leadership quality and decision-making** — arguably the most important variable in whether a battle is decisive or not
- **Intelligence and information** — Midway was decisive because of intelligence, not force ratios
- **Geography and terrain** — Stalingrad, Verdun, the Somme — terrain shaped every major attritional battle
- **Technology and innovation** — tank warfare, air power, nuclear weapons, cyber capabilities
- **Alliance politics and diplomatic context** — the coalitions in WWI and WWII were decisive
- **Domestic politics** beyond a single "will" variable — elections, media, propaganda, public opinion
- **Weather and logistics** — the Russian winter, the monsoon season, the Mud Season on the Western Front
- **Command and control** — communication systems, coordination, C2 degradation

Any one of these could dominate the dynamics in specific wars. The model's claim to "demonstrate" that attrition and shock interact is unfalsifiable because the model has no mechanism for any of these alternative explanations. Of course the model finds that its own two mechanisms explain outcomes — it has no other mechanisms to test.

### 6. Causal Overclaims Throughout

The abstract claims the paper "demonstrates that decisive events and attritional processes are not competing explanations." The conclusion claims the paper "develops a computational framework for distinguishing between decisive shock and strategic exhaustion." The introduction claims to "test this framework."

A simulation with tuned parameters and hand-calibrated presets cannot demonstrate, prove, or establish causation. It can only show that a particular mathematical model, when parameterized in a particular way, produces particular outputs. The authors have built a model with two knobs (shock and attrition) and two meters (DSS and SES), and they are reporting with apparent sincerity that the two meters measure what the two knobs control. This is not a finding; it is a design specification.

The language throughout should be revised from "demonstrates" to "explores," from "shows" to "suggests within the model," and from "confirms" to "is consistent with." The paper's actual contribution — providing a quantitative vocabulary for discussing shock vs. attrition — is valuable but far more modest than the claims made.

### 7. Simulation Produces Artificially Clean Results

The simulation produces smooth, deterministic curves with trivial Gaussian noise (N(0, 0.5)) added. Real wars are chaotic, discontinuous, and governed by events that cannot be predicted from state variables: assassinations, mutinies, defections, weather events, technological surprises, and individual decisions.

The clean results in Figures referenced throughout the paper reflect the model's simplicity, not reality. The "attritional iceberg" finding — that gradual decline precedes decisive collapse — is an artifact of the model's continuous attrition function, not an empirical discovery. In reality, many decisive collapses (France 1940, Kuwait 1990) occurred without prolonged attritional precursors; they were genuine shocks to a system that appeared functional.

### 8. Statistical Methodology Is Flawed

**Logistic regression:** The authors fit a logistic regression with 7 features on an implied sample of ~100 wars (the subset with battle-level data). With 7 features and ~100 observations, the rule of thumb of 10–20 events per variable is barely met for the rarer class. The pseudo-R² of 0.28 suggests substantial unexplained variance, yet the authors present the significant coefficients as confirmatory.

**Ablation study:** The ablation compares four nested models using AIC and likelihood ratio tests, but reports no cross-validation. AIC comparisons on training data are not evidence of out-of-sample performance. The improvements in AIC from adding DSS (-235) and SES (-289) may reflect overfitting to the training sample.

**Survival analysis:** The Cox model achieves R² of 0.12, meaning 88% of variance in war duration is unexplained. The authors acknowledge this is "modest" but proceed to interpret the significant hazard ratios as meaningful. With R² = 0.12, the model is barely better than a coin flip.

**Blind validation:** 10 cases with 6 correct. The exact binomial 95% CI is [26%, 90%]. This result is statistically compatible with chance performance. The authors claim 58% is "above chance" (33% for 3 classes), but with n=10, the power to distinguish 58% from 33% is negligible. This is not a validation; it is an anecdote.

### 9. The "Attritional Iceberg" Thesis Is Unfalsifiable

The core claim — that "the decisive event is the visible tip of a much larger attritional process" — is structured so that no possible evidence could refute it:

- If a war is decided by a battle → the battle was "enabled by attrition" (the iceberg)
- If a war is decided by attrition → that confirms the iceberg directly
- If a war shows both → that confirms both mechanisms interact (the paper's main contribution)
- If a war shows neither → it's classified as "Mixed" and added to the evidence for complexity

What observation would falsify the attritional iceberg? The authors never say. A thesis that explains everything explains nothing. This is not science; it is narrative construction.

### 10. Reproducibility Is Incomplete

The paper claims a "single-command pipeline" reproduces all results, but:

- No random seeds are reported for the simulation's stochastic noise component
- The Python environment (version, library versions, OS) is not specified in the paper
- The logistic regression convergence criteria are not reported
- The Delphi process for DSS weights involves "five domain experts" who are not identified
- The regression imputation models for missing SES components are not described

The supplementary materials may address some of these, but a paper claiming computational reproducibility must include these details in the manuscript or its appendices.

---

## Minor Issues

1. **Abstract length:** At 240 words, the abstract exceeds the typical JPR limit of 150–200 words.

2. **Terminology inconsistency:** The paper uses "decisive shock" and "strategic exhaustion" in the title and abstract, but the simulation calls them "Mahan mechanism" and "attrition." These should be unified.

3. **Table 4 presentation:** Checkmarks and crosses are used without a legend. The "~" symbol for "partial agreement" is undefined in the table caption.

4. **Citation density:** The background section cites only 12 sources for a topic with hundreds of relevant works. Key omissions include Zetterling's work on decisive battles, Posen on military doctrine, and Strachan on WWI strategy.

5. **Equation numbering:** Equations 5–9 (the simulation update rules) are cited as `ref{eq:sim_mil}` etc., but some references in the text don't match the equation numbers as written.

6. **The "Delphi process" claim:** Five experts determining DSS weights via Delphi is mentioned once (Section 3.2) with no further detail. Who are they? What were the disagreements? How were weights reconciled? This is a key methodological detail buried in a sentence.

7. **Figure references:** The paper references Figures 1–4 in the text, but none are included in the manuscript. This is presumably a placeholder issue, but it makes the results section unverifiable.

8. **The 0–100 clamping:** State variables clamped to [0, 100] create artificial floors and ceilings. A military strength of 0.5 and 0.0 are treated identically, which can mask the timing of collapse. The 0–100 scale is arbitrary and should be justified or replaced.

9. **Noise is trivially small:** N(0, 0.5) added to variables on a 0–100 scale represents 0.5% standard deviation. Over 100 months, cumulative noise shifts values by ~5 units — meaningful but the fixed magnitude is never justified.

10. **Victory bonus binary step function:** The political will update includes `v(t) = 0.8 if military > opponent's military, else 0.0`. This creates a discontinuity at the crossover point that could generate artificial oscillations. Real political will responds to trends, not binary win/loss states.

---

## Recommendation

**Reject and resubmit.**

The central idea — that decisive battles and attrition are interacting mechanisms rather than competing hypotheses — is genuinely interesting and potentially important for strategic studies. However, the execution has fundamental problems that undermine the paper's claims:

1. The simulation validation is circular by construction (Criticisms 1, 2)
2. The sensitivity analysis tests the wrong parameters (Criticism 4)
3. The statistical evidence is too weak to support the claims made (Criticism 8)
4. The core thesis is unfalsifiable as stated (Criticism 9)
5. The causal language vastly overstates what the methodology can establish (Criticism 6)

A revised version should: (a) clearly separate the empirical DSS/SES metrics (computed from external data) from the simulation-derived metrics, presenting the former as the paper's actual contribution; (b) conduct genuine sensitivity analysis on all internal parameters; (c) dramatically temper causal claims; (d) present the simulation as an exploration tool, not a validation engine; and (e) add cross-validation to all statistical models. The "attritional iceberg" concept should be reformulated as a falsifiable hypothesis with explicit prediction of what evidence would refute it.

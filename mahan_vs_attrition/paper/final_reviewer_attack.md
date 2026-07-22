# Hostile Review — Reviewer #2

**Manuscript:** "Decisive Shock or Strategic Exhaustion? A Dynamical Model of War Termination Mechanisms"
**Author:** Jake Enholm
**Recommendation:** Reject (major revisions required before reconsideration)

---

## Preamble

This manuscript attempts to develop a computational framework for distinguishing "decisive shock" from "strategic exhaustion" as mechanisms of war termination. The central idea—that these are interacting rather than competing mechanisms—is not novel (see Luttwak 1976, Biddle 2004, Corbett 1911, all cited in the paper itself), but the attempt to formalize it quantitatively is welcome in principle. In practice, however, this paper suffers from pervasive circularity, severe overclaiming, a simulation that encodes its own conclusions, statistical analyses that barely exceed chance, and a falsifiability structure that is essentially decorative. I detail each problem below with specific textual evidence.

---

## 1. OVERCLAIMING

### 1.1 The abstract promises more than the paper delivers

> "This paper develops a dynamical framework for separating shock-driven and exhaustion-driven termination mechanisms in armed conflict."

**Problem:** The paper does not "separate" anything. It assigns post-hoc labels to wars using a composite index whose weights are author-determined, then shows that a simulation parameterized with a "shock" variable and an "attrition" variable produces output that correlates with these labels. This is not separation; it is relabeling.

> "We introduce two complementary metrics, the Decisive Shock Score (DSS) and the Strategic Exhaustion Score (SES), and apply them to a dataset of 4,812 wars."

**Problem:** The DSS can only be computed for 91 of 4,812 wars (1.9%) because it requires battle-level data from the Interstate War Battle Dataset. For the remaining 4,721 wars (98.1%), the DSS is either unavailable or estimated through regression imputation. The phrase "apply them to a dataset of 4,812 wars" creates the impression of comprehensive coverage. It is misleading. The paper should state: "We apply these metrics to 91 wars with complete battle-level data, and to 4,721 additional wars using imputed or partial estimates."

> "A logistic regression using material-capability features achieves 54.8% test accuracy, while a random forest achieves 73.2%."

**Problem:** The logistic regression result is presented as a finding. For a binary classification task (short vs. long wars), 54.8% accuracy is 4.8 percentage points above a 50% baseline. The AUC of 0.561 is barely distinguishable from a random classifier (AUC = 0.50). Presenting this as evidence that "material and structural features contain some predictive information" is technically true but practically misleading—a coin flip with a slight edge is not a contribution to the literature.

### 1.2 The "key contribution" is not new

> "This paper's key contribution is suggesting that decisive events and attritional processes are not competing explanations but interacting mechanisms occurring at different phases of conflict."

**Problem:** This has been argued for decades. Luttwak's dialectical logic of strategy (1976) explicitly models action-reaction interactions. Biddle's force employment framework (2004) shows how material resources interact with tactical choices. Corbett's maritime strategy (1911) distinguishes between the " great决战" and the " war of exhaustion" as complementary, not competing. The paper cites all three authors in its background section but then claims their core insight as its own contribution. What exactly does this paper add beyond restating existing theory in computational form?

### 1.3 The "86% agreement" is presented without context

> "Our mechanism classifier achieves 86% agreement with historical classifications (6/7 cases)"

**Problem:** Six out of seven is not a meaningful sample size for a classification claim. The binomial confidence interval for 6/7 at the 95% level is approximately [29%, 99%], which includes chance-level performance for any binary task. Moreover, the seven cases were selected by the same team that developed the classifier. The authors acknowledge this (limitations section, line 35): "we may have unintentionally tuned the classifier criteria to match prior expectations during development." Yet the abstract presents 86% as a headline result. A reviewer should ask: were these seven cases held out during development? The paper does not say they were.

### 1.4 The 0% blind accuracy is buried

> "Blind simulation evaluation against 24 historical case studies achieves 0% exact-match accuracy with neutral default parameters."

**Problem:** This is arguably the most important result in the paper, and it appears once in the abstract as a subordinate clause, and once in the results section where it is immediately qualified: "(1) the simulation with neutral default parameters lacks discriminative power from initial conditions alone, or (2) exact-match accuracy is too strict a criterion." The paper treats its worst result as a nuance rather than a central finding. A model that achieves 0% exact-match accuracy on a 3-category task (even accounting for the conservatism of exact matching) has no demonstrated predictive value. The paper should lead with this result and explain why it should not undermine the rest of the analysis.

### 1.5 The conclusion overreaches

> "This paper has developed a computational framework for distinguishing between decisive shock and strategic exhaustion as mechanisms of war termination."

**Problem:** The framework does not "distinguish" mechanisms. It computes composite scores from weighted component indices and classifies wars using threshold rules. Whether these scores actually measure "mechanisms" (causal processes) versus "patterns" (correlational features of the data) is never established. The conclusion repeatedly uses language—"developed," "achieved," "demonstrated"—that implies successful construction and validation, when the actual achievements are (a) two new composite indices, (b) a simulation that reproduces its own parameterization, and (c) a classifier tested on 7 hand-picked cases.

---

## 2. CIRCULARITY IN CORE METRICS

### 2.1 The simulation-derived DSS measures the simulation's own shock function

> "DSS captures the magnitude of sudden military declines:
> DSS_sim(t) = min(100, max(0, -ΔMil)/Mil(0) · 50 + 1[Mil(t) < 0.3·Mil(0)] · 30 + 1[Pol(t) < 20] · 20)"

**Problem:** This is the most damaging circularity in the paper. The shock function (`_apply_shock`) reduces `state["military_b"]` by σ·5.0 every 5–7 months. The simulation-derived DSS then measures `ΔMil` between consecutive months—the literal output of the shock function. The capital bonus triggers when `Mil < 0.3·Mil(0)`, a threshold the shock function drives state toward. The surrender bonus triggers when `Pol < 20`, likewise reachable through shock-induced cascades. When the paper reports that "the model produces trajectory classes consistent with the v2 mechanism classifier in 6 of 7 cases," it is reporting that a model with a shock function produces output that correlates with a metric that measures shock function output. This is a tautology, not a finding.

The authors acknowledge this in the limitations section: "A fundamental concern with the simulation-derived DSS and SES metrics is potential circularity." But acknowledgment without remedy is not acceptable. The entire simulation validation exercise (Table 4: mechanism classification) is built on these circular metrics. The paper's mitigation—"comparing simulation outputs against external historical data"—does not address the problem, because the mechanism classification table uses simulation-derived DSS/SES, not the external empirical DSS/SES.

### 2.2 The SES has the same problem

> "SES captures cumulative exhaustion across three dimensions plus duration: SES_sim(t) = (0.3·E_mil(t) + 0.3·E_econ(t) + 0.2·E_pol(t) + 0.2·min(1, t/60))·100"

**Problem:** The attrition function produces cumulative decline in military, economic, and political state variables. SES measures cumulative decline in these same variables. A model with high attrition will produce high SES—not because exhaustion "explains" the outcome, but because SES is a readout of the attrition function's output. Furthermore, the duration factor (`min(1, t/60)`) bakes in the assumption that longer wars are more attritional. If the attrition rate is high, wars last longer (because neither side achieves quick collapse), and the duration factor inflates SES. The metric penalizes duration, which correlates with attrition, creating a self-reinforcing loop.

### 2.3 The hybrid classification rule uses unvalidated thresholds

> "Termination Type = Decisive Shock if DSS − SES ≥ 20; Strategic Exhaustion if SES − DSS ≥ 20"

**Problem:** The thresholds (minimum axis value of 45, mixed threshold of 65, margin of 20) were "calibrated against a small golden set of historical cases" (limitations section). This is overfitting to a handful of cases. Different thresholds would produce different distributions. The paper acknowledges this ("different thresholds would shift the distribution of classifications at the margins") but presents the specific percentages (2.2% decisive, 22.0% exhaustion, 75.8% uncertain) as if they are findings rather than artifacts of the chosen thresholds. No sensitivity analysis of the classification thresholds is reported.

### 2.4 The DSS component weights are arbitrary

> "DSS = Σ w_i · s_i, where w_i are weights summing to 1.0... w_1 = 0.20, w_2 = 0.15, w_3 = 0.12, w_4 = 0.18, w_5 = 0.10, w_6 = 0.10, w_7 = 0.08, w_8 = 0.04, w_9 = 0.03"

**Problem:** The paper does not explain how these weights were determined. The introduction to the methods section mentions "weights determined through a Delphi process" but provides no further detail: who were the experts? What were the disagreements? How were disagreements resolved? The weight structure is critical to the results—if the concentration ratio (w_1 = 0.20) had been weighted at 0.05 instead, the DSS distribution would shift dramatically. No sensitivity analysis of the weights is reported. The same applies to the SES weights (v_1 = 0.18, v_2 = 0.15, etc.).

### 2.5 The predictive DSS is crippled

> "The current preset data provides only force size, economic capacity, and industrial capacity for each side. The remaining five components—logistics vulnerability, surprise indicator, alliance asymmetry, mobilization speed, and regime stability—use fixed neutral values (50.0 or 64.0) because the historical presets lack this data."

**Problem:** The predictive DSS, which is supposed to measure what observers could know before the outcome, varies across only 3 of 8 components. The other 5 contribute a constant baseline. This means the predictive DSS is essentially a function of force ratio, economic disparity, and industrial capacity. The paper acknowledges this as a "data limitation, not a methodological one," but the distinction is irrelevant to the reader: if 62.5% of your predictive metric is constant, it cannot discriminate between cases. The entire outcome information delta analysis (Table 6) is computed against a crippled predictive metric.

---

## 3. UNSUPPORTED HISTORICAL ASSERTIONS

### 3.1 The Battle of Sedan did not "effectively end" the Franco-Prussian War

> "Wawro's analysis of the Franco-Prussian War emphasizes how the Battle of Sedan (1870) effectively ended the conflict by capturing the French emperor and destroying the main field army."

**Problem:** The war continued for five months after Sedan. The Siege of Paris (September 1870 – January 1871), the Loire Campaign, the Battle of Coulmiers, the Battle of Orleans, and the Battle of Le Mans all occurred after Sedan. France raised new armies and continued fighting. To say Sedan "effectively ended" the conflict is a simplification that serves the paper's narrative but misrepresents the historical record. More precise would be: "Sedan was a turning point that made French defeat likely but not immediate."

### 3.2 The Gulf War description omits the air campaign

> "The Gulf War of 1991 is frequently cited as a modern example, where a hundred-hour ground campaign decisively expelled Iraqi forces from Kuwait."

**Problem:** The hundred-hour ground campaign is often cited, but the six-week air campaign (January 17 – February 23, 1991) was arguably the decisive factor. Coalition air power destroyed Iraqi command and control, degraded armored units, and established air supremacy before ground forces moved. By emphasizing only the ground campaign, the paper aligns the Gulf War with the "decisive battle" narrative when the actual mechanism was a combined air-ground operation that unfolded over weeks, not a single decisive engagement. This is a selective reading of history that supports the paper's framework.

### 3.3 The attritional substrate claim for Sedan is circular

> "The Battle of Sedan, for example, is celebrated as a paradigmatic decisive victory, but our metrics reveal that France had already suffered significant manpower depletion, economic strain, and territorial losses before the battle."

**Problem:** The paper claims its metrics "reveal" something about France's pre-Sedan condition. But the metrics are the paper's own construction. The DSS and SES are computed from the same data the paper assembled, using weights the paper chose. Presenting the metrics' output as an independent "revelation" about history is circular. The paper is not discovering that France was weakened before Sedan—historians have known this for 150 years. It is computing a score that reflects its own weighting of historical data and then presenting that score as if it were an independent finding.

### 3.4 "Most wars are won by the side that can sustain losses longer" is presented as the attrition hypothesis

> "The opposing view, rooted in Clausewitz's observations and refined by modern scholars of attrition warfare, holds that wars are decided not by single moments of brilliance but by the gradual exhaustion of an adversary's material and human resources."

**Problem:** This is a caricature of the attrition literature. Clausewitz's actual argument is far more nuanced: war is "a continuation of politics by other means," and the destruction of armed forces is a means to political ends, not an end in itself. The attrition hypothesis as stated here is a straw man that makes it easier for the paper to "resolve" the debate. Real attrition theorists (Clausewitz, Biddle, Reed) do not argue that battles are irrelevant—only that they must be understood in political context. The paper's framing creates a false binary that its own framework then claims to transcend.

---

## 4. FIGURES THAT COULD MISLEAD

### 4.1 Figure 1 (Conceptual Model) is rhetoric, not evidence

> **Caption:** "Conceptual model of the attritional iceberg. The visible decisive shock operates atop a larger attritional substrate that has already shifted the strategic balance."

**Problem:** This is an iceberg metaphor rendered as a figure. It is a rhetorical device, not an empirical finding or a theoretical model. Placing it in the paper with a figure number gives it the visual authority of a scientific diagram. A hostile reviewer would note that the iceberg image "proves" nothing—it is an illustration of the authors' preferred narrative, presented before any evidence has been offered.

### 4.2 Figure 2 (Observed vs. Predictive DSS) has n=8

> **Caption:** "Observed versus predictive DSS for eight historical cases."

**Problem:** Eight data points do not constitute evidence of a systematic pattern. The figure shows the outcome information delta for eight wars, but these wars were selected by the authors. No discussion of selection criteria is provided. The figure visually implies a scatterplot relationship, but with n=8, any apparent pattern is within the range of random variation. The Six Day War is called out as showing the "highest positive delta," but with n=8, this is a single data point, not a finding.

### 4.3 Figure 5 (DSS vs. SES Scatter) acknowledges its own limitation in the caption

> **Caption:** "Because DSS and SES are composite indices, clustering along score boundaries may partially reflect metric construction."

**Problem:** The authors include a caveat in the figure caption acknowledging that clustering may be artifactual. This is honest, but it also undermines the figure's utility. If the spatial distribution of points in the DSS-SES space is partly an artifact of metric construction (specifically, the binary nature of five DSS components), then the figure cannot be interpreted as revealing natural groupings in conflict mechanisms. The figure should not have been presented without a more robust discussion of what the axes actually measure.

### 4.4 Figure 4 (Blind Validation) is a confusion matrix with all zeros in the diagonal

The blind validation figure shows 0% exact-match accuracy across 24 cases. The paper's treatment of this figure is a masterclass in spin: "The results are interpretable in two ways: (1) the simulation with neutral default parameters lacks discriminative power from initial conditions alone, or (2) exact-match accuracy is too strict a criterion." Interpretation (2) is unfalsifiable—if the model fails, the metric is too strict. A more honest framing would be: "The model fails its only genuine predictive test."

### 4.5 Figures 8 and 9 (Sensitivity Heatmaps) test the wrong parameters

The sensitivity analysis varies control parameters (shock strength, attrition rate, economic resilience, political resilience) and internal coefficients. But as the paper's own model assumptions audit acknowledges, the control parameters are inherently robust—they are the mechanism. The internal coefficients that actually implement the mechanisms (battle loss rate 0.04, recruitment rate 0.004, shock damage 5.0, fatigue denominator 60) are the ones that matter, and the paper reports zero classification flips for 22 of 23. The one exception—the battle loss rate—produces a 20% flip rate for Vietnam. The sensitivity heatmaps create a visual impression of robustness while testing parameters that were never at risk of producing instability.

---

## 5. METHODOLOGICAL WEAKNESSES NOT ACKNOWLEDGED

### 5.1 The logistic regression predicts duration, not mechanism

> "Table 2 presents the logistic regression results predicting war duration category (short vs. long) from material-capability features."

**Problem:** The paper's central question is about mechanisms (decisive shock vs. strategic exhaustion), but the logistic regression predicts a completely different outcome variable: war duration (short vs. long). Duration and mechanism are related but distinct concepts. A long war is not necessarily attritional (WWII lasted six years but included decisive battles), and a short war is not necessarily decisive (some short wars end in negotiated settlements). The paper conflates duration with mechanism throughout the results section, presenting the logistic regression results as if they speak to the mechanism question.

### 5.2 No cross-validation for any statistical model

The logistic regression and random forest are evaluated with a train/test split but no cross-validation. With the relatively small sample of wars with complete data (n=91 for DSS, n=1,495 for the duration model), overfitting is a serious concern. The random forest's 73.2% accuracy may not generalize. Standard practice in political science and machine learning is to report cross-validated results, especially when the dataset is small.

### 5.3 No confusion matrix, precision, or recall for the random forest

> "A random forest classifier trained on the same features achieves 73.2% test accuracy."

**Problem:** Accuracy alone is a misleading metric when classes are imbalanced. If 80% of wars are long, a classifier that always predicts "long" achieves 80% accuracy. The paper reports no confusion matrix, no precision/recall breakdown, no F1 score, and no class distribution. Without this information, 73.2% accuracy is uninterpretable.

### 5.4 Multiple testing without correction

The paper runs at least six distinct statistical analyses: (1) logistic regression, (2) random forest, (3) survival analysis, (4) mechanism classification (v2), (5) blind evaluation, and (6) parameter sensitivity analysis. No correction for multiple comparisons is applied. With six tests, the probability of at least one "significant" result at α = 0.05 is approximately 26%, even if all null hypotheses are true.

### 5.5 The v2 classifier was developed on the same data it evaluates

> "Historical mechanism classifications were assigned independently of individual simulation trajectories but were not blinded from the development team."

**Problem:** This is an explicit admission of potential confirmation bias. The authors developed the simulation, designed the v2 classifier, and assigned the historical mechanism classifications—all without blinding. They acknowledge this creates "a potential source of confirmation bias" but mitigate it by noting they used "explicit, reproducible scoring formulas." Reproducibility does not address bias: you can reproducibly encode your priors. The 86% agreement figure is meaningless without independent, blinded evaluation.

### 5.6 Regression imputation for missing SES components is unaudited

> "For conflicts where battle-level data is unavailable, we estimate missing components from aggregate war-year data using regression imputation models trained on wars with complete data."

**Problem:** The imputation methodology is not described. What regression model? What features? What is the imputation error? How does imputation quality vary across wars? If 98% of wars have imputed DSS components, and the imputation model introduces systematic bias, the entire "4,812 wars" analysis is compromised. The paper presents the integrated dataset as a technical achievement but provides no validation of the imputation pipeline.

### 5.7 The simulation has 15+ uncalibrated free parameters

The simulation includes at minimum 15 internal coefficients with no historical calibration: 0.04 (battle loss rate), 0.004 (recruitment per industrial unit), 1.5 (recruitment cap), 5.0 (shock damage), 4.0 (retaliation damage), 0.025 (war costs), 0.01 (blockade), 0.006 (industrial output), 0.2 (casualty pressure), 0.4 (weariness), 0.8 (victory bonus), 0.03 (economic hardship), 0.015 (bombing), 0.004 (recon/industrial), and 60 (fatigue denominator). These are magic numbers. The paper's sensitivity analysis tests only 4 control parameters and 23 internal coefficients, but the 23 includes only one of the above coefficients (the battle loss rate). The remaining 14+ coefficients are never varied.

### 5.8 The model omits every variable that matters in practice

The simulation models war as five scalars updated by fixed-form equations. It omits leadership, intelligence, geography, weather, technology, alliance dynamics, domestic politics (beyond a single "will" variable), media, command and control, logistics networks, terrain, naval power, air power, nuclear weapons, insurgency, terrorism, and dozens of other factors that shape real wars. The paper acknowledges this ("the model is designed to isolate the interaction between shock and attrition mechanisms") but this defense is inadequate: a model that omits everything except its own two mechanisms will inevitably find that its two mechanisms matter. This is not isolation; it is a closed system.

### 5.9 No random seed reporting

The simulation adds Gaussian noise N(0, 0.5) to all state variables each month. The paper does not report random seeds. This means results are not fully reproducible: different runs will produce different trajectories, and the classification of marginal cases may vary. For a paper that claims computational reproducibility, this is a significant omission.

---

## 6. LOGICAL GAPS IN THE ARGUMENT

### 6.1 The "rarity of decisive outcomes" conclusion is drawn from the wrong sample

> "Among the 91 wars with complete battle-level data, 2 (2.2%) are classified as decisively determined by single battles or campaigns."

**Problem:** The paper draws conclusions about the "rarity of decisive outcomes" from the 91 wars with complete data, but these 91 wars are not representative of the 4,812 wars in the dataset. They are the subset for which battle-level data exists—which means they are biased toward well-documented, primarily European and North American interstate wars. The generalization from 91 wars to "the attritional iceberg" pattern across all of warfare is unwarranted. The 4,721 wars without complete data are not evidence for the attritional hypothesis—they are evidence for data unavailability.

### 6.2 The separation of "termination events" from "strategic causes" is a definitional choice, not an empirical finding

> "This separation is the paper's core methodological contribution: a war may end because a capital falls, but the reason it became unwinnable may be exhaustion."

**Problem:** The distinction between "how wars end" and "why they became unwinnable" is a conceptual framework, not an empirical discovery. The paper defines "termination event" as the simulation's termination condition string (e.g., "decisive_victory_a") and "dominant mechanism" as the higher of the DSS and SES scores. These are defined terms, not observed phenomena. The claim that this separation is the "core methodological contribution" conflates conceptual analysis with empirical contribution. Philosophers of war have made this distinction since Clausewitz; the paper's contribution is operationalizing it in a simulation, not discovering it.

### 6.3 The falsification criteria are unfalsifiable in practice

> "If blind validation accuracy (currently based on 15 cases) converges to chance levels (~33% for three categories) as the sample grows to 50+ cases, the simulation's ability to predict termination mechanism from initial conditions alone would be falsified."

**Problem:** The current blind validation achieves 0% accuracy on 24 cases. The falsification criterion requires convergence to chance (33%) with a sample of 50+ cases. The paper claims "none of these falsification criteria have been met with current evidence." But 0% is below chance, not converging to it. The falsification criterion is set at a threshold (50+ cases, convergence to 33%) that cannot be evaluated with current data, making the claim of unfalsifiability practically moot. The paper claims falsifiability in principle while ensuring it cannot be tested in practice.

### 6.4 The model produces 0% blind accuracy but is presented as structurally robust

The paper simultaneously claims: (a) the model is "structurally robust" (0.3% mean flip rate across internal coefficients), and (b) the model achieves 0% exact-match accuracy in blind prediction. These are not compatible claims. Structural robustness means the model's output is stable—but stable output at 0% accuracy is stable failure. The sensitivity analysis demonstrates that the model is robustly wrong in its only genuine predictive test, not that it is robustly right.

### 6.5 The "attritional iceberg" is an artifact of the model's continuous attrition function

> "When the attrition rate is high, the military and economic state variables decline gradually until they cross thresholds where even a moderate shock produces collapse."

**Problem:** This is a description of how the model works, not a discovery about how wars work. The simulation's attrition function produces continuous decline by design. The fact that continuous decline precedes threshold-triggered termination is a mathematical property of the model, not an empirical finding about warfare. The paper presents this as the "attritional iceberg" pattern—as if it were a discovered feature of the real world—when it is simply a description of the simulation's dynamics. Real wars can experience sudden collapse without prolonged attritional precursors (France 1940, Kuwait 1990, the Soviet collapse 1991).

### 6.6 The paper claims to "move beyond" the binary but creates a new one

> "Our framework moves beyond the binary 'decisive or attritional?' question to ask a more nuanced question: when and why do decisive shocks matter relative to accumulated exhaustion?"

**Problem:** The hybrid classification rule (Equation 3) assigns each war to one of five categories: Data Insufficient, Uncertain, Mixed, Decisive Shock, or Strategic Exhaustion. The "Mixed" and "Uncertain" categories absorb most wars (75.8% + 1.4% = 77.2%). The paper claims this is "more nuanced" than a binary classification, but the nuance comes from a large "I don't know" category, not from genuinely intermediate classifications. The framework's actual discriminating power is limited to 22.6% of wars with complete data.

### 6.7 The paper conflates "suggests" with "concludes"

The abstract concludes: "We conclude that the scientific question is not whether wars are won by decisive battles or by attrition, but when decisive shocks exploit an exhaustion-altered state space." This is a conclusion, not a suggestion. But the evidence supporting it is: (a) a logistic regression at 54.8% accuracy, (b) a mechanism classifier tested on 7 hand-picked cases, (c) a simulation that reproduces its own parameterization, and (d) blind prediction at 0%. This is not sufficient evidence for a conclusion of this magnitude. The appropriate language would be: "Our analysis suggests, subject to significant limitations, that..."

---

## 7. STRUCTURAL AND PRESENTATION ISSUES

### 7.1 The paper contains 12 section files, 9 figures, and multiple tables—yet the core evidence is 7 case studies

The paper is long, detailed, and technically sophisticated. But the weight of the apparatus is disproportionate to the evidence. The core validation exercise evaluates 7 cases. The blind validation evaluates 24. The logistic regression operates on a different dependent variable than the paper's central question. The simulation is circular. Strip away the apparatus, and the paper's contribution is: two new composite indices, applied to 91 wars, validated on 7 hand-picked cases, with 0% predictive accuracy in blind tests.

### 7.2 The bibliography is thin for a literature review paper

The background section cites 12 sources for a topic with hundreds of relevant works. Key omissions include: Zetterling (2012) on decisive battles, Strachan (2001) on WWI strategy, Posen (1984) on military doctrine, Terraine (1987) on attrition warfare, van Creveld (1977) on supply and logistics, and Keegan (1976) on the nature of combat. The selective citation creates the impression of a literature review while actually engaging with a narrow slice of the relevant scholarship.

### 7.3 The author is listed as "Data Scientist" with no institutional affiliation

This is not a methodological critique per se, but for a top-tier political science journal, the absence of an institutional affiliation, departmental home, or co-author with domain expertise in strategic studies or conflict research raises questions about peer review within the author's own intellectual community. The paper engages with a rich theoretical tradition (Mahan, Clausewitz, Luttwak, Biddle) but shows no evidence of engagement with the scholars who currently work on these questions.

---

## 8. SUMMARY OF CRITICAL FAILURES

| # | Problem | Category | Severity |
|---|---------|----------|----------|
| 1 | Simulation-derived DSS measures its own shock function output | Circularity | Fatal |
| 2 | Historical presets encode the answer (shock=90 for decisive wars, attrition=80 for attritional) | Circularity | Fatal |
| 3 | 0% blind prediction accuracy, treated as a minor caveat | Logical gap | Fatal |
| 4 | 86% agreement on 7 hand-picked, non-blinded cases presented as a headline result | Overclaim | Severe |
| 5 | Logistic regression at 54.8% accuracy presented as a finding | Overclaim | Severe |
| 6 | DSS and SES component weights have no documented derivation | Methodology | Severe |
| 7 | Classification thresholds calibrated on "a small golden set" with no out-of-sample test | Methodology | Severe |
| 8 | Multiple testing without correction (6+ analyses) | Methodology | Moderate |
| 9 | No cross-validation for ML models | Methodology | Moderate |
| 10 | Random forest accuracy reported without confusion matrix or class distribution | Methodology | Moderate |
| 11 | The "4,812 wars" claim obscures that 98% lack DSS data | Overclaim | Moderate |
| 12 | Duration regression conflated with mechanism classification | Logical gap | Moderate |
| 13 | Conceptual model figure (iceberg) presented as scientific evidence | Misleading figure | Moderate |
| 14 | N=8 scatterplot (Figure 2) presented as systematic pattern | Misleading figure | Moderate |
| 15 | Sedan "effectively ended" the Franco-Prussian War (it did not) | Historical error | Minor |
| 16 | Gulf War description omits the 6-week air campaign | Historical selectivity | Minor |
| 17 | 15+ simulation coefficients have no historical calibration | Methodology | Moderate |
| 18 | Regression imputation for missing data is unaudited | Methodology | Moderate |
| 19 | No random seeds reported | Reproducibility | Minor |
| 20 | Falsification criteria require data that doesn't exist yet | Logical gap | Moderate |

---

## 9. RECOMMENDATION

**Reject.**

This paper has a genuinely interesting core idea—the interaction between decisive shocks and attritional processes in war termination—but the execution is fundamentally flawed. The simulation is circular by construction. The validation is on non-blinded hand-picked cases. The blind prediction achieves 0%. The statistical evidence barely exceeds chance. The composite metrics have unvalidated weights and thresholds. The "attritional iceberg" is an artifact of the model's continuous attrition function, not an empirical discovery.

A revised version would need to: (a) eliminate the circular simulation-derived metrics entirely, relying only on the empirical DSS/SES computed from external data; (b) conduct blinded, pre-registered validation on a held-out sample; (c) report cross-validated results with full confusion matrices for all classifiers; (d) justify every weight, threshold, and coefficient with documented historical evidence or treat them as free parameters with uncertainty; (e) substantially reduce causal language throughout; and (f) engage seriously with the existing literature on the shock-attrition interaction rather than claiming to have identified a new phenomenon.

As it stands, this paper does not meet the standards of a top-tier political science journal.

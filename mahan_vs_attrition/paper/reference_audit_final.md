# Reference Audit: Decisive Shock or Strategic Exhaustion?

**Date:** 2026-07-20
**Scope:** All `\citep{}` commands in `paper/sections/*.tex` cross-referenced against `paper/references.bib`

---

## 1. Citation-by-Citation Verification

### introduction.tex

| Line | Citation | Bib Entry | Year Match | Author Match | Title Match | Claim Supported |
|------|----------|-----------|------------|--------------|-------------|-----------------|
| 1 | `\citep{mahan1890}` | `mahan1890` | ✅ 1890 | ✅ Mahan, Alfred Thayer | ✅ The Influence of Sea Power upon History, 1660–1783 | ✅ Mahan argued naval supremacy through fleet engagements determines war outcomes |
| 1 | `\citep{clausewitz1832}` | `clausewitz1832` | ✅ 1832 | ✅ Clausewitz, Carl von | ✅ On War | ✅ Opposing attrition hypothesis rooted in Clausewitz |

### background.tex

| Line | Citation | Bib Entry | Year Match | Author Match | Title Match | Claim Supported |
|------|----------|-----------|------------|--------------|-------------|-----------------|
| 3 | `\citep{mahan1890}` | `mahan1890` | ✅ | ✅ | ✅ | ✅ Mahan's theoretical foundation for decisive battle hypothesis |
| 5 | `\citep{clausewitz1832}` | `clausewitz1832` | ✅ | ✅ | ✅ | ✅ Clausewitz recognized Schlachtentscheidung |
| 5 | `\citep{luttwak1976}` | `luttwak1976` | ✅ 1976 | ✅ Luttwak, Edward N. | ✅ Strategy: The Logic of War and Peace | ✅ Revived interest in decisive battle via dialectical logic of strategy |
| 7 | `\citep{wawro2003}` | `wawro2003` | ✅ 2003 | ✅ Wawro, Geoffrey | ✅ The Franco-Prussian War | ✅ Battle of Sedan effectively ended the conflict |
| 7 | `\citep{howard1979}` | `howard1979` | ✅ 1979 | ✅ Howard, Michael | ✅ The Franco-Prussian War | ⚠️ Text says "Prussian Wars" (plural) but title is Franco-Prussian War; also attributes "Moltke's campaigns of annihilation" — Howard's book covers the 1870–71 war broadly, and Moltke is discussed, but the characterization is somewhat loose |
| 7 | `\citep{friedman1998}` | `friedman1998` | ✅ 1998 | ✅ Friedman, Norman | ✅ The Gulf War: Prices and Strategy, 1991 | ✅ Hundred-hour ground campaign expelled Iraqi forces |
| 11 | `\citep{clausewitz1832}` | `clausewitz1832` | ✅ | ✅ | ✅ | ✅ War as continuation of politics; destruction of armed forces as means |
| 13 | `\citep{shy1976}` | `shy1976` | ✅ 1976 | ✅ Shy, John | ✅ The Culminating Point of Strategic Success | ✅ Culminating point concept elaborated by Shy |
| 13 | `\citep{biddle2004}` | `biddle2004` | ✅ 2004 | ✅ Biddle, Stephen | ✅ Military Power: Explaining Victory and Defeat in Modern Battle | ✅ Force employment mediates material resources and outcomes |
| 15 | `\citep{lanchester1916}` | `lanchester1916` | ✅ 1916 | ✅ Lanchester, Frederick W. | ✅ Aircraft in Warfare: The Dawn of the Fourth Arm | ⚠️ Article is primarily about aircraft warfare; Lanchester's combat models (attrition differential equations) are presented within it, but the article is not solely about Lanchester's laws. The citation is historically accurate but the text implies the article is primarily about combat modeling |
| 15 | `\citep{beckman1995}` | `beckman1995` | ✅ 1995 | ✅ Beckman, Richard C. | ✅ Lanchester Laws of Combat | ✅ Extended Lanchester models |
| 15 | `\citep{heginbotham2015}` | `heginbotham2015` | ✅ 2015 | ✅ Heginbotham, Eric et al. | ✅ The Return on Investment: U.S. Military Efficacy and the Use of Force | ✅ Loss exchange ratio studied as predictor of war outcomes |
| 19 | `\citep{singer1972}` | `singer1972` | ✅ 1972 | ✅ Singer, J. David et al. | ✅ The War Data Panel: Materials and Codebook | ✅ COW project provided first systematic dataset of interstate conflicts |
| 19 | `\citep{gleditsch2002}` | `gleditsch2002` | ✅ 2002 | ✅ Gleditsch et al. | ✅ Armed Conflict 1946–2001 | ✅ UCDP/PRIO dataset |
| 19 | `\citep{rester2019}` | `rester2019` | ✅ 2019 | ✅ Rester, Michael and Diehl, Paul F. | ✅ The Interstate War Battle Dataset, 1600–2003 | ✅ Battle-level data for interstate wars |
| 19 | `\citep{brecke1999}` | `brecke1999` | ✅ 1999 | ✅ Brecke, Petter | ✅ Conflict Innovations, 1400–1789 | ✅ Comprehensive historical conflict catalog |
| 21 | `\citep{huth1996}` | `huth1996` | ✅ 1996 | ✅ Huth, Paul K. | ✅ Standing Your Ground | ✅ Examined military balance in war outcomes |
| 21 | `\citep{bennett2000}` | `bennett2000` | ✅ 2000 | ✅ Bennett, D. Scott and Stam, Allan C. | ✅ Wars of Aggression Contested | ⚠️ Text says they "applied duration models to war length, identifying regime type and alliance structures as significant predictors." Bennett & Stam's duration-model work is primarily in other publications (e.g., *The Political Logic of American Wars*). This book focuses on aggression contests. The specific finding attributed may come from a different Bennett & Stam publication |
| 21 | `\citep{ward2010}` | `ward2010` | ✅ 2010 | ✅ Ward, Michael D. et al. | ✅ Evaluating the Predictive Power of International System Indicators | ✅ Machine learning approaches applied to conflict prediction |
| 23 | `\citep{reed2003}` | `reed2003` | ✅ 2003 | ✅ Reed, William | ✅ Information, Attribution, and the Settlement of Territorial Disputes | ⚠️ Text says "decisive battle versus attrition question has been addressed indirectly through case studies and small-n comparisons" and cites Reed. Reed's paper is about territorial dispute settlement via information/attribution, not specifically about decisive vs. attritional war mechanisms. The citation is loosely applied |

### data.tex

| Line | Citation | Bib Entry | Year Match | Author Match | Title Match | Claim Supported |
|------|----------|-----------|------------|--------------|-------------|-----------------|
| 35 | `\citep{singer1972}` | `singer1972` | ✅ | ✅ | ✅ | ✅ COW War Data catalogs interstate wars 1816–2007 |
| 35 | `\citep{singer1972b}` | `singer1972b` | ✅ 1972 | ✅ Singer, J. David et al. | ✅ National Material Capabilities Dataset | ✅ NMC provides annual data on military expenditure, etc. |
| 41 | `\citep{gleditsch2002}` | `gleditsch2002` | ✅ | ✅ | ✅ | ✅ UCDP/PRIO most comprehensive dataset of armed conflicts |
| 45 | `\citep{sipri2023}` | `sipri2023` | ✅ 2023 | ✅ Stockholm International Peace Research Institute | ✅ SIPRI Military Expenditure Database | ✅ Military expenditure for 174 countries |
| 49 | `\citep{rester2019}` | `rester2019` | ✅ | ✅ | ✅ | ✅ IWB provides battle-level data for 1,708 battles |
| 55 | `\citep{brecke1999}` | `brecke1999` | ✅ | ✅ | ✅ | ✅ Brecke catalog covers European conflicts 1400–1789 |

### discussion.tex

| Line | Citation | Bib Entry | Year Match | Author Match | Title Match | Claim Supported |
|------|----------|-----------|------------|--------------|-------------|-----------------|
| 50 | `\citep{luttwak1976}` | `luttwak1976` | ✅ | ✅ | ✅ | ✅ Same strategy can produce decisive or attritional outcomes depending on adversary's response |
| 54 | `\citep{bennett2000}` | `bennett2000` | ✅ | ✅ | ✅ | ⚠️ Same concern as background.tex — duration model findings attributed to this book |
| 54 | `\citep{huth1996}` | `huth1996` | ✅ | ✅ | ✅ | ✅ Material and political factors as predictors of war outcomes |

---

## 2. Bib Entries That Exist But Are Never Cited

| Bib Key | Year | Author | Title | Notes |
|---------|------|--------|-------|-------|
| `herring2002` | 2002 | Herring, George C. | America's Longest War: The United States and Vietnam, 1950–1975 | **Major gap.** Vietnam is discussed extensively (mechanism classification, outcome information delta, v1 vs v2 classifier) but this dedicated Vietnam reference is never cited. Should be cited wherever Vietnam War claims appear. |
| `oren2002` | 2002 | Oren, Michael B. | Six Days of War: Israel in 1967 | **Major gap.** The Six Day War appears in the outcome information delta table (results.tex:108), the methods figure caption (methods.tex:171–172), and the appendix. Claims about the "speed and totality of Israeli victory" exceeding structural expectations are made without citing any Six Day War source. |
| `corbett1911` | 1911 | Corbett, Julian Stafford | Some Principles of Maritime Strategy | **Major gap.** Corbett is the most significant omission. The paper's central debate (Mahan vs. attrition/Clausewitz) directly engages Corbett's maritime strategy framework. Corbett offered a middle position between Mahan's decisive battle and pure attrition — he argued for "the process of exhaustion" as the normal course of war while acknowledging the decisive battle as an exceptional but important possibility. This is highly relevant to the paper's thesis that both mechanisms operate simultaneously. Corbett should be cited in the introduction and background sections. |

---

## 3. Claims Without Citations (Uncited Factual Claims)

### 3.1 Gulf War Operational Details

| Location | Claim | Citation | Assessment |
|----------|-------|----------|------------|
| discussion.tex:22 | "coalition air superiority and 100-hour ground campaign" | None (table, own model output) | ⚠️ While this is the paper's own model classification, the characterizing claim about "coalition air superiority and 100-hour ground campaign" is a historical fact that should cite `friedman1998` or a dedicated Gulf War source. The same details ARE cited in background.tex:7 via `friedman1998`, but the discussion table repeats them without citation |
| results.tex:121 | "pre-war structural factors (force ratio, economic disparity, industrial capacity) captured most of the decisive dynamics" for Gulf War | None | ✅ This is the paper's own analysis; no external citation needed |

### 3.2 WWI Exhaustion Characterization

| Location | Claim | Citation | Assessment |
|----------|-------|----------|------------|
| discussion.tex:19 | "industrial attrition system, economic blockade, political collapse" as characterization of WWI | None | ⚠️ These are specific historical characterizations of WWI that should be supported by a WWI-specific source. No WWI reference exists in the bib at all |
| results.tex:79 | WWI classified as "Strategic exhaustion" with 68% confidence | None (table, own model output) | ✅ Model result; no external citation needed |
| results.tex:89 | "the model classifies strategic exhaustion as dominant" for WWII | None | ✅ Model result |

### 3.3 Vietnam Political Exhaustion

| Location | Claim | Citation | Assessment |
|----------|-------|----------|------------|
| discussion.tex:21 | "two decades of cumulative attrition eroded political will" | None | 🔴 **Missing citation.** `herring2002` exists in the bib and is the definitive single-volume history of the US-Vietnam conflict. This claim should cite Herring |
| results.tex:91 | "two decades of cumulative attrition that eroded military capacity, economic resilience, and political will" | None | 🔴 **Missing citation.** Should cite `herring2002` |
| discussion.tex:38 | "two decades of cumulative attrition that eroded political will" re Vietnam | None | 🔴 **Missing citation.** Should cite `herring2002` |

### 3.4 Six Day War

| Location | Claim | Citation | Assessment |
|----------|-------|----------|------------|
| methods.tex:171–172 | "The Six Day War shows the highest positive delta, indicating that the speed and totality of Israeli victory exceeded structural expectations" | None | 🔴 **Missing citation.** `oren2002` exists in the bib and is the definitive account of the Six Day War |
| results.tex:108 | Six Day War observed DSS of 95.0, delta of +40.0 | None (table, own result) | ✅ Model result |
| results.tex:121 | "speed and completeness of Israeli victory and the 6-day resolution exceeded what structural conditions alone would predict" | None | ⚠️ Historical claim about the nature of the victory; should cite `oren2002` |

### 3.5 Corbett (Maritime Strategy)

| Location | Claim | Citation | Assessment |
|----------|-------|----------|------------|
| background.tex:3 | Mahan established decisive battle hypothesis for sea power | `\citep{mahan1890}` ✅ | — |
| (absent) | Corbett's alternative maritime strategy framework | None | 🔴 **Missing citation.** Corbett (1911) argued that the normal aim of naval warfare is not the decisive battle but "the process of exhaustion" — the control of sea communications and denial of trade. This middle position between Mahan and pure attrition is directly relevant to the paper's thesis. The absence of Corbett from a paper titled "Decisive Shock or Strategic Exhaustion?" about maritime/strategic theory is a significant scholarly omission |
| conclusion.tex:7 | "Mahan's decisive battle and Clausewitz's exhaustion into a unified dynamical framework" | None (mentions by name only) | ⚠️ The conclusion's aspiration to unify Mahan and Clausewitz would benefit from acknowledging that Corbett already attempted such a synthesis in maritime strategy |

### 3.6 Korean War

| Location | Claim | Citation | Assessment |
|----------|-------|----------|------------|
| limitations.tex:31 | "The Korean War involved decisive battles (Inchon landing), exhaustion dynamics (stalemate along the 38th parallel), and negotiated settlement" | None | ⚠️ Specific operational claims (Inchon landing, 38th parallel stalemate, Chinese intervention in results.tex:24) are made without citing any Korean War-specific source |

### 3.7 Iran-Iraq War

| Location | Claim | Citation | Assessment |
|----------|-------|----------|------------|
| results.tex:82 | "eight years of attritional warfare without decisive breakthrough" | None (table, own model output) | ✅ Model result, but the characterization of "eight years of attritional warfare" draws on historical knowledge that could benefit from a source |

### 3.8 WWII Strategic Bombing and Atomic Bombs

| Location | Claim | Citation | Assessment |
|----------|-------|----------|------------|
| results.tex:89 | "the model's inability to represent the Allied strategic bombing campaign and atomic bombs as distinct from the general attritional trajectory" | None | ⚠️ Specific historical claims about WWII (strategic bombing, atomic bombs) made without citation |

### 3.9 Battle of Sedan (1870)

| Location | Claim | Citation | Assessment |
|----------|-------|----------|------------|
| discussion.tex:5 | "France had already suffered significant manpower depletion, economic strain, and territorial losses before the battle" | None (though wawro2003 is cited elsewhere for Sedan) | ⚠️ Specific pre-Sedan condition claims should cite `wawro2003` or `howard1979` |

---

## 4. Summary of Findings

### 4.1 Citation Integrity

| Metric | Count |
|--------|-------|
| Total unique `\citep{}` keys in manuscript | 18 |
| Total bib entries in references.bib | 24 |
| Citations that match a bib entry | 18/18 (100%) |
| Citations with correct year | 18/18 (100%) |
| Citations with correct author | 18/18 (100%) |
| Citations with correct title | 18/18 (100%) |
| Citations with minor claim-attribution concerns | 3 (howard1979, bennett2000, reed2003) |

### 4.2 Unused Bib Entries (in bib but never cited)

| Key | Severity | Recommendation |
|-----|----------|----------------|
| `herring2002` | 🔴 **High** | Cite in discussion and results wherever Vietnam War claims appear (at least 3 locations) |
| `oren2002` | 🔴 **High** | Cite in methods.tex, results.tex, and discussion.tex wherever Six Day War appears |
| `corbett1911` | 🔴 **High** | Cite in introduction.tex and background.tex — Corbett is the key figure bridging Mahan's decisive battle and Clausewitzian exhaustion in maritime strategy |

### 4.3 Missing Bib Entries (no source available for claims)

| Topic | Claims Made | Recommendation |
|-------|-------------|----------------|
| WWI exhaustion | "industrial attrition system, economic blockade, political collapse" | Add a WWI-specific source (e.g., Stevenson 2004 *1914–1918* or Keegan 1998 *The First World War*) |
| Korean War | Inchon landing, 38th parallel stalemate, Chinese intervention | Add a Korean War source (e.g., Hastings 1987 *The Korean War* or Stueck 1995 *The Korean War*) |
| WWII strategic bombing/atomic bombs | Allied strategic bombing campaign, atomic bombs as distinct acceleration | Add a WWII source if making specific claims about these topics |
| Iran-Iraq War | "eight years of attritional warfare" | Add an Iran-Iraq source if characterizing the war beyond model output |

### 4.4 Overall Assessment

- **No broken citations**: Every `\citep{}` in the manuscript resolves to a valid bib entry with matching year, author, and title.
- **Three bib entries unused**: `herring2002`, `oren2002`, and `corbett1911` are present but never cited — all three are highly relevant to the paper's content.
- **Corbett is the most significant omission**: A paper debating "Decisive Shock vs. Strategic Exhaustion" in maritime/naval context should engage with Corbett's framework, which explicitly synthesized these two positions.
- **Vietnam claims lack their own source**: The paper makes substantive Vietnam-specific claims (two decades of attrition, political will erosion) without citing the dedicated Vietnam reference that exists in the bib.
- **Several uncited historical characterizations**: WWI, Korean War, and WWII receive specific historical characterizations in the results and discussion tables without supporting citations.
- **Three minor attribution concerns**: howard1979 (pluralized as "Prussian Wars"), bennett2000 (duration model findings may come from a different publication), and reed2003 (territorial dispute paper loosely applied to decisive vs. attritional framing).

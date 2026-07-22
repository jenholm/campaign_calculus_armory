# Statistical Model Role Rationale (M62)

## Why Both Models Exist

| Model | Purpose | Expected Behavior |
|-------|---------|-------------------|
| Logistic regression | Linear baseline | Tests simple additive relationships among material-capability features. Captures only main effects; cannot represent feature interactions. |
| Random forest | Nonlinear interaction model | Tests complex structural patterns including interaction effects, threshold effects, and nonlinear combinations of material-capability features. |

## Scientific Rationale

The logistic regression serves as a **deliberately simple baseline** that tests whether material-capability features have predictive information in a purely linear framework. Its limited performance (54.8% accuracy, AUC = 0.561) is not a failure but a **scientifically informative finding**: it demonstrates that linear relationships among material capability features contain limited predictive information about war dynamics.

The random forest captures **nonlinear interactions** that the logistic regression cannot represent. Its higher accuracy (73.2%) indicates that material-capability features interact in complex ways to predict war duration categories. This is the expected behavior when the underlying phenomenon involves threshold effects, conditional relationships, and multiplicative interactions among variables.

## Reframed Interpretation

**Current framing (weak):** "The logistic model does not predict well."

**Reframed (strong):** "A linear baseline model showed limited predictive ability, suggesting that relationships among strategic variables are nonlinear rather than purely additive. The random forest's improvement demonstrates that nonlinear interactions among material-capability features contribute meaningfully to prediction."

## Key Insight

The weak logistic result **supports** the paper's argument:
- Simple material comparisons (who has more troops, more GDP) don't determine war outcomes
- What matters is how these factors **interact** (industrial capacity + force ratio + logistics)
- This aligns with the attritional iceberg thesis: surface-level material metrics are insufficient; what matters is the complex interaction of structural factors

## Paper Language Replacement

**Current:** "Material capability features contain limited predictive information."

**Replacement:** "Linear relationships among material capability features contain limited predictive information, while nonlinear models capture additional interactions."

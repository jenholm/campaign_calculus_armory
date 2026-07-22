# Equation Audit (M68)

## Equation 5 (Population Support Update)

### Current Form
```
Pop(t+1) = Pop(t) - max(0, 50 - Econ(t)) * rho_bar * 0.03 * f(t)
           - Delta_Mil * 0.15 * 0.2
```

### Issue
The expression `0.15 * 0.2` is awkward and should be simplified.

### Simplified Form
```
Pop(t+1) = Pop(t) - max(0, 50 - Econ(t)) * rho_bar * 0.03 * f(t)
           - 0.03 * Delta_Mil
```

### Verification
- `0.15 * 0.2 = 0.03` ✓
- The coefficient represents the casualty pressure on population support: 3% of battle losses per capita

### Recommendation
Change to `0.03 * Delta_Mil` for clarity. Add comment: "Casualty pressure on population support."

## Equation 7 (Political Will Update)

### Current Form
```
Pol(t+1) = Pol(t) - Delta_Mil * 0.2 - rho_bar * 0.4 * f(t) * (1 - pi/200) + v(t)
```

### Issue
- `Delta_Mil * 0.2` is the casualty pressure coefficient
- `rho_bar * 0.4 * f(t) * (1 - pi/200)` is the war-weariness term
- These are already clean; no simplification needed

### Verification
- The `1 - pi/200` factor maps political resilience [0, 100] to resistance [0.5, 1.0]
- The `v(t) = 0.8` victory bonus is straightforward

### Recommendation
No change needed. The equation is already reasonably clean.

## Shock Equations (Equations 10-12)

### Current Form
```
Mil_B(t) <- Mil_B(t) - sigma * 5.0
Ind_B(t) <- Ind_B(t) - sigma * 5.0 * 0.25
Pol_B(t) <- Pol_B(t) - sigma * 5.0 * 0.2
```

### Issue
`sigma * 5.0 * 0.25` and `sigma * 5.0 * 0.2` are awkward.

### Simplified Form
```
Mil_B(t) <- Mil_B(t) - sigma * 5.0
Ind_B(t) <- Mil_B(t) - sigma * 1.25
Pol_B(t) <- Pol_B(t) - sigma * 1.0
```

### Verification
- `5.0 * 0.25 = 1.25` ✓
- `5.0 * 0.2 = 1.0` ✓

### Recommendation
Use the simplified forms. Add explanatory comments:
- Military damage: base shock magnitude
- Industrial damage: 25% of military damage
- Political damage: 20% of military damage

## Coefficient Justification Summary

| Coefficient | Value | Justification |
|-------------|-------|---------------|
| Battle loss rate (0.04) | Calibrated | Tuned so weakest sides degrade over 20-40 months |
| Recruitment rate (0.004) | Calibrated | Industrial output feeds military replenishment |
| Economic war costs (0.025) | Calibrated | Sustained warfare degrades economic capacity |
| Blockade (0.01) | Calibrated | Secondary economic pressure |
| Casualty pressure on pol (0.2) | Assumption | 20% of battle losses transfer to political will |
| Weariness (0.4) | Calibrated | War-weariness accumulation rate |
| Shock damage (5.0) | Calibrated | Monthly shock magnitude for decisive events |
| Retaliation (4.0) | Assumption | Counter-force retaliation scaling |
| DSS military factor (50.0) | Normalization | Maps military shock to [0, 100] scale |
| Capital bonus (30.0) | Normalization | Bonus for crossing military threshold |
| Surrender bonus (20.0) | Normalization | Bonus for political will collapse |
| SES weights (0.3/0.3/0.2/0.2) | Literature | Military/economic/political/duration decomposition |

## Summary

- Equation 5: Simplify `0.15 * 0.2` to `0.03`
- Equations 10-12: Simplify `5.0 * 0.25` and `5.0 * 0.2`
- All coefficients: classified as calibrated (majority) or assumption-based
- No mathematical errors found

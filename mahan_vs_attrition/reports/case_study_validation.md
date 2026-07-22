# Case Study Validation Report

## Summary
- Total case studies: 10
- Evaluated against model: 6
- Classification agreement: 3/6 (50.0%)
- Mean DSS delta (model - manual): -6.0
- Mean SES delta (model - manual): +0.0

## Per-case comparison

| War | Manual DSS | Manual SES | Manual Class | Model DSS | Model SES | Model Class | Agreement | Notes |
|---|---:|---:|---:|---:|---:|---:|:---:|---|
| Franco-Prussian War | 85 | 45 | decisive_battle_or_campaign | 66 | 45 | decisive_battle_or_campaign | OK | OK |
| Russo-Japanese War | 55 | 70 | mixed | 50 | 70 | strategic_exhaustion | X | Classification mismatch: manual=mixed vs model=strategic_exhaustion; Manual mechanism 'mixed' classifies as mixed but manual DSS/SES thresholds would give mixed_or_uncertain |
| Gulf War 1991 | 80 | 25 | decisive_battle_or_campaign | 70 | 25 | decisive_battle_or_campaign | OK | OK |
| World War I | 60 | 90 | mixed | 58 | 90 | strategic_exhaustion | X | Classification mismatch: manual=mixed vs model=strategic_exhaustion; Manual mechanism 'mixed' classifies as mixed but manual DSS/SES thresholds would give strategic_exhaustion |
| World War II Pacific | 50 | 90 | mixed | 49 | 90 | strategic_exhaustion | X | Classification mismatch: manual=mixed vs model=strategic_exhaustion; Manual mechanism 'mixed' classifies as mixed but manual DSS/SES thresholds would give strategic_exhaustion |
| Vietnam War | 30 | 85 | strategic_exhaustion | 30 | 85 | strategic_exhaustion | OK | OK |
| Thirty Years War | 25 | 85 | strategic_exhaustion | n/a | n/a | n/a | ? | OK |
| Peloponnesian War | 55 | 90 | strategic_exhaustion | n/a | n/a | n/a | ? | OK |
| Second Punic War | 45 | 85 | strategic_exhaustion | n/a | n/a | n/a | ? | OK |
| Mongol Conquest of Khwarezm | 90 | 40 | decisive_battle_or_campaign | n/a | n/a | n/a | ? | OK |

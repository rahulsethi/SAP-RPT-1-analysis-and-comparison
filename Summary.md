# Summary — RPT-1 vs GPT-5 (ML) vs GPT-5 Standalone

## TL;DR
- We compare methods only on rows marked [PREDICT]; pairwise MAE shows disagreement (not accuracy).
- In this run, GPT-5 (ML) and GPT-5 Standalone align on PREDICT rows; both diverge similarly from RPT-1.

## SC1 — Equipment Sourcing (CO2e)
- PREDICT rows: 3
- GPT-5 (ML) vs RPT-1: MAE=15.207, MaxΔ=32.940
- GPT-5 Standalone vs RPT-1: MAE=15.207, MaxΔ=32.940
- GPT-5 Standalone vs GPT-5 (ML): MAE=0.000, MaxΔ=0.000

## SC2 — Predictive Maintenance (RUL)
- PREDICT rows: 5
- GPT-5 (ML) vs RPT-1: MAE=45.860, MaxΔ=187.200
- GPT-5 Standalone vs RPT-1: MAE=45.860, MaxΔ=187.200
- GPT-5 Standalone vs GPT-5 (ML): MAE=0.000, MaxΔ=0.000

## Methods (One-liners)
- RPT-1: SAP baseline (black box).
- GPT-5 (ML): Intended — linear model for SC1, gradient boosting for SC2.
- GPT-5 Standalone: Transparent rules — grouped means + quantity slope (SC1); KNN with robust scaling (SC2).

## Decision Guidance
- Use GPT-5 Standalone when auditability is key; consider GPT-5 (ML) if backtested accuracy gains justify complexity.
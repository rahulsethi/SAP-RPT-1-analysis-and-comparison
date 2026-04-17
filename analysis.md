# Comparative Analysis: RPT-1 vs GPT-5 (ML) vs GPT-5 Standalone

## Executive Summary
- This document summarizes pairwise disagreement metrics between three approaches on rows explicitly marked as [PREDICT] in your input files.
- Without ground truth for [PREDICT] rows, we use pairwise Mean Absolute Error (MAE) as a proxy to indicate how much the methods diverge.

## Files Considered
- SC1 Input: SC1 Equipment Sourcing/SC1_input data/Equipment data.csv
- SC1 Outputs: RPT-1, GPT-5 (ML), GPT-5 Standalone under SC1 Equipment Sourcing/SC1_output/
- SC2 Input: SC2 Predictive Maintainence/SC2_input data/Predictive_maintainence.csv
- SC2 Outputs: RPT-1, GPT-5 (ML), GPT-5 Standalone under SC2 Predictive Maintainence/SC2_output/

## Artifacts & Traceability
- Comparison workbook: [comparison_RPT1_GPT5ML_GPT5standalone.xlsx](comparison_RPT1_GPT5ML_GPT5standalone.xlsx) (original) and [comparison_RPT1_GPT5ML_GPT5standalone_v2.xlsx](comparison_RPT1_GPT5ML_GPT5standalone_v2.xlsx) (with "How to read this workbook" on the Summary sheet)

- SC1 — Equipment Sourcing
	- Input: [SC1 Equipment Sourcing/SC1_input data/Equipment data.csv](SC1%20Equipment%20Sourcing/SC1_input%20data/Equipment%20data.csv)
	- RPT‑1 output: [SC1 Equipment Sourcing/SC1_output/RPT-1 output/Equipment data prediction output RPT-1.csv](SC1%20Equipment%20Sourcing/SC1_output/RPT-1%20output/Equipment%20data%20prediction%20output%20RPT-1.csv)
	- GPT‑5 (ML) predictions: [SC1 Equipment Sourcing/SC1_output/GPT 5 output/Equipment data prediction output GPT-5.csv](SC1%20Equipment%20Sourcing/SC1_output/GPT%205%20output/Equipment%20data%20prediction%20output%20GPT-5.csv)
	- GPT‑5 (ML) explanation: [SC1 Equipment Sourcing/SC1_output/GPT 5 output/Equipment data prediction output GPT-5_explanation.csv](SC1%20Equipment%20Sourcing/SC1_output/GPT%205%20output/Equipment%20data%20prediction%20output%20GPT-5_explanation.csv)
	- GPT‑5 Standalone predictions: [SC1 Equipment Sourcing/SC1_output/GPT 5 output/Equipment data prediction output GPT5_standalone.csv](SC1%20Equipment%20Sourcing/SC1_output/GPT%205%20output/Equipment%20data%20prediction%20output%20GPT5_standalone.csv)
	- GPT‑5 Standalone explanation: [SC1 Equipment Sourcing/SC1_output/GPT 5 output/Equipment data prediction output GPT5_standalone_explanation.csv](SC1%20Equipment%20Sourcing/SC1_output/GPT%205%20output/Equipment%20data%20prediction%20output%20GPT5_standalone_explanation.csv)

- SC2 — Predictive Maintainence
	- Input: [SC2 Predictive Maintainence/SC2_input data/Predictive_maintainence.csv](SC2%20Predictive%20Maintainence/SC2_input%20data/Predictive_maintainence.csv)
	- RPT‑1 output: [SC2 Predictive Maintainence/SC2_output/RPT-1 output/predicitve_maintainence RPT-1 output.csv](SC2%20Predictive%20Maintainence/SC2_output/RPT-1%20output/predicitve_maintainence%20RPT-1%20output.csv)
	- GPT‑5 (ML) predictions: [SC2 Predictive Maintainence/SC2_output/GPT-5 output/predictive_maintainence GPT-5 output.csv](SC2%20Predictive%20Maintainence/SC2_output/GPT-5%20output/predictive_maintainence%20GPT-5%20output.csv)
	- GPT‑5 (ML) explanation: [SC2 Predictive Maintainence/SC2_output/GPT-5 output/predictive_maintainence GPT-5 output_explanation.csv](SC2%20Predictive%20Maintainence/SC2_output/GPT-5%20output/predictive_maintainence%20GPT-5%20output_explanation.csv)
	- GPT‑5 Standalone predictions: [SC2 Predictive Maintainence/SC2_output/GPT-5 output/predictive_maintainence GPT5_standalone output.csv](SC2%20Predictive%20Maintainence/SC2_output/GPT-5%20output/predictive_maintainence%20GPT5_standalone%20output.csv)
	- GPT‑5 Standalone explanation: [SC2 Predictive Maintainence/SC2_output/GPT-5 output/predictive_maintainence GPT5_standalone output_explanation.csv](SC2%20Predictive%20Maintainence/SC2_output/GPT-5%20output/predictive_maintainence%20GPT5_standalone%20output_explanation.csv)

## Input Files Overview

### SC1 — Equipment Sourcing (Equipment data.csv)
- Purpose: Predict per-order CO2e to compare sourcing decisions and logistics impacts.
- Target column: `CO2e` (numeric). Rows with `[PREDICT]` require a model estimate.
- Key columns:
	- `OrderID`: Unique order identifier (join key across outputs).
	- `CO2e`: Emissions in kg CO2e (ground truth when present, else `[PREDICT]`).
	- `Product`: Purchased item (e.g., Laptop, Desk, Printer Toner, Paper Ream).
	- `Group`: Product group/category (e.g., Electronics, Furniture, Supplies).
	- `Urgency`: Shipping priority (e.g., Urgent, Standard) — proxy for mode/expedite.
	- `Quantity`: Ordered units — influences load consolidation and emissions scaling.
	- `Destination`: Delivery city/region — affects lane distance/mode.
	- `Supplier`: Fulfilling supplier — proxy for source location and packaging/mix.

### SC2 — Predictive Maintainence (Predictive_maintainence.csv)
- Purpose: Predict Remaining Useful Life (RUL) to inform maintenance planning.
- Target column: `RUL` (numeric). Rows with `[PREDICT]` require a model estimate.
- Key columns:
	- `Equipment ID`: Unique asset identifier (join key across outputs).
	- `Equipment Age`: Time in service (months or similar unit).
	- `Operating Envr`: Environment category (e.g., Indoor Clean, Outdoor Harsh, Marine).
	- `Operating Hours`: Cumulative run hours.
	- `Current Vibration`: Condition indicator (higher often correlates with wear).
	- `Temp Operating`: Operating temperature proxy.
	- `Load Factor`: Typical load relative to rated capacity.
	- `Maintenance Strat`: Policy in place (Reactive/Preventive/Predictive/Condition Based).
	- `Last Maintenance`: Time since last maintenance event.
	- `Major Repairs`: Count of major repair events (lifecycle stress proxy).
	- `Oil Quality`: Lubricant quality/condition proxy (where applicable).
	- `Pwr Consumption`: Power draw; shifts may reflect efficiency/wear.
	- `Envr Stress Index`: Composite environmental stress score.
	- `Criticality Score`: Business criticality (risk-weighting context).

## Methods Compared
- RPT-1: Provided by SAP RPT-1 playground (baseline).
- GPT-5 (ML): File labeled GPT-5 in outputs; treated here as ML-assisted variant.
- GPT-5 Standalone: No external ML libs; transparent heuristics and KNN-style reasoning.

## Method Internals and Parameters

### RPT-1 (Black Box)
- Weights/Rules/Distributions: Proprietary model from SAP RPT‑1 playground. Internal feature weights, training distributions, and decision rules are not observable from outputs.
- Temperature: Not applicable (not an LLM generation parameter in this context).

### GPT-5 (Standalone) — What actually ran in this workspace
- General: No external ML libraries. Deterministic, transparent logic using only the input CSVs.

- SC1 (Equipment Sourcing — CO2e):
	- Rule hierarchy (baseline selection):
		1) Mean CO2e by (Product, Urgency, Supplier)
		2) Fallback → (Product, Supplier)
		3) Fallback → (Product, Urgency)
		4) Fallback → (Product)
		5) Fallback → Global mean
	- Quantity adjustment (per‑product linear trend):
		- For each Product, fit a simple least‑squares line CO2e ≈ slope·Quantity + intercept using historical rows for that product.
		- Adjustment = slope × (Quantity − product_mean_quantity). If insufficient data (n<3) or degenerate variance, skip adjustment.
	- Weights: Baselines are simple means (equal weighting of contributing historical rows). Quantity adjustment derived from closed‑form OLS (implicit variance‑weighted by data spread).
	- Distributions: Empirical distributions from historical rows only; missing numerics ignored in means/fit. Unseen category combos use higher‑level fallbacks to remain stable out‑of‑distribution.
	- Per‑row evidence: Top 5 “neighbors” among same Product chosen by urgency/supplier match and quantity closeness (heuristic score), reported for auditability.
	- Temperature: Not applicable.

- SC2 (Predictive Maintenance — RUL):
	- Algorithm: KNN‑style regressor with robust standardization and categorical penalties.
	- Standardization/Imputation:
		- For each numeric feature, compute median and IQR on historical (non‑[PREDICT]) rows; impute missing with medians; standardize via (x − median)/IQR.
	- Distance metric:
		- Euclidean distance on standardized numerics + 1.0 penalty per categorical mismatch for Operating Envr and Maintenance Strat.
	- K and weights:
		- K = 7 nearest neighbors; inverse‑distance weighting w = 1/(d+1e‑6); prediction = Σ(wᵢ·RULᵢ)/Σ(wᵢ).
	- Distributions: Robust to outliers via IQR scaling; categorical penalties ensure environment/strategy mismatches are recognized even when numerics are similar.
	- Per‑row evidence: Lists the 7 neighbors (IDs, distances, weights, RUL) and top 5 features with largest standardized differences.
	- Temperature: Not applicable.

### GPT-5 (ML) — Intended approach when ML libraries are allowed
- Note: In this run, GPT‑5 (ML) outputs are numerically identical to GPT‑5 Standalone because external ML packages were not installed. If ML libraries were enabled, the plan was:
	- SC1: Ridge Regression over One‑Hot encoded categorical features + standardized Quantity
		- Preprocessing: ColumnTransformer with OneHotEncoder(handle_unknown=ignore) and StandardScaler for Quantity.
		- Model: Ridge(α=1.0). Coefficients provide linear feature weights. Local contributions via X·β diagnostics.
	- SC2: GradientBoostingRegressor with categorical OHE + standardized numerics
		- Preprocessing: As above for OHE + scaling. Model: GradientBoostingRegressor(random_state=42).
		- Global feature importance: permutation_importance; local sensitivity: replace‑feature‑with‑baseline (median/mode) and observe Δprediction.
- Temperature: Not applicable.

## Key Parameters (Quick Reference)

| Scenario | Method | Core Algorithm | Key Parameters |
|---|---|---|---|
| SC1 (CO2e) | GPT‑5 Standalone | Hierarchical grouped mean + per‑product OLS quantity adjustment | Fallback keys: (Product, Urgency, Supplier) → (Product, Supplier) → (Product, Urgency) → (Product) → Global; OLS requires ≥3 points per product; Neighbor evidence: same Product, score = +2 urgency match, +1 supplier match, +closeness by |ΔQuantity| |
| SC2 (RUL) | GPT‑5 Standalone | KNN‑style regression with robust scaling | K=7; Numeric standardization by median/IQR; Categorical penalty=1.0 per mismatch (Operating Envr, Maintenance Strat); Weights=1/(distance+1e‑6); Missing numerics imputed with medians |
| SC1 (CO2e) | GPT‑5 (ML, intended) | Ridge Regression over OHE + scaler | α=1.0; OneHotEncoder(handle_unknown=ignore); StandardScaler on Quantity |
| SC2 (RUL) | GPT‑5 (ML, intended) | GradientBoostingRegressor over OHE + scaler | random_state=42; global permutation importance; local baseline‑replacement sensitivity |

## Scenario SC1 — Equipment Sourcing (Target: CO2e)
- PREDICT rows: 3

### Pairwise Disagreement (Absolute Differences)
- GPT-5 (ML) vs RPT-1:
- Count compared: 3
- MAE: 15.207
- Median abs diff: 7.370
- Max abs diff: 32.940

- GPT-5 Standalone vs RPT-1:
- Count compared: 3
- MAE: 15.207
- Median abs diff: 7.370
- Max abs diff: 32.940

- GPT-5 Standalone vs GPT-5 (ML):
- Count compared: 3
- MAE: 0.000
- Median abs diff: 0.000
- Max abs diff: 0.000


## Scenario SC2 — Predictive Maintenance (Target: RUL)
- PREDICT rows: 5

### Pairwise Disagreement (Absolute Differences)
- GPT-5 (ML) vs RPT-1:
- Count compared: 5
- MAE: 45.860
- Median abs diff: 9.200
- Max abs diff: 187.200

- GPT-5 Standalone vs RPT-1:
- Count compared: 5
- MAE: 45.860
- Median abs diff: 9.200
- Max abs diff: 187.200

- GPT-5 Standalone vs GPT-5 (ML):
- Count compared: 5
- MAE: 0.000
- Median abs diff: 0.000
- Max abs diff: 0.000


## Observations & Interpretation
- Lower MAE indicates closer agreement; higher MAE signals methodological differences.
- GPT-5 Standalone offers full transparency (grouped means + quantity adjustment in SC1; robust KNN in SC2) and per-row neighbor evidence.
- GPT-5 (ML) typically tracks patterns more tightly when features interact nonlinearly, but at the cost of reduced transparency.
- RPT-1 serves as a benchmark; divergences point to assumptions in sourcing or maintenance risk modeling.

## Limitations
- No ground truth for [PREDICT] rows; pairwise MAE is not accuracy.
- SC1 quantity effects and SC2 neighbor definitions can be tuned (e.g., weighting, penalties, K).
- Distributional drift (e.g., suppliers or environments not seen in history) may widen disagreement across any pair.

## Recommendations
- Run a backtest: mask a subset of known rows and compare predictions to true values to estimate actual accuracy per method.
- Calibrate SC1 quantity slope and SC2 K/penalties using backtest MAE/MAPE for your cost or risk objectives.
- Adopt GPT-5 Standalone when auditability is a priority; adopt GPT-5 (ML) when accuracy gains on backtests justify less transparency.

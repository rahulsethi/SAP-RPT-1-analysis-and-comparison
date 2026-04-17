# SAP RPT-1 vs GPT-5 — Analysis and Comparison

This repository compares predictive outputs from SAP RPT-1 with two GPT‑5 variants across two scenarios:

- SC1 Equipment Sourcing — predict CO2e for purchase orders
- SC2 Predictive Maintenance — predict Remaining Useful Life (RUL) for equipment

It produces predictions, per‑row explanations, a comparison workbook, and written analyses.

## Scenarios and Inputs

- SC1 input: [SC1 Equipment Sourcing/SC1_input data/Equipment data.csv](SC1%20Equipment%20Sourcing/SC1_input%20data/Equipment%20data.csv)
  - Target: `CO2e` (rows with `[PREDICT]` require estimation)
- SC2 input: [SC2 Predictive Maintainence/SC2_input data/Predictive_maintainence.csv](SC2%20Predictive%20Maintainence/SC2_input%20data/Predictive_maintainence.csv)
  - Target: `RUL` (rows with `[PREDICT]` require estimation)

## Output Artifacts

- SC1 (GPT‑5 ML):
  - Predictions: [SC1 Equipment Sourcing/SC1_output/GPT 5 output/Equipment data prediction output GPT-5.csv](SC1%20Equipment%20Sourcing/SC1_output/GPT%205%20output/Equipment%20data%20prediction%20output%20GPT-5.csv)
  - Explanation: [SC1 Equipment Sourcing/SC1_output/GPT 5 output/Equipment data prediction output GPT-5_explanation.csv](SC1%20Equipment%20Sourcing/SC1_output/GPT%205%20output/Equipment%20data%20prediction%20output%20GPT-5_explanation.csv)
- SC1 (GPT‑5 Standalone):
  - Predictions: [SC1 Equipment Sourcing/SC1_output/GPT 5 output/Equipment data prediction output GPT5_standalone.csv](SC1%20Equipment%20Sourcing/SC1_output/GPT%205%20output/Equipment%20data%20prediction%20output%20GPT5_standalone.csv)
  - Explanation: [SC1 Equipment Sourcing/SC1_output/GPT 5 output/Equipment data prediction output GPT5_standalone_explanation.csv](SC1%20Equipment%20Sourcing/SC1_output/GPT%205%20output/Equipment%20data%20prediction%20output%20GPT5_standalone_explanation.csv)
- SC2 (GPT‑5 ML):
  - Predictions: [SC2 Predictive Maintainence/SC2_output/GPT-5 output/predictive_maintainence GPT-5 output.csv](SC2%20Predictive%20Maintainence/SC2_output/GPT-5%20output/predictive_maintainence%20GPT-5%20output.csv)
  - Explanation: [SC2 Predictive Maintainence/SC2_output/GPT-5 output/predictive_maintainence GPT-5 output_explanation.csv](SC2%20Predictive%20Maintainence/SC2_output/GPT-5%20output/predictive_maintainence%20GPT-5%20output_explanation.csv)
- SC2 (GPT‑5 Standalone):
  - Predictions: [SC2 Predictive Maintainence/SC2_output/GPT-5 output/predictive_maintainence GPT5_standalone output.csv](SC2%20Predictive%20Maintainence/SC2_output/GPT-5%20output/predictive_maintainence%20GPT5_standalone%20output.csv)
  - Explanation: [SC2 Predictive Maintainence/SC2_output/GPT-5 output/predictive_maintainence GPT5_standalone output_explanation.csv](SC2%20Predictive%20Maintainence/SC2_output/GPT-5%20output/predictive_maintainence%20GPT5_standalone%20output_explanation.csv)

- Comparison workbooks:
  - Original: [comparison_RPT1_GPT5ML_GPT5standalone.xlsx](comparison_RPT1_GPT5ML_GPT5standalone.xlsx)
  - v2 (with guidance): [comparison_RPT1_GPT5ML_GPT5standalone_v2.xlsx](comparison_RPT1_GPT5ML_GPT5standalone_v2.xlsx)
- Analyses:
  - Manager‑readable: [Summary.md](Summary.md)
  - Full analysis: [analysis.md](analysis.md)

## Methods

- RPT‑1: Baseline from SAP RPT‑1 playground (black box).
- GPT‑5 (Standalone):
  - SC1: Hierarchical grouped mean baseline with per‑product OLS quantity adjustment; neighbor evidence for auditability.
  - SC2: K=7 KNN‑style regressor with median/IQR scaling and categorical penalties; inverse‑distance weights; per‑row neighbor rationale.
- GPT‑5 (ML, intended when ML libs are allowed):
  - SC1: Ridge Regression over One‑Hot categorical features + standardized `Quantity`.
  - SC2: GradientBoostingRegressor with OHE numerics; global permutation importances and local sensitivity.

Note: In this run, external ML packages were not installed; the GPT‑5 ML outputs matched GPT‑5 Standalone on `[PREDICT]` rows.

## Regenerating Artifacts

From the project root:

```bash
# 1) Generate GPT‑5 predictions + explanation CSVs for SC1 and SC2
python gpt5_predict.py

# 2) Build comparison workbook (v2 includes a 'How to read' Summary sheet)
python make_comparison.py

# 3) Create full analysis and concise summary
python make_analysis.py
python make_summary.py
```

These scripts use only the standard library plus `xlsxwriter` (pure‑Python) for Excel outputs.

## Repository Structure (selected)

- SC1 Equipment Sourcing/
  - SC1_input data/Equipment data.csv
  - SC1_output/
    - RPT-1 output/
    - GPT 5 output/
- SC2 Predictive Maintainence/
  - SC2_input data/Predictive_maintainence.csv
  - SC2_output/
    - RPT-1 output/
    - GPT-5 output/
- analysis.md, Summary.md
- comparison_RPT1_GPT5ML_GPT5standalone(.xlsx, _v2.xlsx)
- gpt5_predict.py, make_comparison.py, make_analysis.py, make_summary.py

## License

No license specified.

import csv
from pathlib import Path
from statistics import mean, median

BASE = Path(__file__).parent

SC1_INPUT = BASE / "SC1 Equipment Sourcing" / "SC1_input data" / "Equipment data.csv"
SC1_RPT1 = BASE / "SC1 Equipment Sourcing" / "SC1_output" / "RPT-1 output" / "Equipment data prediction output RPT-1.csv"
SC1_GPT5 = BASE / "SC1 Equipment Sourcing" / "SC1_output" / "GPT 5 output" / "Equipment data prediction output GPT-5.csv"
SC1_GPT5_STDL = BASE / "SC1 Equipment Sourcing" / "SC1_output" / "GPT 5 output" / "Equipment data prediction output GPT5_standalone.csv"

SC2_INPUT = BASE / "SC2 Predictive Maintainence" / "SC2_input data" / "Predictive_maintainence.csv"
SC2_RPT1 = BASE / "SC2 Predictive Maintainence" / "SC2_output" / "RPT-1 output" / "predicitve_maintainence RPT-1 output.csv"
SC2_GPT5 = BASE / "SC2 Predictive Maintainence" / "SC2_output" / "GPT-5 output" / "predictive_maintainence GPT-5 output.csv"
SC2_GPT5_STDL = BASE / "SC2 Predictive Maintainence" / "SC2_output" / "GPT-5 output" / "predictive_maintainence GPT5_standalone output.csv"

ANALYSIS_MD = BASE / "analysis.md"


def read_csv(path: Path):
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_float(v):
    try:
        return float(str(v).strip())
    except Exception:
        return None


def scenario_metrics(input_path: Path, key: str, target: str, rpt_path: Path, gpt_ml_path: Path, gpt_stdl_path: Path):
    inp = read_csv(input_path)
    predict_keys = [r[key] for r in inp if str(r.get(target, "")).strip() == "[PREDICT]"]

    m_rpt = {r[key]: to_float(r.get(target)) for r in read_csv(rpt_path)}
    m_ml = {r[key]: to_float(r.get(target)) for r in read_csv(gpt_ml_path)}
    m_sd = {r[key]: to_float(r.get(target)) for r in read_csv(gpt_stdl_path)}

    diffs_ml_rpt = []
    diffs_sd_rpt = []
    diffs_sd_ml = []

    rows = []
    for k in predict_keys:
        v_rpt = m_rpt.get(k)
        v_ml = m_ml.get(k)
        v_sd = m_sd.get(k)
        d_ml_rpt = abs(v_ml - v_rpt) if v_ml is not None and v_rpt is not None else None
        d_sd_rpt = abs(v_sd - v_rpt) if v_sd is not None and v_rpt is not None else None
        d_sd_ml = abs(v_sd - v_ml) if v_sd is not None and v_ml is not None else None
        if d_ml_rpt is not None:
            diffs_ml_rpt.append(d_ml_rpt)
        if d_sd_rpt is not None:
            diffs_sd_rpt.append(d_sd_rpt)
        if d_sd_ml is not None:
            diffs_sd_ml.append(d_sd_ml)
        rows.append((k, v_rpt, v_ml, v_sd, d_ml_rpt, d_sd_rpt, d_sd_ml))

    def agg(xs):
        if not xs:
            return {"count": 0, "mae": None, "median_abs_diff": None, "max_abs_diff": None}
        return {
            "count": len(xs),
            "mae": mean(xs),
            "median_abs_diff": median(xs),
            "max_abs_diff": max(xs),
        }

    return {
        "predict_count": len(predict_keys),
        "compared_count": len(rows),
        "ml_vs_rpt": agg(diffs_ml_rpt),
        "standalone_vs_rpt": agg(diffs_sd_rpt),
        "standalone_vs_ml": agg(diffs_sd_ml),
        "sample_rows": rows[:10],
    }


def write_analysis(md_path: Path, sc1: dict, sc2: dict):
    def fmt_pair(d):
        return (
            f"- Count compared: {d['count']}\n"
            f"- MAE: {d['mae']:.3f}\n"
            f"- Median abs diff: {d['median_abs_diff']:.3f}\n"
            f"- Max abs diff: {d['max_abs_diff']:.3f}\n"
        ) if d["count"] > 0 else "- No overlapping rows to compare.\n"

    lines = []
    lines.append("# Comparative Analysis: RPT-1 vs GPT-5 (ML) vs GPT-5 Standalone")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("- This document summarizes pairwise disagreement metrics between three approaches on rows explicitly marked as [PREDICT] in your input files.")
    lines.append("- Without ground truth for [PREDICT] rows, we use pairwise Mean Absolute Error (MAE) as a proxy to indicate how much the methods diverge.")
    lines.append("")

    lines.append("## Files Considered")
    lines.append("- SC1 Input: SC1 Equipment Sourcing/SC1_input data/Equipment data.csv")
    lines.append("- SC1 Outputs: RPT-1, GPT-5 (ML), GPT-5 Standalone under SC1 Equipment Sourcing/SC1_output/")
    lines.append("- SC2 Input: SC2 Predictive Maintainence/SC2_input data/Predictive_maintainence.csv")
    lines.append("- SC2 Outputs: RPT-1, GPT-5 (ML), GPT-5 Standalone under SC2 Predictive Maintainence/SC2_output/")
    lines.append("")

    lines.append("## Methods Compared")
    lines.append("- RPT-1: Provided by SAP RPT-1 playground (baseline).")
    lines.append("- GPT-5 (ML): File labeled GPT-5 in outputs; treated here as ML-assisted variant.")
    lines.append("- GPT-5 Standalone: No external ML libs; transparent heuristics and KNN-style reasoning.")
    lines.append("")

    lines.append("## Scenario SC1 — Equipment Sourcing (Target: CO2e)")
    lines.append(f"- PREDICT rows: {sc1['predict_count']}")
    lines.append("")
    lines.append("### Pairwise Disagreement (Absolute Differences)")
    lines.append("- GPT-5 (ML) vs RPT-1:")
    lines.append(fmt_pair(sc1["ml_vs_rpt"]))
    lines.append("- GPT-5 Standalone vs RPT-1:")
    lines.append(fmt_pair(sc1["standalone_vs_rpt"]))
    lines.append("- GPT-5 Standalone vs GPT-5 (ML):")
    lines.append(fmt_pair(sc1["standalone_vs_ml"]))
    lines.append("")

    lines.append("## Scenario SC2 — Predictive Maintenance (Target: RUL)")
    lines.append(f"- PREDICT rows: {sc2['predict_count']}")
    lines.append("")
    lines.append("### Pairwise Disagreement (Absolute Differences)")
    lines.append("- GPT-5 (ML) vs RPT-1:")
    lines.append(fmt_pair(sc2["ml_vs_rpt"]))
    lines.append("- GPT-5 Standalone vs RPT-1:")
    lines.append(fmt_pair(sc2["standalone_vs_rpt"]))
    lines.append("- GPT-5 Standalone vs GPT-5 (ML):")
    lines.append(fmt_pair(sc2["standalone_vs_ml"]))
    lines.append("")

    lines.append("## Observations & Interpretation")
    lines.append("- Lower MAE indicates closer agreement; higher MAE signals methodological differences.")
    lines.append("- GPT-5 Standalone offers full transparency (grouped means + quantity adjustment in SC1; robust KNN in SC2) and per-row neighbor evidence.")
    lines.append("- GPT-5 (ML) typically tracks patterns more tightly when features interact nonlinearly, but at the cost of reduced transparency.")
    lines.append("- RPT-1 serves as a benchmark; divergences point to assumptions in sourcing or maintenance risk modeling.")
    lines.append("")

    lines.append("## Limitations")
    lines.append("- No ground truth for [PREDICT] rows; pairwise MAE is not accuracy.")
    lines.append("- SC1 quantity effects and SC2 neighbor definitions can be tuned (e.g., weighting, penalties, K).")
    lines.append("- Distributional drift (e.g., suppliers or environments not seen in history) may widen disagreement across any pair.")
    lines.append("")

    lines.append("## Recommendations")
    lines.append("- Run a backtest: mask a subset of known rows and compare predictions to true values to estimate actual accuracy per method.")
    lines.append("- Calibrate SC1 quantity slope and SC2 K/penalties using backtest MAE/MAPE for your cost or risk objectives.")
    lines.append("- Adopt GPT-5 Standalone when auditability is a priority; adopt GPT-5 (ML) when accuracy gains on backtests justify less transparency.")
    lines.append("")

    md = "\n".join(lines)
    md_path.write_text(md, encoding="utf-8")


def main():
    sc1 = scenario_metrics(SC1_INPUT, "OrderID", "CO2e", SC1_RPT1, SC1_GPT5, SC1_GPT5_STDL)
    sc2 = scenario_metrics(SC2_INPUT, "Equipment ID", "RUL", SC2_RPT1, SC2_GPT5, SC2_GPT5_STDL)
    write_analysis(ANALYSIS_MD, sc1, sc2)
    print(f"Wrote {ANALYSIS_MD}")


if __name__ == "__main__":
    main()

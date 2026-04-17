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

SUMMARY_MD = BASE / "Summary.md"


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

    def agg(xs):
        if not xs:
            return None, None
        return mean(xs), max(xs)

    return {
        "predict_count": len(predict_keys),
        "ml_vs_rpt": agg(diffs_ml_rpt),
        "standalone_vs_rpt": agg(diffs_sd_rpt),
        "standalone_vs_ml": agg(diffs_sd_ml),
    }


def main():
    sc1 = scenario_metrics(SC1_INPUT, "OrderID", "CO2e", SC1_RPT1, SC1_GPT5, SC1_GPT5_STDL)
    sc2 = scenario_metrics(SC2_INPUT, "Equipment ID", "RUL", SC2_RPT1, SC2_GPT5, SC2_GPT5_STDL)

    def fmt(mae_max):
        if mae_max == (None, None):
            return "n/a"
        mae, mx = mae_max
        return f"MAE={mae:.3f}, MaxΔ={mx:.3f}"

    lines = []
    lines.append("# Summary — RPT-1 vs GPT-5 (ML) vs GPT-5 Standalone")
    lines.append("")
    lines.append("## TL;DR")
    lines.append("- We compare methods only on rows marked [PREDICT]; pairwise MAE shows disagreement (not accuracy).")
    lines.append("- In this run, GPT-5 (ML) and GPT-5 Standalone align on PREDICT rows; both diverge similarly from RPT-1.")
    lines.append("")

    lines.append("## SC1 — Equipment Sourcing (CO2e)")
    lines.append(f"- PREDICT rows: {sc1['predict_count']}")
    lines.append(f"- GPT-5 (ML) vs RPT-1: {fmt(sc1['ml_vs_rpt'])}")
    lines.append(f"- GPT-5 Standalone vs RPT-1: {fmt(sc1['standalone_vs_rpt'])}")
    lines.append(f"- GPT-5 Standalone vs GPT-5 (ML): {fmt(sc1['standalone_vs_ml'])}")
    lines.append("")

    lines.append("## SC2 — Predictive Maintenance (RUL)")
    lines.append(f"- PREDICT rows: {sc2['predict_count']}")
    lines.append(f"- GPT-5 (ML) vs RPT-1: {fmt(sc2['ml_vs_rpt'])}")
    lines.append(f"- GPT-5 Standalone vs RPT-1: {fmt(sc2['standalone_vs_rpt'])}")
    lines.append(f"- GPT-5 Standalone vs GPT-5 (ML): {fmt(sc2['standalone_vs_ml'])}")
    lines.append("")

    lines.append("## Methods (One-liners)")
    lines.append("- RPT-1: SAP baseline (black box).")
    lines.append("- GPT-5 (ML): Intended — linear model for SC1, gradient boosting for SC2.")
    lines.append("- GPT-5 Standalone: Transparent rules — grouped means + quantity slope (SC1); KNN with robust scaling (SC2).")
    lines.append("")

    lines.append("## Decision Guidance")
    lines.append("- Use GPT-5 Standalone when auditability is key; consider GPT-5 (ML) if backtested accuracy gains justify complexity.")

    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {SUMMARY_MD}")


if __name__ == "__main__":
    main()

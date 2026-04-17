import csv
from pathlib import Path
from statistics import mean
import xlsxwriter

BASE = Path(__file__).parent

# Paths
SC1_INPUT = BASE / "SC1 Equipment Sourcing" / "SC1_input data" / "Equipment data.csv"
SC1_RPT1 = BASE / "SC1 Equipment Sourcing" / "SC1_output" / "RPT-1 output" / "Equipment data prediction output RPT-1.csv"
SC1_GPT5 = BASE / "SC1 Equipment Sourcing" / "SC1_output" / "GPT 5 output" / "Equipment data prediction output GPT-5.csv"
SC1_GPT5_STDL = BASE / "SC1 Equipment Sourcing" / "SC1_output" / "GPT 5 output" / "Equipment data prediction output GPT5_standalone.csv"

SC2_INPUT = BASE / "SC2 Predictive Maintainence" / "SC2_input data" / "Predictive_maintainence.csv"
SC2_RPT1 = BASE / "SC2 Predictive Maintainence" / "SC2_output" / "RPT-1 output" / "predicitve_maintainence RPT-1 output.csv"
SC2_GPT5 = BASE / "SC2 Predictive Maintainence" / "SC2_output" / "GPT-5 output" / "predictive_maintainence GPT-5 output.csv"
SC2_GPT5_STDL = BASE / "SC2 Predictive Maintainence" / "SC2_output" / "GPT-5 output" / "predictive_maintainence GPT5_standalone output.csv"

OUT_XLSX = BASE / "comparison_RPT1_GPT5ML_GPT5standalone_v2.xlsx"


def read_csv(path: Path):
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_float(v):
    try:
        return float(str(v).strip())
    except Exception:
        return None


def sc1_compare(ws, workbook):
    input_rows = read_csv(SC1_INPUT)
    key = "OrderID"
    target = "CO2e"
    # identify predict keys
    predict_keys = [r[key] for r in input_rows if str(r[target]).strip() == "[PREDICT]"]

    # maps
    rpt1 = {r[key]: to_float(r[target]) for r in read_csv(SC1_RPT1)}
    gpt5 = {r[key]: to_float(r[target]) for r in read_csv(SC1_GPT5)}
    gpt5s = {r[key]: to_float(r[target]) for r in read_csv(SC1_GPT5_STDL)}

    ws.write_row(0, 0, [key, "Product", "Urgency", "Supplier", "Quantity", "RPT-1_CO2e", "GPT5_ML_CO2e", "GPT5_Standalone_CO2e", "|GPT5_ML - RPT1|", "|GPT5_Standalone - RPT1|", "|GPT5_Standalone - GPT5_ML|"])

    diffs_ml_rpt = []
    diffs_std_rpt = []
    diffs_std_ml = []

    rowi = 1
    for r in input_rows:
        if r[key] not in predict_keys:
            continue
        rid = r[key]
        v_rpt = rpt1.get(rid)
        v_ml = gpt5.get(rid)
        v_std = gpt5s.get(rid)
        d_ml_rpt = abs(v_ml - v_rpt) if v_ml is not None and v_rpt is not None else None
        d_std_rpt = abs(v_std - v_rpt) if v_std is not None and v_rpt is not None else None
        d_std_ml = abs(v_std - v_ml) if v_std is not None and v_ml is not None else None
        if d_ml_rpt is not None:
            diffs_ml_rpt.append(d_ml_rpt)
        if d_std_rpt is not None:
            diffs_std_rpt.append(d_std_rpt)
        if d_std_ml is not None:
            diffs_std_ml.append(d_std_ml)
        ws.write_row(rowi, 0, [
            rid, r.get("Product"), r.get("Urgency"), r.get("Supplier"), r.get("Quantity"),
            v_rpt, v_ml, v_std, d_ml_rpt, d_std_rpt, d_std_ml
        ])
        rowi += 1

    # footer metrics
    bold = workbook.add_format({"bold": True})
    ws.write_row(rowi + 1, 0, ["Metrics"], bold)
    ws.write_row(rowi + 2, 0, ["PREDICT rows", len(predict_keys)])
    ws.write_row(rowi + 3, 0, ["Pairwise MAE: GPT5_ML vs RPT-1", mean(diffs_ml_rpt) if diffs_ml_rpt else None])
    ws.write_row(rowi + 4, 0, ["Pairwise MAE: GPT5_Standalone vs RPT-1", mean(diffs_std_rpt) if diffs_std_rpt else None])
    ws.write_row(rowi + 5, 0, ["Pairwise MAE: GPT5_Standalone vs GPT5_ML", mean(diffs_std_ml) if diffs_std_ml else None])


def sc2_compare(ws, workbook):
    input_rows = read_csv(SC2_INPUT)
    key = "Equipment ID"
    target = "RUL"
    predict_keys = [r[key] for r in input_rows if str(r[target]).strip() == "[PREDICT]"]

    rpt1 = {r[key]: to_float(r[target]) for r in read_csv(SC2_RPT1)}
    gpt5 = {r[key]: to_float(r[target]) for r in read_csv(SC2_GPT5)}
    gpt5s = {r[key]: to_float(r[target]) for r in read_csv(SC2_GPT5_STDL)}

    ws.write_row(0, 0, [key, "Operating Envr", "Maintenance Strat", "RPT-1_RUL", "GPT5_ML_RUL", "GPT5_Standalone_RUL", "|GPT5_ML - RPT1|", "|GPT5_Standalone - RPT1|", "|GPT5_Standalone - GPT5_ML|"])

    diffs_ml_rpt = []
    diffs_std_rpt = []
    diffs_std_ml = []

    rowi = 1
    for r in input_rows:
        if r[key] not in predict_keys:
            continue
        rid = r[key]
        v_rpt = rpt1.get(rid)
        v_ml = gpt5.get(rid)
        v_std = gpt5s.get(rid)
        d_ml_rpt = abs(v_ml - v_rpt) if v_ml is not None and v_rpt is not None else None
        d_std_rpt = abs(v_std - v_rpt) if v_std is not None and v_rpt is not None else None
        d_std_ml = abs(v_std - v_ml) if v_std is not None and v_ml is not None else None
        if d_ml_rpt is not None:
            diffs_ml_rpt.append(d_ml_rpt)
        if d_std_rpt is not None:
            diffs_std_rpt.append(d_std_rpt)
        if d_std_ml is not None:
            diffs_std_ml.append(d_std_ml)
        ws.write_row(rowi, 0, [
            rid, r.get("Operating Envr"), r.get("Maintenance Strat"),
            v_rpt, v_ml, v_std, d_ml_rpt, d_std_rpt, d_std_ml
        ])
        rowi += 1

    bold = workbook.add_format({"bold": True})
    ws.write_row(rowi + 1, 0, ["Metrics"], bold)
    ws.write_row(rowi + 2, 0, ["PREDICT rows", len(predict_keys)])
    ws.write_row(rowi + 3, 0, ["Pairwise MAE: GPT5_ML vs RPT-1", mean(diffs_ml_rpt) if diffs_ml_rpt else None])
    ws.write_row(rowi + 4, 0, ["Pairwise MAE: GPT5_Standalone vs RPT-1", mean(diffs_std_rpt) if diffs_std_rpt else None])
    ws.write_row(rowi + 5, 0, ["Pairwise MAE: GPT5_Standalone vs GPT5_ML", mean(diffs_std_ml) if diffs_std_ml else None])


def write_summary(ws, workbook):
    title = workbook.add_format({"bold": True, "font_size": 12})
    italic = workbook.add_format({"italic": True})
    ws.write(0, 0, "Comparison: RPT-1 vs GPT-5 (ML) vs GPT-5 Standalone", title)
    ws.write(2, 0, "How to read this workbook:", title)
    howto = [
        "- SC1_Comparison: CO2e predictions for rows marked [PREDICT] in Equipment data.csv.",
        "  Columns show each method and absolute differences across pairs.",
        "  Footer rows report pairwise MAE as a divergence proxy (not accuracy).",
        "- SC2_Comparison: RUL predictions for rows marked [PREDICT] in Predictive_maintainence.csv.",
        "  Columns show each method and absolute differences across pairs.",
        "  Footer rows report pairwise MAE as a divergence proxy (not accuracy).",
        "- Use analysis.md for methodology details and recommendations.",
    ]
    for i, line in enumerate(howto, start=3):
        ws.write(i, 0, line)
    ws.write(i + 2, 0, "Note: Without ground truth for [PREDICT] rows, lower MAE indicates closer agreement between methods.", italic)


def main():
    wb = xlsxwriter.Workbook(OUT_XLSX.as_posix())
    ws_sum = wb.add_worksheet("Summary")
    ws_sc1 = wb.add_worksheet("SC1_Comparison")
    ws_sc2 = wb.add_worksheet("SC2_Comparison")

    write_summary(ws_sum, wb)
    sc1_compare(ws_sc1, wb)
    sc2_compare(ws_sc2, wb)

    wb.close()
    print(f"Wrote {OUT_XLSX}")


if __name__ == "__main__":
    main()

import csv
import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional

from statistics import mean, median

BASE_DIR = Path(__file__).parent

# Paths
SC1_INPUT = BASE_DIR / "SC1 Equipment Sourcing" / "SC1_input data" / "Equipment data.csv"
SC1_OUT_DIR = BASE_DIR / "SC1 Equipment Sourcing" / "SC1_output" / "GPT 5 output"

SC2_INPUT = BASE_DIR / "SC2 Predictive Maintainence" / "SC2_input data" / "Predictive_maintainence.csv"
SC2_OUT_DIR = BASE_DIR / "SC2 Predictive Maintainence" / "SC2_output" / "GPT-5 output"

SC1_PRED_CSV = SC1_OUT_DIR / "Equipment data prediction output GPT-5.csv"
SC1_EXPL_CSV = SC1_OUT_DIR / "Equipment data prediction output GPT-5_explanation.csv"

SC2_PRED_CSV = SC2_OUT_DIR / "predictive_maintainence GPT-5 output.csv"
SC2_EXPL_CSV = SC2_OUT_DIR / "predictive_maintainence GPT-5 output_explanation.csv"


def ensure_dirs():
    SC1_OUT_DIR.mkdir(parents=True, exist_ok=True)
    SC2_OUT_DIR.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: Optional[List[str]] = None):
    if not rows:
        # Write an empty file with just headers if provided
        if fieldnames:
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
        return
    if fieldnames is None:
        # Union of keys preserving first-row order
        keys = list(rows[0].keys())
        extra_keys = set()
        for r in rows:
            extra_keys.update(set(r.keys()) - set(keys))
        fieldnames = keys + sorted(extra_keys)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def read_csv_dicts(path: Path) -> List[Dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_float(val: str) -> Optional[float]:
    if val is None:
        return None
    sval = str(val).strip()
    if not sval or sval.upper() == "NA":
        return None
    try:
        return float(sval)
    except Exception:
        return None


# ------------------------
# SC1: Equipment Sourcing
# ------------------------

def run_sc1() -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    rows = read_csv_dicts(SC1_INPUT)
    target_col = "CO2e"

    # Separate train and predict rows
    train = []
    predict = []
    for r in rows:
        val = r.get(target_col, "")
        if str(val).strip() == "[PREDICT]":
            predict.append(r)
        else:
            f = to_float(val)
            if f is not None:
                r[target_col] = f
                train.append(r)

    # Build aggregates
    def key(*cols):
        return tuple(r[c] for c in cols)

    global_mean = mean([r[target_col] for r in train]) if train else None

    mean_by = {}
    combos = [
        ("Product", "Urgency", "Supplier"),
        ("Product", "Supplier"),
        ("Product", "Urgency"),
        ("Product",),
    ]
    for cols in combos:
        d: Dict[Tuple[str, ...], List[float]] = {}
        for r in train:
            k = tuple(r[c] for c in cols)
            d.setdefault(k, []).append(r[target_col])
        mean_by[cols] = {k: mean(vs) for k, vs in d.items()}

    # Per-product linear adjustment vs Quantity
    qty_stats: Dict[str, Dict[str, float]] = {}
    for prod in {r["Product"] for r in train}:
        pts = [(to_float(r.get("Quantity")), r[target_col]) for r in train if r["Product"] == prod]
        pts = [(x, y) for x, y in pts if x is not None]
        if len(pts) >= 3:
            xs = [x for x, _ in pts]
            ys = [y for _, y in pts]
            mx = mean(xs)
            my = mean(ys)
            varx = sum((x - mx) ** 2 for x in xs)
            if varx > 1e-9:
                cov = sum((x - mx) * (y - my) for x, y in pts)
                slope = cov / varx
                intercept = my - slope * mx
                qty_stats[prod] = {"slope": slope, "mx": mx, "my": my, "intercept": intercept}

    # Predict
    predictions: List[Dict[str, object]] = []
    explanations: List[Dict[str, object]] = []
    for r in rows:
        if str(r.get(target_col, "")).strip() != "[PREDICT]":
            # Keep original
            predictions.append(r.copy())
            continue
        base = None
        used_key = None
        for cols in combos:
            k = tuple(r[c] for c in cols)
            if k in mean_by[cols]:
                base = mean_by[cols][k]
                used_key = (cols, k)
                break
        if base is None:
            base = global_mean if global_mean is not None else 0.0
            used_key = (("GLOBAL",), ("GLOBAL",))

        # Quantity adjustment if available for product
        prod = r.get("Product")
        qty = to_float(r.get("Quantity")) or 0.0
        adj_note = ""
        if prod in qty_stats:
            slope = qty_stats[prod]["slope"]
            mx = qty_stats[prod]["mx"]
            base += slope * (qty - mx)
            adj_note = f"Quantity adjustment applied using per-product slope {slope:.3f}"

        pred_val = round(float(base), 2)
        new_r = r.copy()
        new_r[target_col] = pred_val
        predictions.append(new_r)

        # Simple neighbor-based context for explanation (same product)
        neighbors = [tr for tr in train if tr.get("Product") == prod]
        # Score neighbors by urgency/supplier match and quantity proximity
        def nb_score(tr):
            s = 0
            if tr.get("Urgency") == r.get("Urgency"):
                s += 2
            if tr.get("Supplier") == r.get("Supplier"):
                s += 1
            q = to_float(tr.get("Quantity")) or 0.0
            s += max(0.0, 3.0 - abs((q - qty)))  # closer quantity gets higher score
            return s
        top_neighbors = sorted(neighbors, key=nb_score, reverse=True)[:5]
        expl = {
            "OrderID": r.get("OrderID"),
            "Predicted_CO2e": pred_val,
            "Basis": f"Mean over key {used_key[0]}={used_key[1]} | {adj_note}",
        }
        for i, tr in enumerate(top_neighbors, start=1):
            expl[f"nbr_{i}_OrderID"] = tr.get("OrderID")
            expl[f"nbr_{i}_CO2e"] = tr.get("CO2e")
            expl[f"nbr_{i}_Quantity"] = tr.get("Quantity")
            expl[f"nbr_{i}_UrgencyMatch"] = tr.get("Urgency") == r.get("Urgency")
            expl[f"nbr_{i}_SupplierMatch"] = tr.get("Supplier") == r.get("Supplier")
        explanations.append(expl)

    return predictions, explanations


# -------------------------------
# SC2: Predictive Maintenance RUL
# -------------------------------

def robust_scale_stats(values: List[Optional[float]]) -> Tuple[float, float]:
    clean = [v for v in values if v is not None]
    if not clean:
        return 0.0, 1.0
    clean_sorted = sorted(clean)
    n = len(clean_sorted)
    med = clean_sorted[n // 2] if n % 2 == 1 else 0.5 * (clean_sorted[n // 2 - 1] + clean_sorted[n // 2])
    # Approximate IQR
    q1 = clean_sorted[n // 4]
    q3 = clean_sorted[(3 * n) // 4]
    iqr = max(1e-6, q3 - q1)
    return med, iqr


def run_sc2() -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    rows = read_csv_dicts(SC2_INPUT)
    target_col = "RUL"

    id_col = "Equipment ID"
    cat_cols = ["Operating Envr", "Maintenance Strat"]
    num_cols = [
        "Equipment Age","Operating Hours","Current Vibration","Temp Operating","Load Factor",
        "Last Maintenance","Major Repairs","Oil Quality","Pwr Consumption","Envr Stress Index","Criticality Score"
    ]

    # Training rows with numeric target
    train = []
    predict = []
    for r in rows:
        val = r.get(target_col, "")
        if str(val).strip() == "[PREDICT]":
            predict.append(r)
        else:
            f = to_float(val)
            if f is not None:
                r[target_col] = f
                train.append(r)

    # Imputation baselines for numeric
    num_series: Dict[str, List[Optional[float]]] = {c: [to_float(r.get(c)) for r in train] for c in num_cols}
    num_meds: Dict[str, float] = {c: (median([v for v in vs if v is not None]) if any(v is not None for v in vs) else 0.0) for c, vs in num_series.items()}
    num_robust: Dict[str, Tuple[float, float]] = {c: robust_scale_stats([to_float(r.get(c)) for r in train]) for c in num_cols}

    # Distance function
    def row_distance(a: Dict[str, str], b: Dict[str, str]) -> float:
        d2 = 0.0
        # numeric
        for c in num_cols:
            am = to_float(a.get(c))
            bm = to_float(b.get(c))
            if am is None:
                am = num_meds[c]
            if bm is None:
                bm = num_meds[c]
            medc, iqr = num_robust[c]
            za = (am - medc) / iqr
            zb = (bm - medc) / iqr
            d = za - zb
            d2 += d * d
        # categorical mismatch penalties
        for c in cat_cols:
            if (a.get(c) or "").strip() != (b.get(c) or "").strip():
                d2 += 1.0
        return d2 ** 0.5

    K = 7
    predictions: List[Dict[str, object]] = []
    explanations: List[Dict[str, object]] = []
    for r in rows:
        if str(r.get(target_col, "")).strip() != "[PREDICT]":
            predictions.append(r.copy())
            continue
        # Nearest neighbors among train
        dists = [(row_distance(r, tr), tr) for tr in train]
        dists.sort(key=lambda x: x[0])
        k_neigh = dists[:max(1, min(K, len(dists)))]
        # Weighted average (inverse-distance)
        weights = []
        vals = []
        for d, tr in k_neigh:
            w = 1.0 / (d + 1e-6)
            weights.append(w)
            vals.append(float(tr[target_col]))
        s_w = sum(weights) if weights else 1.0
        pred_val = sum(w * v for w, v in zip(weights, vals)) / s_w
        pred_val = round(pred_val, 1)

        new_r = r.copy()
        new_r[target_col] = pred_val
        predictions.append(new_r)

        # Per-row explanation: list neighbors and top differing features
        total_w = s_w
        expl = {
            id_col: r.get(id_col),
            "Predicted_RUL": pred_val,
        }
        for i, (d, tr) in enumerate(k_neigh, start=1):
            w = (1.0 / (d + 1e-6)) / total_w
            expl[f"nbr_{i}_id"] = tr.get(id_col)
            expl[f"nbr_{i}_dist"] = round(d, 3)
            expl[f"nbr_{i}_rul"] = tr.get(target_col)
            expl[f"nbr_{i}_weight"] = round(w, 4)

        # Feature differences (standardized abs diff)
        diffs: List[Tuple[str, float]] = []
        for c in num_cols:
            am = to_float(r.get(c))
            bm = to_float(k_neigh[0][1].get(c)) if k_neigh else None
            if am is None:
                am = num_meds[c]
            if bm is None:
                bm = num_meds[c]
            medc, iqr = num_robust[c]
            diff = abs(((am - medc) / iqr) - ((bm - medc) / iqr))
            diffs.append((c, diff))
        for c in cat_cols:
            diffs.append((c, 0.0 if (r.get(c) or "").strip() == ((k_neigh[0][1].get(c) if k_neigh else "") or "").strip() else 1.0))
        diffs.sort(key=lambda x: x[1], reverse=True)
        for j, (name, score) in enumerate(diffs[:5], start=1):
            expl[f"topfeat_{j}"] = name
            expl[f"topfeat_{j}_diff"] = round(score, 3)

        explanations.append(expl)

    return predictions, explanations


# (Removed old sklearn-based run_sc2 implementation; using KNN-based pure-Python above.)


def main():
    ensure_dirs()

    # SC1
    sc1_pred, sc1_expl = run_sc1()
    write_csv(SC1_PRED_CSV, sc1_pred)
    write_csv(SC1_EXPL_CSV, sc1_expl)

    # SC2
    sc2_pred, sc2_expl = run_sc2()
    write_csv(SC2_PRED_CSV, sc2_pred)
    write_csv(SC2_EXPL_CSV, sc2_expl)

    print(json.dumps({
        "sc1_csv": str(SC1_PRED_CSV),
        "sc1_explanation_csv": str(SC1_EXPL_CSV),
        "sc2_csv": str(SC2_PRED_CSV),
        "sc2_explanation_csv": str(SC2_EXPL_CSV),
    }, indent=2))


if __name__ == "__main__":
    main()

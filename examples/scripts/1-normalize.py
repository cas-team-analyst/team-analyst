"""
Script 1: Normalize triangle data to long format + write Excel outputs.
Run once per project. Outputs are the foundation for all downstream methods.

Usage (run from the project root):
    python scripts/1-normalize.py

Inputs (configure the SOURCES list below):
    - One or more Excel/CSV triangle files with wide-format layout
      (rows = accident periods, columns = development ages)

Outputs:
    output/prep/
        triangles.pkl / triangles.csv   (internal long-format, preserves categorical ordering)
    output/data-processing/
        long.xlsx                        (Accident Period, Development Age, Measure, Value)
        triangles.xlsx                   (wide format, one sheet per measure)
        pre-method-triangle-diagnostics.xlsx  (11 diagnostic ratio triangles)
"""

import pandas as pd
import numpy as np
import os


def _try_int(series):
    """Convert series to int if all values are numeric, else return as-is."""
    try:
        return series.astype(str).apply(lambda x: int(float(x)))
    except (ValueError, TypeError):
        return series.astype(str)


# ── Configure these paths ──────────────────────────────────────────────────────
OUTPUT_PREP_DIR = "output/prep"
OUTPUT_DATA_DIR = "output/data-processing"

SOURCES = [
    dict(
        file_path="data/canonical-triangles.xlsx",
        sheet_name="Incurred",
        measure="Incurred Loss",
        unit_type="Dollars",
        header_row=1, period_column=1, first_data_column=2,
    ),
    dict(
        file_path="data/canonical-triangles.xlsx",
        sheet_name="Paid",
        measure="Paid Loss",
        unit_type="Dollars",
        header_row=1, period_column=1, first_data_column=2,
    ),
    dict(
        file_path="data/canonical-triangles.xlsx",
        sheet_name="Reported",
        measure="Reported Count",
        unit_type="Count",
        header_row=1, period_column=1, first_data_column=2,
    ),
    dict(
        file_path="data/canonical-triangles.xlsx",
        sheet_name="Closed",
        measure="Closed Count",
        unit_type="Count",
        header_row=1, period_column=1, first_data_column=2,
    ),
    dict(
        file_path="data/canonical-triangles.xlsx",
        sheet_name="Exposure",
        measure="Exposure",
        unit_type="Count",
        header_row=1, period_column=1, first_data_column=2,
    ),
]
# ── End configuration ──────────────────────────────────────────────────────────

# Display name for each measure (used as sheet names in Excel)
MEASURE_DISPLAY = {
    "Incurred Loss":   "Incurred",
    "Paid Loss":       "Paid",
    "Reported Count":  "Reported",
    "Closed Count":    "Closed",
    "Exposure":        "Exposure",
}


def read_triangle(file_path, sheet_name, measure, unit_type,
                  header_row, period_column, first_data_column):
    """Read one wide-format triangle sheet and return a long-format DataFrame."""
    header_row_0      = header_row - 1
    period_col_0      = period_column - 1
    first_data_col_0  = first_data_column - 1

    if file_path.lower().endswith(".csv"):
        raw    = pd.read_csv(file_path, header=None, dtype=str)
        source = file_path
    else:
        raw    = pd.read_excel(file_path, sheet_name=sheet_name,
                               header=None, dtype=str, engine="openpyxl")
        source = f"{file_path} | {sheet_name}"

    ages = []
    for col_idx in range(first_data_col_0, raw.shape[1]):
        val = raw.iloc[header_row_0, col_idx]
        if pd.notna(val) and str(val).strip():
            ages.append(str(val).strip())
        else:
            break

    rows    = []
    periods = []
    for row_idx in range(header_row_0 + 1, len(raw)):
        period_val = raw.iloc[row_idx, period_col_0]
        if pd.isna(period_val) or str(period_val).strip() == "":
            continue
        period = str(period_val).strip()
        if period not in periods:
            periods.append(period)
        for age_idx, age in enumerate(ages):
            cell = raw.iloc[row_idx, first_data_col_0 + age_idx]
            if pd.notna(cell) and str(cell).strip() != "":
                rows.append(dict(period=period, age=age, value=float(cell),
                                 measure=measure, unit_type=unit_type, source=source))

    if not rows:
        return pd.DataFrame()

    df             = pd.DataFrame(rows)
    df["period"]   = pd.Categorical(df["period"],   categories=periods, ordered=True)
    df["age"]      = pd.Categorical(df["age"],      categories=ages,    ordered=True)
    df["measure"]  = df["measure"].astype("category")
    df["unit_type"]= df["unit_type"].astype("category")
    return df


def validate(df):
    required = ["period", "age", "value", "measure", "unit_type"]
    missing  = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    for col in ["period", "age"]:
        if df[col].dtype.name != "category":
            raise ValueError(f"'{col}' must be an ordered category")
        if not df[col].cat.ordered:
            raise ValueError(f"'{col}' category must be ordered=True")
    if df["value"].isna().any():
        raise ValueError("'value' column contains nulls — check source data")


def to_wide(df_long, measure):
    """Convert long-format data for one measure to a wide DataFrame."""
    subset = df_long[df_long["measure"] == measure].copy()
    if subset.empty:
        return pd.DataFrame()
    subset["age_int"]    = _try_int(subset["age"])
    subset["period_int"] = _try_int(subset["period"])
    pivot = subset.pivot(index="period_int", columns="age_int", values="value")
    pivot.index.name   = MEASURE_DISPLAY.get(measure, measure)
    pivot.columns.name = None
    return pivot


def write_long_excel(df, path):
    """Write canonical-long format: Accident Period, Development Age, Measure, Value."""
    out = df[["period", "age", "measure", "value"]].copy()
    out["period"] = _try_int(out["period"])
    out["age"]    = _try_int(out["age"])
    out.columns   = ["Accident Period", "Development Age", "Measure", "Value"]
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        out.to_excel(writer, sheet_name="canonical-long", index=False)
    print(f"  Saved → {path}")


def write_triangles_excel(df, path):
    """Write wide-format triangles, one sheet per measure."""
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for measure, display in MEASURE_DISPLAY.items():
            wide = to_wide(df, measure)
            if not wide.empty:
                wide.to_excel(writer, sheet_name=display)
    print(f"  Saved → {path}")


def compute_diagnostics(df):
    """Compute pre-method triangle diagnostic ratios from the long-format data."""
    wide = {}
    for measure in MEASURE_DISPLAY:
        subset = df[df["measure"] == measure].copy()
        if subset.empty:
            continue
        subset["age_int"]    = _try_int(subset["age"])
        subset["period_int"] = _try_int(subset["period"])
        w = subset.pivot(index="period_int", columns="age_int", values="value")
        w.columns.name = None
        wide[measure] = w

    inc  = wide.get("Incurred Loss")
    paid = wide.get("Paid Loss")
    rep  = wide.get("Reported Count")
    cls  = wide.get("Closed Count")
    exp  = wide.get("Exposure")

    diagnostics = {}

    def safe_div(num, den, label):
        if num is None or den is None:
            return
        n, d = num.align(den, join="left", axis=1)
        result = n.divide(d).where(d != 0)
        result.index.name   = label
        result.columns.name = None
        diagnostics[label]  = result

    def safe_sub(a, b, label):
        if a is None or b is None:
            return
        x, y = a.align(b, join="left", axis=1)
        result = (x - y).where(x.notna() & y.notna())
        result.index.name   = label
        result.columns.name = None
        diagnostics[label]  = result

    safe_div(inc,  rep,  "Incurred Severity")
    safe_div(inc,  exp,  "Incurred Loss Rate")
    safe_div(paid, rep,  "Paid Severity")
    safe_div(paid, exp,  "Paid Loss Rate")
    safe_div(paid, inc,  "Paid-to-Incurred")
    safe_sub(inc,  paid, "Case Reserves")
    safe_div(rep,  exp,  "Reported Frequency")
    safe_div(cls,  exp,  "Closed Frequency")
    safe_div(cls,  rep,  "Closed-to-Reported")
    safe_sub(rep,  cls,  "Open Counts")

    case_res = diagnostics.get("Case Reserves")
    open_cnt = diagnostics.get("Open Counts")
    if case_res is not None and open_cnt is not None:
        n, d = case_res.align(open_cnt, join="left", axis=1)
        result = n.divide(d).where(d != 0)
        result.index.name   = "Average Open Case Reserve"
        result.columns.name = None
        diagnostics["Average Open Case Reserve"] = result

    return diagnostics


def write_diagnostics_excel(diagnostics, path):
    """Write pre-method triangle diagnostics, one sheet per metric."""
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, data in diagnostics.items():
            if data is not None and not data.empty:
                data.to_excel(writer, sheet_name=sheet_name)
    print(f"  Saved → {path}")


def main():
    os.makedirs(OUTPUT_PREP_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DATA_DIR, exist_ok=True)

    frames = []
    for src in SOURCES:
        print(f"  Reading {src['measure']} from {src['file_path']} / {src.get('sheet_name','')}")
        df = read_triangle(**src)
        print(f"    → {len(df)} observations across "
              f"{df['period'].nunique()} periods, {df['age'].nunique()} ages")
        frames.append(df)

    all_data = pd.concat(frames, ignore_index=True)

    # Re-apply consistent categorical ordering from the first source
    ref = frames[0]
    all_data["period"]    = pd.Categorical(all_data["period"],
                                           categories=ref["period"].cat.categories, ordered=True)
    all_data["age"]       = pd.Categorical(all_data["age"],
                                           categories=ref["age"].cat.categories,    ordered=True)
    all_data["measure"]   = all_data["measure"].astype("category")
    all_data["unit_type"] = all_data["unit_type"].astype("category")

    # Validate (skip Exposure from uniqueness check — same values repeated by design)
    validate(all_data[all_data["measure"] != "Exposure"])

    # ── Internal prep outputs ──────────────────────────────────────────────────
    all_data.to_pickle(f"{OUTPUT_PREP_DIR}/triangles.pkl")
    all_data.to_csv(f"{OUTPUT_PREP_DIR}/triangles.csv", index=False)

    # ── Excel outputs ──────────────────────────────────────────────────────────
    write_long_excel(     all_data, f"{OUTPUT_DATA_DIR}/long.xlsx")
    write_triangles_excel(all_data, f"{OUTPUT_DATA_DIR}/triangles.xlsx")
    diagnostics = compute_diagnostics(all_data)
    write_diagnostics_excel(diagnostics, f"{OUTPUT_DATA_DIR}/pre-method-triangle-diagnostics.xlsx")

    print(f"\nNormalized {len(all_data)} total rows across {all_data['measure'].nunique()} measures.")
    print(f"Periods : {all_data['period'].cat.categories.tolist()}")
    print(f"Ages    : {all_data['age'].cat.categories.tolist()}")
    print(f"Measures: {all_data['measure'].cat.categories.tolist()}")


if __name__ == "__main__":
    print("=== Step 1: Normalizing triangles ===")
    main()

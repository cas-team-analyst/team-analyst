"""
Script 6: Apply the Bornhuetter-Ferguson (BF) method.

BF blends the chain-ladder and initial-expected methods using % developed
as the credibility weight. Fully deterministic — no agent selections required.

    BF Ultimate = Actual + (1 - % developed) x Expected Ultimate

Usage (run from the project root):
    python scripts/6-apply-bf.py

Inputs:
    output/prep/diagonal.pkl
    output/chain-ladder/cl_cdfs.csv         (pct_developed by measure x age)
    output/initial-expected/ie_ultimates.csv

Outputs:
    output/bornhuetter-ferguson/
        bornhuetter-ferguson.xlsx   (canonical format: Incurred, Paid, Reported, Closed sheets)
        bf_ultimates.csv            (internal: BF ultimates per period x measure)
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


INPUT_DIAGONAL     = "output/prep/diagonal.pkl"
INPUT_CL_CDFS      = "output/chain-ladder/cl_cdfs.csv"
INPUT_IE_ULTIMATES = "output/initial-expected/ie_ultimates.csv"
OUTPUT_DIR         = "output/bornhuetter-ferguson"

MEASURE_DISPLAY = {
    "Incurred Loss":  "Incurred",
    "Paid Loss":      "Paid",
    "Reported Count": "Reported",
    "Closed Count":   "Closed",
}

UNPAID_PROXY = {
    "Incurred Loss":  "Paid Loss",
    "Paid Loss":      "Paid Loss",
    "Reported Count": "Closed Count",
    "Closed Count":   "Closed Count",
}

# Column name for the "unreported/unpaid" fraction and dollar amount
PERCENT_COL = {
    "Incurred Loss":  "% Unreported",
    "Paid Loss":      "% Unpaid",
    "Reported Count": "% Unreported",
    "Closed Count":   "% Unpaid",
}
DOLLAR_COL = {
    "Incurred Loss":  "$ Unreported",
    "Paid Loss":      "$ Unpaid",
    "Reported Count": "Unreported Counts",
    "Closed Count":   "Unpaid Counts",
}
ACTUAL_COL = {
    "Incurred Loss":  "$ Reported",
    "Paid Loss":      "$ Paid",
    "Reported Count": "Reported Counts",
    "Closed Count":   "Closed Counts",
}


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    diag   = pd.read_pickle(INPUT_DIAGONAL)
    cl_cdf = pd.read_csv(INPUT_CL_CDFS)
    ie_ult = pd.read_csv(INPUT_IE_ULTIMATES)

    # Standardise keys to string
    for df in (diag, cl_cdf, ie_ult):
        for col in ("period","measure","age","current_age"):
            if col in df.columns:
                df[col] = df[col].astype(str)

    # Build lookup: (measure, age) -> pct_developed
    pct_lookup = cl_cdf.set_index(["measure", "age"])["pct_developed"].to_dict()
    cdf_lookup = cl_cdf.set_index(["measure", "age"])["cdf"].to_dict()

    # Build lookup: (period, measure) -> expected_ultimate
    ie_lookup = ie_ult.set_index(["period", "measure"])["expected_ultimate"].to_dict()

    # Diagonal lookup: (period, measure) -> actual
    diag_lookup = diag.set_index(["period", "measure"])["value"].to_dict()

    rows = []
    for _, r in diag.iterrows():
        measure = r["measure"]
        if measure not in MEASURE_DISPLAY:
            continue

        period   = r["period"]
        age      = r["age"]
        actual   = r["value"]

        pct_dev  = pct_lookup.get((measure, age), np.nan)
        cdf      = cdf_lookup.get((measure, age), np.nan)
        expected = ie_lookup.get((period, measure), np.nan)

        pct_undev  = (1 - pct_dev) if pd.notna(pct_dev) else np.nan
        dollar_undev = pct_undev * expected if pd.notna(pct_undev) and pd.notna(expected) else np.nan
        bf_ult       = actual + dollar_undev if pd.notna(dollar_undev) else np.nan
        bf_ibnr      = dollar_undev

        proxy  = UNPAID_PROXY.get(measure)
        proxy_actual = diag_lookup.get((period, proxy), actual)
        bf_unpaid    = bf_ult - proxy_actual if pd.notna(bf_ult) else np.nan

        rows.append(dict(
            period       = period,
            measure      = measure,
            current_age  = age,
            actual       = round(actual, 2),
            expected     = round(expected, 2) if pd.notna(expected) else np.nan,
            cdf          = cdf,
            pct_dev      = pct_dev,
            pct_undev    = pct_undev,
            dollar_undev = round(dollar_undev, 2) if pd.notna(dollar_undev) else np.nan,
            bf_ultimate  = round(bf_ult, 2)       if pd.notna(bf_ult)       else np.nan,
            bf_ibnr      = round(bf_ibnr, 2)      if pd.notna(bf_ibnr)     else np.nan,
            bf_unpaid    = round(bf_unpaid, 2)     if pd.notna(bf_unpaid)   else np.nan,
        ))

    bf = pd.DataFrame(rows)

    # Save internal CSV
    bf.to_csv(f"{OUTPUT_DIR}/bf_ultimates.csv", index=False)

    # Write canonical Excel
    with pd.ExcelWriter(f"{OUTPUT_DIR}/bornhuetter-ferguson.xlsx", engine="openpyxl") as writer:
        for measure, display in MEASURE_DISPLAY.items():
            sub = bf[bf["measure"] == measure].copy()
            if sub.empty:
                continue
            sub["period_int"] = _try_int(sub["period"])
            sub["age_int"] = _try_int(sub["current_age"])
            sub = sub.sort_values("period_int")

            pct_col    = PERCENT_COL[measure]
            dollar_col = DOLLAR_COL[measure]
            actual_col = ACTUAL_COL[measure]

            out = pd.DataFrame({
                "Accident Period":  _try_int(sub["period"]).values,
                "Current Age": _try_int(sub["current_age"]).values,
                "Initial Expected": sub["expected"].values,
                "CDF":              sub["cdf"].values,
                pct_col:            sub["pct_undev"].values,
                dollar_col:         sub["dollar_undev"].values,
                actual_col:         sub["actual"].values,
                "Ultimate":         sub["bf_ultimate"].values,
                "IBNR":             sub["bf_ibnr"].values,
                "Unpaid":           sub["bf_unpaid"].values,
            })
            out.to_excel(writer, sheet_name=display, index=False)

    print(f"  Saved -> {OUTPUT_DIR}/bornhuetter-ferguson.xlsx, bf_ultimates.csv")

    print("\nBF summary by measure:")
    pd.set_option("display.float_format", lambda x: f"{x:,.2f}")
    for m in bf["measure"].unique():
        sub = bf[bf["measure"] == m]
        if sub["bf_ultimate"].isna().all():
            continue
        print(f"  {m}: Actual={sub['actual'].sum():,.0f}  "
              f"BF Ultimate={sub['bf_ultimate'].sum():,.0f}  "
              f"IBNR={sub['bf_ibnr'].sum():,.0f}")


if __name__ == "__main__":
    print("=== Step 6: Applying Bornhuetter-Ferguson method ===")
    main()

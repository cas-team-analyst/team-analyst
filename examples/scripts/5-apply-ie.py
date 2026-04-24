"""
Script 5: Apply the Initial Expected (IE) method using ELR × Exposure.

Reads Expected Loss Ratios and Expected Frequencies from the ELR file,
multiplies by the latest Exposure diagonal to compute initial expected
ultimates, then writes canonical Excel output.

Usage (run from the project root):
    python scripts/5-apply-ie.py

Inputs:
    output/prep/diagonal.pkl
    output/chain-ladder/cl_ultimates.csv
    data/elrs.xlsx                          (ELR file with loss ratios and frequencies)

ELR file format:
    Sheet "ELR" with columns:
      - Accident Period
      - Expected Loss Ratio    (e.g., 0.75 = 75% of exposure)
      - Expected Frequency     (e.g., 1.35 counts per exposure unit)

Outputs:
    output/initial-expected/
        initial-expected.xlsx   (Loss: period, age, exposure, loss rate, selected loss;
                                 Counts: period, age, exposure, frequency, selected counts)
        ie_ultimates.csv        (internal: expected ultimates per period x measure)
    output/inputs/
        ie_inputs.json          (copy of computed IE inputs for reference)
"""

import pandas as pd
import numpy as np
import json
import os


def _try_int(series):
    """Convert series to int if all values are numeric, else return as-is."""
    try:
        return series.astype(str).apply(lambda x: int(float(x)))
    except (ValueError, TypeError):
        return series.astype(str)


# ── Configure these paths ──────────────────────────────────────────────────────
INPUT_DIAGONAL   = "output/prep/diagonal.pkl"
INPUT_CL_ULTS    = "output/chain-ladder/cl_ultimates.csv"
ELR_FILE         = "data/canonical-elrs.xlsx"
ELR_SHEET        = "ELR"
OUTPUT_DIR       = "output/initial-expected"
OUTPUT_INPUTS    = "output/inputs"
# ── End configuration ──────────────────────────────────────────────────────────

# Unpaid = Ultimate(this measure) - diagonal(proxy measure)
UNPAID_PROXY = {
    "Incurred Loss":  "Paid Loss",
    "Paid Loss":      "Paid Loss",
    "Reported Count": "Closed Count",
    "Closed Count":   "Closed Count",
}


def load_elrs(path, sheet_name):
    """Load the ELR file and return a DataFrame with period, elr, expected_frequency."""
    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    df.columns = df.columns.str.strip()

    # Standardise column names
    col_map = {}
    for col in df.columns:
        cl = col.lower().replace("_", " ")
        if "accident" in cl and "period" in cl:
            col_map[col] = "period"
        elif "loss" in cl and "rate" in cl:
            col_map[col] = "elr"
        elif "frequency" in cl or ("expected" in cl and "freq" in cl):
            col_map[col] = "expected_frequency"

    df = df.rename(columns=col_map)
    df["period"] = df["period"].astype(str).str.strip()

    # Try to convert period to int string for consistency
    try:
        df["period"] = df["period"].apply(lambda x: str(int(float(x))))
    except (ValueError, TypeError):
        pass

    return df


def compute_ie_inputs(elr_df, diag):
    """Compute IE ultimate = ELR × Exposure for losses, Frequency × Exposure for counts."""
    # Get latest exposure per period from the diagonal
    exp = diag[diag["measure"] == "Exposure"].copy()
    if exp.empty:
        raise ValueError("No 'Exposure' measure found in the diagonal. "
                         "Ensure the triangles file includes an Exposure sheet.")

    exp["period"] = exp["period"].astype(str)
    exp_lookup = exp.set_index("period")["value"].to_dict()

    ie_rows = []
    for _, row in elr_df.iterrows():
        period = str(row["period"])
        exposure = exp_lookup.get(period, np.nan)

        if pd.isna(exposure):
            print(f"  Warning: No exposure found for period {period}, skipping")
            continue

        # Loss IE = ELR × Exposure
        if "elr" in row.index and pd.notna(row.get("elr")):
            loss_ult = float(row["elr"]) * float(exposure)
            ie_rows.append(dict(period=period, measure="Incurred Loss",
                                expected_ultimate=loss_ult))
            ie_rows.append(dict(period=period, measure="Paid Loss",
                                expected_ultimate=loss_ult))

        # Count IE = Expected Frequency × Exposure
        if "expected_frequency" in row.index and pd.notna(row.get("expected_frequency")):
            count_ult = float(row["expected_frequency"]) * float(exposure)
            ie_rows.append(dict(period=period, measure="Reported Count",
                                expected_ultimate=count_ult))
            ie_rows.append(dict(period=period, measure="Closed Count",
                                expected_ultimate=count_ult))

    return pd.DataFrame(ie_rows)


def build_ie_results(diag, cl_ults, ie_df):
    """Merge diagonal, CL ultimates, and IE inputs into one result DataFrame."""
    diag = diag.copy()
    diag["period"]  = diag["period"].astype(str)
    diag["measure"] = diag["measure"].astype(str)
    diag["age"]     = diag["age"].astype(str)

    cl_wide = cl_ults.pivot_table(index="period", columns="measure",
                                  values="cl_ultimate", aggfunc="first")

    results = []
    for _, r in diag.iterrows():
        period  = r["period"]
        measure = r["measure"]
        actual  = r["value"]

        ie_row = ie_df[(ie_df["period"] == period) & (ie_df["measure"] == measure)]
        ie_ult = float(ie_row["expected_ultimate"].iloc[0]) if not ie_row.empty else np.nan

        # CL ultimates for sibling measures
        cl_inc = cl_wide.get("Incurred Loss", {}).get(period, np.nan)
        cl_paid= cl_wide.get("Paid Loss",     {}).get(period, np.nan)
        cl_rep = cl_wide.get("Reported Count",{}).get(period, np.nan)
        cl_cls = cl_wide.get("Closed Count",  {}).get(period, np.nan)

        proxy_measure = UNPAID_PROXY.get(measure)
        proxy_actual  = diag[diag["measure"] == proxy_measure]
        proxy_actual  = proxy_actual[proxy_actual["period"] == period]
        proxy_val     = float(proxy_actual["value"].iloc[0]) if not proxy_actual.empty else actual

        ibnr   = (ie_ult - actual)     if pd.notna(ie_ult) else np.nan
        unpaid = (ie_ult - proxy_val)  if pd.notna(ie_ult) else np.nan

        results.append(dict(
            period       = period,
            measure      = measure,
            current_age  = r["age"],
            actual       = round(actual, 2),
            cl_incurred  = cl_inc,
            cl_paid      = cl_paid,
            cl_reported  = cl_rep,
            cl_closed    = cl_cls,
            ie_ultimate  = round(ie_ult, 2) if pd.notna(ie_ult) else np.nan,
            ie_ibnr      = round(ibnr,   2) if pd.notna(ibnr)   else np.nan,
            ie_unpaid    = round(unpaid, 2) if pd.notna(unpaid)  else np.nan,
        ))

    return pd.DataFrame(results)


def exposure_for_periods(diag):
    """Extract the latest exposure value per period."""
    exp = diag[diag["measure"] == "Exposure"].copy()
    if exp.empty:
        return {}
    exp["period"] = exp["period"].astype(str)
    exp["age_int"] = _try_int(exp["age"])
    latest = exp.sort_values("age_int").groupby("period").last()
    return latest["value"].to_dict()


def write_ie_excel(results, exp_by_period, elr_df, path):
    """Write initial-expected Excel: Loss and Counts sheets with display columns only."""
    elr_by_period = (
        dict(zip(elr_df["period"].astype(str), elr_df["elr"]))
        if "elr" in elr_df.columns
        else {}
    )
    freq_by_period = (
        dict(zip(elr_df["period"].astype(str), elr_df["expected_frequency"]))
        if "expected_frequency" in elr_df.columns
        else {}
    )

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        # ── Loss sheet (one row per accident period; incurred IE ultimate) ───
        loss_measures = ["Incurred Loss", "Paid Loss"]
        loss = results[results["measure"].isin(loss_measures)].copy()
        inc = loss[loss["measure"] == "Incurred Loss"].set_index("period")
        if not inc.empty:
            out_loss = pd.DataFrame({
                "Accident Period":     _try_int(inc.index.to_series()),
                "Current Age":         _try_int(inc["current_age"]),
                "Exposure":            [exp_by_period.get(str(p), np.nan) for p in inc.index],
                "Selected Loss Rate":  [elr_by_period.get(str(p), np.nan) for p in inc.index],
                "Selected Loss":       inc["ie_ultimate"],
            })
            out_loss.to_excel(writer, sheet_name="Loss", index=False)

        # ── Counts sheet (one row per period; reported-count IE ultimate) ────
        count_measures = ["Reported Count", "Closed Count"]
        counts = results[results["measure"].isin(count_measures)].copy()
        rep = counts[counts["measure"] == "Reported Count"].set_index("period")
        if not rep.empty:
            out_counts = pd.DataFrame({
                "Accident Period":       _try_int(rep.index.to_series()),
                "Current Age":           _try_int(rep["current_age"]),
                "Exposure":              [exp_by_period.get(str(p), np.nan) for p in rep.index],
                "Selected Frequency":    [freq_by_period.get(str(p), np.nan) for p in rep.index],
                "Selected Counts":       rep["ie_ultimate"],
            })
            out_counts.to_excel(writer, sheet_name="Counts", index=False)

    print(f"  Saved -> {path}")


def main():
    os.makedirs(OUTPUT_DIR,    exist_ok=True)
    os.makedirs(OUTPUT_INPUTS, exist_ok=True)

    diag    = pd.read_pickle(INPUT_DIAGONAL)
    diag["period"]  = diag["period"].astype(str)
    diag["measure"] = diag["measure"].astype(str)
    diag["age"]     = diag["age"].astype(str)

    cl_ults = pd.read_csv(INPUT_CL_ULTS)
    cl_ults["period"]  = cl_ults["period"].astype(str)
    cl_ults["measure"] = cl_ults["measure"].astype(str)

    # Load ELRs and compute IE inputs from ELR × Exposure
    elr_df = load_elrs(ELR_FILE, ELR_SHEET)
    print(f"Loaded ELRs for {len(elr_df)} periods")

    ie_df = compute_ie_inputs(elr_df, diag)
    print(f"Computed {len(ie_df)} IE input entries")

    # Save IE inputs as JSON for reference
    ie_json = ie_df.to_dict("records")
    with open(f"{OUTPUT_INPUTS}/ie_inputs.json", "w") as f:
        json.dump(ie_json, f, indent=2)

    exp_by_period = exposure_for_periods(diag)
    results       = build_ie_results(diag, cl_ults, ie_df)

    # Save internal CSV
    ie_out = results[["period","measure","current_age","actual","ie_ultimate","ie_ibnr","ie_unpaid"]].copy()
    ie_out.columns = ["period","measure","current_age","actual","expected_ultimate","ie_ibnr","ie_unpaid"]
    ie_out.to_csv(f"{OUTPUT_DIR}/ie_ultimates.csv", index=False)

    write_ie_excel(results, exp_by_period, elr_df, f"{OUTPUT_DIR}/initial-expected.xlsx")

    print("\nIE summary by measure:")
    pd.set_option("display.float_format", lambda x: f"{x:,.2f}")
    for m in results["measure"].unique():
        sub = results[results["measure"] == m]
        if sub["ie_ultimate"].isna().all():
            continue
        print(f"  {m}: Actual={sub['actual'].sum():,.0f}  "
              f"IE Ultimate={sub['ie_ultimate'].sum():,.0f}  "
              f"IBNR={sub['ie_ibnr'].sum():,.0f}")

    print(f"  Saved -> {OUTPUT_DIR}/ie_ultimates.csv, initial-expected.xlsx")


if __name__ == "__main__":
    print("=== Step 5: Applying Initial Expected method (ELR × Exposure) ===")
    main()
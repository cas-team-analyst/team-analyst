"""
Script 4: Apply chain-ladder LDF selections to project ultimates.

Reads selections from output/selections/cl_selections.json (written by the agent),
converts them to CDFs, projects ultimates, then writes canonical Excel output.

Usage (run from the project root):
    python scripts/4-apply-cl-selections.py

Inputs:
    output/prep/triangles.pkl
    output/prep/diagonal.pkl
    output/selections/cl_selections.json

Selections JSON format:
    [
      {"measure": "Incurred Loss", "interval": "12-24", "selected_ldf": 1.7500, "reasoning": "..."},
      {"measure": "Incurred Loss", "interval": "tail",  "selected_ldf": 1.0150, "reasoning": "..."},
      ...
    ]
    Exposure is handled automatically (CDF = 1, fully developed).

Outputs:
    output/chain-ladder/
        chain-ladder.xlsx    (canonical format: one sheet per measure)
        cl_cdfs.csv          (internal: CDFs and % developed per measure x age)
        cl_ultimates.csv     (internal: projected ultimates per period x measure)
    output/inputs/
        cl_selections.json   (copy of selections for reference)
"""

import pandas as pd
import numpy as np
import json
import os
import shutil


def _try_int(series):
    """Convert series to int if all values are numeric, else return as-is."""
    try:
        return series.astype(str).apply(lambda x: int(float(x)))
    except (ValueError, TypeError):
        return series.astype(str)


INPUT_TRIANGLES  = "output/prep/triangles.pkl"
INPUT_DIAGONAL   = "output/prep/diagonal.pkl"
SELECTIONS_JSON  = "output/selections/cl_selections.json"
OUTPUT_DIR       = "output/chain-ladder"
OUTPUT_INPUTS    = "output/inputs"

MEASURE_DISPLAY = {
    "Incurred Loss":  "Incurred",
    "Paid Loss":      "Paid",
    "Reported Count": "Reported",
    "Closed Count":   "Closed",
    "Exposure":       "Exposure",
}

# Unpaid = Ultimate(this measure) - diagonal(proxy measure)
UNPAID_PROXY = {
    "Incurred Loss":  "Paid Loss",
    "Paid Loss":      "Paid Loss",
    "Reported Count": "Closed Count",
    "Closed Count":   "Closed Count",
}


def build_cdfs(selections_list, ages):
    by_measure = {}
    for s in selections_list:
        m = s["measure"]
        by_measure.setdefault(m, {})[s["interval"]] = s["selected_ldf"]

    intervals = [f"{ages[i]}-{ages[i+1]}" for i in range(len(ages) - 1)]
    results   = []

    for measure, sel in by_measure.items():
        tail = sel.get("tail", 1.000)
        cdfs = {ages[-1]: tail}

        for i in range(len(ages) - 2, -1, -1):
            ata           = sel.get(intervals[i], np.nan)
            cdfs[ages[i]] = ata * cdfs[ages[i + 1]]

        for age, cdf in cdfs.items():
            results.append(dict(
                measure       = measure,
                age           = age,
                cdf           = round(float(cdf), 6),
                pct_developed = round(1.0 / float(cdf), 6) if cdf and cdf != 0 else np.nan,
            ))

    return pd.DataFrame(results)


def add_exposure_cdfs(cdf_df, ages, measures_in_diagonal):
    if "Exposure" not in cdf_df["measure"].values and "Exposure" in measures_in_diagonal:
        rows = [dict(measure="Exposure", age=a, cdf=1.0, pct_developed=1.0) for a in ages]
        cdf_df = pd.concat([cdf_df, pd.DataFrame(rows)], ignore_index=True)
    return cdf_df


def project_ultimates(diag, cdf_df):
    cdf_lookup = cdf_df.set_index(["measure", "age"])[["cdf", "pct_developed"]]
    rows = []
    for _, r in diag.iterrows():
        key = (str(r["measure"]), str(r["age"]))
        if key in cdf_lookup.index:
            cdf      = cdf_lookup.loc[key, "cdf"]
            pct      = cdf_lookup.loc[key, "pct_developed"]
            ultimate = r["value"] * cdf if pd.notna(cdf) else np.nan
            ibnr     = ultimate - r["value"] if pd.notna(ultimate) else np.nan
        else:
            cdf, pct, ultimate, ibnr = np.nan, np.nan, np.nan, np.nan

        rows.append(dict(
            period       = str(r["period"]),
            measure      = str(r["measure"]),
            current_age  = str(r["age"]),
            actual       = round(r["value"], 2),
            cdf          = cdf,
            pct_developed= pct,
            cl_ultimate  = round(ultimate, 2) if pd.notna(ultimate) else np.nan,
            cl_ibnr      = round(ibnr,    2)  if pd.notna(ibnr)     else np.nan,
        ))
    return pd.DataFrame(rows)


def add_unpaid(ultimates_df):
    diag_lookup = ultimates_df.set_index(["period", "measure"])["actual"].to_dict()
    unpaid_vals = []
    for _, r in ultimates_df.iterrows():
        proxy = UNPAID_PROXY.get(r["measure"])
        if proxy is None:
            unpaid_vals.append(np.nan)
        else:
            proxy_actual = diag_lookup.get((r["period"], proxy), np.nan)
            if pd.notna(r["cl_ultimate"]) and pd.notna(proxy_actual):
                unpaid_vals.append(round(r["cl_ultimate"] - proxy_actual, 2))
            else:
                unpaid_vals.append(np.nan)
    ultimates_df = ultimates_df.copy()
    ultimates_df["cl_unpaid"] = unpaid_vals
    return ultimates_df


def write_chain_ladder_excel(ultimates_df, path):
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for measure, display in MEASURE_DISPLAY.items():
            sub = ultimates_df[ultimates_df["measure"] == measure].copy()
            if sub.empty:
                continue
            sub["period_int"] = _try_int(sub["period"])
            sub["age_int"] = _try_int(sub["current_age"])
            sub = sub.sort_values("period_int")

            if measure == "Exposure":
                out = pd.DataFrame({
                    "Accident Period": _try_int(sub["period"]).values,
                    "Current Age": _try_int(sub["current_age"]).values,
                    "Exposure":        sub["actual"].values,
                    "CDF":             sub["cdf"].values,
                    "Ultimate":        sub["cl_ultimate"].values,
                })
            else:
                out = pd.DataFrame({
                    "Accident Period": _try_int(sub["period"]).values,
                    "Current Age": _try_int(sub["current_age"]).values,
                    display:           sub["actual"].values,
                    "CDF":             sub["cdf"].values,
                    "Ultimate":        sub["cl_ultimate"].values,
                    "IBNR":            sub["cl_ibnr"].values,
                    "Unpaid":          sub["cl_unpaid"].values,
                })
            out.to_excel(writer, sheet_name=display, index=False)
    print(f"  Saved -> {path}")


def main():
    os.makedirs(OUTPUT_DIR,    exist_ok=True)
    os.makedirs(OUTPUT_INPUTS, exist_ok=True)

    with open(SELECTIONS_JSON) as f:
        selections = json.load(f)
    print(f"Loaded {len(selections)} selections")

    df   = pd.read_pickle(INPUT_TRIANGLES)
    diag = pd.read_pickle(INPUT_DIAGONAL)
    ages = [str(a) for a in df["age"].cat.categories.tolist()]
    measures_in_diag = [str(m) for m in diag["measure"].unique()]

    cdf_df    = build_cdfs(selections, ages)
    cdf_df    = add_exposure_cdfs(cdf_df, ages, measures_in_diag)
    ultimates = project_ultimates(diag, cdf_df)
    ultimates = add_unpaid(ultimates)

    print("\nChain Ladder summary by measure:")
    pd.set_option("display.float_format", lambda x: f"{x:,.2f}")
    for m in ultimates["measure"].unique():
        sub = ultimates[ultimates["measure"] == m]
        if sub["cl_ultimate"].isna().all():
            continue
        print(f"  {m}: Actual={sub['actual'].sum():,.0f}  "
              f"Ultimate={sub['cl_ultimate'].sum():,.0f}  "
              f"IBNR={sub['cl_ibnr'].sum():,.0f}")

    cdf_df.to_csv(   f"{OUTPUT_DIR}/cl_cdfs.csv",      index=False)
    ultimates.to_csv(f"{OUTPUT_DIR}/cl_ultimates.csv", index=False)
    write_chain_ladder_excel(ultimates, f"{OUTPUT_DIR}/chain-ladder.xlsx")
    shutil.copy2(SELECTIONS_JSON, f"{OUTPUT_INPUTS}/cl_selections.json")
    print(f"  Saved -> {OUTPUT_DIR}/cl_cdfs.csv, cl_ultimates.csv")


if __name__ == "__main__":
    print("=== Step 4: Applying CL selections ===")
    main()

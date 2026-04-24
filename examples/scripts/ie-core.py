"""
IE core: read inputs and compute Initial Expected ultimates.

Inputs:
    output/prep/diagonal.pkl      (for latest Exposure per period)
    data/canonical-elrs.xlsx      (ELR and Expected Frequency per period)

Output:
    DataFrame with columns: period, measure, expected_ultimate
"""

import pandas as pd
import numpy as np

INPUT_DIAGONAL = "output/prep/diagonal.pkl"
ELR_FILE       = "data/canonical-elrs.xlsx"
ELR_SHEET      = "ELR"


def load_exposure(diagonal_path):
    diag = pd.read_pickle(diagonal_path)
    exp = diag[diag["measure"].astype(str) == "Exposure"].copy()
    exp["period"] = exp["period"].astype(str)
    return exp.set_index("period")["value"].to_dict()


def load_elrs(path, sheet_name):
    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    df.columns = df.columns.str.strip()
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
    try:
        df["period"] = df["period"].apply(lambda x: str(int(float(x))))
    except (ValueError, TypeError):
        pass
    return df


def compute_ie_ultimates(elr_df, exposure):
    rows = []
    for _, row in elr_df.iterrows():
        period = str(row["period"])
        exp = exposure.get(period, np.nan)
        if pd.isna(exp):
            print(f"  Warning: No exposure for period {period}, skipping")
            continue
        if "elr" in row.index and pd.notna(row.get("elr")):
            loss_ult = float(row["elr"]) * float(exp)
            rows.append(dict(period=period, measure="Incurred Loss", expected_ultimate=loss_ult))
            rows.append(dict(period=period, measure="Paid Loss",     expected_ultimate=loss_ult))
        if "expected_frequency" in row.index and pd.notna(row.get("expected_frequency")):
            count_ult = float(row["expected_frequency"]) * float(exp)
            rows.append(dict(period=period, measure="Reported Count", expected_ultimate=count_ult))
            rows.append(dict(period=period, measure="Closed Count",   expected_ultimate=count_ult))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    exposure = load_exposure(INPUT_DIAGONAL)
    elr_df   = load_elrs(ELR_FILE, ELR_SHEET)
    ie       = compute_ie_ultimates(elr_df, exposure)
    print(ie.to_string(index=False))

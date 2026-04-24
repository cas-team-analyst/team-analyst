"""
BF core: compute Bornhuetter-Ferguson ultimates from CL and IE outputs.

Formula:
    BF Ultimate = Actual + (1 - pct_developed) x IE Expected
    BF IBNR     = (1 - pct_developed) x IE Expected

Inputs (all from prior scripts):
    output/prep/diagonal.pkl                     (actual values per period × measure)
    output/chain-ladder/cl_cdfs.csv              (cdf, pct_developed per measure × age)
    output/initial-expected/ie_ultimates.csv     (expected_ultimate per period × measure)

Output:
    DataFrame with columns: period, measure, actual, pct_developed, expected,
                            bf_ibnr, bf_ultimate
"""

import pandas as pd
import numpy as np

INPUT_DIAGONAL     = "output/prep/diagonal.pkl"
INPUT_CL_CDFS      = "output/chain-ladder/cl_cdfs.csv"
INPUT_IE_ULTIMATES = "output/initial-expected/ie_ultimates.csv"

MEASURES = ["Incurred Loss", "Paid Loss", "Reported Count", "Closed Count"]


def compute_bf(diagonal, cl_cdfs, ie_ultimates):
    pct_lookup = cl_cdfs.set_index(["measure", "age"])["pct_developed"].to_dict()
    ie_lookup  = ie_ultimates.set_index(["period", "measure"])["expected_ultimate"].to_dict()

    rows = []
    for _, r in diagonal.iterrows():
        measure = str(r["measure"])
        if measure not in MEASURES:
            continue
        period   = str(r["period"])
        actual   = r["value"]
        pct_dev  = pct_lookup.get((measure, str(r["age"])), np.nan)
        expected = ie_lookup.get((period, measure), np.nan)

        bf_ibnr    = (1 - pct_dev) * expected if pd.notna(pct_dev) and pd.notna(expected) else np.nan
        bf_ultimate = actual + bf_ibnr          if pd.notna(bf_ibnr) else np.nan

        rows.append(dict(
            period      = period,
            measure     = measure,
            actual      = actual,
            pct_developed = pct_dev,
            expected    = expected,
            bf_ibnr     = bf_ibnr,
            bf_ultimate = bf_ultimate,
        ))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    diagonal    = pd.read_pickle(INPUT_DIAGONAL)
    diagonal["period"]  = diagonal["period"].astype(str)
    diagonal["measure"] = diagonal["measure"].astype(str)
    diagonal["age"]     = diagonal["age"].astype(str)

    cl_cdfs      = pd.read_csv(INPUT_CL_CDFS)
    cl_cdfs["measure"] = cl_cdfs["measure"].astype(str)
    cl_cdfs["age"]     = cl_cdfs["age"].astype(str)

    ie_ultimates = pd.read_csv(INPUT_IE_ULTIMATES)
    ie_ultimates["period"]  = ie_ultimates["period"].astype(str)
    ie_ultimates["measure"] = ie_ultimates["measure"].astype(str)

    bf = compute_bf(diagonal, cl_cdfs, ie_ultimates)
    print(bf.to_string(index=False))

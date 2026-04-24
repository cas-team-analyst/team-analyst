"""
CL core: build CDFs from selected LDFs and project Chain Ladder ultimates.

Inputs:
    output/prep/triangles.pkl           (for ordered age list)
    output/prep/diagonal.pkl            (latest actual per period × measure)
    output/selections/cl_selections.json

Output:
    DataFrame with columns: period, measure, current_age, actual, cdf, pct_developed,
                            cl_ultimate, cl_ibnr
"""

import pandas as pd
import numpy as np
import json

INPUT_TRIANGLES = "output/prep/triangles.pkl"
INPUT_DIAGONAL  = "output/prep/diagonal.pkl"
SELECTIONS_JSON = "output/selections/cl_selections.json"


def build_cdfs(selections, ages):
    """Convert selected LDFs (including tail) into cumulative CDFs per measure × age."""
    by_measure = {}
    for s in selections:
        by_measure.setdefault(s["measure"], {})[s["interval"]] = s["selected_ldf"]

    intervals = [f"{ages[i]}-{ages[i+1]}" for i in range(len(ages) - 1)]
    rows = []
    for measure, sel in by_measure.items():
        tail = sel.get("tail", 1.0)
        cdfs = {ages[-1]: tail}
        for i in range(len(ages) - 2, -1, -1):
            cdfs[ages[i]] = sel.get(intervals[i], np.nan) * cdfs[ages[i + 1]]
        for age, cdf in cdfs.items():
            rows.append(dict(measure=measure, age=age, cdf=cdf,
                             pct_developed=1.0 / cdf if cdf else np.nan))
    return pd.DataFrame(rows)


def project_ultimates(diagonal, cdf_df):
    """Multiply each diagonal value by its CDF to get the CL ultimate."""
    cdf_lookup = cdf_df.set_index(["measure", "age"])[["cdf", "pct_developed"]]
    rows = []
    for _, r in diagonal.iterrows():
        key = (str(r["measure"]), str(r["age"]))
        if key in cdf_lookup.index:
            cdf = cdf_lookup.loc[key, "cdf"]
            pct = cdf_lookup.loc[key, "pct_developed"]
            ultimate = r["value"] * cdf
            ibnr     = ultimate - r["value"]
        else:
            cdf = pct = ultimate = ibnr = np.nan
        rows.append(dict(
            period       = str(r["period"]),
            measure      = str(r["measure"]),
            current_age  = str(r["age"]),
            actual       = r["value"],
            cdf          = cdf,
            pct_developed= pct,
            cl_ultimate  = ultimate,
            cl_ibnr      = ibnr,
        ))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    triangles = pd.read_pickle(INPUT_TRIANGLES)
    diagonal  = pd.read_pickle(INPUT_DIAGONAL)
    ages      = [str(a) for a in triangles["age"].cat.categories]

    with open(SELECTIONS_JSON) as f:
        selections = json.load(f)

    cdf_df    = build_cdfs(selections, ages)
    ultimates = project_ultimates(diagonal, cdf_df)

    print(ultimates.to_string(index=False))

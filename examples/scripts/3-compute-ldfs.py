"""
Script 3: Compute age-to-age factors (LDFs) and summary statistics.

For each (period, measure), computes the ratio of consecutive development ages.
Then summarizes across periods using several averaging methods so the agent
can make informed LDF selections.

Usage (run from the project root):
    python scripts/3-compute-ldfs.py

Inputs:
    output/prep/triangles.pkl

Outputs (written to OUTPUT_DIR):
    - ldf_triangle.pkl / ldf_triangle.csv  : per-period LDF for each interval
    - ldf_averages.pkl / ldf_averages.csv  : summary statistics for each interval × measure
      Columns per interval:
        weighted_all, simple_all, excl_hi_lo_all
        weighted_3yr, simple_3yr, excl_hi_lo_3yr
        weighted_5yr, simple_5yr, excl_hi_lo_5yr
        cv_3yr, cv_5yr       -- coefficient of variation (volatility)
        slope_3yr, slope_5yr -- linear trend (positive = rising LDFs over time)
"""

import pandas as pd
import numpy as np
import os

INPUT_FILE = "output/prep/triangles.pkl"
OUTPUT_DIR = "output/prep"


def compute_ldf_triangle(df):
    """Add prior_age, ldf (current/prior), and weight (= prior value) columns."""
    df = df.copy()
    ages = df["age"].cat.categories.tolist()
    df["_age_code"] = df["age"].cat.codes
    df = df.sort_values(["measure", "period", "_age_code"]).reset_index(drop=True)

    grp = ["period", "measure"]
    df["prior_age"]   = df.groupby(grp, observed=True)["age"].shift(1)
    df["prior_value"] = df.groupby(grp, observed=True)["value"].shift(1)
    df["ldf"]         = df["value"] / df["prior_value"].replace(0, np.nan)
    df["weight"]      = df["prior_value"]

    df["prior_age"] = pd.Categorical(df["prior_age"], categories=ages, ordered=True)

    intervals = [f"{ages[i]}-{ages[i+1]}" for i in range(len(ages)-1)]
    df["interval"] = df.apply(
        lambda r: f"{r['prior_age']}-{r['age']}" if pd.notna(r["prior_age"]) else None,
        axis=1
    )
    df["interval"] = pd.Categorical(df["interval"], categories=intervals, ordered=True)
    df = df.drop(columns=["_age_code", "prior_value"])
    return df


def _averages(factors, weights, n=None):
    """Weighted average, simple average, and exclude-high-low average."""
    if n:
        factors, weights = factors.tail(n), weights.tail(n)
    if len(factors) == 0:
        return np.nan, np.nan, np.nan
    w_sum = weights.sum()
    w_avg = (factors * weights).sum() / w_sum if w_sum > 0 else np.nan
    s_avg = factors.mean()
    ehl   = factors.sort_values().iloc[1:-1].mean() if len(factors) > 2 else s_avg
    return w_avg, s_avg, ehl


def _cv_slope(factors, n):
    fn = factors.tail(n)
    cv    = fn.std() / fn.mean() if len(fn) > 1 and fn.mean() != 0 else np.nan
    slope = float(np.polyfit(np.arange(len(fn)), fn.values, 1)[0]) if len(fn) > 1 else np.nan
    return cv, slope


def compute_ldf_averages(df_ldf):
    """Aggregate LDF statistics by measure × interval."""
    df = df_ldf[df_ldf["ldf"].notna()].copy()
    df = df.sort_values(["measure", "interval", "period"])

    def summarize(g):
        f, w = g["ldf"], g["weight"]
        wa, sa, ea   = _averages(f, w)
        w3, s3, e3   = _averages(f, w, 3)
        w5, s5, e5   = _averages(f, w, 5)
        cv3,  sl3    = _cv_slope(f, 3)
        cv5,  sl5    = _cv_slope(f, 5)
        return pd.Series(dict(
            weighted_all=wa, simple_all=sa, excl_hi_lo_all=ea,
            weighted_3yr=w3, simple_3yr=s3, excl_hi_lo_3yr=e3,
            weighted_5yr=w5, simple_5yr=s5, excl_hi_lo_5yr=e5,
            cv_3yr=cv3, cv_5yr=cv5, slope_3yr=sl3, slope_5yr=sl5,
        ))

    result = (df.groupby(["measure", "interval"], observed=True)
                .apply(summarize, include_groups=False)
                .reset_index())

    # Preserve measure/interval ordering
    result["measure"]  = pd.Categorical(result["measure"],  categories=df["measure"].cat.categories)
    result["interval"] = pd.Categorical(result["interval"], categories=df["interval"].cat.categories, ordered=True)

    # Round to 4 decimal places
    num_cols = [c for c in result.columns if c not in ["measure", "interval"]]
    result[num_cols] = result[num_cols].round(4)
    return result


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_pickle(INPUT_FILE)
    print(f"Loaded {len(df)} rows from {INPUT_FILE}")

    ldf_tri = compute_ldf_triangle(df)
    ldf_avg = compute_ldf_averages(ldf_tri)

    n_with_ldf = ldf_tri["ldf"].notna().sum()
    print(f"\nComputed {n_with_ldf} LDFs across "
          f"{ldf_tri['measure'].nunique()} measures, "
          f"{ldf_tri['interval'].dropna().nunique()} intervals")

    print("\nLDF averages sample (first measure):")
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 160)
    pd.set_option("display.float_format", lambda x: f"{x:.4f}")
    first_measure = ldf_avg["measure"].cat.categories[0]
    print(ldf_avg[ldf_avg["measure"] == first_measure].to_string(index=False))

    ldf_tri.to_pickle(f"{OUTPUT_DIR}/ldf_triangle.pkl")
    ldf_tri.to_csv(f"{OUTPUT_DIR}/ldf_triangle.csv", index=False)
    ldf_avg.to_pickle(f"{OUTPUT_DIR}/ldf_averages.pkl")
    ldf_avg.to_csv(f"{OUTPUT_DIR}/ldf_averages.csv", index=False)

    print(f"\nSaved → {OUTPUT_DIR}/ldf_triangle.[pkl|csv]  and  ldf_averages.[pkl|csv]")


if __name__ == "__main__":
    print("=== Step 3: Computing LDFs and averages ===")
    main()

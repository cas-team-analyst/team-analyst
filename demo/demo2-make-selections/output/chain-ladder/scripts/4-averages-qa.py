"""
goal: Calculate LDF averages and QA metrics by measure and development interval.

usage: Run from project root:
    .venv/Scripts/Activate.ps1; python demo/demo2-make-selections/output/chain-ladder/scripts/4-averages-qa.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_PATH = str(SCRIPT_DIR / "../data/") + "/"
METHOD_ID = "chainladder"


def calculate_ldf_averages(df_enhanced: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate LDF averages and QA metrics in wide format.

    Returns columns: measure, interval, weighted_all, simple_all, avg_exclude_high_low_all,
    weighted_3yr/5yr/10yr, simple_3yr/5yr/10yr, avg_exclude_high_low_3yr/5yr/10yr,
    cv_3yr/5yr/10yr, slope_3yr/5yr/10yr
    """
    df_with_ldfs = df_enhanced[df_enhanced['ldf'].notna()].copy()
    df_with_ldfs = df_with_ldfs.sort_values(['measure', 'interval', 'period'])

    unique_measures = df_with_ldfs['measure'].unique()
    interval_categories = df_with_ldfs['interval'].cat.categories.tolist()

    def calculate_group_summary(group):
        factors = group['ldf']
        weights = group['weight']

        def calc_avgs(f, w, n=None):
            if n:
                f, w = f.tail(n), w.tail(n)
            if len(f) == 0:
                return np.nan, np.nan, np.nan
            w_sum = w.sum()
            w_avg = (f * w).sum() / w_sum if w_sum > 0 else np.nan
            s_avg = f.mean()
            ehl_avg = f.sort_values().iloc[1:-1].mean() if len(f) > 2 else s_avg
            return w_avg, s_avg, ehl_avg

        all_w, all_s, all_ehl = calc_avgs(factors, weights)
        w3, s3, ehl3 = calc_avgs(factors, weights, 3)
        w5, s5, ehl5 = calc_avgs(factors, weights, 5)
        w10, s10, ehl10 = calc_avgs(factors, weights, 10)

        def calc_cv_slope(f, n):
            fn = f.tail(n)
            cv = fn.std() / fn.mean() if len(fn) > 1 and fn.mean() != 0 else np.nan
            slope = np.polyfit(np.arange(len(fn)), fn.values, 1)[0] if len(fn) > 1 else np.nan
            return cv, slope

        cv_3yr, slope_3yr = calc_cv_slope(factors, 3)
        cv_5yr, slope_5yr = calc_cv_slope(factors, 5)
        cv_10yr, slope_10yr = calc_cv_slope(factors, 10)

        return pd.Series({
            'cv_3yr': cv_3yr, 'cv_5yr': cv_5yr, 'cv_10yr': cv_10yr,
            'slope_3yr': slope_3yr, 'slope_5yr': slope_5yr, 'slope_10yr': slope_10yr,
            'weighted_all': all_w, 'simple_all': all_s, 'avg_exclude_high_low_all': all_ehl,
            'weighted_3yr': w3, 'simple_3yr': s3, 'avg_exclude_high_low_3yr': ehl3,
            'weighted_5yr': w5, 'simple_5yr': s5, 'avg_exclude_high_low_5yr': ehl5,
            'weighted_10yr': w10, 'simple_10yr': s10, 'avg_exclude_high_low_10yr': ehl10,
        })

    df_summary = (df_with_ldfs
                  .groupby(['measure', 'interval'], observed=True)
                  .apply(calculate_group_summary, include_groups=False)
                  .reset_index())

    df_summary['measure'] = pd.Categorical(df_summary['measure'], categories=unique_measures)
    df_summary['interval'] = pd.Categorical(df_summary['interval'], categories=interval_categories, ordered=True)

    avg_cols = [c for c in df_summary.columns if c not in ['measure', 'interval']]
    for col in avg_cols:
        df_summary[col] = df_summary[col].round(4)

    return df_summary


if __name__ == "__main__":
    input_file = OUTPUT_PATH + f"2_{METHOD_ID}_enhanced.parquet"
    df_enhanced = pd.read_parquet(input_file)
    print(f"Loaded {len(df_enhanced)} rows, {df_enhanced['ldf'].notna().sum()} with LDFs")
    print(f"Measures: {df_enhanced['measure'].unique().tolist()}")

    df_summary = calculate_ldf_averages(df_enhanced)
    print(f"\nCalculated {len(df_summary)} summary rows")

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.float_format', '{:.4f}'.format)

    # Show sample of averages
    print("\nSample averages (first measure, first 5 intervals):")
    sample = df_summary.head(5)[['measure', 'interval', 'weighted_all', 'simple_all', 'weighted_3yr', 'weighted_5yr']]
    print(sample.to_string())

    df_summary.to_parquet(OUTPUT_PATH + f"4_{METHOD_ID}_ldf_averages.parquet", index=False)
    df_summary.to_csv(OUTPUT_PATH + f"4_{METHOD_ID}_ldf_averages.csv", index=False)
    print(f"\nSaved: {OUTPUT_PATH}4_{METHOD_ID}_ldf_averages.[parquet|csv]")

    prior_selections_path = Path(OUTPUT_PATH) / "../prior-selections.csv"
    if prior_selections_path.exists():
        df_prior = pd.read_csv(prior_selections_path)
        print(f"\nFound {len(df_prior)} prior selections:")
        for _, row in df_prior.iterrows():
            print(f"  {row['measure']} | {row['interval']}: {row['selection']:.4f}")
    else:
        print("\nNo prior selections found (optional)")

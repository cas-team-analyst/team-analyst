# Calculates multiple types of averages (weighted, simple, excluding outliers) for the loss
# development factors using different time periods (3, 5, 10 years, or all available data). Also
# computes quality metrics like volatility and trends to help actuaries pick the best average.

"""
goal: Calculate LDF averages and select between them to set baseline selections which the user can then override.
contents:
    calculate_ldf_averages(): Calculate LDF averages and QA metrics by measure and development interval.

run-note: When copied to a project, run from the scripts/ directory:
    cd scripts/
    python 1d-ldf-averages.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

from modules import config

# Paths from modules/config.py — override here if needed:
OUTPUT_PATH = config.PROCESSED_DATA
METHOD_ID   = "chainladder"


def huber_mean(x, k=1.5, max_iter=25, tol=1e-6):
    """
    Robust mean via Huber's M-estimator (downweights points beyond k scaled
    MAD-deviations from the running center instead of dropping them outright).

    Args:
        x: array-like of factors
        k: tuning constant (1.5 is the standard default; smaller = more robust)
        max_iter: max iterations for the reweighting loop
        tol: convergence tolerance

    Returns:
        Huber mean, or np.nan if x is empty
    """
    x = np.asarray(x, dtype=float)
    if len(x) == 0:
        return np.nan
    if len(x) <= 2:
        return x.mean()

    mu = np.median(x)
    mad = np.median(np.abs(x - mu))
    scale = mad / 0.6745 if mad > 0 else x.std()
    if scale == 0:
        return mu

    for _ in range(max_iter):
        resid = (x - mu) / scale
        abs_resid = np.abs(resid)
        with np.errstate(divide='ignore'):
            weights = np.where(abs_resid <= k, 1.0, k / np.where(abs_resid == 0, 1.0, abs_resid))
        new_mu = np.sum(weights * x) / np.sum(weights)
        if abs(new_mu - mu) < tol:
            mu = new_mu
            break
        mu = new_mu

    return mu


def calculate_ldf_averages(df_enhanced: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate LDF averages and QA metrics in a single wide format DataFrame.
    Works with long format data from 1b-calculate-ldfs.py.
    
    Args:
        df_enhanced: Long format DataFrame with columns: period, age, value, measure, source,
                     prior_age, ldf, weight, interval
    
    Returns:
        Wide format DataFrame with columns:
        - measure: Type of measure (Incurred Loss, Paid Loss, etc.)
        - interval: Development interval (Dev Pd 1-Dev Pd 2, etc.)
        - weighted_all, simple_all, avg_exclude_high_low_all, median_all, huber_all,
          winsorized_all: Averages using all data
        - min_all, max_all: Minimum and maximum using all data
        - weighted_3yr, simple_3yr, median_3yr, huber_3yr: Averages using last 3 periods
        - weighted_5yr, simple_5yr, avg_exclude_high_low_5yr, median_5yr, huber_5yr,
          winsorized_5yr: Averages using last 5 periods
        - weighted_10yr, simple_10yr, avg_exclude_high_low_10yr, median_10yr, huber_10yr,
          winsorized_10yr: Averages using last 10 periods
        - cv_3yr, cv_5yr, cv_10yr: Coefficient of variation (volatility measure)
        - slope_3yr, slope_5yr, slope_10yr: Linear trend

        median, huber, and winsorized are robust to outliers: median and Huber mean
        (M-estimator) are computed for every window; winsorized (cap high/low instead
        of dropping them) mirrors avg_exclude_high_low and is only computed for
        all/5yr/10yr windows since it needs 3+ points to be meaningful.
    """
    # Filter to rows with valid LDF values (excludes first age in each period)
    df_with_ldfs = df_enhanced[df_enhanced['ldf'].notna()].copy()
    
    # Sort by period within each group for recency filtering
    df_with_ldfs = df_with_ldfs.sort_values(['measure', 'interval', 'period'])
    
    # Get unique measures and intervals for categorical ordering
    unique_measures = df_with_ldfs['measure'].unique()
    interval_categories = df_with_ldfs['interval'].cat.categories.tolist()
    
    def calculate_group_summary(group):
        """Calculate all averages and QA metrics for a single measure-interval combination."""
        factors = group['ldf']
        weights = group['weight']
        
        def calc_avgs(f, w, n=None):
            """Calculate weighted, simple, exclude-high-low, median, Huber, and winsorized averages."""
            if n:
                # Take last n observations
                f, w = f.tail(n), w.tail(n)

            # Skip if no data
            if len(f) == 0:
                return dict.fromkeys(
                    ['weighted', 'simple', 'exclude_high_low', 'median', 'huber', 'winsorized'], np.nan)

            # Weighted average
            w_sum = w.sum()
            w_avg = (f * w).sum() / w_sum if w_sum > 0 else np.nan

            # Simple average
            s_avg = f.mean()

            # Median: robust to outliers, no exclusion needed
            med = f.median()

            # Huber mean: robust to outliers, downweights rather than drops
            huber = huber_mean(f.values)

            if len(f) > 2:
                sorted_f = f.sort_values().reset_index(drop=True)
                # Exclude high and low (medial average)
                ehl_avg = sorted_f.iloc[1:-1].mean()
                # Winsorized: cap (don't drop) the single highest/lowest value
                winsorized = sorted_f.copy()
                winsorized.iloc[0] = winsorized.iloc[1]
                winsorized.iloc[-1] = winsorized.iloc[-2]
                winz_avg = winsorized.mean()
            else:
                ehl_avg = s_avg
                winz_avg = s_avg

            return {
                'weighted': w_avg, 'simple': s_avg, 'exclude_high_low': ehl_avg,
                'median': med, 'huber': huber, 'winsorized': winz_avg,
            }

        # Calculate averages for different time periods
        all_stats = calc_avgs(factors, weights)
        s3 = calc_avgs(factors, weights, 3)
        s5 = calc_avgs(factors, weights, 5)
        s10 = calc_avgs(factors, weights, 10)
        
        # Min and Max
        min_all = factors.min() if len(factors) > 0 else np.nan
        max_all = factors.max() if len(factors) > 0 else np.nan

        # CV and slope for 3, 5, and 10 year periods
        def calc_cv_slope(f, n):
            """Calculate CV and slope for n periods."""
            fn = f.tail(n)
            cv = fn.std() / fn.mean() if len(fn) > 1 and fn.mean() != 0 else np.nan
            if len(fn) > 1:
                x = np.arange(len(fn))
                slope = np.polyfit(x, fn.values, 1)[0]
            else:
                slope = np.nan
            return cv, slope
        
        cv_3yr, slope_3yr = calc_cv_slope(factors, 3)
        cv_5yr, slope_5yr = calc_cv_slope(factors, 5)
        cv_10yr, slope_10yr = calc_cv_slope(factors, 10)

        # Return as Series with all values
        return pd.Series({
            'cv_3yr': cv_3yr, 'cv_5yr': cv_5yr, 'cv_10yr': cv_10yr,
            'slope_3yr': slope_3yr, 'slope_5yr': slope_5yr, 'slope_10yr': slope_10yr,
            'weighted_all': all_stats['weighted'], 'simple_all': all_stats['simple'],
            'avg_exclude_high_low_all': all_stats['exclude_high_low'],
            'median_all': all_stats['median'], 'huber_all': all_stats['huber'],
            'winsorized_all': all_stats['winsorized'],
            'min_all': min_all, 'max_all': max_all,
            'weighted_3yr': s3['weighted'], 'simple_3yr': s3['simple'],
            'median_3yr': s3['median'], 'huber_3yr': s3['huber'],
            'weighted_5yr': s5['weighted'], 'simple_5yr': s5['simple'],
            'avg_exclude_high_low_5yr': s5['exclude_high_low'],
            'median_5yr': s5['median'], 'huber_5yr': s5['huber'],
            'winsorized_5yr': s5['winsorized'],
            'weighted_10yr': s10['weighted'], 'simple_10yr': s10['simple'],
            'avg_exclude_high_low_10yr': s10['exclude_high_low'],
            'median_10yr': s10['median'], 'huber_10yr': s10['huber'],
            'winsorized_10yr': s10['winsorized'],
        })
    
    # Group by measure and interval, apply calculations
    df_summary = (df_with_ldfs
                  .groupby(['measure', 'interval'], observed=True)
                  .apply(calculate_group_summary, include_groups=False)
                  .reset_index())
    
    # Round all average columns to 4 decimal places
    avg_cols = ['weighted_all', 'simple_all', 'avg_exclude_high_low_all',
                'median_all', 'huber_all', 'winsorized_all',
                'min_all', 'max_all',
                'weighted_3yr', 'simple_3yr', 'median_3yr', 'huber_3yr',
                'weighted_5yr', 'simple_5yr', 'avg_exclude_high_low_5yr',
                'median_5yr', 'huber_5yr', 'winsorized_5yr',
                'weighted_10yr', 'simple_10yr', 'avg_exclude_high_low_10yr',
                'median_10yr', 'huber_10yr', 'winsorized_10yr',
                'cv_3yr', 'cv_5yr', 'cv_10yr',
                'slope_3yr', 'slope_5yr', 'slope_10yr']
    for col in avg_cols:
        if col in df_summary.columns:
            df_summary[col] = df_summary[col].round(4)
    
    return df_summary


if __name__ == "__main__":  # pragma: no cover
    """Test the calculate_ldf_averages function."""
    # Read enhanced data from step 2
    input_file = OUTPUT_PATH + f"2_enhanced.csv"
    df_enhanced = pd.read_csv(input_file, dtype={'age': str, 'period': str, 'interval': str, 'prior_age': str})
    # Restore ordered categoricals from input file order (CSV drops dtype).
    # interval order drives the column sequence in the output averages table.
    _age_order = list(dict.fromkeys(df_enhanced['age'].dropna()))
    _period_order = list(dict.fromkeys(df_enhanced['period'].dropna()))
    _interval_order = list(dict.fromkeys(df_enhanced['interval'].dropna()))
    df_enhanced['age'] = pd.Categorical(df_enhanced['age'], categories=_age_order, ordered=True)
    df_enhanced['period'] = pd.Categorical(df_enhanced['period'], categories=_period_order, ordered=True)
    df_enhanced['interval'] = pd.Categorical(df_enhanced['interval'], categories=_interval_order, ordered=True)
    print(f"Loaded {len(df_enhanced)} rows, {df_enhanced['ldf'].notna().sum()} with LDFs")
    print(f"Measures: {df_enhanced['measure'].unique().tolist()}")
    
    # Calculate LDF summary
    df_summary = calculate_ldf_averages(df_enhanced)
    print(f"\nCalculated {len(df_summary)} summary rows")
    
    # Display summary by measure
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.float_format', '{:.4f}'.format)
    
    # Save output
    df_summary.to_csv(OUTPUT_PATH + f"4_ldf_averages.csv", index=False)
    print(f"\nSaved to: {OUTPUT_PATH}4_ldf_averages.csv")
    
    # Check for prior selections
    prior_selections_path = Path(OUTPUT_PATH) / "../prior-selections.csv"
    if prior_selections_path.exists():
        df_prior = pd.read_csv(prior_selections_path)
        print(f"\nFound {len(df_prior)} prior selections:")
        for _, row in df_prior.iterrows():
            print(f"  {row['measure']} | {row['interval']}: {row['selection']:.4f}")
    else:
        print("\nNo prior selections found (optional)")



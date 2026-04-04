# Calculates multiple types of averages (weighted, simple, excluding outliers) for the loss
# development factors using different time periods (3, 5, 10 years, or all available data). Also
# computes quality metrics like volatility and trends to help actuaries pick the best average.

"""
goal: Calculate LDF averages and select between them to set baseline selections which the user can then override.
contents:
    calculate_ldf_averages(): Calculate LDF averages and QA metrics by measure and development interval.

run-note: When copied to a project, run from the scripts/ directory:
    cd scripts/
    python 1d-averages-qa.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Replace when using this file in an actual project:
OUTPUT_PATH = "../processed-data/"
METHOD_ID = "chainladder"


def calculate_ldf_averages(df_enhanced: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate LDF averages and QA metrics in a single wide format DataFrame.
    Works with long format data from 2-enhance-data.py.
    
    Args:
        df_enhanced: Long format DataFrame with columns: period, age, value, measure, source,
                     prior_age, ldf, weight, interval
    
    Returns:
        Wide format DataFrame with columns:
        - measure: Type of measure (Incurred Loss, Paid Loss, etc.)
        - interval: Development interval (Dev Pd 1-Dev Pd 2, etc.)
        - weighted_all, simple_all, avg_exclude_high_low_all: Averages using all data
        - weighted_3yr, simple_3yr, avg_exclude_high_low_3yr: Averages using last 3 periods
        - weighted_5yr, simple_5yr, avg_exclude_high_low_5yr: Averages using last 5 periods
        - weighted_10yr, simple_10yr, avg_exclude_high_low_10yr: Averages using last 10 periods
        - cv_3yr, cv_5yr, cv_10yr: Coefficient of variation (volatility measure)
        - slope_3yr, slope_5yr, slope_10yr: Linear trend
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
            """Calculate weighted, simple, and exclude-high-low averages."""
            if n:
                # Take last n observations
                f, w = f.tail(n), w.tail(n)
            
            # Skip if no data
            if len(f) == 0:
                return np.nan, np.nan, np.nan
            
            # Weighted average
            w_sum = w.sum()
            w_avg = (f * w).sum() / w_sum if w_sum > 0 else np.nan
            
            # Simple average
            s_avg = f.mean()
            
            # Exclude high and low (medial average)
            ehl_avg = f.sort_values().iloc[1:-1].mean() if len(f) > 2 else s_avg
                
            return w_avg, s_avg, ehl_avg
        
        # Calculate averages for different time periods
        all_w, all_s, all_ehl = calc_avgs(factors, weights)
        w3, s3, ehl3 = calc_avgs(factors, weights, 3)
        w5, s5, ehl5 = calc_avgs(factors, weights, 5)
        w10, s10, ehl10 = calc_avgs(factors, weights, 10)

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
            'weighted_all': all_w, 'simple_all': all_s, 'avg_exclude_high_low_all': all_ehl,
            'weighted_3yr': w3, 'simple_3yr': s3, 'avg_exclude_high_low_3yr': ehl3,
            'weighted_5yr': w5, 'simple_5yr': s5, 'avg_exclude_high_low_5yr': ehl5,
            'weighted_10yr': w10, 'simple_10yr': s10, 'avg_exclude_high_low_10yr': ehl10,
        })
    
    # Group by measure and interval, apply calculations
    df_summary = (df_with_ldfs
                  .groupby(['measure', 'interval'], observed=True)
                  .apply(calculate_group_summary, include_groups=False)
                  .reset_index())
    
    # Preserve categorical types
    df_summary['measure'] = pd.Categorical(df_summary['measure'], categories=unique_measures)
    df_summary['interval'] = pd.Categorical(df_summary['interval'], categories=interval_categories, ordered=True)
    
    # Round all average columns to 4 decimal places
    avg_cols = ['weighted_all', 'simple_all', 'avg_exclude_high_low_all',
                'weighted_3yr', 'simple_3yr', 'avg_exclude_high_low_3yr',
                'weighted_5yr', 'simple_5yr', 'avg_exclude_high_low_5yr',
                'weighted_10yr', 'simple_10yr', 'avg_exclude_high_low_10yr',
                'cv_3yr', 'cv_5yr', 'cv_10yr',
                'slope_3yr', 'slope_5yr', 'slope_10yr']
    for col in avg_cols:
        if col in df_summary.columns:
            df_summary[col] = df_summary[col].round(4)
    
    return df_summary


if __name__ == "__main__":
    """Test the calculate_ldf_averages function."""
    # Read enhanced data from step 2
    input_file = OUTPUT_PATH + f"2_{METHOD_ID}_enhanced.parquet"
    df_enhanced = pd.read_parquet(input_file)
    print(f"Loaded {len(df_enhanced)} rows, {df_enhanced['ldf'].notna().sum()} with LDFs")
    print(f"Measures: {df_enhanced['measure'].unique().tolist()}")
    
    # Calculate LDF summary
    df_summary = calculate_ldf_averages(df_enhanced)
    print(f"\nCalculated {len(df_summary)} summary rows")
    
    # Display summary by measure
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.float_format', '{:.4f}'.format)
    
    # Save output - parquet preserves categorical types, CSV for inspection
    df_summary.to_parquet(OUTPUT_PATH + f"4_{METHOD_ID}_ldf_averages.parquet", index=False)
    df_summary.to_csv(OUTPUT_PATH + f"4_{METHOD_ID}_ldf_averages.csv", index=False)
    print(f"\nSaved to: {OUTPUT_PATH}4_{METHOD_ID}_ldf_averages.[parquet|csv]")
    
    # Check for prior selections
    prior_selections_path = Path(OUTPUT_PATH) / "../prior-selections.csv"
    if prior_selections_path.exists():
        df_prior = pd.read_csv(prior_selections_path)
        print(f"\nFound {len(df_prior)} prior selections:")
        for _, row in df_prior.iterrows():
            print(f"  {row['measure']} | {row['interval']}: {row['selection']:.4f}")
    else:
        print("\nNo prior selections found (optional)")



"""
goal: Calculate LDF averages and select between them to set baseline selections which the user can then override.
contents:
    calculate_ldf_summary(): Calculate LDF averages and QA metrics by measure and development interval.
"""

import pandas as pd
import numpy as np

# Replace when using this file in an actual project:
OUTPUT_PATH = "../test-output/"
METHOD_ID = "chainladder"


def calculate_ldf_summary(df_enhanced: pd.DataFrame) -> pd.DataFrame:
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
        - weighted_all, simple_all, medial_all: Averages using all data
        - weighted_3yr, simple_3yr, medial_3yr: Averages using last 3 periods
        - weighted_5yr, simple_5yr, medial_5yr: Averages using last 5 periods
        - cv: Coefficient of variation (volatility measure)
        - slope: Linear trend slope
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
            """Calculate weighted, simple, and medial averages."""
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
            
            # Medial average (exclude highest and lowest)
            m_avg = f.sort_values().iloc[1:-1].mean() if len(f) > 2 else s_avg
                
            return w_avg, s_avg, m_avg
        
        # Calculate averages for different time periods
        all_w, all_s, all_m = calc_avgs(factors, weights)
        w3, s3, m3 = calc_avgs(factors, weights, 3)
        w5, s5, m5 = calc_avgs(factors, weights, 5)
        
        # Calculate QA metrics
        if len(factors) > 1:
            # Coefficient of variation
            cv = factors.std() / factors.mean() if factors.mean() != 0 else 0.0
            
            # Trend calculation (simple linear slope)
            if len(factors) >= 3:
                y = factors.values
                x = np.arange(len(y))
                slope = np.polyfit(x, y, 1)[0]
            else:
                slope = 0.0
        else:
            cv = 0.0
            slope = 0.0
        
        # Return as Series with all values
        return pd.Series({
            'weighted_all': all_w, 'simple_all': all_s, 'medial_all': all_m,
            'weighted_3yr': w3, 'simple_3yr': s3, 'medial_3yr': m3,
            'weighted_5yr': w5, 'simple_5yr': s5, 'medial_5yr': m5,
            'cv': round(cv, 4),
            'slope': round(slope, 4)
        })
    
    # Group by measure and interval, apply calculations
    df_summary = (df_with_ldfs
                  .groupby(['measure', 'interval'], observed=True)
                  .apply(calculate_group_summary, include_groups=False)
                  .reset_index())
    
    # Preserve categorical types
    df_summary['measure'] = pd.Categorical(df_summary['measure'], categories=unique_measures)
    df_summary['interval'] = pd.Categorical(df_summary['interval'], categories=interval_categories, ordered=True)
    
    # Round all average columns to 4 decimal places (cv and slope already rounded)
    avg_cols = ['weighted_all', 'simple_all', 'medial_all',
                'weighted_3yr', 'simple_3yr', 'medial_3yr',
                'weighted_5yr', 'simple_5yr', 'medial_5yr']
    for col in avg_cols:
        if col in df_summary.columns:
            df_summary[col] = df_summary[col].round(4)
    
    return df_summary


if __name__ == "__main__":
    """Test the calculate_ldf_summary function."""
    # Read enhanced data from step 2
    input_file = OUTPUT_PATH + f"2_{METHOD_ID}_enhanced_data.parquet"
    df_enhanced = pd.read_parquet(input_file)
    print(f"Loaded {len(df_enhanced)} rows, {df_enhanced['ldf'].notna().sum()} with LDFs")
    print(f"Measures: {df_enhanced['measure'].unique().tolist()}")
    
    # Calculate LDF summary (averages + QA metrics)
    df_summary = calculate_ldf_summary(df_enhanced)
    print(f"\nCalculated {len(df_summary)} summary rows")
    
    # Display summary by measure
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.float_format', '{:.4f}'.format)
    
    print("\nLDF Summary (Weighted All + QA Metrics):")
    for measure in df_summary['measure'].unique():
        measure_data = df_summary[df_summary['measure'] == measure]
        print(f"\n  {measure}:")
        for _, row in measure_data.iterrows():
            print(f"    {row['interval']}: LDF={row['weighted_all']:.4f}, CV={row['cv']:.4f}, Slope={row['slope']:.4f}")
    
    # Save output - parquet preserves categorical types, CSV for inspection
    df_summary.to_parquet(OUTPUT_PATH + f"4_{METHOD_ID}_ldf_summary.parquet", index=False)
    df_summary.to_csv(OUTPUT_PATH + f"4_{METHOD_ID}_ldf_summary.csv", index=False)
    print(f"\nSaved to: {OUTPUT_PATH}4_{METHOD_ID}_ldf_summary.[parquet|csv]")


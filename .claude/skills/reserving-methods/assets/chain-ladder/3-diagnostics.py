"""
goal: Create diagnostics that will support LDF selection. All operations are performed in long format using groupby and merge operations.
contents:
 calculate_diagnostics(): Calculate actuarial diagnostics from enhanced triangle data to help with LDF selection.
"""

import pandas as pd
import numpy as np
from typing import Optional

# Replace when using this file in an actual project:
OUTPUT_PATH = "../test-output/"
METHOD_ID = "chainladder"


def calculate_diagnostics(df_enhanced: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate actuarial diagnostics to help with LDF selection decisions.
    
    Diagnostics include:
    - Severities (Incurred/Paid per claim)
    - Paid to Incurred ratios
    - Case Reserves
    - Open claim counts
    - Closure rates
    - Loss rates (if exposure provided)
    
    Args:
        df_enhanced: Enhanced long format DataFrame from 2-enhance-data.py
                     Should have columns: period, age, value, measure, source, etc.
        exposure: Optional DataFrame with exposure data for calculating rates
    
    Returns:
        Single DataFrame in long format with columns: period, age, and one column per diagnostic
    """
    # Get all unique period/age combinations from the data
    base_data = df_enhanced[['period', 'age']].drop_duplicates().reset_index(drop=True)
    
    # Create separate dataframes for each measure (still in long format)
    # Aggregate if there are multiple sources
    measure_dfs = {}
    for measure in df_enhanced['measure'].unique():
        measure_subset = df_enhanced[df_enhanced['measure'] == measure].copy()
        
        # Group by period and age, taking first value if duplicates
        grouped = measure_subset.groupby(['period', 'age'], observed=True)['value'].first().reset_index()
        
        # Store with standardized key
        key = measure.lower().replace(' ', '_')
        measure_dfs[key] = grouped.rename(columns={'value': key})
    
    # Start with base data
    result_df = base_data.copy()
    
    # Helper function to merge a measure into result
    def merge_measure(measure_key):
        if measure_key in measure_dfs:
            return measure_dfs[measure_key]
        return None
    
    # Merge all measures we need for calculations
    for measure_key in ['incurred_loss', 'paid_loss', 'reported_count', 'closed_count']:
        measure_df = merge_measure(measure_key)
        if measure_df is not None:
            result_df = result_df.merge(measure_df, on=['period', 'age'], how='left')
    
    # Calculate cumulative diagnostics (simple operations on columns)
    
    # Incurred Severity (cumulative)
    if 'incurred_loss' in result_df.columns and 'reported_count' in result_df.columns:
        result_df['incurred_severity'] = np.where(
            result_df['incurred_loss'] == 0,
            0,
            result_df['incurred_loss'] / result_df['reported_count'].replace(0, np.nan)
        )
    
    # Paid Severity (cumulative)
    if 'paid_loss' in result_df.columns and 'closed_count' in result_df.columns:
        result_df['paid_severity'] = np.where(
            result_df['paid_loss'] == 0,
            0,
            result_df['paid_loss'] / result_df['closed_count'].replace(0, np.nan)
        )
    
    # Paid to Incurred ratio
    if 'paid_loss' in result_df.columns and 'incurred_loss' in result_df.columns:
        result_df['paid_to_incurred'] = np.where(
            result_df['paid_loss'] == 0,
            0,
            result_df['paid_loss'] / result_df['incurred_loss'].replace(0, np.nan)
        )
    
    # Case Reserves
    if 'incurred_loss' in result_df.columns and 'paid_loss' in result_df.columns:
        result_df['case_reserves'] = result_df['incurred_loss'] - result_df['paid_loss']
    
    # Open Counts
    if 'reported_count' in result_df.columns and 'closed_count' in result_df.columns:
        result_df['open_counts'] = result_df['reported_count'] - result_df['closed_count']
    
    # Average Case Reserves
    if all(col in result_df.columns for col in ['incurred_loss', 'paid_loss', 'reported_count', 'closed_count']):
        reserves = result_df['incurred_loss'] - result_df['paid_loss']
        opens = result_df['reported_count'] - result_df['closed_count']
        result_df['average_case_reserves'] = np.where(
            reserves == 0,
            0,
            reserves / opens.replace(0, np.nan)
        )
    
    # Cumulative Closure Rate
    if 'closed_count' in result_df.columns and 'reported_count' in result_df.columns:
        result_df['cumulative_closure_rate'] = np.where(
            result_df['closed_count'] == 0,
            0,
            result_df['closed_count'] / result_df['reported_count'].replace(0, np.nan)
        )
    
    # Calculate incremental diagnostics using groupby and shift
    # Sort by period and age to ensure proper ordering for shift operations
    result_df = result_df.sort_values(['period', 'age']).reset_index(drop=True)
    
    # For incremental calculations, we need to compute differences within each period
    for col in ['incurred_loss', 'paid_loss', 'reported_count', 'closed_count']:
        if col in result_df.columns:
            # Create incremental column by grouping by period and taking diff
            result_df[f'{col}_incr'] = result_df.groupby('period', observed=True)[col].diff()
            # First age for each period should be the cumulative value
            result_df[f'{col}_incr'] = result_df[f'{col}_incr'].fillna(result_df[col])
    
    # Incurred Severity (incremental)
    if 'incurred_loss_incr' in result_df.columns and 'reported_count_incr' in result_df.columns:
        result_df['incurred_severity_incr'] = np.where(
            result_df['incurred_loss_incr'] == 0,
            0,
            result_df['incurred_loss_incr'] / result_df['reported_count_incr'].replace(0, np.nan)
        )
    
    # Paid Severity (incremental)
    if 'paid_loss_incr' in result_df.columns and 'closed_count_incr' in result_df.columns:
        result_df['paid_severity_incr'] = np.where(
            result_df['paid_loss_incr'] == 0,
            0,
            result_df['paid_loss_incr'] / result_df['closed_count_incr'].replace(0, np.nan)
        )
    
    # Incremental Closure Rate
    if 'closed_count_incr' in result_df.columns and 'reported_count_incr' in result_df.columns:
        result_df['incremental_closure_rate'] = np.where(
            result_df['closed_count_incr'] == 0,
            0,
            result_df['closed_count_incr'] / result_df['reported_count_incr'].replace(0, np.nan)
        )
    
    # Drop temporary incremental columns used for calculation
    temp_cols = [col for col in result_df.columns if col.endswith('_incr') and col not in [
        'incurred_severity_incr', 'paid_severity_incr', 'incremental_closure_rate'
    ]]
    result_df = result_df.drop(columns=temp_cols)
    
    # Drop the raw measure columns, keep only diagnostics
    measure_cols = ['incurred_loss', 'paid_loss', 'reported_count', 'closed_count']
    result_df = result_df.drop(columns=[col for col in measure_cols if col in result_df.columns])
    
    # Ensure categorical types
    result_df['period'] = result_df['period'].astype('category')
    result_df['age'] = result_df['age'].astype('category')
    
    return result_df


if __name__ == "__main__":
    """Test the calculate_diagnostics function."""
    # Read enhanced data from step 2
    input_file = OUTPUT_PATH + f"2_{METHOD_ID}_enhanced_data.parquet"
    df = pd.read_parquet(input_file)
    print(f"Loaded {len(df)} rows, {df['measure'].nunique()} measures")
    
    # Calculate diagnostics
    diagnostics_df = calculate_diagnostics(df)
    print(f"Calculated {len(diagnostics_df.columns) - 2} diagnostic columns")
    
    # Display sample
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.float_format', lambda x: f'{x:.2f}')
    print("\nSample with non-null diagnostics:")
    sample = diagnostics_df.dropna(subset=['incurred_severity', 'paid_severity'], how='all').head(10)
    print(sample)
    
    # Round all numeric columns to 4 decimal places
    numeric_cols = diagnostics_df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        diagnostics_df[col] = diagnostics_df[col].round(4)
    
    # Save outputs
    diagnostics_df.to_parquet(OUTPUT_PATH + f"3_{METHOD_ID}_diagnostics.parquet", index=False)
    diagnostics_df.to_csv(OUTPUT_PATH + f"3_{METHOD_ID}_diagnostics.csv", index=False)
    print(f"\nSaved to: {OUTPUT_PATH}3_{METHOD_ID}_diagnostics.[parquet|csv]")
    print("parquet preserves categorical types, CSV for inspection")

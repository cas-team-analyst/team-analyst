# Calculates various statistics that help actuaries spot patterns and anomalies in the claims
# data. Computes metrics like average claim severity, payment percentages, closure rates, and
# other diagnostic measures that inform decisions about future claim development.

"""
goal: Create diagnostics that will support LDF selection. All operations are performed in long format using groupby and merge operations.
contents:
 calculate_diagnostics(): Calculate actuarial diagnostics from enhanced triangle data to help with LDF selection.

run-note: When copied to a project, run from the scripts/ directory:
    cd scripts/
    python 1c-diagnostics.py
"""

import pandas as pd
import numpy as np
from typing import Optional

from modules import config

# Paths from modules/config.py — override here if needed:
OUTPUT_PATH = config.PROCESSED_DATA
METHOD_ID   = "chainladder"


def calculate_diagnostics(df_enhanced: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate actuarial diagnostics to help with LDF selection decisions.
    
    Diagnostics include:
    - Severities (Incurred/Paid per claim)
    - Paid to Incurred ratios
    - Average Case Reserve (case reserves per open claim)
    - Open claim counts
    - Claim closure rate (cumulative) and incremental closure rate
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
    # Each diagnostic checks for required columns before calculation
    
    # Incurred Severity (cumulative) - requires incurred_loss and reported_count
    if 'incurred_loss' in result_df.columns and 'reported_count' in result_df.columns:
        result_df['incurred_severity'] = np.where(
            result_df['incurred_loss'] == 0,
            0,
            result_df['incurred_loss'] / result_df['reported_count'].replace(0, np.nan)
        )
    
    # Paid Severity (cumulative) - requires paid_loss and closed_count
    if 'paid_loss' in result_df.columns and 'closed_count' in result_df.columns:
        result_df['paid_severity'] = np.where(
            result_df['paid_loss'] == 0,
            0,
            result_df['paid_loss'] / result_df['closed_count'].replace(0, np.nan)
        )
    
    # Paid to Incurred ratio - requires paid_loss and incurred_loss
    if 'paid_loss' in result_df.columns and 'incurred_loss' in result_df.columns:
        result_df['paid_to_incurred'] = np.where(
            result_df['paid_loss'] == 0,
            0,
            result_df['paid_loss'] / result_df['incurred_loss'].replace(0, np.nan)
        )
    
    # Open Counts - requires reported_count and closed_count
    if 'reported_count' in result_df.columns and 'closed_count' in result_df.columns:
        result_df['open_counts'] = result_df['reported_count'] - result_df['closed_count']
    
    # Average Case Reserves - requires incurred_loss, paid_loss, reported_count, and closed_count
    if all(col in result_df.columns for col in ['incurred_loss', 'paid_loss', 'reported_count', 'closed_count']):
        reserves = result_df['incurred_loss'] - result_df['paid_loss']
        opens = result_df['reported_count'] - result_df['closed_count']
        result_df['average_case_reserve'] = np.where(
            reserves == 0,
            0,
            reserves / opens.replace(0, np.nan)
        )
    
    # Claim Closure Rate (cumulative) - requires closed_count and reported_count
    if 'closed_count' in result_df.columns and 'reported_count' in result_df.columns:
        result_df['claim_closure_rate'] = np.where(
            result_df['closed_count'] == 0,
            0,
            result_df['closed_count'] / result_df['reported_count'].replace(0, np.nan)
        )
    
    # Calculate incremental diagnostics using groupby and shift
    # Sort by period and age to ensure proper ordering for shift operations
    result_df = result_df.sort_values(['period', 'age']).reset_index(drop=True)
    
    # For incremental calculations, we need to compute differences within each period
    # Only create incremental columns for measures that exist in the data
    available_measures = ['incurred_loss', 'paid_loss', 'reported_count', 'closed_count']
    for col in available_measures:
        if col in result_df.columns:
            # Create incremental column by grouping by period and taking diff
            result_df[f'{col}_incr'] = result_df.groupby('period', observed=True)[col].diff()
            # First age for each period should be the cumulative value
            result_df[f'{col}_incr'] = result_df[f'{col}_incr'].fillna(result_df[col])
    
    # Incurred Severity (incremental) - requires incurred_loss and reported_count
    if 'incurred_loss_incr' in result_df.columns and 'reported_count_incr' in result_df.columns:
        result_df['incremental_incurred_severity'] = np.where(
            result_df['incurred_loss_incr'] == 0,
            0,
            result_df['incurred_loss_incr'] / result_df['reported_count_incr'].replace(0, np.nan)
        )
    
    # Paid Severity (incremental) - requires paid_loss and closed_count
    if 'paid_loss_incr' in result_df.columns and 'closed_count_incr' in result_df.columns:
        result_df['incremental_paid_severity'] = np.where(
            result_df['paid_loss_incr'] == 0,
            0,
            result_df['paid_loss_incr'] / result_df['closed_count_incr'].replace(0, np.nan)
        )
    
    # Incremental Closure Rate - requires closed_count and reported_count
    if 'closed_count_incr' in result_df.columns and 'reported_count_incr' in result_df.columns:
        result_df['incremental_closure_rate'] = np.where(
            result_df['closed_count_incr'] == 0,
            0,
            result_df['closed_count_incr'] / result_df['reported_count_incr'].replace(0, np.nan)
        )
    
    # Drop temporary incremental columns used for calculation
    temp_cols = [col for col in result_df.columns if col.endswith('_incr') and col not in [
        'incremental_incurred_severity', 'incremental_paid_severity', 'incremental_closure_rate'
    ]]
    result_df = result_df.drop(columns=temp_cols)
    
    # Rename reported_count to reported_claims (keep as diagnostic)
    if 'reported_count' in result_df.columns:
        result_df = result_df.rename(columns={'reported_count': 'reported_claims'})

    # Drop the raw measure columns, keep only diagnostics
    measure_cols = ['incurred_loss', 'paid_loss', 'closed_count']
    result_df = result_df.drop(columns=[col for col in measure_cols if col in result_df.columns])
    
    # Ensure categorical types
    result_df['period'] = result_df['period'].astype('category')
    result_df['age'] = result_df['age'].astype('category')
    
    return result_df


if __name__ == "__main__":
    """Test the calculate_diagnostics function."""
    # Read enhanced data from step 2
    input_file = OUTPUT_PATH + f"2_enhanced.parquet"
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
    # Build subset list dynamically based on available columns
    sample_cols = [col for col in ['incurred_severity', 'paid_severity'] if col in diagnostics_df.columns]
    if sample_cols:
        sample = diagnostics_df.dropna(subset=sample_cols, how='all').head(10)
    else:
        sample = diagnostics_df.head(10)
    print(sample)
    
    # Round all numeric columns to 4 decimal places
    numeric_cols = diagnostics_df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        diagnostics_df[col] = diagnostics_df[col].round(4)
    
    # Save outputs
    diagnostics_df.to_parquet(OUTPUT_PATH + f"3_diagnostics.parquet", index=False)
    diagnostics_df.to_csv(OUTPUT_PATH + f"3_diagnostics.csv", index=False)
    print(f"\nSaved to: {OUTPUT_PATH}3_diagnostics.[parquet|csv]")
    print("parquet preserves categorical types, CSV for inspection")

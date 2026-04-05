# Computes initial expected ultimates by multiplying expected loss rates and frequencies
# by exposure to get expected ultimate losses and claim counts for each period.

"""
goal: Calculate Initial Expected ultimates for all periods and measures.

inputs:
    ../processed-data/1_triangles.parquet - Triangle data including Exposure measure (diagonal used)
    ../processed-data/1_expected_loss_rates.parquet - Expected loss rates and frequencies by period

outputs:
    ../ultimates/initial-expected.parquet - Expected ultimates by period and measure
    ../ultimates/initial-expected.csv - Same data in CSV format

run-note: When copied to a project, run from the scripts/ directory:
    cd scripts/
    python 3-initial-expected.py
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Replace these when using this file in an actual project:
INPUT_TRIANGLE_DATA = "../processed-data/1_triangles.parquet"
INPUT_EXPECTED_RATES = "../processed-data/1_expected_loss_rates.parquet"
OUTPUT_PATH = "../ultimates/"


def extract_exposure_diagonal(triangle_data: pd.DataFrame) -> dict:
    """
    Extract the latest (diagonal) exposure value for each period.
    
    The diagonal represents the most mature value for each period, which is
    the total exposure for that period.
    
    Args:
        triangle_data: DataFrame with triangle data including Exposure measure
    
    Returns:
        Dictionary mapping period (str) to exposure value (float)
    """
    # Filter to Exposure measure only
    exposure_data = triangle_data[triangle_data['measure'] == 'Exposure'].copy()
    
    if exposure_data.empty:
        raise ValueError("No Exposure measure found in triangle data. Initial Expected calculation requires Exposure.")
    
    # For each period, get the latest age (diagonal value)
    # Group by period and take the last value (most mature)
    exposure_diagonal = exposure_data.groupby('period', observed=True).agg({
        'value': 'last',  # Last value is the most mature (diagonal)
        'age': 'last'
    }).reset_index()
    
    # Convert to dictionary
    exposure_dict = dict(zip(
        exposure_diagonal['period'].astype(str),
        exposure_diagonal['value'].astype(float)
    ))
    
    print(f"  Extracted exposure for {len(exposure_dict)} period(s)")
    return exposure_dict


def compute_initial_expected_ultimates(expected_rates: pd.DataFrame, exposure: dict) -> pd.DataFrame:
    """
    Compute initial expected ultimates by multiplying rates and frequencies by exposure.
    
    For each period:
    - Expected Loss Ultimate = Expected Loss Rate * Exposure (applies to Incurred Loss and Paid Loss)
    - Expected Count Ultimate = Expected Frequency * Exposure (applies to Reported Count and Closed Count)
    
    Args:
        expected_rates: DataFrame with columns: period, expected_loss_rate, expected_freq
        exposure: Dictionary mapping period to exposure value
    
    Returns:
        DataFrame with columns: period, measure, expected_ultimate
    """
    rows = []
    
    for _, row in expected_rates.iterrows():
        period = str(row['period'])
        
        # Get exposure for this period
        exp = exposure.get(period)
        if exp is None or pd.isna(exp):
            print(f"  Warning: No exposure found for period {period}, skipping")
            continue
        
        # Compute loss ultimate (applies to both Incurred and Paid)
        if pd.notna(row.get('expected_loss_rate')):
            loss_ultimate = float(row['expected_loss_rate']) * float(exp)
            rows.append({
                'period': period,
                'measure': 'Incurred Loss',
                'expected_ultimate': loss_ultimate
            })
            rows.append({
                'period': period,
                'measure': 'Paid Loss',
                'expected_ultimate': loss_ultimate
            })
        
        # Compute count ultimate (applies to both Reported and Closed)
        if pd.notna(row.get('expected_freq')):
            count_ultimate = float(row['expected_freq']) * float(exp)
            rows.append({
                'period': period,
                'measure': 'Reported Count',
                'expected_ultimate': count_ultimate
            })
            rows.append({
                'period': period,
                'measure': 'Closed Count',
                'expected_ultimate': count_ultimate
            })
    
    if not rows:
        raise ValueError("No initial expected ultimates could be computed. Check that expected_loss_rate and expected_freq have values.")
    
    result_df = pd.DataFrame(rows)
    
    # Convert to appropriate types
    result_df['period'] = result_df['period'].astype(str)
    result_df['measure'] = result_df['measure'].astype('category')
    result_df['expected_ultimate'] = result_df['expected_ultimate'].astype(float)
    
    print(f"  Computed {len(result_df)} expected ultimate(s) across {len(result_df['period'].unique())} period(s)")
    
    return result_df


if __name__ == "__main__":
    print("Computing Initial Expected ultimates...")
    
    # Load triangle data
    print(f"\nReading triangle data from: {INPUT_TRIANGLE_DATA}")
    df_triangles = pd.read_parquet(INPUT_TRIANGLE_DATA)
    
    # Load expected rates (optional - skip if not available)
    if not Path(INPUT_EXPECTED_RATES).exists():
        print("  Expected loss rates file not found (optional). Skipping Initial Expected calculation.")
        sys.exit(0)
    print(f"Reading expected rates from: {INPUT_EXPECTED_RATES}")
    
    df_expected_rates = pd.read_parquet(INPUT_EXPECTED_RATES)
    
    # Extract exposure diagonal
    print("\nExtracting exposure values...")
    exposure_dict = extract_exposure_diagonal(df_triangles)
    
    # Compute initial expected ultimates
    print("\nComputing initial expected ultimates...")
    df_ie = compute_initial_expected_ultimates(df_expected_rates, exposure_dict)
    
    # Create output directory if it doesn't exist
    output_dir = Path(OUTPUT_PATH)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save results
    output_parquet = output_dir / "initial-expected.parquet"
    output_csv = output_dir / "initial-expected.csv"
    
    df_ie.to_parquet(output_parquet, index=False)
    df_ie.to_csv(output_csv, index=False)
    
    print(f"\nSaved initial expected ultimates:")
    print(f"  Parquet: {output_parquet}")
    print(f"  CSV: {output_csv}")
    
    print("\nSample of results:")
    print(df_ie.head(10).to_string(index=False))
    
    print("\nInitial Expected calculation complete!")
